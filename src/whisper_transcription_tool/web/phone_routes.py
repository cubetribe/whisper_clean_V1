"""API-Routen für die Telefonaufnahme-Funktionalität.

Stellt die API-Endpoints für die Telefonanrufsaufnahme mit BlackHole zur Verfügung.
Ermittelbare Aufnahmegeräte, Steuerung von Aufnahmen und Verarbeitung aufgenommener
Audiospuren.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import der Aufnahmeklassen
from ..module3_phone import AudioRecorder, DeviceManager, RecordingConfig, RecordingSession

router = APIRouter(prefix="/api/phone")
logger = logging.getLogger(__name__)

# Globale Instanz des AudioRecorders
audio_recorder = AudioRecorder()


class RecordingRequest(BaseModel):
    """Anforderung zum Starten einer Aufnahme."""
    input_device_id: str
    output_device_id: str
    sample_rate: int = 44100
    max_duration_sec: int = 0  # 0 = unbegrenzt


@router.get("/devices")
async def get_audio_devices():
    """Liste aller verfügbaren Audiogeräte."""
    try:
        devices = DeviceManager.list_devices()
        blackhole_found = DeviceManager.is_blackhole_installed()
        
        # Trennung von Ein- und Ausgabegeräten
        input_devices = [d for d in devices if d['is_input']]
        output_devices = [d for d in devices if d['is_output']]
        
        # Default-Markierung hinzufügen
        default_input = DeviceManager.get_default_input_device()
        default_output = DeviceManager.get_default_output_device()
        
        for device in input_devices:
            device['is_default'] = (device['id'] == default_input.get('id', -1))
            
        for device in output_devices:
            device['is_default'] = (device['id'] == default_output.get('id', -1))
        
        return {
            "input_devices": input_devices,
            "output_devices": output_devices,
            "blackhole_found": blackhole_found
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Audiogeräte: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recording/start")
async def start_recording(request: RecordingRequest):
    """Startet eine neue Aufnahmesitzung."""
    try:
        # Prüfen, ob BlackHole installiert ist
        if not DeviceManager.is_blackhole_installed():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "BlackHole nicht installiert. Bitte installieren Sie BlackHole."
                }
            )
        
        # Aufnahmekonfiguration erstellen
        output_dir = Path("recordings")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = RecordingConfig(
            input_device_id=request.input_device_id,
            output_device_id=request.output_device_id,
            sample_rate=request.sample_rate,
            max_duration_sec=request.max_duration_sec,
            output_directory=str(output_dir)
        )
        
        # Session erstellen
        session = audio_recorder.create_session(config)
        
        # Aufnahme starten
        success = audio_recorder.start_recording(session.session_id)
        
        if success:
            return {
                "success": True,
                "session_id": session.session_id,
                "message": "Aufnahme gestartet"
            }
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Fehler beim Starten der Aufnahme"
                }
            )
            
    except Exception as e:
        logger.error(f"Fehler beim Starten der Aufnahme: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/recording/{session_id}/pause")
async def pause_recording(session_id: str):
    """Pausiert eine laufende Aufnahme."""
    try:
        session = audio_recorder.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Sitzung {session_id} nicht gefunden"
                }
            )
        
        success = audio_recorder.pause_recording()
        
        return {
            "success": success,
            "message": "Aufnahme pausiert" if success else "Fehler beim Pausieren"
        }
    except Exception as e:
        logger.error(f"Fehler beim Pausieren der Aufnahme: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/recording/{session_id}/resume")
async def resume_recording(session_id: str):
    """Setzt eine pausierte Aufnahme fort."""
    try:
        session = audio_recorder.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Sitzung {session_id} nicht gefunden"
                }
            )
        
        success = audio_recorder.resume_recording()
        
        return {
            "success": success,
            "message": "Aufnahme fortgesetzt" if success else "Fehler beim Fortsetzen"
        }
    except Exception as e:
        logger.error(f"Fehler beim Fortsetzen der Aufnahme: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/recording/{session_id}/stop")
async def stop_recording(session_id: str):
    """Beendet eine laufende Aufnahme."""
    try:
        session = audio_recorder.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Sitzung {session_id} nicht gefunden"
                }
            )
        
        # Aufnahme stoppen
        success = audio_recorder.stop_recording()
        
        if success:
            # Aktualisierte Informationen holen
            session = audio_recorder.get_session(session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "files": session.file_paths,
                "duration": session.duration_seconds,
                "message": "Aufnahme beendet"
            }
        else:
            # Immer 200 OK, auch wenn Stop fehlgeschlagen (z.B. keine aktive Aufnahme)
            return {
                "success": False,
                "session_id": session_id,
                "message": "Keine aktive Aufnahme oder bereits gestoppt"
            }
    except Exception as e:
        logger.error(f"Fehler beim Beenden der Aufnahme: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


def transcribe_recording_task(session_id: str) -> Dict:
    """Hintergrundaufgabe zum Aufbereiten der Aufnahmedateien.
    
    Args:
        session_id: ID der Aufnahmesitzung
        
    Returns:
        Dict: Ergebnis mit Dateipfaden der Audioaufnahmen
    """
    try:
        session = audio_recorder.get_session(session_id)
        if not session:
            return {
                "success": False,
                "error": f"Sitzung {session_id} nicht gefunden"
            }
        
        # Audiodateien aus der Session holen
        mic_file = session.file_paths.get('microphone')
        sys_file = session.file_paths.get('system')
        
        if not mic_file or not sys_file:
            return {
                "success": False,
                "error": "Audiodateien nicht gefunden"
            }
        
        # Audio-Dateien für Frontend-Anzeige vorbereiten
        audio_files = [
            {"path": mic_file, "type": "mic"},
            {"path": sys_file, "type": "sys"}
        ]
        
        return {
            "success": True,
            "session_id": session_id,
            "audio_files": audio_files
        }
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung der Aufnahme: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/recording/{session_id}/process")
async def process_recording(session_id: str, background_tasks: BackgroundTasks):
    """Verarbeitet eine aufgenommene Audiositzung."""
    try:
        session = audio_recorder.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Sitzung {session_id} nicht gefunden"
                }
            )
        
        # Für asynchrone Verarbeitung vorbereiten
        # Dies startet die Transkription als Hintergrundaufgabe
        # In einer echten Implementierung würde hier der Fortschritt über WebSockets oder einen anderen
        # Mechanismus zurückgemeldet werden
        
        # Transkriptionsverzeichnis erstellen
        transcript_dir = Path("transcripts")
        transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # Vorläufiges Ergebnis (simuliert)
        result = transcribe_recording_task(session_id)
        
        return result
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/")
async def process_phone_recordings(
    track_a: UploadFile = File(...),
    track_b: UploadFile = File(...)
):
    """Verarbeitet hochgeladene Telefonspur-Dateien.
    
    Dies ist der ursprüngliche Endpunkt für den Datei-Upload,
    der weiterhin für die Kompatibilität beibehalten wird.
    """
    try:
        # Dateien speichern
        track_a_path = f"uploads/{uuid.uuid4()}_{track_a.filename}"
        track_b_path = f"uploads/{uuid.uuid4()}_{track_b.filename}"
        
        os.makedirs("uploads", exist_ok=True)
        
        with open(track_a_path, "wb") as f:
            f.write(track_a.file.read())
            
        with open(track_b_path, "wb") as f:
            f.write(track_b.file.read())
        
        # Hier würde die tatsächliche Verarbeitung erfolgen
        # Dies ist ein Platzhalter für die eigentliche Implementierung
        
        output_file = f"transcripts/phone_{uuid.uuid4()}.srt"
        
        return {
            "success": True,
            "track_a": track_a.filename,
            "track_b": track_b.filename,
            "output_file": output_file
        }
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung von Telefondateien: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
