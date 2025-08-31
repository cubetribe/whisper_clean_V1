"""
Audio chunking module for handling large audio files.
Splits audio files into manageable chunks for transcription.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

from ..core.config import load_config
from ..core.events import publish, EventType
from ..core.exceptions import DependencyError
from ..core.utils import ensure_directory_exists, run_command

logger = logging.getLogger(__name__)


class AudioChunker:
    """Handles splitting of large audio files into chunks."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize AudioChunker with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        
        # Default chunking settings
        self.chunk_config = self.config.get("chunking", {
            "enabled": True,
            "max_duration_minutes": 20,
            "overlap_seconds": 10,
            "auto_detect_threshold": 20,  # Auto-enable for files > 20 minutes
            "format": "wav"  # Output format for chunks
        })
        
        # Get FFmpeg path from config
        self.ffmpeg_path = self.config.get("ffmpeg", {}).get("binary_path", "ffmpeg")
        self.ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
        
        # Temp directory for chunks
        self.temp_dir = self.config.get("output", {}).get(
            "temp_directory", 
            os.path.join(tempfile.gettempdir(), "whisper_chunks")
        )
        ensure_directory_exists(self.temp_dir)
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            duration = float(data.get("format", {}).get("duration", 0))
            logger.info(f"Audio duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            
            return duration
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get audio duration: {e}")
            raise DependencyError(f"FFprobe failed: {e}")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse duration: {e}")
            return 0
    
    def should_chunk(self, audio_path: str) -> bool:
        """
        Determine if audio file should be chunked.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if file should be chunked
        """
        if not self.chunk_config.get("enabled", True):
            return False
        
        duration_seconds = self.get_audio_duration(audio_path)
        duration_minutes = duration_seconds / 60
        
        threshold = self.chunk_config.get("auto_detect_threshold", 20)
        should_chunk = duration_minutes > threshold
        
        logger.info(f"Audio duration: {duration_minutes:.1f} min, threshold: {threshold} min, chunking: {should_chunk}")
        
        return should_chunk
    
    def split_audio(self, audio_path: str, output_dir: Optional[str] = None) -> List[Dict[str, any]]:
        """
        Split audio file into chunks.
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory for output chunks (uses temp if not specified)
            
        Returns:
            List of chunk information dicts with paths and metadata
        """
        if output_dir is None:
            # Create unique temp directory for this session
            session_id = os.path.splitext(os.path.basename(audio_path))[0]
            output_dir = os.path.join(self.temp_dir, f"chunks_{session_id}")
        
        ensure_directory_exists(output_dir)
        
        # Get audio duration
        total_duration = self.get_audio_duration(audio_path)
        if total_duration == 0:
            raise ValueError("Could not determine audio duration")
        
        # Calculate chunk parameters
        chunk_duration = self.chunk_config.get("max_duration_minutes", 20) * 60  # Convert to seconds
        overlap = self.chunk_config.get("overlap_seconds", 10)
        
        # Output format
        output_format = self.chunk_config.get("format", "wav")
        output_pattern = os.path.join(output_dir, f"chunk_%03d.{output_format}")
        
        logger.info(f"Splitting audio into {chunk_duration}s chunks with {overlap}s overlap")
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-i", audio_path,
            "-f", "segment",
            "-segment_time", str(chunk_duration),
            "-reset_timestamps", "1",
        ]
        
        # Add format-specific options
        if output_format == "wav":
            cmd.extend(["-c:a", "pcm_s16le"])
        else:
            cmd.extend(["-c:a", "copy"])
        
        cmd.append(output_pattern)
        
        # Execute splitting
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        try:
            publish(EventType.PROGRESS_UPDATE, {
                "task": "chunking",
                "status": "Splitting audio file...",
                "progress": 0
            })
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find created chunk files
            chunks = []
            chunk_files = sorted([f for f in os.listdir(output_dir) if f.startswith("chunk_")])
            
            for i, chunk_file in enumerate(chunk_files):
                chunk_path = os.path.join(output_dir, chunk_file)
                chunk_info = {
                    "index": i,
                    "path": chunk_path,
                    "filename": chunk_file,
                    "start_time": i * chunk_duration,
                    "duration": min(chunk_duration, total_duration - (i * chunk_duration))
                }
                chunks.append(chunk_info)
                
                logger.info(f"Created chunk {i+1}/{len(chunk_files)}: {chunk_file}")
                
                publish(EventType.PROGRESS_UPDATE, {
                    "task": "chunking",
                    "status": f"Created chunk {i+1}/{len(chunk_files)}",
                    "progress": ((i + 1) / len(chunk_files)) * 100
                })
            
            logger.info(f"Successfully split audio into {len(chunks)} chunks")
            
            publish(EventType.CUSTOM, {
                "type": "CHUNKING_COMPLETED",
                "chunks": len(chunks),
                "total_duration": total_duration
            })
            
            return chunks
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr}")
            raise DependencyError(f"Failed to split audio: {e.stderr}")
    
    def merge_transcriptions(self, transcriptions: List[Dict], remove_overlap: bool = True) -> str:
        """
        Merge chunk transcriptions into a single text.
        
        Args:
            transcriptions: List of transcription results with text and timing
            remove_overlap: Whether to remove overlapping text
            
        Returns:
            Merged transcription text
        """
        if not transcriptions:
            return ""
        
        merged_text = []
        last_end_text = ""
        
        for i, trans in enumerate(transcriptions):
            text = trans.get("text", "").strip()
            
            if remove_overlap and i > 0 and self.chunk_config.get("overlap_seconds", 0) > 0:
                # Simple overlap removal: check if beginning of current chunk
                # matches end of previous chunk
                if last_end_text and text.startswith(last_end_text[-100:]):
                    # Remove overlapping part
                    overlap_len = len(last_end_text[-100:])
                    text = text[overlap_len:].strip()
            
            if text:
                merged_text.append(text)
                # Store last 100 chars for overlap detection
                last_end_text = text
        
        return " ".join(merged_text)
    
    def cleanup_chunks(self, chunk_dir: str):
        """
        Clean up temporary chunk files.
        
        Args:
            chunk_dir: Directory containing chunk files
        """
        try:
            import shutil
            if os.path.exists(chunk_dir):
                shutil.rmtree(chunk_dir)
                logger.info(f"Cleaned up chunk directory: {chunk_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup chunks: {e}")


def is_audio_chunkable(audio_path: str, config: Optional[Dict] = None) -> bool:
    """
    Quick check if audio file should be chunked.
    
    Args:
        audio_path: Path to audio file
        config: Optional configuration
        
    Returns:
        True if file should be chunked
    """
    chunker = AudioChunker(config)
    return chunker.should_chunk(audio_path)


def chunk_audio_file(audio_path: str, config: Optional[Dict] = None) -> List[Dict[str, any]]:
    """
    Convenience function to chunk an audio file.
    
    Args:
        audio_path: Path to audio file
        config: Optional configuration
        
    Returns:
        List of chunk information
    """
    chunker = AudioChunker(config)
    return chunker.split_audio(audio_path)