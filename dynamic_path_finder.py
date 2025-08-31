#!/usr/bin/env python3
"""
Dynamischer Pfadfinder für die Whisper Transkriptionstool App

Dieses Skript erkennt den eigenen Speicherort und aktualisiert die Konfiguration entsprechend.
Es sollte bei jedem Start der App ausgeführt werden, um sicherzustellen, dass alle Pfade korrekt sind.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

# Logging einrichten
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('path_finder')

# Konfigurationsdatei und Standardwerte
CONFIG_FILE = os.path.expanduser('~/.whisper_tool.json')


def get_app_path():
    """
    Ermittelt den Pfad zur aktuellen Anwendung.
    
    Returns:
        Path: Der absolute Pfad zum Anwendungsverzeichnis
    """
    # Der Pfad dieses Skripts ist der Ausgangspunkt
    script_path = Path(os.path.abspath(__file__))
    # Das Stammverzeichnis der Anwendung ist das Verzeichnis, das das Skript enthält
    app_path = script_path.parent
    
    logger.info(f"Ermittelter App-Pfad: {app_path}")
    return app_path


def update_config(app_path):
    """
    Aktualisiert die Konfigurationsdatei mit den korrekten Pfaden.
    
    Args:
        app_path (Path): Der Pfad zum Anwendungsverzeichnis
    """
    # Standardkonfiguration
    default_config = {
        "whisper": {
            "binary_path": str(app_path / "deps/whisper.cpp/build/bin/whisper-cli"),
            "model_path": str(app_path / "models"),
            "default_model": "large-v3-turbo",
            "threads": 4
        },
        "ffmpeg": {
            "binary_path": "/usr/local/bin/ffmpeg",
            "audio_format": "wav",
            "sample_rate": 16000
        },
        "output": {
            "default_directory": str(app_path / "transcriptions"),
            "temp_directory": str(app_path / "transcriptions/temp"),
            "default_format": "txt"
        },
        "chatbot": {
            "mode": "local",
            "model": "mistral-7b"
        },
        "disk_management": {
            "min_required_space_gb": 2.0,
            "max_disk_usage_percent": 90,
            "enable_auto_cleanup": True,
            "cleanup_age_hours": 24,
            "batch_warning_threshold_gb": 5.0
        },
        "mp3_conversion": {
            "enabled": True,
            "bitrate": "192k",
            "delete_original": True,
            "minimum_size_mb": 5.0,
            "verify_integrity": True
        }
    }
    
    # Überprüfen, ob die Konfigurationsdatei existiert
    config = default_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
                
            # Bestehende Konfiguration mit neuen Pfaden aktualisieren
            config = existing_config
            
            # Pfade aktualisieren
            config['whisper']['binary_path'] = str(app_path / "deps/whisper.cpp/build/bin/whisper-cli")
            config['whisper']['model_path'] = str(app_path / "models")
            config['output']['default_directory'] = str(app_path / "transcriptions")
            config['output']['temp_directory'] = str(app_path / "transcriptions/temp")
            
            logger.info("Bestehende Konfiguration aktualisiert")
        except Exception as e:
            logger.error(f"Fehler beim Laden der bestehenden Konfiguration: {e}")
            logger.info("Verwende Standardkonfiguration")
    else:
        logger.info("Keine bestehende Konfiguration gefunden, erstelle neue Konfiguration")
    
    # Konfiguration speichern
    try:
        # Verzeichnisse erstellen
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        os.makedirs(app_path / "models", exist_ok=True)
        os.makedirs(app_path / "transcriptions/temp", exist_ok=True)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Konfiguration gespeichert in {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
    
    return config


def ensure_permissions(app_path):
    """
    Stellt sicher, dass alle ausführbaren Dateien die richtigen Berechtigungen haben.
    
    Args:
        app_path (Path): Der Pfad zum Anwendungsverzeichnis
    """
    try:
        # Whisper-CLI executable machen
        whisper_cli = app_path / "deps/whisper.cpp/build/bin/whisper-cli"
        if whisper_cli.exists():
            subprocess.run(['chmod', '+x', str(whisper_cli)], check=True)
            logger.info(f"Ausführungsrechte für {whisper_cli} gesetzt")
        
        # Start-Server-Script executable machen
        start_server = app_path / "start_server.sh"
        if start_server.exists():
            subprocess.run(['chmod', '+x', str(start_server)], check=True)
            logger.info(f"Ausführungsrechte für {start_server} gesetzt")
    except Exception as e:
        logger.error(f"Fehler beim Setzen der Ausführungsrechte: {e}")


def main():
    """
    Hauptfunktion, die die dynamische Pfadfindung und Konfiguration durchführt.
    """
    try:
        # App-Pfad ermitteln
        app_path = get_app_path()
        
        # Konfiguration aktualisieren
        config = update_config(app_path)
        
        # Ausführungsrechte setzen
        ensure_permissions(app_path)
        
        logger.info("Dynamische Pfadkonfiguration erfolgreich abgeschlossen")
        return True
    except Exception as e:
        logger.error(f"Fehler bei der dynamischen Pfadkonfiguration: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
