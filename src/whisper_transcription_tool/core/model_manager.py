import logging
from pathlib import Path
from typing import List, Dict
import httpx
import time
import math
import asyncio

from .config import load_config
from .models import WhisperModel
from .logging_setup import get_logger
from .events import publish, EventType

logger = get_logger(__name__)
config = load_config()

# Erweiterte Modell-Informationen mit Größen, Empfehlungen und Anwendungsfällen
# Dict[Modellname, (Dateiname, Größe in MB, Beschreibung, Empfehlung)]
MODEL_INFO: Dict[str, tuple] = {
    # Fokussierung auf die wichtigsten Modelle
    "tiny": (
        "tiny", 
        75, 
        "Kleinstes Modell, sehr schnell", 
        "Geeignet für Geräte mit sehr begrenzten Ressourcen oder wenn Geschwindigkeit wichtiger ist als Genauigkeit."
    ),
    "tiny.en": (
        "tiny.en", 
        75, 
        "Kleinstes Modell, optimiert für Englisch", 
        "Für englische Inhalte auf ressourcenbeschränkten Geräten. Schneller als das multilingual tiny-Modell."
    ),
    "base": (
        "base", 
        142, 
        "Basismodell, guter Kompromiss", 
        "Ausgewogene Balance zwischen Größe und Leistung. Gut für einfache Transkriptionen."
    ),
    "medium": (
        "medium", 
        1500, 
        "Mittelgroßes Modell, gute Genauigkeit", 
        "Empfohlen für die meisten Anwendungsfälle mit guter Erkennungsqualität und akzeptabler Verarbeitungszeit."
    ),
    "large-v3": (
        "large-v3", 
        2900, 
        "Größtes Modell, beste Genauigkeit", 
        "Höchste Genauigkeit, benötigt aber viel RAM und Rechenleistung. Für professionelle Transkriptionen und schwierige Audiobedingungen."
    ),
    "large-v3-turbo": (
        "large-v3-turbo", 
        1500, 
        "Optimierte Version des large-v3-Modells", 
        "Fast so genau wie large-v3, aber deutlich schneller. Beste Wahl für einen Kompromiss aus Geschwindigkeit und Genauigkeit."
    )
}

# Legacy-Mapping für Rückwärtskompatibilität (falls benötigt)
MODEL_FILENAME_MAPPING: Dict[str, str] = {
    model_name: info[0] for model_name, info in MODEL_INFO.items()
}

# Weitere unterstützte Modelle (werden nicht aktiv angeboten, aber können verwendet werden)
LEGACY_MODEL_MAPPING: Dict[str, str] = {
    "small": "small",
    "small.en": "small.en",
    "base.en": "base.en",
    "medium.en": "medium.en",
    "large-v1": "large-v1",
    "large-v2": "large-v2",
    "large.en": "large-v3"  # Standardmäßig auf v3 mappen
}

# Aktualisiere das Mapping um Legacy-Modelle zu ergänzen
MODEL_FILENAME_MAPPING.update(LEGACY_MODEL_MAPPING)


def get_model_filename(model_name: str) -> str:
    """Konvertiert einen vereinfachten Modellnamen in den tatsächlichen Dateinamen.
    
    Args:
        model_name: Der vereinfachte Modellname (z.B. 'large', 'base.en')
        
    Returns:
        Der tatsächliche Dateiname für das Modell (z.B. 'large-v3', 'base.en')
    """
    return MODEL_FILENAME_MAPPING.get(model_name, model_name)


def get_model_info(model_name: str) -> dict:
    """Gibt erweiterte Informationen zu einem Modell zurück.
    
    Args:
        model_name: Der Modellname (z.B. 'large', 'tiny')
        
    Returns:
        Ein Dictionary mit Informationen zum Modell (Dateiname, Größe, Beschreibung, Empfehlung)
        Falls das Modell nicht in MODEL_INFO existiert, werden Standardwerte zurückgegeben.
    """
    if model_name in MODEL_INFO:
        filename, size_mb, description, recommendation = MODEL_INFO[model_name]
        return {
            "name": model_name,
            "filename": filename,
            "size_mb": size_mb,
            "description": description,
            "recommendation": recommendation
        }
    else:
        # Für Legacy-Modelle oder unbekannte Modelle
        filename = MODEL_FILENAME_MAPPING.get(model_name, model_name)
        return {
            "name": model_name,
            "filename": filename,
            "size_mb": 0,  # Unbekannte Größe
            "description": f"Modell {model_name}",
            "recommendation": "Keine Informationen verfügbar"
        }


