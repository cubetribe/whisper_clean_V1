"""
Video processing utilities for the Whisper Transcription Tool.
Handles video format detection, optimization, and other video-related tasks.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.logging_setup import get_logger
from ..core.utils import get_file_extension, is_video_file
from .ffmpeg_wrapper import get_video_info

logger = get_logger(__name__)

# Common video formats and their extensions
VIDEO_FORMATS = {
    "mp4": {"container": "MP4", "common_codecs": ["h264", "hevc", "av1"]},
    "mov": {"container": "QuickTime", "common_codecs": ["h264", "prores", "mjpeg"]},
    "avi": {"container": "AVI", "common_codecs": ["mjpeg", "xvid", "divx"]},
    "mkv": {"container": "Matroska", "common_codecs": ["h264", "hevc", "vp9"]},
    "webm": {"container": "WebM", "common_codecs": ["vp8", "vp9", "av1"]},
    "flv": {"container": "Flash Video", "common_codecs": ["h264", "vp6"]},
    "wmv": {"container": "Windows Media", "common_codecs": ["wmv", "vc1"]},
}

# Common audio formats and their extensions
AUDIO_FORMATS = {
    "wav": {"container": "WAV", "common_codecs": ["pcm_s16le", "pcm_f32le"]},
    "mp3": {"container": "MP3", "common_codecs": ["mp3", "libmp3lame"]},
    "aac": {"container": "AAC", "common_codecs": ["aac"]},
    "ogg": {"container": "Ogg", "common_codecs": ["vorbis", "opus"]},
    "flac": {"container": "FLAC", "common_codecs": ["flac"]},
    "m4a": {"container": "M4A", "common_codecs": ["aac", "alac"]},
}


def get_optimal_audio_format(ffmpeg_capabilities: Dict[str, bool]) -> str:
    """
    Determine the optimal audio format based on FFmpeg capabilities.
    
    Args:
        ffmpeg_capabilities: Dictionary with FFmpeg capability flags
        
    Returns:
        Optimal audio format extension
    """
    # Prefer WAV for maximum compatibility with Whisper
    if True:  # WAV is always supported
        return "wav"
    
    # Fallbacks in order of preference
    if ffmpeg_capabilities.get("has_libopus", False):
        return "opus"
    
    if ffmpeg_capabilities.get("has_libvorbis", False):
        return "ogg"
    
    if ffmpeg_capabilities.get("has_libmp3lame", False):
        return "mp3"
    
    if ffmpeg_capabilities.get("has_aac", False):
        return "aac"
    
    # Default to WAV if nothing else is available
    return "wav"


def get_optimal_audio_params(video_info: Dict) -> Dict:
    """
    Determine optimal audio extraction parameters based on video info.
    
    Args:
        video_info: Dictionary with video information
        
    Returns:
        Dictionary with optimal audio parameters
    """
    params = {
        "sample_rate": 16000,  # Default for Whisper
        "channels": 1,         # Mono for Whisper
        "bitrate": None        # Let FFmpeg decide
    }
    
    # If video has high-quality audio, preserve a higher sample rate
    if video_info.get("audio_sample_rate", 0) > 16000:
        # But cap at 48kHz for efficiency
        params["sample_rate"] = min(video_info.get("audio_sample_rate", 16000), 48000)
    
    return params


def estimate_transcription_time(video_info: Dict, model: str = "large-v3-turbo") -> float:
    """
    Estimate the time it will take to transcribe a video.
    
    Args:
        video_info: Dictionary with video information
        model: Whisper model to use
        
    Returns:
        Estimated transcription time in seconds
    """
    # Get video duration
    duration = video_info.get("duration", 0)
    
    # Base processing factors (very rough estimates)
    model_factors = {
        "tiny": 0.1,
        "base": 0.2,
        "small": 0.5,
        "medium": 1.0,
        "large": 2.0,
        "large-v3": 2.2,
        "large-v3-turbo": 1.8  # Turbo is faster than regular large-v3
    }
    
    # Get model factor
    model_factor = model_factors.get(model, 1.0)
    
    # Estimate transcription time (very rough estimate)
    # For Apple Silicon, transcription is often faster than real-time
    estimated_time = duration * model_factor * 0.5  # 0.5 factor for Apple Silicon
    
    return max(estimated_time, 10)  # Minimum 10 seconds


def get_video_segments(
    video_info: Dict,
    segment_duration: int = 600  # 10 minutes
) -> List[Dict]:
    """
    Split a video into logical segments for processing.
    
    Args:
        video_info: Dictionary with video information
        segment_duration: Duration of each segment in seconds
        
    Returns:
        List of segment dictionaries with start and end times
    """
    # Get video duration
    duration = video_info.get("duration", 0)
    
    # If duration is unknown or very short, return a single segment
    if duration <= 0 or duration <= segment_duration:
        return [{"start": 0, "end": None, "index": 0}]
    
    # Split into segments
    segments = []
    start_time = 0
    index = 0
    
    while start_time < duration:
        end_time = min(start_time + segment_duration, duration)
        segments.append({
            "start": start_time,
            "end": end_time,
            "index": index
        })
        start_time = end_time
        index += 1
    
    return segments


def format_time(seconds: float) -> str:
    """
    Format time in seconds to HH:MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def detect_video_files(directory: Union[str, Path]) -> List[str]:
    """
    Detect video files in a directory.
    
    Args:
        directory: Directory to scan
        
    Returns:
        List of video file paths
    """
    video_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_video_file(file_path):
                video_files.append(file_path)
    
    return video_files
