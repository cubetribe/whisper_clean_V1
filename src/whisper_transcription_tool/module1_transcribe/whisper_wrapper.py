"""
Whisper.cpp wrapper for the Whisper Transcription Tool.
Handles direct interaction with the Whisper.cpp binary.
"""

import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.exceptions import DependencyError, TranscriptionError
from ..core.logging_setup import get_logger
from ..core.utils import run_command

logger = get_logger(__name__)


def detect_whisper_cpp() -> Optional[str]:
    """
    Detect the Whisper.cpp binary on the system.
    
    Returns:
        Path to whisper binary if found, None otherwise
    """
    # Check common locations
    common_locations = [
        "./whisper",
        "/usr/local/bin/whisper",
        "/usr/bin/whisper",
        str(Path.home() / "whisper.cpp" / "main"),
        str(Path.home() / "whisper.cpp" / "whisper")
    ]
    
    # Check if whisper is in PATH
    whisper_path = subprocess.run(
        ["which", "whisper"], 
        capture_output=True, 
        text=True
    ).stdout.strip()
    
    if whisper_path:
        return whisper_path
    
    # Check common locations
    for location in common_locations:
        if os.path.exists(location) and os.access(location, os.X_OK):
            return location
    
    return None


def check_whisper_cpp_compatibility() -> Tuple[bool, str]:
    """
    Check if Whisper.cpp is compatible with the current system.
    
    Returns:
        Tuple of (compatible, message)
    """
    system = platform.system()
    machine = platform.machine()
    
    # Check for Apple Silicon
    if system == "Darwin" and machine == "arm64":
        return True, "Apple Silicon detected, Whisper.cpp should work with Metal acceleration."
    
    # Check for other systems
    if system == "Linux":
        return True, "Linux detected, Whisper.cpp should work."
    
    if system == "Darwin":
        return True, "macOS detected, Whisper.cpp should work."
    
    if system == "Windows":
        return True, "Windows detected, Whisper.cpp should work but may require additional setup."
    
    return False, f"Unsupported system: {system} {machine}"


def run_whisper_cpp(
    whisper_path: str,
    model_path: str,
    audio_path: str,
    output_dir: str,
    language: Optional[str] = None,
    threads: int = 4,
    use_metal: bool = False,
    translate: bool = False,
    output_formats: List[str] = ["txt"],
    verbose: bool = False
) -> Tuple[int, str, str]:
    """
    Run Whisper.cpp with the specified parameters.
    
    Args:
        whisper_path: Path to whisper binary
        model_path: Path to model file
        audio_path: Path to audio file
        output_dir: Directory to save output files
        language: Language code (None for auto-detection)
        threads: Number of threads to use
        use_metal: Whether to use Metal acceleration on Apple Silicon
        translate: Whether to translate to English
        output_formats: List of output formats
        verbose: Whether to enable verbose output
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Prepare command
    cmd = [
        whisper_path,
        "-m", model_path,
        "-f", audio_path,
        "-t", str(threads),
        "-of", os.path.join(output_dir, "output")
    ]
    
    # Add language if specified
    if language:
        cmd.extend(["-l", language])
    
    # Add output formats
    for fmt in output_formats:
        cmd.append(f"-o{fmt}")
    
    # Add Metal flag if requested and on Apple Silicon
    if use_metal and platform.system() == "Darwin" and platform.machine() == "arm64":
        cmd.append("-metal")
    
    # Add translate flag if requested
    if translate:
        cmd.append("-tr")
    
    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")
    
    # Run command
    logger.debug(f"Running Whisper.cpp command: {' '.join(cmd)}")
    return run_command(cmd)


def get_whisper_cpp_version(whisper_path: str) -> Optional[str]:
    """
    Get the version of Whisper.cpp.
    
    Args:
        whisper_path: Path to whisper binary
        
    Returns:
        Version string if available, None otherwise
    """
    try:
        result = subprocess.run(
            [whisper_path, "-h"],
            capture_output=True,
            text=True
        )
        
        # Try to extract version from help output
        for line in result.stdout.split("\n"):
            if "version" in line.lower():
                return line.strip()
        
        return None
    except Exception as e:
        logger.error(f"Error getting Whisper.cpp version: {e}")
        return None


def compile_whisper_cpp(target_dir: str) -> Optional[str]:
    """
    Compile Whisper.cpp from source.
    
    Args:
        target_dir: Directory to clone and compile Whisper.cpp
        
    Returns:
        Path to compiled whisper binary if successful, None otherwise
    """
    logger.info(f"Compiling Whisper.cpp in {target_dir}")
    
    try:
        # Clone repository
        os.makedirs(target_dir, exist_ok=True)
        clone_cmd = ["git", "clone", "https://github.com/ggerganov/whisper.cpp", target_dir]
        returncode, stdout, stderr = run_command(clone_cmd)
        
        if returncode != 0:
            logger.error(f"Error cloning Whisper.cpp repository: {stderr}")
            return None
        
        # Compile
        make_cmd = ["make"]
        
        # Check for Apple Silicon and enable Metal if available
        if platform.system() == "Darwin" and platform.machine() == "arm64":
            make_cmd.append("WHISPER_COREML=1")
        
        returncode, stdout, stderr = run_command(make_cmd, cwd=target_dir)
        
        if returncode != 0:
            logger.error(f"Error compiling Whisper.cpp: {stderr}")
            return None
        
        # Check if binary was created
        binary_path = os.path.join(target_dir, "main")
        if os.path.exists(binary_path) and os.access(binary_path, os.X_OK):
            logger.info(f"Successfully compiled Whisper.cpp at {binary_path}")
            return binary_path
        
        return None
    except Exception as e:
        logger.error(f"Error compiling Whisper.cpp: {e}")
        return None


def parse_whisper_output(output_dir: str, formats: List[str]) -> Dict:
    """
    Parse Whisper.cpp output files.
    
    Args:
        output_dir: Directory containing output files
        formats: List of output formats to parse
        
    Returns:
        Dictionary with parsed output
    """
    result = {}
    
    # Parse text output
    if "txt" in formats:
        txt_path = os.path.join(output_dir, "output.txt")
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                result["text"] = f.read()
    
    # Parse JSON output
    if "json" in formats:
        json_path = os.path.join(output_dir, "output.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                result["json"] = json.load(f)
    
    # Parse SRT output
    if "srt" in formats:
        srt_path = os.path.join(output_dir, "output.srt")
        if os.path.exists(srt_path):
            with open(srt_path, "r", encoding="utf-8") as f:
                result["srt"] = f.read()
    
    # Parse VTT output
    if "vtt" in formats:
        vtt_path = os.path.join(output_dir, "output.vtt")
        if os.path.exists(vtt_path):
            with open(vtt_path, "r", encoding="utf-8") as f:
                result["vtt"] = f.read()
    
    return result