def get_recommended_models() -> List[dict]:
    """Gibt eine Liste der empfohlenen Modelle mit allen Informationen zurück.
    
    Returns:
        Eine Liste von Dictionaries mit Modellinformationen, sortiert nach Größe.
    """
    return [get_model_info(model_name) for model_name in MODEL_INFO.keys()]


def get_downloaded_models(model_dir_str: str) -> List[str]:
    """Check the specified model directory for downloaded model files.

    Scans the directory for files matching the pattern 'ggml-*.bin' (e.g., 'ggml-base.bin', 'ggml-large-v3-turbo.bin').
    Maps these found filenames back to the model names.

    Args:
        model_dir_str: The path to the directory containing model files (can include '~').

    Returns:
        A list of model names (like 'base', 'large-v3') found in the directory.
    """
    downloaded = []
    try:
        model_dir = Path(model_dir_str).expanduser().resolve() # Expand ~ and resolve path
    except Exception as e:
        logger.error(f"Error resolving model directory path '{model_dir_str}': {e}")
        return [] # Return empty list if path is invalid

    if not model_dir.is_dir():
        logger.warning(f"Model directory '{model_dir}' does not exist or is not a directory.")
        return []

    logger.info(f"Scanning for models in: {model_dir}")

    try:
        # Scan for model files (both old and new format)
        for item in model_dir.glob("ggml-*.bin"):
            if item.is_file():
                # Extract the model name from the filename (e.g., 'ggml-large-v3.bin' -> 'large-v3')
                model_name = item.stem[len('ggml-'):]
                logger.debug(f"Found model file: {item.name} -> model name: {model_name}")
                
                # For older models (base, small, etc.), these would be added directly
                # For newer models with version tags (large-v3), these will also be added with versions
                if model_name not in downloaded:
                    downloaded.append(model_name)
                    
                # Special case: If we find a versioned model like 'large-v3', also mark 'large' as available
                if '-v' in model_name:
                    base_name = model_name.split('-v')[0]
                    if base_name not in downloaded:
                        downloaded.append(base_name)
                        logger.debug(f"Also adding base model name: {base_name}")

    except OSError as e:
        logger.warning(f"Error scanning model directory {model_dir}: {e}")
        return []

    logger.info(f"Found downloaded models corresponding to: {downloaded}")
    return downloaded


# --- Download Logic ---

