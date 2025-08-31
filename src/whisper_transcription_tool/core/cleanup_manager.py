"""
Cleanup Manager for temporary files in the Whisper Transcription Tool.
Automatically removes audio/video files after successful transcription.
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

from .config import load_config
from .events import publish, EventType

logger = logging.getLogger(__name__)

# File extensions to clean up
AUDIO_VIDEO_EXTENSIONS = {
    '.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.wma',
    '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'
}

# File extensions to keep (transcription results)
KEEP_EXTENSIONS = {
    '.txt', '.srt', '.vtt', '.json', '.csv'
}


class CleanupManager:
    """Manages cleanup of temporary files."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize CleanupManager with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        
        # Cleanup settings
        self.cleanup_config = self.config.get("cleanup", {
            "enabled": True,
            "auto_cleanup_after_transcription": True,
            "cleanup_age_hours": 24,  # Files older than 24 hours
            "keep_transcriptions": True,  # Keep .txt, .srt, etc.
            "cleanup_chunks": True,  # Clean chunk directories
            "max_temp_size_gb": 10.0  # Max size before forced cleanup
        })
        
        # Get temp directory from config
        self.temp_dir = self.config.get("output", {}).get(
            "temp_directory",
            os.path.join(Path.home(), "transcriptions", "temp")
        )
        
        # Track cleaned files for reporting
        self.cleaned_files = []
        self.space_freed = 0
    
    def cleanup_file(self, file_path: str, force: bool = False) -> bool:
        """
        Clean up a single file.
        
        Args:
            file_path: Path to file to clean
            force: Force deletion even if not audio/video
            
        Returns:
            True if file was deleted
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # Get file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Check if file should be kept
            if not force and ext in KEEP_EXTENSIONS:
                logger.debug(f"Keeping transcription file: {file_path}")
                return False
            
            # Check if file is audio/video or force is True
            if force or ext in AUDIO_VIDEO_EXTENSIONS:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                
                self.cleaned_files.append(file_path)
                self.space_freed += file_size
                
                logger.info(f"Deleted {file_path} ({self._format_size(file_size)})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def cleanup_directory(self, directory: str, recursive: bool = True) -> int:
        """
        Clean up all audio/video files in a directory.
        
        Args:
            directory: Directory to clean
            recursive: Clean subdirectories too
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(directory):
            return 0
        
        deleted_count = 0
        
        # Handle chunk directories specially
        if "chunk" in os.path.basename(directory).lower():
            try:
                shutil.rmtree(directory)
                logger.info(f"Deleted chunk directory: {directory}")
                return 1
            except Exception as e:
                logger.error(f"Error deleting chunk directory {directory}: {e}")
                return 0
        
        # Process files in directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isfile(item_path):
                if self.cleanup_file(item_path):
                    deleted_count += 1
            
            elif os.path.isdir(item_path) and recursive:
                # Recursively clean subdirectories
                deleted_count += self.cleanup_directory(item_path, recursive=True)
        
        return deleted_count
    
    def cleanup_old_files(self, max_age_hours: Optional[float] = None) -> int:
        """
        Clean up files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours (uses config if not specified)
            
        Returns:
            Number of files deleted
        """
        if max_age_hours is None:
            max_age_hours = self.cleanup_config.get("cleanup_age_hours", 24)
        
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        deleted_count = 0
        
        logger.info(f"Cleaning up files older than {max_age_hours} hours in {self.temp_dir}")
        
        for root, dirs, files in os.walk(self.temp_dir):
            # Clean up chunk directories
            for dir_name in dirs:
                if "chunk" in dir_name.lower():
                    dir_path = os.path.join(root, dir_name)
                    dir_age = current_time - os.path.getmtime(dir_path)
                    
                    if dir_age > max_age_seconds:
                        try:
                            shutil.rmtree(dir_path)
                            logger.info(f"Deleted old chunk directory: {dir_path}")
                            deleted_count += 1
                        except Exception as e:
                            logger.error(f"Error deleting directory {dir_path}: {e}")
            
            # Clean up old audio/video files
            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = os.path.splitext(file_name)[1].lower()
                
                if ext in AUDIO_VIDEO_EXTENSIONS:
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        
                        if file_age > max_age_seconds:
                            if self.cleanup_file(file_path):
                                deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error checking file {file_path}: {e}")
        
        return deleted_count
    
    def cleanup_after_transcription(self, audio_path: str, keep_original: bool = False) -> bool:
        """
        Clean up audio file and chunks after successful transcription.
        
        Args:
            audio_path: Path to original audio file
            keep_original: Whether to keep the original file
            
        Returns:
            True if cleanup was successful
        """
        if not self.cleanup_config.get("auto_cleanup_after_transcription", True):
            logger.debug("Auto-cleanup is disabled")
            return False
        
        success = True
        
        # Clean up the original audio file
        if not keep_original and os.path.exists(audio_path):
            if self.cleanup_file(audio_path):
                logger.info(f"Cleaned up original audio file: {audio_path}")
            else:
                success = False
        
        # Clean up chunk directories if they exist
        if self.cleanup_config.get("cleanup_chunks", True):
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            chunk_dir = os.path.join(self.temp_dir, f"chunks_{base_name}")
            
            if os.path.exists(chunk_dir):
                try:
                    shutil.rmtree(chunk_dir)
                    logger.info(f"Cleaned up chunk directory: {chunk_dir}")
                except Exception as e:
                    logger.error(f"Error cleaning chunk directory: {e}")
                    success = False
        
        # Publish cleanup event
        if self.space_freed > 0:
            publish(EventType.CUSTOM, {
                "type": "CLEANUP_COMPLETED",
                "files_deleted": len(self.cleaned_files),
                "space_freed": self._format_size(self.space_freed)
            })
        
        return success
    
    def get_temp_directory_size(self) -> Tuple[float, int]:
        """
        Get the total size of the temp directory.
        
        Returns:
            Tuple of (size in bytes, number of files)
        """
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.temp_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    pass
        
        return total_size, file_count
    
    def check_and_cleanup(self) -> Dict[str, any]:
        """
        Check temp directory size and perform cleanup if needed.
        
        Returns:
            Dictionary with cleanup statistics
        """
        size_bytes, file_count = self.get_temp_directory_size()
        size_gb = size_bytes / (1024 ** 3)
        
        stats = {
            "temp_size_gb": size_gb,
            "file_count": file_count,
            "cleaned_files": 0,
            "space_freed": 0
        }
        
        # Check if cleanup is needed
        max_size = self.cleanup_config.get("max_temp_size_gb", 10.0)
        
        if size_gb > max_size:
            logger.warning(f"Temp directory size ({size_gb:.2f} GB) exceeds limit ({max_size} GB)")
            
            # Reset counters
            self.cleaned_files = []
            self.space_freed = 0
            
            # Perform cleanup
            deleted = self.cleanup_old_files()
            
            stats["cleaned_files"] = len(self.cleaned_files)
            stats["space_freed"] = self.space_freed
            
            logger.info(f"Cleanup completed: {deleted} files deleted, {self._format_size(self.space_freed)} freed")
        
        return stats
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


def cleanup_temp_directory(config: Optional[Dict] = None) -> Dict[str, any]:
    """
    Convenience function to perform temp directory cleanup.
    
    Args:
        config: Optional configuration
        
    Returns:
        Cleanup statistics
    """
    manager = CleanupManager(config)
    return manager.check_and_cleanup()


def cleanup_after_transcription(audio_path: str, config: Optional[Dict] = None) -> bool:
    """
    Convenience function to cleanup after transcription.
    
    Args:
        audio_path: Path to audio file
        config: Optional configuration
        
    Returns:
        True if cleanup was successful
    """
    manager = CleanupManager(config)
    return manager.cleanup_after_transcription(audio_path)