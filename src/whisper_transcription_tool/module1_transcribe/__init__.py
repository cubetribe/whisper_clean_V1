"""
Transcription module for the Whisper Transcription Tool.
Handles audio transcription using Whisper.cpp on Apple Silicon.
"""

# Setze Umgebungsvariablen fuer dynamische Bibliotheken
import os
import sys

# Finde den Projektpfad
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
            return None
        current_dir = parent_dir
    
    # Gehe ein Level hoeher vom 'src' Verzeichnis
    return os.path.dirname(current_dir)

# Projektverzeichnis ermitteln
project_dir = find_project_root()
if project_dir:
    # Setze DYLD_LIBRARY_PATH fuer dynamische Bibliotheken
    whisper_lib_paths = [
        os.path.join(project_dir, 'deps', 'whisper.cpp', 'build', 'src'),
        os.path.join(project_dir, 'deps', 'whisper.cpp', 'build', 'ggml', 'src'),
        os.path.join(project_dir, 'deps', 'whisper.cpp', 'build', 'ggml', 'src', 'ggml-blas'),
        os.path.join(project_dir, 'deps', 'whisper.cpp', 'build', 'ggml', 'src', 'ggml-metal')
    ]
    
    # Bestehende Pfade beibehalten
    existing_paths = os.environ.get('DYLD_LIBRARY_PATH', '').split(':')
    if existing_paths == ['']:
        existing_paths = []
    
    # Neue Pfade hinzufuegen und doppelte vermeiden
    for path in whisper_lib_paths:
        if os.path.exists(path) and path not in existing_paths:
            existing_paths.append(path)
    
    # Umgebungsvariable aktualisieren
    os.environ['DYLD_LIBRARY_PATH'] = ':'.join(existing_paths)

    # Alter Workaround entfernt - nicht mehr benötigt da lokale Pfade verwendet werden


import json
import os
import platform
import requests
import subprocess
import tempfile
import json
import shutil
import psutil
from typing import Optional, Dict, List, Union, Tuple
from enum import Enum
from pathlib import Path
import logging

from ..core.config import load_config
from ..core.events import publish, EventType
from ..core.utils import ensure_directory_exists
from ..core.constants import WHISPER_CPP_MODELS_URL
from ..core.exceptions import DependencyError, ModelError
from ..core.audio_chunker import AudioChunker, is_audio_chunkable
from ..core.cleanup_manager import cleanup_after_transcription

from ..core.logging_setup import get_logger
from ..core.models import OutputFormat, TranscriptionRequest, TranscriptionResult, WhisperModel
from ..core.utils import check_program_exists, ensure_directory_exists, get_output_path, run_command
from .output_formatter import text_to_srt, segments_to_srt
from .whisper_wrapper import parse_whisper_output

logger = get_logger(__name__)

# Constants
WHISPER_CPP_REPO = "https://github.com/ggerganov/whisper.cpp"
WHISPER_CPP_MODELS_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
DEFAULT_MODEL = WhisperModel.LARGE_V3_TURBO  # Using large-v3-turbo as specified by user

# Global variables to track current transcription process and cancellation
current_transcription_process = None
cancellation_requested = False

def cancel_current_transcription():
    """Cancel the currently running transcription process."""
    global current_transcription_process, cancellation_requested
    
    # Set cancellation flag
    cancellation_requested = True
    logger.info(f"Cancel requested, current process: {current_transcription_process}")
    
    # Cancel active process if exists
    if current_transcription_process and current_transcription_process.poll() is None:
        logger.info(f"Cancelling current transcription process PID: {current_transcription_process.pid}")
        current_transcription_process.terminate()
        try:
            current_transcription_process.wait(timeout=5)
            logger.info("Process terminated successfully")
        except subprocess.TimeoutExpired:
            logger.warning("Process didn't terminate, killing it")
            current_transcription_process.kill()
            current_transcription_process.wait()
        current_transcription_process = None
        
        # Send cancel event
        publish(EventType.CUSTOM, {
            "type": "TRANSCRIPTION_CANCELLED",
            "message": "Transkription wurde abgebrochen"
        })
        return True
    else:
        logger.warning("No active transcription process to cancel")
    return cancellation_requested

