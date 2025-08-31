"""File management module for the Whisper Transcription Tool.
Handles cleanup of temporary files and disk space monitoring."""


import os
import time
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from .constants import DEFAULT_TEMP_DIR, DEFAULT_OUTPUT_DIR, SUPPORTED_AUDIO_FORMATS, SUPPORTED_VIDEO_FORMATS
from .logging_setup import get_logger
from .config import load_config

logger = get_logger(__name__)


class FileManager:
    """Class to manage files and cleanup temporary directories."""

    def __init__(self, config=None):
        """Initialize the file manager with config."""
        self.config = config or load_config()
        
        # Festlegen der Verzeichnisse
        self.temp_dir = self.config.get("output", {}).get("temp_directory", DEFAULT_TEMP_DIR)
        
        # Speicherplatzmanagement-Einstellungen
        self.min_required_space_gb = self.config.get("disk_management", {}).get("min_required_space_gb", 2.0)
        self.max_disk_usage_percent = self.config.get("disk_management", {}).get("max_disk_usage_percent", 90)
        self.enable_auto_cleanup = self.config.get("disk_management", {}).get("enable_auto_cleanup", True)

        self._ensure_temp_dir()

    def _ensure_temp_dir(self):
        """Ensure the temporary directory exists."""
        temp_dir = self._get_temp_dir()
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def _get_temp_dir(self) -> str:
        """Get the configured temporary directory path."""
        temp_dir = self.config.get("output", {}).get("temp_directory", DEFAULT_TEMP_DIR)
        return os.path.expanduser(temp_dir)

    def _get_output_dir(self) -> str:
        """Get the configured output directory path."""
        output_dir = self.config.get("output", {}).get("default_directory", DEFAULT_OUTPUT_DIR)
        return os.path.expanduser(output_dir)

    def cleanup_after_transcription(self, session_id: str) -> Dict:
        """Clean up temporary files after a transcription session."""
        temp_dir = self._get_temp_dir()
        session_dir = os.path.join(temp_dir, session_id) if session_id else temp_dir

        if not os.path.exists(session_dir):
            logger.warning(f"Session directory does not exist: {session_dir}")
            return {"status": "warning", "files_deleted": 0, "space_freed": 0, "message": "Session directory not found"}

        stats = {"files_deleted": 0, "space_freed": 0}

        try:
            # Only remove audio/video files to preserve output files
            for root, dirs, files in os.walk(session_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()

                    # Check if it's a temporary audio/video file
                    if any(file_ext.endswith(fmt) for fmt in SUPPORTED_AUDIO_FORMATS) or \
                       any(file_ext.endswith(fmt) for fmt in SUPPORTED_VIDEO_FORMATS):

                        # Skip if it's in the final output directory
                        if self._get_output_dir() in file_path:
                            continue

                        # Get file size before deletion
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            stats["files_deleted"] += 1
                            stats["space_freed"] += file_size
                            logger.info(f"Deleted temporary file: {file_path} ({file_size} bytes)")
                        except Exception as e:
                            logger.error(f"Error deleting file {file_path}: {e}")

            # Convert bytes to MB for better readability
            stats["space_freed_mb"] = round(stats["space_freed"] / (1024 * 1024), 2)
            stats["status"] = "success"
            stats["message"] = f"Cleanup successful: {stats['files_deleted']} files deleted, {stats['space_freed_mb']} MB freed"

            logger.info(f"Cleanup after transcription: {stats['message']}")
            return stats

        except Exception as e:
            logger.error(f"Error during cleanup after transcription: {e}")
            return {"status": "error", "message": f"Error during cleanup: {str(e)}"}

    def cleanup_temp_directory(self, age_threshold_hours: int = 24) -> Dict:
        """Clean up the entire temporary directory based on file age."""
        temp_dir = self._get_temp_dir()

        if not os.path.exists(temp_dir):
            logger.warning(f"Temporary directory does not exist: {temp_dir}")
            return {"status": "warning", "message": "Temporary directory not found"}

        stats = {"dirs_deleted": 0, "files_deleted": 0, "space_freed": 0}
        cutoff_time = datetime.now() - timedelta(hours=age_threshold_hours)

        try:
            # Walk through the temporary directory
            for root, dirs, files in os.walk(temp_dir, topdown=False):  # topdown=False to process subdirs first
                # Skip the root temp directory itself
                if root == temp_dir:
                    continue

                # Process files
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()

                    # Skip output files like .txt, .srt, .json
                    if file_ext in ['.txt', '.srt', '.vtt', '.json']:
                        # Check if they're older than threshold
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_time:
                            try:
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                stats["files_deleted"] += 1
                                stats["space_freed"] += file_size
                                logger.info(f"Deleted old output file: {file_path} ({file_size} bytes)")
                            except Exception as e:
                                logger.error(f"Error deleting file {file_path}: {e}")
                        continue

                    # Delete all audio/video temporary files
                    if any(file_ext.endswith(fmt) for fmt in SUPPORTED_AUDIO_FORMATS) or \
                       any(file_ext.endswith(fmt) for fmt in SUPPORTED_VIDEO_FORMATS):
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            stats["files_deleted"] += 1
                            stats["space_freed"] += file_size
                            logger.info(f"Deleted temporary file: {file_path} ({file_size} bytes)")
                        except Exception as e:
                            logger.error(f"Error deleting file {file_path}: {e}")

                # Check if directory is empty and older than threshold
                if not os.listdir(root):
                    try:
                        dir_time = datetime.fromtimestamp(os.path.getmtime(root))
                        if dir_time < cutoff_time:
                            shutil.rmtree(root)
                            stats["dirs_deleted"] += 1
                            logger.info(f"Deleted empty directory: {root}")
                    except Exception as e:
                        logger.error(f"Error deleting directory {root}: {e}")

            # Convert bytes to MB for better readability
            stats["space_freed_mb"] = round(stats["space_freed"] / (1024 * 1024), 2)
            stats["status"] = "success"
            stats["message"] = (f"Cleanup successful: {stats['dirs_deleted']} directories and "
                               f"{stats['files_deleted']} files deleted, {stats['space_freed_mb']} MB freed")

            logger.info(f"Temporary directory cleanup: {stats['message']}")
            return stats

        except Exception as e:
            logger.error(f"Error during temporary directory cleanup: {e}")
            return {"status": "error", "message": f"Error during cleanup: {str(e)}"}

    def monitor_disk_space(self, min_free_space_gb: float = 5.0) -> Dict:
        """Monitor available disk space and return stats."""
        temp_dir = self._get_temp_dir()

        try:
            # Get disk usage statistics
            total, used, free = shutil.disk_usage(temp_dir)

            # Convert to GB for better readability
            total_gb = round(total / (1024**3), 2)
            used_gb = round(used / (1024**3), 2)
            free_gb = round(free / (1024**3), 2)

            # Check if free space is below threshold
            status = "ok"
            if free_gb < min_free_space_gb:
                status = "warning"
                logger.warning(f"Low disk space: {free_gb} GB free (threshold: {min_free_space_gb} GB)")

            # Get temp directory size
            temp_size = 0
            for root, dirs, files in os.walk(temp_dir):
                temp_size += sum(os.path.getsize(os.path.join(root, file)) for file in files if os.path.exists(os.path.join(root, file)))

            temp_size_gb = round(temp_size / (1024**3), 2)

            stats = {
                "status": status,
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "temp_dir_gb": temp_size_gb,
                "percent_used": round((used / total) * 100, 1),
                "percent_free": round((free / total) * 100, 1),
                "min_required_gb": min_free_space_gb
            }

            logger.info(f"Disk space: {free_gb} GB free of {total_gb} GB, temp dir size: {temp_size_gb} GB")
            return stats

        except Exception as e:
            logger.error(f"Error monitoring disk space: {e}")
            return {"status": "error", "message": f"Error monitoring disk space: {str(e)}"}

    def emergency_cleanup(self) -> Dict:
        """Perform emergency cleanup when disk space is critically low."""
        try:
            # First, get current disk space
            space_stats = self.monitor_disk_space()

            if space_stats.get("status") == "error":
                return space_stats

            # If we have enough space, no need for emergency cleanup
            if space_stats.get("free_gb", 0) > 1.0:  # Arbitrary threshold of 1 GB
                return {"status": "ok", "message": "Emergency cleanup not needed"}

            # Perform aggressive cleanup - delete ALL temporary audio/video files
            result = self.cleanup_temp_directory(age_threshold_hours=0)

            # Get updated disk space after cleanup
            updated_stats = self.monitor_disk_space()

            result.update({
                "before_free_gb": space_stats.get("free_gb", 0),
                "after_free_gb": updated_stats.get("free_gb", 0),
                "space_gained_gb": round(updated_stats.get("free_gb", 0) - space_stats.get("free_gb", 0), 2)
            })

            return result

        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")
            return {"status": "error", "message": f"Error during emergency cleanup: {str(e)}"}

    def convert_wav_to_mp3(self, 
                          wav_file_path: str, 
                          bitrate: str = "192k", 
                          delete_original: bool = True) -> Dict:
        """Convert a WAV file to MP3 format.

        Args:
            wav_file_path: Path to the WAV file
            bitrate: MP3 bitrate (default: "192k")
            delete_original: Whether to delete the original WAV file

        Returns:
            Dict with conversion stats
        """
        from ..module2_extract.ffmpeg_wrapper import detect_ffmpeg, extract_audio_advanced

        if not os.path.exists(wav_file_path) or not wav_file_path.lower().endswith('.wav'):
            return {"status": "error", "message": "Invalid WAV file path"}

        # Generate output path
        mp3_file_path = os.path.splitext(wav_file_path)[0] + '.mp3'

        # Check if MP3 already exists
        if os.path.exists(mp3_file_path):
            return {"status": "warning", "message": "MP3 file already exists", 
                    "mp3_path": mp3_file_path}

        try:
            # Get file size before conversion
            original_size = os.path.getsize(wav_file_path)

            # Detect FFmpeg
            ffmpeg_path = detect_ffmpeg()
            if not ffmpeg_path:
                return {"status": "error", "message": "FFmpeg not found"}

            # Convert WAV to MP3
            result = extract_audio_advanced(
                ffmpeg_path=ffmpeg_path,
                video_path=wav_file_path,  # Using WAV as source
                output_path=mp3_file_path,
                audio_format="mp3",
                bitrate=bitrate
            )

            if result[0] != 0:
                return {"status": "error", "message": f"FFmpeg error: {result[2]}"}

            # Check if MP3 file was created successfully
            if not os.path.exists(mp3_file_path):
                return {"status": "error", "message": "MP3 file not created"}

            mp3_size = os.path.getsize(mp3_file_path)

            # Delete original WAV if requested
            if delete_original:
                os.remove(wav_file_path)
                logger.info(f"Deleted original WAV file: {wav_file_path}")

            return {
                "status": "success",
                "message": "WAV converted to MP3 successfully",
                "wav_path": wav_file_path,
                "mp3_path": mp3_file_path,
                "original_size_mb": round(original_size / (1024 * 1024), 2),
                "mp3_size_mb": round(mp3_size / (1024 * 1024), 2),
                "size_reduction_mb": round((original_size - mp3_size) / (1024 * 1024), 2),
                "size_reduction_percent": round((original_size - mp3_size) / original_size * 100, 1)
            }

        except Exception as e:
            logger.error(f"Error converting WAV to MP3: {e}")
            return {"status": "error", "message": f"Error during conversion: {str(e)}"}
