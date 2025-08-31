"""
Utility functions for the Whisper Transcription Tool.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .logging_setup import get_logger

logger = get_logger(__name__)


def run_command(
    cmd: List[str], 
    cwd: Optional[str] = None, 
    env: Optional[Dict[str, str]] = None,
    capture_output: bool = True,
    check: bool = False
) -> Tuple[int, str, str]:
    """
    Run a shell command and return the result.
    
    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory
        env: Environment variables
        capture_output: Whether to capture stdout and stderr
        check: Whether to raise an exception if the command fails
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                check=check
            )
            return result.returncode, "", ""
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return e.returncode, e.stdout if hasattr(e, 'stdout') else "", e.stderr if hasattr(e, 'stderr') else ""
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return -1, "", str(e)


def check_program_exists(program: str) -> bool:
    """
    Check if a program exists in the system PATH.
    
    Args:
        program: Name of the program to check
        
    Returns:
        True if the program exists, False otherwise
    """
    return shutil.which(program) is not None


def ensure_directory_exists(directory: Union[str, Path]) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension without the dot
    """
    return os.path.splitext(str(file_path))[1][1:].lower()


def is_audio_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is an audio file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is an audio file, False otherwise
    """
    audio_extensions = ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac']
    return get_file_extension(file_path) in audio_extensions


def is_video_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a video file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a video file, False otherwise
    """
    video_extensions = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv']
    return get_file_extension(file_path) in video_extensions


def get_output_path(
    input_path: Union[str, Path], 
    output_dir: Optional[Union[str, Path]] = None,
    output_format: str = 'txt'
) -> str:
    """
    Generate an output path based on the input path.
    
    Args:
        input_path: Path to the input file
        output_dir: Directory to save the output file (None for same directory)
        output_format: Output file format
        
    Returns:
        Output file path
    """
    input_path = Path(input_path)
    
    # Use the same directory as the input file if output_dir is not specified
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        ensure_directory_exists(output_dir)
    
    # Generate output filename
    output_filename = f"{input_path.stem}.{output_format}"
    
    return str(output_dir / output_filename)
