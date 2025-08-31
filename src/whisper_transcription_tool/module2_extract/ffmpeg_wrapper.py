"""
FFmpeg wrapper for the Whisper Transcription Tool.
Handles direct interaction with the FFmpeg binary.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.exceptions import DependencyError
from ..core.logging_setup import get_logger
from ..core.utils import run_command

logger = get_logger(__name__)


def detect_ffmpeg() -> Optional[str]:
    """
    Detect the FFmpeg binary on the system.
    
    Returns:
        Path to FFmpeg binary if found, None otherwise
    """
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
    
    # Check if ffmpeg is in PATH
    try:
        ffmpeg_path = subprocess.run(
            ["which", "ffmpeg"] if platform.system() != "Windows" else ["where", "ffmpeg"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if ffmpeg_path:
            return ffmpeg_path
    except Exception:
        pass
    
    # Check common locations
    for location in common_locations:
        if os.path.exists(location) and os.access(location, os.X_OK):
            return location
    
    return None


def get_video_info(
    ffmpeg_path: str,
    video_path: str
) -> Dict:
    """
    Get information about a video file.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    # Prepare command
    cmd = [
        ffmpeg_path,
        "-i", video_path,
        "-hide_banner"
    ]
    
    # Run FFmpeg (this will fail, but we want the error output)
    returncode, stdout, stderr = run_command(cmd)
    
    # Parse output
    info = {
        "path": video_path,
        "filename": os.path.basename(video_path),
        "size": os.path.getsize(video_path),
        "duration": None,
        "video_codec": None,
        "audio_codec": None,
        "width": None,
        "height": None,
        "fps": None,
        "audio_channels": None,
        "audio_sample_rate": None,
    }
    
    # Extract information from stderr
    for line in stderr.split("\n"):
        line = line.strip()
        
        # Duration
        if "Duration:" in line:
            duration_part = line.split("Duration:")[1].split(",")[0].strip()
            hours, minutes, seconds = map(float, duration_part.split(":"))
            info["duration"] = hours * 3600 + minutes * 60 + seconds
        
        # Video stream
        if "Stream #" in line and "Video:" in line:
            # Extract video codec
            codec_part = line.split("Video:")[1].strip()
            info["video_codec"] = codec_part.split(",")[0].strip()
            
            # Extract resolution
            if ", " in codec_part:
                for part in codec_part.split(", "):
                    if "x" in part and part[0].isdigit():
                        width, height = map(int, part.split("x"))
                        info["width"] = width
                        info["height"] = height
                    
                    # Extract FPS
                    if " fps" in part:
                        fps_part = part.split(" fps")[0].strip()
                        if fps_part[-1].isdigit():
                            info["fps"] = float(fps_part)
        
        # Audio stream
        if "Stream #" in line and "Audio:" in line:
            # Extract audio codec
            codec_part = line.split("Audio:")[1].strip()
            info["audio_codec"] = codec_part.split(",")[0].strip()
            
            # Extract audio channels
            if "stereo" in line.lower():
                info["audio_channels"] = 2
            elif "mono" in line.lower():
                info["audio_channels"] = 1
            elif " ch" in line:
                for part in line.split(" "):
                    if part.endswith(" ch") and part[0].isdigit():
                        info["audio_channels"] = int(part.split(" ")[0])
            
            # Extract sample rate
            if " Hz" in line:
                for part in line.split(", "):
                    if " Hz" in part:
                        sample_rate_part = part.split(" Hz")[0].strip()
                        if sample_rate_part.isdigit():
                            info["audio_sample_rate"] = int(sample_rate_part)
    
    return info


def extract_audio_advanced(
    ffmpeg_path: str,
    video_path: str,
    output_path: str,
    audio_format: str = "wav",
    sample_rate: int = 16000,
    channels: int = 1,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    bitrate: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    Extract audio from a video file with advanced options.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        video_path: Path to video file
        output_path: Path to save extracted audio
        audio_format: Audio format (wav, mp3, etc.)
        sample_rate: Audio sample rate
        channels: Number of audio channels
        start_time: Start time in seconds
        end_time: End time in seconds
        bitrate: Audio bitrate (e.g., "128k")
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Prepare command
    cmd = [
        ffmpeg_path,
        "-i", video_path,
        "-vn",  # No video
        "-ar", str(sample_rate),  # Sample rate
        "-ac", str(channels),  # Channels
        "-y"  # Overwrite output file
    ]
    
    # Add start time if specified
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    
    # Add end time if specified
    if end_time is not None:
        cmd.extend(["-to", str(end_time)])
    
    # Add bitrate if specified
    if bitrate is not None:
        cmd.extend(["-b:a", bitrate])
    
    # Add output path
    cmd.append(output_path)
    
    # Run FFmpeg
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    return run_command(cmd)


def extract_thumbnail(
    ffmpeg_path: str,
    video_path: str,
    output_path: str,
    time_position: float = 0,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Tuple[int, str, str]:
    """
    Extract a thumbnail from a video file.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        video_path: Path to video file
        output_path: Path to save thumbnail
        time_position: Time position in seconds
        width: Thumbnail width
        height: Thumbnail height
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Prepare command
    cmd = [
        ffmpeg_path,
        "-i", video_path,
        "-ss", str(time_position),
        "-frames:v", "1",
        "-y"  # Overwrite output file
    ]
    
    # Add size if specified
    if width is not None and height is not None:
        cmd.extend(["-s", f"{width}x{height}"])
    
    # Add output path
    cmd.append(output_path)
    
    # Run FFmpeg
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    return run_command(cmd)


def check_ffmpeg_capabilities(ffmpeg_path: str) -> Dict[str, bool]:
    """
    Check FFmpeg capabilities.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        
    Returns:
        Dictionary with capability flags
    """
    capabilities = {
        "has_libmp3lame": False,
        "has_libvorbis": False,
        "has_libopus": False,
        "has_hevc": False,
        "has_h264": False,
        "has_aac": False,
        "has_cuda": False,
        "has_vaapi": False,
        "has_videotoolbox": False,
    }
    
    try:
        # Run FFmpeg with -codecs flag
        result = subprocess.run(
            [ffmpeg_path, "-codecs"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            output = result.stdout.lower()
            
            # Check for encoders
            capabilities["has_libmp3lame"] = "libmp3lame" in output
            capabilities["has_libvorbis"] = "libvorbis" in output
            capabilities["has_libopus"] = "libopus" in output
            capabilities["has_hevc"] = "hevc" in output or "h265" in output
            capabilities["has_h264"] = "h264" in output
            capabilities["has_aac"] = "aac" in output
            
            # Check for hardware acceleration
            capabilities["has_cuda"] = "cuda" in output
            capabilities["has_vaapi"] = "vaapi" in output
            capabilities["has_videotoolbox"] = "videotoolbox" in output
    
    except Exception as e:
        logger.error(f"Error checking FFmpeg capabilities: {e}")
    
    return capabilities
