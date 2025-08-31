"""
Audio processing utilities for phone call recordings.
Handles audio synchronization, noise reduction, and other audio-related tasks.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.logging_setup import get_logger
from ..core.utils import run_command
from ..module2_extract.ffmpeg_wrapper import detect_ffmpeg

logger = get_logger(__name__)


def normalize_audio(
    ffmpeg_path: str,
    audio_path: str,
    output_path: str,
    target_level: float = -16.0
) -> Tuple[int, str, str]:
    """
    Normalize audio to a target level.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        audio_path: Path to audio file
        output_path: Path to save normalized audio
        target_level: Target audio level in dB
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Prepare command
    cmd = [
        ffmpeg_path,
        "-i", audio_path,
        "-filter:a", f"loudnorm=I={target_level}:TP=-1.5:LRA=11",
        "-y",  # Overwrite output file
        output_path
    ]
    
    # Run FFmpeg
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    return run_command(cmd)


def reduce_noise(
    ffmpeg_path: str,
    audio_path: str,
    output_path: str,
    noise_reduction: float = 0.21
) -> Tuple[int, str, str]:
    """
    Reduce noise in audio.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        audio_path: Path to audio file
        output_path: Path to save processed audio
        noise_reduction: Noise reduction amount (0.0 to 1.0)
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Prepare command
    cmd = [
        ffmpeg_path,
        "-i", audio_path,
        "-af", f"afftdn=nf={noise_reduction}",
        "-y",  # Overwrite output file
        output_path
    ]
    
    # Run FFmpeg
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    return run_command(cmd)


def enhance_speech(
    ffmpeg_path: str,
    audio_path: str,
    output_path: str
) -> Tuple[int, str, str]:
    """
    Enhance speech in audio.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        audio_path: Path to audio file
        output_path: Path to save processed audio
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Prepare command with a chain of filters for speech enhancement
    cmd = [
        ffmpeg_path,
        "-i", audio_path,
        "-af", "highpass=f=200,lowpass=f=3000,equalizer=f=1000:width_type=h:width=200:g=4",
        "-y",  # Overwrite output file
        output_path
    ]
    
    # Run FFmpeg
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    return run_command(cmd)


def preprocess_phone_audio(
    audio_path: str,
    output_path: Optional[str] = None,
    normalize: bool = True,
    noise_reduce: bool = True,
    enhance: bool = True
) -> str:
    """
    Preprocess phone call audio for better transcription.
    
    Args:
        audio_path: Path to audio file
        output_path: Path to save processed audio (None for temporary file)
        normalize: Whether to normalize audio
        noise_reduce: Whether to reduce noise
        enhance: Whether to enhance speech
        
    Returns:
        Path to processed audio file
    """
    # Get FFmpeg path
    ffmpeg_path = detect_ffmpeg()
    if not ffmpeg_path:
        logger.warning("FFmpeg not found, skipping audio preprocessing")
        return audio_path
    
    # Create temporary directory if output_path is not provided
    temp_dir = None
    if output_path is None:
        temp_dir = tempfile.TemporaryDirectory()
        output_path = os.path.join(temp_dir.name, "processed_audio.wav")
    
    # Create intermediate paths for processing chain
    current_input = audio_path
    
    try:
        # Normalize audio
        if normalize:
            normalize_output = output_path if not (noise_reduce or enhance) else os.path.join(os.path.dirname(output_path), "normalized.wav")
            logger.info(f"Normalizing audio: {audio_path} -> {normalize_output}")
            returncode, _, stderr = normalize_audio(ffmpeg_path, current_input, normalize_output)
            
            if returncode != 0:
                logger.warning(f"Audio normalization failed: {stderr}")
            else:
                current_input = normalize_output
        
        # Reduce noise
        if noise_reduce:
            noise_reduce_output = output_path if not enhance else os.path.join(os.path.dirname(output_path), "noise_reduced.wav")
            logger.info(f"Reducing noise: {current_input} -> {noise_reduce_output}")
            returncode, _, stderr = reduce_noise(ffmpeg_path, current_input, noise_reduce_output)
            
            if returncode != 0:
                logger.warning(f"Noise reduction failed: {stderr}")
            else:
                current_input = noise_reduce_output
        
        # Enhance speech
        if enhance:
            logger.info(f"Enhancing speech: {current_input} -> {output_path}")
            returncode, _, stderr = enhance_speech(ffmpeg_path, current_input, output_path)
            
            if returncode != 0:
                logger.warning(f"Speech enhancement failed: {stderr}")
            else:
                current_input = output_path
        
        # If no processing was done, copy the file
        if current_input == audio_path:
            logger.info(f"No processing done, copying file: {audio_path} -> {output_path}")
            shutil.copy(audio_path, output_path)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error preprocessing audio: {e}")
        return audio_path


