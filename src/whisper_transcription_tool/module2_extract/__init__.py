"""
Video-Audio extraction module for the Whisper Transcription Tool.
Handles extraction of audio from video files using FFmpeg.
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.config import load_config
from ..core.events import EventType, publish
from ..core.exceptions import DependencyError, ExtractionError
from ..core.logging_setup import get_logger
from ..core.models import ExtractionRequest, ExtractionResult
from ..core.utils import check_program_exists, ensure_directory_exists, get_output_path, run_command

logger = get_logger(__name__)


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed.
    
    Returns:
        True if installed, False otherwise
    """
    return check_program_exists("ffmpeg")


def get_ffmpeg_path(config: Optional[Dict] = None) -> str:
    """
    Get the path to the FFmpeg binary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to FFmpeg binary
    """
    if config and "ffmpeg" in config and "binary_path" in config["ffmpeg"]:
        binary_path = config["ffmpeg"]["binary_path"]
        if os.path.exists(binary_path):
            return binary_path
    
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    
    # Check common locations based on platform
    common_locations = []
    
    # Standard Unix-like system paths
    if platform.system() != "Windows":
        common_locations.extend([
            "/usr/local/bin/ffmpeg",
            "/usr/bin/ffmpeg",
            "/opt/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg"
        ])
    else:  # Windows paths
        # Check Program Files directories
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        common_locations.extend([
            os.path.join(program_files, "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(program_files_x86, "ffmpeg", "bin", "ffmpeg.exe"),
            "C:\\ffmpeg\\bin\\ffmpeg.exe"
        ])
    
    for location in common_locations:
        if os.path.exists(location) and os.access(location, os.X_OK):
            return location
    
    raise DependencyError("FFmpeg not found. Please install FFmpeg or specify the binary path in the configuration.")


def get_ffmpeg_version(ffmpeg_path: str) -> Optional[str]:
    """
    Get the FFmpeg version.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        
    Returns:
        FFmpeg version string if available, None otherwise
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Extract version from first line
            return result.stdout.split("\n")[0]
        
        return None
    except Exception as e:
        logger.error(f"Error getting FFmpeg version: {e}")
        return None


def extract_audio(
    video_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    audio_format: Optional[str] = None,
    sample_rate: Optional[int] = None,
    config: Optional[Dict] = None
) -> ExtractionResult:
    """
    Extract audio from a video file.
    
    Args:
        video_path: Path to video file
        output_path: Path to save extracted audio
        audio_format: Audio format (wav, mp3, etc.)
        sample_rate: Audio sample rate
        config: Configuration dictionary
        
    Returns:
        ExtractionResult object
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Get FFmpeg configuration
    if audio_format is None and "ffmpeg" in config and "audio_format" in config["ffmpeg"]:
        audio_format = config["ffmpeg"]["audio_format"]
    else:
        audio_format = audio_format or "wav"
    
    if sample_rate is None and "ffmpeg" in config and "sample_rate" in config["ffmpeg"]:
        sample_rate = config["ffmpeg"]["sample_rate"]
    else:
        sample_rate = sample_rate or 16000
    
    # Validate video file
    video_path = str(video_path)
    if not os.path.exists(video_path):
        error_msg = f"Video file not found: {video_path}"
        logger.error(error_msg)
        return ExtractionResult(success=False, error=error_msg)
    
    # Generate output path if not provided
    if output_path is None:
        output_dir = config["output"]["default_directory"] if "output" in config and "default_directory" in config["output"] else None
        output_path = get_output_path(video_path, output_dir, audio_format)
    else:
        output_path = str(output_path)
    
    # Ensure output directory exists
    ensure_directory_exists(os.path.dirname(output_path))
    
    # Publish event
    publish(EventType.EXTRACTION_STARTED, {
        "video_path": video_path,
        "output_path": output_path,
        "audio_format": audio_format,
        "sample_rate": sample_rate
    })
    
    try:
        # Get FFmpeg path
        ffmpeg_path = get_ffmpeg_path(config)
        
        # Prepare command
        cmd = [
            ffmpeg_path,
            "-i", video_path,
            "-vn",  # No video
            "-ar", str(sample_rate),  # Sample rate
            "-ac", "1",  # Mono
            "-y",  # Overwrite output file
            output_path
        ]
        
        # Run FFmpeg
        logger.info(f"Running command: {' '.join(cmd)}")
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode != 0:
            error_msg = f"FFmpeg failed with return code {returncode}: {stderr}"
            logger.error(error_msg)
            publish(EventType.EXTRACTION_FAILED, {
                "video_path": video_path,
                "error": error_msg
            })
            return ExtractionResult(success=False, error=error_msg, stderr=stderr)
        
        # Check if output file was created
        if not os.path.exists(output_path):
            error_msg = f"Output file not created: {output_path}"
            logger.error(error_msg)
            publish(EventType.EXTRACTION_FAILED, {
                "video_path": video_path,
                "error": error_msg
            })
            return ExtractionResult(success=False, error=error_msg)
        
        # Publish success event
        publish(EventType.EXTRACTION_COMPLETED, {
            "video_path": video_path,
            "audio_path": output_path
        })
        
        # Return result
        return ExtractionResult(
            success=True,
            audio_path=output_path,
            video_path=video_path
        )
    
    except Exception as e:
        error_msg = f"Error extracting audio: {str(e)}"
        logger.error(error_msg)
        publish(EventType.EXTRACTION_FAILED, {
            "video_path": video_path,
            "error": error_msg
        })
        return ExtractionResult(success=False, error=error_msg)


def extract_and_transcribe(
    video_path: Union[str, Path],
    output_format: str = "txt",
    language: Optional[str] = None,
    model: str = "large-v3-turbo",
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[Dict] = None
) -> Dict:
    """
    Extract audio from video and transcribe it.
    
    Args:
        video_path: Path to video file
        output_format: Output format for transcription
        language: Language code (None for auto-detection)
        model: Whisper model to use
        output_path: Output file path
        config: Configuration dictionary
        
    Returns:
        Dictionary with extraction and transcription results
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Extract audio
    extraction_result = extract_audio(video_path, config=config)
    
    if not extraction_result.success:
        return {
            "extraction": extraction_result.to_dict(),
            "transcription": {
                "success": False,
                "error": "Audio extraction failed"
            }
        }
    
    # Import transcription module
    from ..module1_transcribe import transcribe_audio
    
    # Transcribe audio
    transcription_result = transcribe_audio(
        extraction_result.audio_path,
        output_format=output_format,
        language=language,
        model=model,
        output_path=output_path,
        config=config
    )
    
    # Return combined result
    return {
        "extraction": extraction_result.to_dict(),
        "transcription": transcription_result.to_dict()
    }


def install_ffmpeg() -> bool:
    """
    Attempt to install FFmpeg.
    
    Returns:
        True if installation was successful, False otherwise
    """
    system = platform.system()
    
    try:
        if system == "Linux":
            # Try apt-get (Debian/Ubuntu)
            cmd = ["sudo", "apt-get", "update"]
            run_command(cmd)
            
            cmd = ["sudo", "apt-get", "install", "-y", "ffmpeg"]
            returncode, stdout, stderr = run_command(cmd)
            
            if returncode == 0:
                logger.info("FFmpeg installed successfully via apt-get")
                return True
        
        elif system == "Darwin":
            # Try brew (macOS)
            cmd = ["brew", "install", "ffmpeg"]
            returncode, stdout, stderr = run_command(cmd)
            
            if returncode == 0:
                logger.info("FFmpeg installed successfully via brew")
                return True
        
        # If we get here, installation failed or is not supported
        logger.error(f"Automatic FFmpeg installation not supported on {system}")
        return False
    
    except Exception as e:
        logger.error(f"Error installing FFmpeg: {e}")
        return False
