"""
Model management for the Whisper Transcription Tool.
Handles downloading, caching, and managing Whisper models.
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import requests
from tqdm import tqdm

from ..core.events import EventType, publish
from ..core.exceptions import ModelError
from ..core.logging_setup import get_logger
from ..core.models import WhisperModel
from ..core.utils import ensure_directory_exists

logger = get_logger(__name__)

# Constants
WHISPER_CPP_MODELS_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
DEFAULT_MODEL = WhisperModel.LARGE_V3_TURBO  # Using large-v3-turbo as specified by user

# Model sizes in MB (approximate)
MODEL_SIZES = {
    "tiny": 75,
    "base": 142,
    "small": 466,
    "medium": 1500,
    "large": 3000,
    "large-v3": 3100,
    "large-v3-turbo": 3200,
}


def get_models_directory(config: Optional[Dict] = None) -> str:
    """
    Get the directory where models are stored.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to models directory
    """
    models_dir = str(Path.home() / "whisper_models")
    if config and "whisper" in config and "model_path" in config["whisper"]:
        models_dir = config["whisper"]["model_path"]
    
    # Ensure models directory exists
    ensure_directory_exists(models_dir)
    
    return models_dir


def list_available_models() -> List[str]:
    """
    List all available Whisper models that can be downloaded.
    
    Returns:
        List of available model names
    """
    return [model.value for model in WhisperModel]


def list_downloaded_models(config: Optional[Dict] = None) -> List[str]:
    """
    List downloaded Whisper models.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of downloaded model names
    """
    models_dir = get_models_directory(config)
    
    # List model files
    model_files = []
    for file in os.listdir(models_dir):
        if file.startswith("ggml-") and file.endswith(".bin"):
            model_name = file[5:-4]  # Remove "ggml-" prefix and ".bin" suffix
            model_files.append(model_name)
    
    return model_files


def get_model_path(model_name: str, config: Optional[Dict] = None) -> str:
    """
    Get the path to a Whisper model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        Path to model file
    """
    models_dir = get_models_directory(config)
    
    # Check if model file exists
    model_path = os.path.join(models_dir, f"ggml-{model_name}.bin")
    if os.path.exists(model_path):
        return model_path
    
    # If not, raise an error
    raise ModelError(f"Model {model_name} not found at {model_path}. Please download it first.")


def download_model(model_name: str, config: Optional[Dict] = None, force: bool = False) -> str:
    """
    Download a Whisper model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        force: Force download even if model already exists
        
    Returns:
        Path to downloaded model file
    """
    models_dir = get_models_directory(config)
    
    # Construct model path and URL
    model_path = os.path.join(models_dir, f"ggml-{model_name}.bin")
    model_url = f"{WHISPER_CPP_MODELS_URL}/ggml-{model_name}.bin"
    
    # Check if model already exists
    if os.path.exists(model_path) and not force:
        logger.info(f"Model {model_name} already exists at {model_path}")
        return model_path
    
    # Check available disk space
    if platform.system() != "Windows":  # statvfs not available on Windows
        disk_stats = os.statvfs(models_dir)
        free_space = disk_stats.f_frsize * disk_stats.f_bavail
        required_space = MODEL_SIZES.get(model_name, 3000) * 1024 * 1024  # Convert MB to bytes
        
        if free_space < required_space:
            raise ModelError(
                f"Not enough disk space to download model {model_name}. "
                f"Required: {required_space / (1024 * 1024):.1f} MB, "
                f"Available: {free_space / (1024 * 1024):.1f} MB"
            )
    
    # Download model
    logger.info(f"Downloading model {model_name} from {model_url}")
    publish(EventType.MODEL_DOWNLOAD_STARTED, {"model": model_name, "url": model_url})
    
    try:
        with requests.get(model_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            # Create a temporary file for downloading
            temp_path = model_path + ".download"
            
            with open(temp_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {model_name}") as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                            
                            # Report progress
                            if total_size > 0:
                                progress = (pbar.n / total_size) * 100
                                publish(EventType.PROGRESS_UPDATE, {
                                    "task": "model_download",
                                    "progress": progress,
                                    "model": model_name
                                })
            
            # Move the temporary file to the final location
            shutil.move(temp_path, model_path)
        
        logger.info(f"Model {model_name} downloaded to {model_path}")
        publish(EventType.MODEL_DOWNLOAD_COMPLETED, {"model": model_name, "path": model_path})
        return model_path
    
    except Exception as e:
        # Clean up temporary file if it exists
        temp_path = model_path + ".download"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        logger.error(f"Error downloading model {model_name}: {e}")
        publish(EventType.MODEL_DOWNLOAD_FAILED, {"model": model_name, "error": str(e)})
        raise ModelError(f"Failed to download model {model_name}: {e}")


def ensure_model_exists(model_name: str, config: Optional[Dict] = None) -> str:
    """
    Ensure that a model exists, downloading it if necessary.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        Path to model file
    """
    try:
        return get_model_path(model_name, config)
    except ModelError:
        logger.info(f"Model {model_name} not found, downloading...")
        return download_model(model_name, config)


def delete_model(model_name: str, config: Optional[Dict] = None) -> bool:
    """
    Delete a downloaded model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        model_path = get_model_path(model_name, config)
        os.remove(model_path)
        logger.info(f"Model {model_name} deleted from {model_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting model {model_name}: {e}")
        return False


def get_model_info(model_name: str, config: Optional[Dict] = None) -> Dict:
    """
    Get information about a model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        Dictionary with model information
    """
    models_dir = get_models_directory(config)
    model_path = os.path.join(models_dir, f"ggml-{model_name}.bin")
    
    info = {
        "name": model_name,
        "size_mb": MODEL_SIZES.get(model_name, "Unknown"),
        "downloaded": os.path.exists(model_path),
    }
    
    if info["downloaded"]:
        info["path"] = model_path
        info["size_bytes"] = os.path.getsize(model_path)
    
    return info