def detect_silence(
    ffmpeg_path: str,
    audio_path: str,
    noise_threshold: float = -50.0,
    min_silence_duration: float = 1.0
) -> List[Dict]:
    """
    Detect silence in audio.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        audio_path: Path to audio file
        noise_threshold: Noise threshold in dB
        min_silence_duration: Minimum silence duration in seconds
        
    Returns:
        List of silence segments with start and end times
    """
    # Prepare command
    cmd = [
        ffmpeg_path,
        "-i", audio_path,
        "-af", f"silencedetect=noise={noise_threshold}dB:d={min_silence_duration}",
        "-f", "null",
        "-"
    ]
    
    # Run FFmpeg
    logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
    returncode, _, stderr = run_command(cmd)
    
    if returncode != 0:
        logger.warning(f"Silence detection failed: {stderr}")
        return []
    
    # Parse output
    silence_segments = []
    for line in stderr.split("\n"):
        if "silence_start" in line:
            start_time = float(line.split("silence_start: ")[1].split(" ")[0])
            silence_segments.append({"start": start_time, "end": None})
        elif "silence_end" in line and silence_segments:
            end_time = float(line.split("silence_end: ")[1].split(" ")[0])
            silence_segments[-1]["end"] = end_time
            silence_segments[-1]["duration"] = end_time - silence_segments[-1]["start"]
    
    return silence_segments


def split_audio_by_silence(
    ffmpeg_path: str,
    audio_path: str,
    output_dir: str,
    noise_threshold: float = -50.0,
    min_silence_duration: float = 1.0
) -> List[str]:
    """
    Split audio by silence.
    
    Args:
        ffmpeg_path: Path to FFmpeg binary
        audio_path: Path to audio file
        output_dir: Directory to save split audio files
        noise_threshold: Noise threshold in dB
        min_silence_duration: Minimum silence duration in seconds
        
    Returns:
        List of paths to split audio files
    """
    # Detect silence
    silence_segments = detect_silence(ffmpeg_path, audio_path, noise_threshold, min_silence_duration)
    
    if not silence_segments:
        logger.warning(f"No silence detected in {audio_path}")
        return [audio_path]
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create segments
    segments = []
    file_duration = silence_segments[-1]["end"] if silence_segments else 0
    
    # Add segment from start to first silence
    if silence_segments and silence_segments[0]["start"] > 0:
        segments.append({
            "start": 0,
            "end": silence_segments[0]["start"],
            "index": 0
        })
    
    # Add segments between silences
    for i in range(len(silence_segments) - 1):
        segments.append({
            "start": silence_segments[i]["end"],
            "end": silence_segments[i + 1]["start"],
            "index": len(segments)
        })
    
    # Add segment from last silence to end
    if silence_segments and silence_segments[-1]["end"] < file_duration:
        segments.append({
            "start": silence_segments[-1]["end"],
            "end": file_duration,
            "index": len(segments)
        })
    
    # Extract segments
    output_files = []
    for segment in segments:
        # Skip very short segments
        if segment["end"] - segment["start"] < 0.5:
            continue
        
        output_file = os.path.join(output_dir, f"segment_{segment['index']:03d}.wav")
        
        # Prepare command
        cmd = [
            ffmpeg_path,
            "-i", audio_path,
            "-ss", str(segment["start"]),
            "-to", str(segment["end"]),
            "-y",  # Overwrite output file
            output_file
        ]
        
        # Run FFmpeg
        logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")
        returncode, _, stderr = run_command(cmd)
        
        if returncode != 0:
            logger.warning(f"Segment extraction failed: {stderr}")
        else:
            output_files.append(output_file)
    
    return output_files
