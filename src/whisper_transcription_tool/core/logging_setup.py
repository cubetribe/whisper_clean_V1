"""
Logging setup for the Whisper Transcription Tool.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union

# Configure default logging format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FILE = str(Path.home() / ".whisper_tool" / "whisper_tool.log")


def setup_logging(
    log_level: Union[int, str] = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = DEFAULT_LOG_FILE,
    log_format: str = DEFAULT_LOG_FORMAT,
    config: Optional[Dict] = None,
) -> None:
    """
    Set up logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for no file logging)
        log_format: Logging format string
        config: Configuration dictionary that may contain logging settings
    """
    # Override with config if provided
    if config and "logging" in config:
        log_config = config["logging"]
        log_level = log_config.get("level", log_level)
        log_file = log_config.get("file", log_file)
        log_format = log_config.get("format", log_format)
    
    # Convert string log level to numeric if needed
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # Add file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Failed to set up file logging to {log_file}: {e}")
    
    # Set lower level for our own loggers
    logging.getLogger("whisper_transcription_tool").setLevel(log_level)
    
    logging.info(f"Logging initialized at level {logging.getLevelName(log_level)}")
    if log_file:
        logging.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