# Modellgrößen in MB und geschätzter RAM-Bedarf in MB
# Diese Werte sind Schätzungen und können je nach System variieren
MODEL_SIZES = {
    "tiny": {"disk": 75, "ram": 300},
    "base": {"disk": 140, "ram": 500},
    "small": {"disk": 450, "ram": 1024},
    "medium": {"disk": 1500, "ram": 2500},
    "large": {"disk": 3000, "ram": 4500},
    "large-v1": {"disk": 3000, "ram": 4500},
    "large-v2": {"disk": 3000, "ram": 4500},
    "large-v3": {"disk": 3000, "ram": 4500},
    "large-v3-turbo": {"disk": 1500, "ram": 3000}
}

def check_whisper_cpp_installed(binary_path: Optional[str] = None) -> bool:
    """
    Check if Whisper.cpp is installed.
    
    Args:
        binary_path: Path to whisper binary
        
    Returns:
        True if installed, False otherwise
    """
    if binary_path and os.path.exists(binary_path):
        return True
    
    return check_program_exists("whisper") or check_program_exists("./whisper")


def get_whisper_binary_path(config: Optional[Dict] = None) -> str:
    """
    Get the path to the Whisper.cpp binary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to whisper binary
    """
    if config and "whisper" in config and "binary_path" in config["whisper"]:
        binary_path = config["whisper"]["binary_path"]
        if os.path.exists(binary_path):
            return binary_path
    
    # Check if whisper is in PATH
    whisper_path = shutil.which("whisper")
    if whisper_path:
        return whisper_path
    
    # Check common locations
    common_locations = [
        "./whisper",
        "/usr/local/bin/whisper",
        "/usr/bin/whisper",
        str(Path.home() / "whisper.cpp" / "main"),
        str(Path.home() / "whisper.cpp" / "whisper")
    ]
    
    for location in common_locations:
        if os.path.exists(location) and os.access(location, os.X_OK):
            return location
    
    raise DependencyError("Whisper.cpp binary not found. Please install Whisper.cpp or specify the binary path in the configuration.")


def get_model_path(model_name: str, config: Optional[Dict] = None) -> str:
    """
    Get the path to a Whisper model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        Path to model file
    """
    # Get models directory from config
    models_dir = str(Path.home() / "whisper_models")
    if config and "whisper" in config and "model_path" in config["whisper"]:
        models_dir = config["whisper"]["model_path"]
    
    # Ensure models directory exists
    ensure_directory_exists(models_dir)
    
    # Check if model file exists
    model_path = os.path.join(models_dir, f"ggml-{model_name}.bin")
    if os.path.exists(model_path):
        return model_path
    
    # If not, raise an error (download_model should be called separately)
    raise ModelError(f"Model {model_name} not found at {model_path}. Please download it first.")


def check_memory_for_model(model_name: str) -> Tuple[bool, str]:
    """
    Überprüft, ob genügend Speicher für das gewählte Modell verfügbar ist.
    
    Args:
        model_name: Name des Modells
        
    Returns:
        Tuple aus (hat_genug_speicher, nachricht)
    """
    logger = get_logger(__name__)
    
    # Standardwerte für unbekannte Modelle
    required_ram = 500  # MB
    
    # Hole Modellgröße aus der Modelltabelle
    if model_name in MODEL_SIZES:
        required_ram = MODEL_SIZES[model_name]["ram"]
    else:
        logger.warning(f"Unbekanntes Modell: {model_name}, verwende Standardspeicheranforderung")
    
    # Verfügbaren Speicher prüfen
    try:
        # Verfügbarer Speicher in MB
        available_ram = psutil.virtual_memory().available / (1024 * 1024)
        
        logger.info(f"Verfügbarer RAM: {available_ram:.2f} MB, Benötigt für Modell {model_name}: {required_ram} MB")
        
        if available_ram < required_ram:
            message = f"Nicht genügend RAM verfügbar! Verfügbar: {available_ram:.2f} MB, Benötigt: {required_ram} MB"
            logger.warning(message)
            return False, message
        else:
            return True, f"Ausreichend RAM verfügbar: {available_ram:.2f} MB"
    except Exception as e:
        logger.error(f"Fehler bei der Speicherprüfung: {e}")
        # Im Fehlerfall erlauben wir die Modellladung, geben aber eine Warnung aus
        return True, f"Speicherprüfung fehlgeschlagen: {e}"

