"""
LLM model management for the Whisper Transcription Tool.
Handles downloading, caching, and managing LLM models.
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from tqdm import tqdm

from ..core.events import EventType, publish
from ..core.exceptions import ModelError
from ..core.logging_setup import get_logger
from ..core.utils import ensure_directory_exists

logger = get_logger(__name__)

# Common LLM models and their URLs
LLM_MODELS = {
    "mistral-7b": {
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size_mb": 4500,
        "description": "Mistral 7B Instruct v0.2 (Q4_K_M quantization)"
    },
    "llama2-7b": {
        "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
        "size_mb": 4200,
        "description": "Llama 2 7B Chat (Q4_K_M quantization)"
    },
    "phi-2": {
        "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
        "size_mb": 1600,
        "description": "Microsoft Phi-2 (Q4_K_M quantization)"
    }
}


def get_models_directory(config: Optional[Dict] = None) -> str:
    """
    Get the directory where LLM models are stored.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to models directory
    """
    models_dir = str(Path.home() / "llm_models")
    if config and "chatbot" in config and "models_dir" in config["chatbot"]:
        models_dir = config["chatbot"]["models_dir"]
    
    # Ensure models directory exists
    ensure_directory_exists(models_dir)
    
    return models_dir


def list_available_models() -> List[Dict]:
    """
    List all available LLM models that can be downloaded.
    
    Returns:
        List of available model information
    """
    return [
        {
            "name": name,
            "description": info["description"],
            "size_mb": info["size_mb"]
        }
        for name, info in LLM_MODELS.items()
    ]


def list_downloaded_models(config: Optional[Dict] = None) -> List[str]:
    """
    List downloaded LLM models.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of downloaded model names
    """
    models_dir = get_models_directory(config)
    
    # List model files
    downloaded_models = []
    
    for model_name, model_info in LLM_MODELS.items():
        # Check for model file with different extensions
        model_found = False
        for ext in [".gguf", ".bin", ""]:
            model_path = os.path.join(models_dir, f"{model_name}{ext}")
            if os.path.exists(model_path):
                downloaded_models.append(model_name)
                model_found = True
                break
        
        # Also check for model file with full name
        if not model_found:
            model_url = model_info["url"]
            filename = os.path.basename(model_url)
            model_path = os.path.join(models_dir, filename)
            if os.path.exists(model_path):
                downloaded_models.append(model_name)
    
    return downloaded_models


def get_model_path(model_name: str, config: Optional[Dict] = None) -> str:
    """
    Get the path to an LLM model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        Path to model file
    """
    models_dir = get_models_directory(config)
    
    # Check for model file with different extensions
    for ext in [".gguf", ".bin", ""]:
        model_path = os.path.join(models_dir, f"{model_name}{ext}")
        if os.path.exists(model_path):
            return model_path
    
    # Check for model file with full name
    if model_name in LLM_MODELS:
        model_url = LLM_MODELS[model_name]["url"]
        filename = os.path.basename(model_url)
        model_path = os.path.join(models_dir, filename)
        if os.path.exists(model_path):
            return model_path
    
    # If not found, raise an error
    raise ModelError(f"Model {model_name} not found. Please download it first.")


def download_model(model_name: str, config: Optional[Dict] = None, force: bool = False) -> str:
    """
    Download an LLM model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        force: Force download even if model already exists
        
    Returns:
        Path to downloaded model file
    """
    if model_name not in LLM_MODELS:
        raise ModelError(f"Unknown model: {model_name}")
    
    models_dir = get_models_directory(config)
    model_info = LLM_MODELS[model_name]
    model_url = model_info["url"]
    filename = os.path.basename(model_url)
    model_path = os.path.join(models_dir, filename)
    
    # Check if model already exists
    try:
        existing_path = get_model_path(model_name, config)
        if not force:
            logger.info(f"Model {model_name} already exists at {existing_path}")
            return existing_path
    except ModelError:
        pass  # Model not found, continue with download
    
    # Check available disk space
    if platform.system() != "Windows":  # statvfs not available on Windows
        disk_stats = os.statvfs(models_dir)
        free_space = disk_stats.f_frsize * disk_stats.f_bavail
        required_space = model_info["size_mb"] * 1024 * 1024  # Convert MB to bytes
        
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
    if model_name not in LLM_MODELS:
        return {
            "name": model_name,
            "description": "Unknown model",
            "size_mb": "Unknown",
            "downloaded": False
        }
    
    model_info = LLM_MODELS[model_name]
    
    info = {
        "name": model_name,
        "description": model_info["description"],
        "size_mb": model_info["size_mb"],
        "downloaded": False
    }
    
    try:
        model_path = get_model_path(model_name, config)
        info["downloaded"] = True
        info["path"] = model_path
        info["size_bytes"] = os.path.getsize(model_path)
    except ModelError:
        pass
    
    return info
