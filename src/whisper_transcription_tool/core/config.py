"""
Configuration management for the Whisper Transcription Tool.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

# Finde Projekt-Wurzelverzeichnis, um relative Pfade zu verwenden
def find_project_root():
    """Find the project root directory."""
    # Beginne mit dem aktuellen Verzeichnis der Datei
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigiere nach oben bis zum Projektverzeichnis
    # Wir suchen nach dem 'src' Verzeichnis als Indikator
    while current_dir and not current_dir.endswith('src'):
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Wir haben das Root-Verzeichnis erreicht ohne 'src' zu finden
            return str(Path.home())
        current_dir = parent_dir
    
    # Gehe ein Level hoeher vom 'src' Verzeichnis
    return os.path.dirname(current_dir)

# Projektverzeichnis ermitteln für relative Pfade
PROJECT_ROOT = find_project_root()

DEFAULT_CONFIG = {
    "whisper": {
        "model_path": os.path.join(PROJECT_ROOT, "models"),
        "default_model": "large-v3-turbo",  # Using large-v3-turbo as specified by user
        "threads": 4,
    },
    "ffmpeg": {
        "binary_path": "/opt/homebrew/bin/ffmpeg",
        "audio_format": "wav",
        "sample_rate": 16000,
    },
    "output": {
        "default_directory": os.path.join(PROJECT_ROOT, "transcriptions"),
        "temp_directory": os.path.join(PROJECT_ROOT, "transcriptions", "temp"),
        "default_format": "txt",
    },
    "chunking": {
        "enabled": True,
        "max_duration_minutes": 20,
        "overlap_seconds": 10,
        "auto_detect_threshold": 20,  # Auto-enable for files > 20 minutes
        "format": "wav"
    },
    "chatbot": {
        "mode": "local",
        "model": "mistral-7b",
    },
    "disk_management": {
        "min_required_space_gb": 2.0,      # Mindestens 2 GB freier Speicherplatz
        "max_disk_usage_percent": 90,     # Maximale Speichernutzung in Prozent
        "enable_auto_cleanup": True,      # Automatische Bereinigung aktivieren
        "cleanup_age_hours": 24,         # Dateien älter als 24 Stunden bereinigen
        "batch_warning_threshold_gb": 5.0 # Mindestens 5 GB für Stapelverarbeitung
    },
    "cleanup": {
        "enabled": True,
        "auto_cleanup_after_transcription": True,  # Automatisch nach Transkription aufräumen
        "cleanup_age_hours": 24,  # Dateien älter als 24 Stunden löschen
        "keep_transcriptions": True,  # Transkriptions-Dateien behalten (.txt, .srt, etc.)
        "cleanup_chunks": True,  # Chunk-Verzeichnisse löschen
        "max_temp_size_gb": 5.0  # Maximale Temp-Verzeichnisgröße bevor automatisches Cleanup
    },
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file or use default configuration.
    
    Args:
        config_path: Path to configuration file (JSON or YAML)
        
    Returns:
        Dict containing configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    # Check for config file in default locations if not specified
    if not config_path:
        default_locations = [
            Path.home() / ".whisper_tool.json",
            Path.home() / ".whisper_tool.yaml",
            Path.home() / ".whisper_tool.yml",
            Path.home() / ".config" / "whisper_tool" / "config.json",
            Path.home() / ".config" / "whisper_tool" / "config.yaml",
        ]
        
        for path in default_locations:
            if path.exists():
                config_path = str(path)
                break
    
    # Load config from file if it exists
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith(('.yaml', '.yml')):
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)
                
                # Update config with user settings
                _update_nested_dict(config, user_config)
                logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    else:
        logger.info("Using default configuration")
    
    # Create directories if they don't exist
    os.makedirs(config["whisper"]["model_path"], exist_ok=True)
    os.makedirs(config["output"]["default_directory"], exist_ok=True)
    
    return config


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        with open(config_path, 'w') as f:
            if config_path.endswith(('.yaml', '.yml')):
                yaml.dump(config, f, default_flow_style=False)
            else:
                json.dump(config, f, indent=4)
                
        logger.info(f"Saved configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")
        return False


def _update_nested_dict(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update nested dictionary recursively.
    
    Args:
        d: Dictionary to update
        u: Dictionary with updates
        
    Returns:
        Updated dictionary
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _update_nested_dict(d[k], v)
        else:
            d[k] = v
    return d