def download_model(model_name: str, config: Optional[Dict] = None) -> str:
    """
    Download a Whisper model.
    
    Args:
        model_name: Name of the model
        config: Configuration dictionary
        
    Returns:
        Path to downloaded model file
    """
    # Speicherprüfung durchführen
    has_enough_memory, message = check_memory_for_model(model_name)
    if not has_enough_memory:
        raise ModelError(f"Speicherprüfung fehlgeschlagen: {message}")
    
    # Get models directory from config
    models_dir = str(Path.home() / "whisper_models")
    if config and "whisper" in config and "model_path" in config["whisper"]:
        models_dir = config["whisper"]["model_path"]
    
    # Ensure models directory exists
    ensure_directory_exists(models_dir)
    
    # Construct model path and URL
    model_path = os.path.join(models_dir, f"ggml-{model_name}.bin")
    model_url = f"{WHISPER_CPP_MODELS_URL}/ggml-{model_name}.bin"
    
    # Check if model already exists
    if os.path.exists(model_path):
        logger.info(f"Model {model_name} already exists at {model_path}")
        return model_path
    
    # Download model
    logger.info(f"Downloading model {model_name} from {model_url}")
    publish(EventType.MODEL_DOWNLOAD_STARTED, {"model": model_name, "url": model_url})
    
    try:
        with requests.get(model_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(model_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Report progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            publish(EventType.PROGRESS_UPDATE, {
                                "task": "model_download",
                                "progress": progress,
                                "model": model_name
                            })
        
        logger.info(f"Model {model_name} downloaded to {model_path}")
        publish(EventType.MODEL_DOWNLOAD_COMPLETED, {"model": model_name, "path": model_path})
        return model_path
    
    except Exception as e:
        logger.error(f"Error downloading model {model_name}: {e}")
        publish(EventType.MODEL_DOWNLOAD_FAILED, {"model": model_name, "error": str(e)})
        raise ModelError(f"Failed to download model {model_name}: {e}")


def list_models(config: Optional[Dict] = None) -> List[str]:
    """
    List available Whisper models.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of available model names
    """
    # Get models directory from config
    models_dir = str(Path.home() / "whisper_models")
    if config and "whisper" in config and "model_path" in config["whisper"]:
        models_dir = config["whisper"]["model_path"]
    
    # Ensure models directory exists
    ensure_directory_exists(models_dir)
    
    # List model files
    model_files = []
    for file in os.listdir(models_dir):
        if file.startswith("ggml-") and file.endswith(".bin"):
            model_name = file[5:-4]  # Remove "ggml-" prefix and ".bin" suffix
            model_files.append(model_name)
    
    return model_files


def transcribe_audio(
    audio_path: Union[str, Path],
    output_format: Union[str, OutputFormat] = OutputFormat.TXT,
    language: Optional[str] = None,
    model: Union[str, WhisperModel] = DEFAULT_MODEL,
    output_path: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    srt_max_chars: Optional[int] = None,
    srt_max_duration: Optional[float] = None,
    srt_linebreaks: bool = True,
    config: Optional[Dict] = None
) -> TranscriptionResult:
    """
    Transcribe an audio file using Whisper.cpp.
    
    Args:
        audio_path: Path to audio file
        output_format: Output format
        language: Language code (None for auto-detection)
        model: Whisper model to use
        output_path: Output file path
        output_dir: Custom output directory (overrides default_directory from config)
        srt_max_chars: Max chars per subtitle segment for SRT
        srt_max_duration: Max duration per subtitle segment in seconds
        config: Configuration dictionary
        
    Returns:
        TranscriptionResult object
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Convert string parameters to enums if needed
    if isinstance(output_format, str):
        output_format = OutputFormat(output_format)
    
    if isinstance(model, str):
        model = WhisperModel(model)
    
    # Validate audio file
    audio_path = str(audio_path)
    if not os.path.exists(audio_path):
        error_msg = f"Audio file not found: {audio_path}"
        logger.error(error_msg)
        return TranscriptionResult(success=False, error=error_msg)
    
    # Generate transcription ID for tracking
    import uuid
    transcription_id = str(uuid.uuid4())[:8]
    
    # Sende initiale Status-Nachricht
    publish(EventType.PROGRESS_UPDATE, {
        'task': 'transcription',
        'status': 'Initialisiere Transkription...',
        'progress': 0,
        'user_id': transcription_id,
        'phase': 'initialization'
    })
    
    # Check if file should be chunked for processing
    chunking_enabled = config.get("chunking", {}).get("enabled", True)
    
    # Analysiere Audio-Datei
    publish(EventType.PROGRESS_UPDATE, {
        'task': 'transcription',
        'status': 'Analysiere Audio-Datei...',
        'progress': 2,
        'user_id': transcription_id,
        'phase': 'analyzing'
    })
    
    if chunking_enabled and is_audio_chunkable(audio_path, config):
        logger.info(f"Audio file is large, will process in chunks")
        
        # Get audio duration for status message
        from ..core.audio_chunker import AudioChunker
        chunker = AudioChunker(config)
        duration_seconds = chunker.get_audio_duration(audio_path)
        duration_minutes = duration_seconds / 60
        num_chunks = int(duration_minutes / 20) + 1
        
        publish(EventType.PROGRESS_UPDATE, {
            'task': 'transcription',
            'status': f'Audio-Datei ist {duration_minutes:.1f} Minuten lang. Teile in {num_chunks} Segmente auf...',
            'user_id': transcription_id
        })
        
        return transcribe_audio_chunked(
            audio_path=audio_path,
            output_format=output_format,
            language=language,
            model=model,
            output_path=output_path,
            output_dir=output_dir,
            srt_max_chars=srt_max_chars,
            srt_max_duration=srt_max_duration,
            srt_linebreaks=srt_linebreaks,
            config=config
        )
    
    # Generate output path if not provided
    if output_path is None:
        # Bestimme das Ausgabeverzeichnis - entweder benutzerdefiniert oder Standard
        output_directory = output_dir if output_dir else config["output"]["default_directory"]
        logger.info(f"Ausgabeverzeichnis: {output_directory}")
        
        # Verwende die utility-Funktion, um den vollständigen Pfad zu generieren
        output_path = get_output_path(audio_path, output_directory, output_format.value)
    else:
        output_path = str(output_path)
    
    # Ensure output directory exists
    ensure_directory_exists(os.path.dirname(output_path))
    
    # Publish event
    publish(EventType.TRANSCRIPTION_STARTED, {
        "audio_path": audio_path,
        "model": model.value,
        "language": language,
        "output_format": output_format.value,
        "output_path": output_path
    })
    
    # Status update für normale Transkription
    publish(EventType.PROGRESS_UPDATE, {
        'task': 'transcription',
        'status': f'Starte Transkription mit Modell {model.value}...',
        'user_id': transcription_id
    })
    
    publish(EventType.PROGRESS_UPDATE, {
        "task": "transcription",
        "status": f"Transkription mit Modell {model.value} wird gestartet...",
        "progress": 5,
        "user_id": transcription_id
    })
    
    try:
        # Get whisper binary path
        whisper_path = get_whisper_binary_path(config)
        
        # Get model path (download if needed)
        try:
            model_path = get_model_path(model.value, config)
        except ModelError:
            logger.info(f"Model {model.value} not found, downloading...")
            model_path = download_model(model.value, config)
        
        # Prepare command
        cmd = [
            whisper_path,
            "-m", model_path,
            "-f", audio_path,
            "-otxt",
            "-osrt"  # Die `-ojson` Option wird nicht unterstützt
        ]
        
        # Add language if specified
        if language:
            cmd.extend(["-l", language])
        
        # Add threads parameter if specified in config
        if "whisper" in config and "threads" in config["whisper"]:
            cmd.extend(["-t", str(config["whisper"]["threads"])])
        
        # Metal wird automatisch erkannt, wenn verfügbar
        # Keine explizite Option notwendig für Whisper.cpp auf Apple Silicon
        
        # Verwende das konfigurierte temporäre Verzeichnis
        system_temp = False
        if "output" in config and "temp_directory" in config["output"]:
            temp_dir = config["output"]["temp_directory"]
            # Stelle sicher, dass das Verzeichnis existiert
            os.makedirs(temp_dir, exist_ok=True)
            logger.info(f"Verwende konfiguriertes Temp-Verzeichnis: {temp_dir}")
        else:
            # Fallback: Erstelle ein temporäres Verzeichnis im Projektordner
            # Ermittle das Projektverzeichnis
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigiere zu src
            while current_dir and not os.path.basename(current_dir) == 'src':
                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:
                    break
                current_dir = parent_dir
            # Projektverzeichnis ist eine Ebene höher als src
            project_dir = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'src' else os.path.dirname(os.path.abspath(__file__))
            # Erstelle Temp-Verzeichnis im Projektordner
            temp_dir = os.path.join(project_dir, "transcriptions", "temp")
            os.makedirs(temp_dir, exist_ok=True)
            logger.info(f"Fallback-Temp-Verzeichnis erstellt: {temp_dir}")
            # Aktualisiere die Konfiguration
            if "output" not in config:
                config["output"] = {}
            config["output"]["temp_directory"] = temp_dir
            
        try:
            # Überprüfe, ob die Eingabedatei ein Video ist
            is_video = False
            video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm"]
            for ext in video_extensions:
                if audio_path.lower().endswith(ext):
                    is_video = True
                    break
            
            audio_input_path = audio_path
            temp_audio_path = None
            
            # Wenn es sich um ein Video handelt, extrahiere die Audiodaten
            if is_video:
                logger.info(f"Eingabedatei ist ein Video. Extrahiere Audiodaten...")
                filename = os.path.basename(audio_path)
                name, _ = os.path.splitext(filename)
                temp_audio_path = os.path.join(temp_dir, f"{name}_audio.wav")
                
                try:
                    # Verwende ffmpeg zur Extraktion der Audiodaten
                    ffmpeg_cmd = [
                        "ffmpeg", "-i", audio_path, "-vn", "-acodec", "pcm_s16le",
                        "-ar", "16000", "-ac", "1", temp_audio_path, "-y"
                    ]
                    
                    logger.info(f"Ausführen des Befehls: {' '.join(ffmpeg_cmd)}")
                    result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
                    
                    if os.path.exists(temp_audio_path):
                        logger.info(f"Audiodaten erfolgreich extrahiert: {temp_audio_path}")
                        audio_input_path = temp_audio_path
                    else:
                        logger.warning(f"Konnte Audiodaten nicht extrahieren. Versuche direkte Verarbeitung.")
                except Exception as e:
                    logger.warning(f"Fehler bei der Audioextraktion: {e}. Versuche direkte Verarbeitung.")
            
            # Set the current directory to temp_dir (important for output files)
            os.chdir(temp_dir)
            
            # Aktualisiere den Whisper-Befehl mit dem richtigen Audioeingabepfad
            for i, arg in enumerate(cmd):
                if arg == "-f" and i + 1 < len(cmd):
                    cmd[i + 1] = audio_input_path
                    break
            
            # Add output file parameter - use absolute path
            output_prefix = os.path.join(temp_dir, "output")
            logger.info(f"Setting output prefix to: {output_prefix}")
            cmd.extend(["-of", output_prefix])
            
            # Run whisper.cpp with Fortschrittsu00fcberwachung
            logger.info(f"Running command: {' '.join(cmd)}")
            logger.info(f"Working in directory: {temp_dir}, checking existence: {os.path.exists(temp_dir)}")
            
            # Status update
            publish(EventType.PROGRESS_UPDATE, {
                "task": "transcription",
                "status": "Whisper-Modell wird geladen und Transkription läuft...",
                "progress": 20
            })
            
            # Prozess starten mit Pipes, um Ausgabe in Echtzeit zu lesen
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered
                cwd=temp_dir
            )
            
            # Prozess global speichern für Abbruch
            global current_transcription_process
            current_transcription_process = process
            
            # UUID fu00fcr diese Transkription generieren
            import uuid
            transcription_id = str(uuid.uuid4())
            
            stdout = []
            stderr = []
            
            # Fortschrittsanzeige-Muster (wird von Whisper.cpp ausgegeben)
            import re
            progress_pattern = re.compile(r'\[(\s*)([0-9]+)%\]')
            
            # Standard-Ausgabe und Fehlerausgabe in Echtzeit verarbeiten
            while True:
                # Stdout verarbeiten, wenn verfu00fcgbar
                stdout_line = process.stdout.readline()
                if stdout_line:
                    stdout.append(stdout_line)
                    # Debug-Ausgabe im Terminal anzeigen
                    terminal_msg = f"[WHISPER PROGRESS] {stdout_line.strip()}"
                    print(terminal_msg, flush=True)
                    logger.debug(f"Whisper stdout: {stdout_line.strip()}")
                    
                    # Terminal output über WebSocket senden
                    publish(EventType.PROGRESS_UPDATE, {
                        'task': 'transcription',
                        'terminal_output': terminal_msg,
                        'user_id': transcription_id
                    })
                    
                    # Fortschritt erkennen und Event veru00f6ffentlichen
                    match = progress_pattern.search(stdout_line)
                    if match:
                        progress = int(match.group(2))
                        # Terminal-Ausgabe für Progress
                        print(f"[PROGRESS UPDATE] Transkription bei {progress}%", flush=True)                        # Fortschrittsereignis veru00f6ffentlichen
                        publish(EventType.PROGRESS_UPDATE, {
                            'task': 'transcription',
                            'progress': progress,
                            'status': f'Transkribiere... {progress}%',
                            'terminal_output': f"[PROGRESS UPDATE] Transkription bei {progress}%",
                            'audio_path': audio_path,
                            'user_id': transcription_id  # ID zur Identifizierung des Clients
                        })
                
                # Stderr verarbeiten, wenn verfu00fcgbar
                stderr_line = process.stderr.readline()
                if stderr_line:
                    stderr.append(stderr_line)
                    logger.debug(f"Whisper stderr: {stderr_line.strip()}")
                
                # Pru00fcfen, ob der Prozess abgeschlossen ist
                if process.poll() is not None:
                    # Restliche Ausgabe lesen
                    for line in process.stdout.readlines():
                        stdout.append(line)
                    for line in process.stderr.readlines():
                        stderr.append(line)
                    break
            
            # Ergebnis zusammensetzen
            returncode = process.returncode
            stdout_text = ''.join(stdout)
            stderr_text = ''.join(stderr)
            
            # Debug: Liste der Dateien im temporären Verzeichnis nach dem Befehl
            logger.info(f"Files in {temp_dir} after command:")
            try:
                for file in os.listdir(temp_dir):
                    logger.info(f"Found file: {os.path.join(temp_dir, file)}")
            except Exception as e:
                logger.error(f"Error listing files in {temp_dir}: {e}")
            
            logger.info(f"Command stdout: {stdout_text[:500]}...")
            logger.info(f"Command stderr: {stderr_text[:500]}...")
            
            # Abschluss-Fortschritt senden
            if returncode == 0:
                publish(EventType.PROGRESS_UPDATE, {
                    'task': 'transcription',
                    'progress': 95,
                    'status': 'Verarbeite Transkriptionsergebnis...',
                    'audio_path': audio_path,
                    'user_id': transcription_id,
                    'phase': 'post_processing'
                })
            else:
                publish(EventType.PROGRESS_UPDATE, {
                    'task': 'transcription',
                    'progress': 0,
                    'status': 'Transkription fehlgeschlagen',
                    'audio_path': audio_path,
                    'user_id': transcription_id,
                    'phase': 'failed'
                })
            
            if returncode != 0:
                error_msg = f"Whisper.cpp failed with return code {returncode}: {stderr}"
                logger.error(error_msg)
                publish(EventType.TRANSCRIPTION_FAILED, {
                    "audio_path": audio_path,
                    "error": error_msg
                })
                return TranscriptionResult(success=False, error=error_msg, stderr=stderr)
            
            # Read output text
            txt_output = os.path.join(temp_dir, "output.txt")
            if not os.path.exists(txt_output):
                error_msg = f"Output file not found: {txt_output}"
                logger.error(error_msg)
                publish(EventType.TRANSCRIPTION_FAILED, {
                    "audio_path": audio_path,
                    "error": error_msg
                })
                return TranscriptionResult(success=False, error=error_msg)
            
            with open(txt_output, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Convert to requested format
            if output_format == OutputFormat.TXT:
                # Copy the txt file to output path
                shutil.copy(txt_output, output_path)
            elif output_format == OutputFormat.SRT:
                logger.info("Processing SRT output format (immer eigene Generierung mit segments_to_srt).")
                json_output = parse_whisper_output(temp_dir, ["json"]).get("json")
                if json_output and isinstance(json_output, dict) and "segments" in json_output:
                    srt_content = segments_to_srt(json_output["segments"], max_chars=srt_max_chars, max_duration=srt_max_duration, linebreaks=srt_linebreaks)
                    
                    # JSON-Kontroll-Export erzeugen (bei jeder SRT-Transkription)
                    try:
                        from .output_formatter import export_json_control
                        json_control_path = export_json_control(json_output["segments"], output_path)
                        logger.info(f"JSON-Kontroll-Export erstellt: {json_control_path}")
                    except Exception as e:
                        logger.warning(f"Fehler beim Erstellen des JSON-Kontroll-Exports: {str(e)}")
                else:
                    srt_content = text_to_srt(text, max_chars=srt_max_chars, max_duration=srt_max_duration, linebreaks=srt_linebreaks)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                logger.info(f"SRT wurde immer mit segments_to_srt erzeugt (max_chars={srt_max_chars}, max_duration={srt_max_duration}, linebreaks={srt_linebreaks}) und gespeichert unter: {output_path}")
            elif output_format == OutputFormat.VTT:
                # Convert txt to VTT (simplified)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write("WEBVTT\n\n00:00:00.000 --> 00:05:00.000\n" + text + "\n\n")
            elif output_format == OutputFormat.JSON:
                # Create a simple JSON structure
                json_data = {
                    "text": text,
                    "segments": [{"text": text, "start": 0, "end": 300}]
                }
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2)
            
            # Send final progress update
            publish(EventType.PROGRESS_UPDATE, {
                'task': 'transcription',
                'progress': 100,
                'status': 'Transkription abgeschlossen',
                'audio_path': audio_path,
                'user_id': transcription_id,
                'phase': 'completed'
            })
            
            # Publish success event
            publish(EventType.TRANSCRIPTION_COMPLETED, {
                "audio_path": audio_path,
                "output_path": output_path,
                "model": model.value,
                "language": language
            })
            
            # Clean up audio file after successful transcription
            try:
                cleanup_after_transcription(audio_path, config)
                logger.info(f"Cleaned up audio file: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup audio file: {e}")
            
            # Return result
            return TranscriptionResult(
                success=True,
                text=text,
                output_file=output_path,
                language=language,
                model=model.value
            )
        finally:
            # Clean up temporary directory if we created one
            if system_temp and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
    
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        logger.error(error_msg)
        publish(EventType.TRANSCRIPTION_FAILED, {
            "audio_path": audio_path,
            "error": error_msg
        })
        return TranscriptionResult(success=False, error=error_msg)


def transcribe_audio_chunked(
    audio_path: Union[str, Path],
    output_format: Union[str, OutputFormat] = OutputFormat.TXT,
    language: Optional[str] = None,
    model: Union[str, WhisperModel] = DEFAULT_MODEL,
    output_path: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    srt_max_chars: Optional[int] = None,
    srt_max_duration: Optional[float] = None,
    srt_linebreaks: bool = True,
    config: Optional[Dict] = None
) -> TranscriptionResult:
    """
    Transcribe a large audio file by splitting it into chunks.
    
    Args:
        Same as transcribe_audio
        
    Returns:
        TranscriptionResult object
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Convert string parameters to enums if needed
    if isinstance(output_format, str):
        output_format = OutputFormat(output_format)
    
    if isinstance(model, str):
        model = WhisperModel(model)
    
    audio_path = str(audio_path)
    chunker = AudioChunker(config)
    
    # Generate transcription ID for tracking
    import uuid
    transcription_id = str(uuid.uuid4())[:8]
    
    try:
        # Split audio into chunks
        logger.info(f"Splitting large audio file into chunks...")
        
        # Get audio duration for status message
        duration_seconds = chunker.get_audio_duration(audio_path)
        duration_minutes = duration_seconds / 60
        num_expected_chunks = int(duration_minutes / 20) + 1
        
        publish(EventType.PROGRESS_UPDATE, {
            'task': 'transcription',
            'status': f'Audio-Datei ist {duration_minutes:.1f} Minuten lang. Erstelle {num_expected_chunks} Segmente...',
            'user_id': transcription_id
        })
        
        publish(EventType.PROGRESS_UPDATE, {
            "task": "chunking",
            "status": "Audio-Datei wird in Chunks aufgeteilt...",
            "progress": 0,
            "user_id": transcription_id
        })
        publish(EventType.CUSTOM, {
            "type": "CHUNKING_STARTED",
            "audio_path": audio_path,
            "user_id": transcription_id
        })
        
        chunks = chunker.split_audio(audio_path)
        logger.info(f"Created {len(chunks)} chunks for processing")
        
        publish(EventType.PROGRESS_UPDATE, {
            'task': 'transcription',
            'status': f'{len(chunks)} Segmente erstellt. Starte Transkription...',
            'user_id': transcription_id
        })
        
        publish(EventType.PROGRESS_UPDATE, {
            "task": "chunking",
            "status": f"{len(chunks)} Chunks erfolgreich erstellt",
            "chunks": len(chunks),
            "progress": 100,
            "user_id": transcription_id
        })
        
        # Transcribe each chunk
        chunk_transcriptions = []
        all_segments = []
        
        for i, chunk_info in enumerate(chunks):
            chunk_num = i + 1
            logger.info(f"Processing chunk {chunk_num}/{len(chunks)}: {chunk_info['filename']}")
            
            # Calculate overall progress for chunks
            base_progress = (i / len(chunks)) * 90  # 0-90% for chunks, 90-100% for merging
            
            # Status update for current chunk
            publish(EventType.PROGRESS_UPDATE, {
                'task': 'transcription',
                'status': f'Verarbeite Segment {chunk_num}/{len(chunks)}...',
                'progress': base_progress,
                'user_id': transcription_id,
                'phase': 'chunk_processing',
                'chunk_current': chunk_num,
                'chunk_total': len(chunks)
            })
            
            publish(EventType.CUSTOM, {
                "type": "CHUNK_STARTED",
                "chunk": chunk_num,
                "total": len(chunks),
                "filename": chunk_info['filename'],
                "user_id": transcription_id
            })
            
            # Transcribe chunk (recursive call without chunking)
            chunk_config = config.copy()
            chunk_config["chunking"]["enabled"] = False  # Disable chunking for individual chunks
            
            chunk_result = transcribe_audio(
                audio_path=chunk_info['path'],
                output_format=OutputFormat.JSON,  # Get JSON for segment timing
                language=language,
                model=model,
                config=chunk_config
            )
            
            if not chunk_result.success:
                logger.error(f"Failed to transcribe chunk {chunk_num}: {chunk_result.error}")
                publish(EventType.CUSTOM, {
                    "type": "CHUNK_FAILED",
                    "chunk": chunk_num,
                    "error": chunk_result.error
                })
                # Continue with other chunks even if one fails
                continue
            
            # Adjust timestamps for chunk position
            chunk_start_time = chunk_info['start_time']
            if chunk_result.segments:
                adjusted_segments = []
                for segment in chunk_result.segments:
                    adjusted_segment = segment.copy()
                    adjusted_segment['start'] = segment.get('start', 0) + chunk_start_time
                    adjusted_segment['end'] = segment.get('end', 0) + chunk_start_time
                    adjusted_segments.append(adjusted_segment)
                all_segments.extend(adjusted_segments)
            
            chunk_transcriptions.append({
                "chunk": chunk_num,
                "text": chunk_result.text,
                "start_time": chunk_start_time
            })
            
            publish(EventType.CUSTOM, {
                "type": "CHUNK_COMPLETED",
                "chunk": chunk_num,
                "total": len(chunks),
                "progress": (chunk_num / len(chunks)) * 100
            })
        
        # Merge transcriptions
        logger.info("Merging chunk transcriptions...")
        merged_text = chunker.merge_transcriptions(chunk_transcriptions, remove_overlap=True)
        
        # Generate output path if not provided
        if output_path is None:
            output_directory = output_dir if output_dir else config["output"]["default_directory"]
            output_path = get_output_path(audio_path, output_directory, output_format.value)
        else:
            output_path = str(output_path)
        
        # Ensure output directory exists
        ensure_directory_exists(os.path.dirname(output_path))
        
        # Save output in requested format
        if output_format == OutputFormat.TXT:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(merged_text)
        elif output_format == OutputFormat.SRT:
            if all_segments:
                srt_content = segments_to_srt(all_segments, max_chars=srt_max_chars, 
                                             max_duration=srt_max_duration, linebreaks=srt_linebreaks)
            else:
                srt_content = text_to_srt(merged_text, max_chars=srt_max_chars, 
                                        max_duration=srt_max_duration, linebreaks=srt_linebreaks)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
        elif output_format == OutputFormat.VTT:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n00:00:00.000 --> 00:05:00.000\n" + merged_text + "\n\n")
        elif output_format == OutputFormat.JSON:
            output_data = {
                "text": merged_text,
                "segments": all_segments,
                "chunks": len(chunks)
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Clean up chunks
        chunk_dir = os.path.dirname(chunks[0]['path']) if chunks else None
        if chunk_dir:
            chunker.cleanup_chunks(chunk_dir)
        
        logger.info(f"Successfully transcribed {len(chunks)} chunks")
        
        publish(EventType.TRANSCRIPTION_COMPLETED, {
            "audio_path": audio_path,
            "output_path": output_path,
            "chunks": len(chunks),
            "text": merged_text
        })
        
        # Clean up audio file and chunks after successful transcription
        try:
            config = load_config()
            cleanup_after_transcription(audio_path, config)
            logger.info(f"Cleaned up audio file and chunks: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup audio file: {e}")
        
        return TranscriptionResult(
            success=True,
            text=merged_text,
            output_file=output_path,
            segments=all_segments,
            model=model.value,
            language=language
        )
        
    except Exception as e:
        error_msg = f"Error in chunked transcription: {str(e)}"
        logger.error(error_msg)
        publish(EventType.TRANSCRIPTION_FAILED, {
            "audio_path": audio_path,
            "error": error_msg
        })
        return TranscriptionResult(success=False, error=error_msg)


# Removed parse_args and main CLI logic from this module (moved to main.py)