async def download_model(model_name: str, model_dir_str: str) -> None:
    """Downloads a Whisper model file if it doesn't exist.

    Args:
        model_name: The name of the model to download (e.g., 'base', 'small.en').
        model_dir_str: The directory to save the model in.
    """
    # Initialize size variables to handle potential errors before assignment
    total_size_bytes = 0
    total_size_mb = 0.0
    downloaded_bytes = 0
    file_path = None # Initialize file_path to None
    model_url = "" # Initialize model_url

    try:
        # Validate model name
        # Find the corresponding enum member
        try:
            model_enum = WhisperModel(model_name)
        except ValueError:
            logger.error(f"Invalid model name for download: {model_name}")
            # Publish failure event
            publish(EventType.PROGRESS_UPDATE, {
                "model_name": model_name,
                "status": "failed",
                "message": f"Invalid model name: {model_name}",
                "progress": 0,
                "total_size_mb": 0,
                "downloaded_mb": 0,
                "speed_mbps": 0,
                "eta_seconds": 0
            })
            return

        # Determine the expected filename (e.g., ggml-base.bin)
        # Verwende die Mapping-Funktion, um den korrekten Dateinamen zu erhalten
        model_filename = get_model_filename(model_name)
        filename = f"ggml-{model_filename}.bin"
        model_url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{filename}"
        logger.info(f"Using model filename '{filename}' for model '{model_name}'.")

        model_dir = Path(model_dir_str).expanduser().resolve()
        # Ensure directory exists (should be handled by set-directory logic, but double-check)
        if not model_dir.is_dir():
            logger.error(f"Target directory for model download does not exist: {model_dir}")
            publish(EventType.PROGRESS_UPDATE, {
                "model_name": model_name,
                "status": "failed",
                "message": f"Target directory not found: {model_dir}",
                "progress": 0, "total_size_mb": 0, "downloaded_mb": 0, "speed_mbps": 0, "eta_seconds": 0
            })
            return

        file_path = model_dir / filename

        logger.info(f"Starting download for model '{model_name}' from {model_url} to {file_path}")

        # Variables for progress tracking
        start_time = time.time()
        last_update_time = start_time

        try:
            # --- Inner Try: Handles HTTP communication --- 
            # Initial request to get headers (especially content-length)
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                head_response = await client.head(model_url)
                head_response.raise_for_status()
                total_size_bytes = int(head_response.headers.get('content-length', 0))
                total_size_mb = total_size_bytes / (1024 * 1024) if total_size_bytes else 0

                logger.info(f"Model size: {total_size_mb:.2f} MB")
                if total_size_bytes == 0:
                    logger.warning("Content-Length header missing or zero, progress calculation might be inaccurate.")

                # Publish initial 'starting' event
                publish(EventType.PROGRESS_UPDATE, {
                    "model_name": model_name,
                    "status": "starting",
                    "message": "Download started...",
                    "progress": 0,
                    "total_size_mb": round(total_size_mb, 2),
                    "downloaded_mb": 0,
                    "speed_mbps": 0,
                    "eta_seconds": None # ETA unknown at start
                })

                # Actual download stream
                async with client.stream('GET', model_url) as response:
                    response.raise_for_status()
                    # Ensure content-length matches if it wasn't zero initially
                    stream_total_size = int(response.headers.get('content-length', 0))
                    if total_size_bytes == 0 and stream_total_size > 0:
                        total_size_bytes = stream_total_size
                        total_size_mb = total_size_bytes / (1024 * 1024)
                        logger.info(f"Model size confirmed from stream: {total_size_mb:.2f} MB")

                    # Größerer Chunk-Size für schnelleren Download
                    chunk_size = 1024 * 1024  # 1 MB Chunks statt 8 KB für effizienteren Download
                    update_interval = 0.2     # Häufigere Updates (alle 200ms)
                    
                    # Explizites Feedback über Beginn des Downloads
                    logger.info(f"Starting actual file download for {model_name}")
                    publish(EventType.PROGRESS_UPDATE, {
                        "model_name": model_name,
                        "status": "downloading",
                        "message": "Download gestartet...",
                        "progress": 0,
                        "total_size_mb": round(total_size_mb, 2),
                        "downloaded_mb": 0,
                        "speed_mbps": 0,
                        "eta_seconds": None
                    })
                    
                    with open(file_path, 'wb') as f:
                        # Fortschrittsbalken-Zähler und Aktualisierungslogik
                        download_start_time = time.time()
                        
                        # Verwende größere Chunks für effizienteren Download
                        async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                            if chunk:  # Stellen Sie sicher, dass der Chunk Daten enthält
                                f.write(chunk)
                                downloaded_bytes += len(chunk)

                                current_time = time.time()
                                elapsed_time = current_time - download_start_time

                                # Häufigere Updates für flüssigere UI-Aktualisierung
                                if current_time - last_update_time >= update_interval or downloaded_bytes == total_size_bytes:
                                    # Stellen Sie sicher, dass total_size_bytes nicht Null ist
                                    if total_size_bytes > 0:
                                        progress = (downloaded_bytes / total_size_bytes) * 100
                                    else:
                                        progress = 0
                                        
                                    downloaded_mb = downloaded_bytes / (1024 * 1024)

                                    # Berechne Geschwindigkeit (MB/s)
                                    if elapsed_time > 0:
                                        speed_bytes_sec = downloaded_bytes / elapsed_time
                                        speed_mbps = speed_bytes_sec / (1024 * 1024)  # MB pro Sekunde (nicht Megabits)
                                    else:
                                        speed_mbps = 0

                                    # Berechne ETA (Sekunden)
                                    if speed_bytes_sec > 0 and total_size_bytes > 0:
                                        eta_seconds = (total_size_bytes - downloaded_bytes) / speed_bytes_sec
                                        eta_seconds = max(0, int(eta_seconds))  # Sicherstellen, dass ETA nicht negativ ist
                                    else:
                                        eta_seconds = 0  # Verwende einen Standard-Wert anstatt None

                                    # Veröffentliche Fortschrittsinformationen
                                    logger.info(f"Download progress: {progress:.2f}% - {downloaded_mb:.2f} MB of {total_size_mb:.2f} MB - Speed: {speed_mbps:.2f} MB/s - ETA: {eta_seconds} sec")
                                    
                                    # Erzeuge das Event-Objekt für Logging-Zwecke
                                    progress_data = {
                                        "model_name": model_name,
                                        "status": "downloading",
                                        "message": f"Modell wird heruntergeladen... ({downloaded_mb:.1f}/{total_size_mb:.1f} MB)",
                                        "progress": round(progress, 2),
                                        "total_size_mb": round(total_size_mb, 2),
                                        "downloaded_mb": round(downloaded_mb, 2),
                                        "speed_mbps": round(speed_mbps, 2),
                                        "eta_seconds": eta_seconds
                                    }
                                    
                                    # Log vor dem Publishing
                                    logger.debug(f"Publishing progress event: {progress_data}")
                                    
                                    # Veröffentliche das Event
                                    publish(EventType.PROGRESS_UPDATE, progress_data)
                                    last_update_time = current_time

        # --- End of Inner Try --- 

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while downloading {model_url}: {e.response.status_code}", exc_info=True)
            publish(EventType.PROGRESS_UPDATE, {
                "model_name": model_name,
                "status": "failed",
                "message": f"HTTP Fehler {e.response.status_code} beim Zugriff auf {model_url}. Existiert das Modell?",
                "progress": 0,
                "total_size_mb": 0, # Size unknown due to error
                "downloaded_mb": 0,
                "speed_mbps": 0,
                "eta_seconds": None
            })
            # Clean up potentially incomplete file
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed incomplete file after HTTP error: {file_path}")
                except OSError as unlink_err:
                    logger.error(f"Error removing incomplete file {file_path}: {unlink_err}")
            return # Stop execution after handling HTTP error

        except httpx.NetworkError as e:
            logger.error(f"Network error occurred while downloading {model_url}: {e}", exc_info=True)
            publish(EventType.PROGRESS_UPDATE, {"model_name": model_name, "status": "failed", "message": f"Netzwerkfehler: {e}", "progress": round((downloaded_bytes / total_size_bytes * 100) if total_size_bytes else 0, 2), "total_size_mb": round(total_size_mb, 2), "downloaded_mb": round(downloaded_bytes / (1024*1024), 2), "speed_mbps": 0, "eta_seconds": None})
            if file_path and file_path.exists(): file_path.unlink(missing_ok=True)
            return

        except httpx.TimeoutException as e:
            logger.error(f"Timeout occurred while downloading {model_url}: {e}", exc_info=True)
            publish(EventType.PROGRESS_UPDATE, {"model_name": model_name, "status": "failed", "message": f"Zeitüberschreitung: {e}", "progress": round((downloaded_bytes / total_size_bytes * 100) if total_size_bytes else 0, 2), "total_size_mb": round(total_size_mb, 2), "downloaded_mb": round(downloaded_bytes / (1024*1024), 2), "speed_mbps": 0, "eta_seconds": None})
            if file_path and file_path.exists(): file_path.unlink(missing_ok=True)
            return

        # --- This block runs only if the inner try was successful --- 
        elapsed_total = time.time() - start_time
        
        # Integritätsprüfung nach Download: Dateigröße vergleichen
        actual_size_bytes = file_path.stat().st_size
        actual_size_mb = actual_size_bytes / (1024 * 1024)
        
        # Toleranz von 1% für Größenvergleich (wegen möglicher Header-Unterschiede etc.)
        size_tolerance_percent = 1.0
        expected_min_bytes = total_size_bytes * (100 - size_tolerance_percent) / 100
        expected_max_bytes = total_size_bytes * (100 + size_tolerance_percent) / 100
        
        logger.info(f"Integrity check: Expected ~{total_size_mb:.2f} MB, Got {actual_size_mb:.2f} MB")
        
        if total_size_bytes > 0 and (actual_size_bytes < expected_min_bytes or actual_size_bytes > expected_max_bytes):
            # Die Datei hat nicht die erwartete Größe - möglicherweise beschädigt
            error_msg = f"Integrity check failed: Expected ~{total_size_mb:.2f} MB, got {actual_size_mb:.2f} MB"
            logger.error(error_msg)
            
            # Lösche die fehlerhafte Datei
            file_path.unlink()
            logger.info(f"Removed potentially corrupt file: {file_path}")
            
            # Fehler melden
            publish(EventType.PROGRESS_UPDATE, {
                "model_name": model_name,
                "status": "failed",
                "message": f"Integritätsprüfung fehlgeschlagen: {error_msg}",
                "progress": 100,  # Download wurde abgeschlossen, aber Datei ist ungültig
                "total_size_mb": round(total_size_mb, 2),
                "downloaded_mb": round(actual_size_mb, 2),
                "speed_mbps": 0,
                "eta_seconds": 0
            })
            return
        
        # Download war erfolgreich und Integritätsprüfung bestanden
        logger.info(f"Model '{model_name}' downloaded successfully in {elapsed_total:.2f} seconds and passed integrity check.")
        publish(EventType.PROGRESS_UPDATE, {
            "model_name": model_name,
            "status": "completed",
            "message": "Download abgeschlossen und Integritätsprüfung bestanden",
            "progress": 100,
            "total_size_mb": round(total_size_mb, 2),
            "downloaded_mb": round(total_size_mb, 2),
            "speed_mbps": 0,
            "eta_seconds": 0
        })

    # --- Outer Except: Catches setup errors or truly unexpected errors --- 
    except Exception as e:
        logger.error(f"An unexpected error occurred during model download setup or execution: {e}", exc_info=True)
        publish(EventType.PROGRESS_UPDATE, {
            "model_name": model_name,
            "status": "failed",
            "message": f"Unerwarteter Fehler: {e}",
            "progress": 0, # Progress unknown
            "total_size_mb": round(total_size_mb, 2), # May be 0 if error occurred early
            "downloaded_mb": round(downloaded_bytes / (1024*1024), 2), # May be 0
            "speed_mbps": 0,
            "eta_seconds": None
        })
        # Clean up potentially incomplete file
        if file_path and file_path.exists(): # Use file_path directly
            try:
                file_path.unlink()
                logger.info(f"Removed incomplete file after unexpected error: {file_path}")
            except OSError as unlink_err:
                logger.error(f"Error removing incomplete file {file_path}: {unlink_err}")


def get_model_download_url(model_name: str) -> str | None:
    """Returns the download URL for a given model name."""
    # Example URLs (adjust based on the actual source, e.g., Hugging Face)
    # These might change!
    base_url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{model}.bin"
    
    model_map = {
        WhisperModel.TINY_EN.value: base_url.format(model="tiny.en"),
        WhisperModel.TINY.value: base_url.format(model="tiny"),
        WhisperModel.BASE_EN.value: base_url.format(model="base.en"),
        WhisperModel.BASE.value: base_url.format(model="base"),
        WhisperModel.SMALL_EN.value: base_url.format(model="small.en"),
        WhisperModel.SMALL.value: base_url.format(model="small"),
        WhisperModel.MEDIUM_EN.value: base_url.format(model="medium.en"),
        WhisperModel.MEDIUM.value: base_url.format(model="medium"),
        WhisperModel.LARGE_V1.value: base_url.format(model="large-v1"),
        WhisperModel.LARGE_V2.value: base_url.format(model="large-v2"),
        WhisperModel.LARGE_V3.value: base_url.format(model="large-v3"),
    }
    return model_map.get(model_name)
