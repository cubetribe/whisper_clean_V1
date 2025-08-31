"""Audioaufnahme-Modul mit BlackHole-Integration.

Dieses Modul stellt Funktionen zur Aufzeichnung von Telefonaten mit getrennten
Spuren fu00fcr Mikrofon und Systemton bereit. Es nutzt BlackHole als virtuelle
Audioschnittstelle, um den Systemton abzugreifen.
"""

import sounddevice as sd
import numpy as np
import threading
import time
import wave
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Callable, Any
import logging
from pathlib import Path

from .models import RecordingSession, RecordingConfig, RecordingStatus

logger = logging.getLogger(__name__)


class DeviceManager:
    """Verwaltet Audio-Ein- und Ausgabegeru00e4te.
    
    Diese Klasse ermu00f6glicht die Erkennung und Verwaltung der Audiogeru00e4te
    inkl. BlackHole als virtuelle Audioschnittstelle.
    """
    
    @staticmethod
    def list_devices() -> List[Dict]:
        """Gibt eine Liste der verfu00fcgbaren Audiogeru00e4te zuru00fcck."""
        devices = sd.query_devices()
        return [{
            'id': i,
            'name': device['name'],
            'channels_in': device['max_input_channels'],
            'channels_out': device['max_output_channels'],
            'default_samplerate': device['default_samplerate'],
            'is_input': device['max_input_channels'] > 0,
            'is_output': device['max_output_channels'] > 0
        } for i, device in enumerate(devices)]
    
    @staticmethod
    def find_blackhole_device() -> Optional[Dict]:
        """Sucht nach BlackHole Audiogeru00e4ten."""
        devices = DeviceManager.list_devices()
        for device in devices:
            if 'BlackHole' in device['name']:
                return device
        return None
    
    @staticmethod
    def get_default_input_device() -> Dict:
        """Gibt das Standard-Eingabegeru00e4t zuru00fcck."""
        try:
            device_id = sd.default.device[0]
            devices = DeviceManager.list_devices()
            for device in devices:
                if device['id'] == device_id:
                    return device
            # Fallback: Erstes Eingabegeru00e4t
            input_devices = [d for d in devices if d['is_input']]
            return input_devices[0] if input_devices else {}
        except Exception as e:
            logger.error(f"Fehler beim Ermitteln des Standard-Eingabegeru00e4ts: {e}")
            return {}
    
    @staticmethod
    def get_default_output_device() -> Dict:
        """Gibt das Standard-Ausgabegeru00e4t zuru00fcck."""
        try:
            device_id = sd.default.device[1]
            devices = DeviceManager.list_devices()
            for device in devices:
                if device['id'] == device_id:
                    return device
            # Fallback: Erstes Ausgabegeru00e4t
            output_devices = [d for d in devices if d['is_output']]
            return output_devices[0] if output_devices else {}
        except Exception as e:
            logger.error(f"Fehler beim Ermitteln des Standard-Ausgabegeru00e4ts: {e}")
            return {}
    
    @staticmethod
    def is_blackhole_installed() -> bool:
        """Pru00fcft, ob BlackHole installiert ist."""
        return DeviceManager.find_blackhole_device() is not None
    
    @staticmethod
    def recommend_setup() -> Dict:
        """Empfiehlt eine Geru00e4tekonfiguration fu00fcr die Aufnahme."""
        devices = DeviceManager.list_devices()
        blackhole = DeviceManager.find_blackhole_device()
        input_device = DeviceManager.get_default_input_device()
        
        if not blackhole:
            return {
                'status': 'error',
                'message': 'BlackHole nicht gefunden. Bitte installieren Sie BlackHole.',
                'installation_guide': 'https://github.com/ExistentialAudio/BlackHole'
            }
        
        return {
            'status': 'ok',
            'recommended_setup': {
                'input_device': input_device,
                'output_device': blackhole,
                'sample_rate': int(blackhole.get('default_samplerate', 44100))
            }
        }


class AudioRecorder:
    """Aufnahme-Manager fu00fcr Audiosignale mit getrennten Kanu00e4len.
    
    Nutzt BlackHole als virtuelles Loopback-Geru00e4t, um Mikrofon- und
    Systemton getrennt aufzunehmen.
    """
    
    def __init__(self):
        """Initialisiert den Aufnahme-Manager."""
        self.sessions: Dict[str, RecordingSession] = {}
        self.active_session_id: Optional[str] = None
        self.recording_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_pause': [],
            'on_resume': [],
            'on_stop': [],
            'on_error': [],
            'on_progress': [],
        }
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Registriert einen Callback fu00fcr Ereignisse.
        
        Args:
            event_type: Ereignistyp ('on_start', 'on_pause', etc.)
            callback: Callback-Funktion
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
    
    def _trigger_callbacks(self, event_type: str, **kwargs) -> None:
        """Lu00f6st registrierte Callbacks aus."""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"Fehler beim Ausfu00fchren des {event_type}-Callbacks: {e}")
    
    def create_session(self, config: RecordingConfig) -> RecordingSession:
        """Erstellt eine neue Aufnahmesitzung.
        
        Args:
            config: Konfiguration fu00fcr die Aufnahme
            
        Returns:
            RecordingSession: Die erstellte Sitzung
        """
        session = RecordingSession(config=config)
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        """Gibt eine Aufnahmesitzung zuru00fcck.
        
        Args:
            session_id: ID der Sitzung
            
        Returns:
            Optional[RecordingSession]: Die Sitzung oder None
        """
        return self.sessions.get(session_id)
    
    def start_recording(self, session_id: str) -> bool:
        """Startet die Aufnahme.
        
        Args:
            session_id: ID der Sitzung
            
        Returns:
            bool: True, wenn erfolgreich gestartet
        """
        if self.active_session_id:
            logger.warning(f"Es lu00e4uft bereits eine Aufnahme ({self.active_session_id})")
            return False
        
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Sitzung {session_id} nicht gefunden")
            return False
        
        if session.status != RecordingStatus.NOT_STARTED and session.status != RecordingStatus.PAUSED:
            logger.warning(f"Sitzung {session_id} hat ungu00fcltigen Status: {session.status}")
            return False
        
        self.active_session_id = session_id
        session.start()
        
        # Recording-Thread starten
        self.stop_event.clear()
        self.recording_thread = threading.Thread(
            target=self._recording_worker,
            args=(session,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self._trigger_callbacks('on_start', session=session)
        return True
    
    def _recording_worker(self, session: RecordingSession) -> None:
        """Worker-Funktion fu00fcr die Aufnahme.
        
        Args:
            session: Aufnahmesitzung
        """
        try:
            config = session.config
            
            # Ausgabedateien vorbereiten
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(config.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            mic_filename = f"{config.filename_prefix}_mic_{timestamp}.{config.format}"
            sys_filename = f"{config.filename_prefix}_sys_{timestamp}.{config.format}"
            
            mic_path = output_dir / mic_filename
            sys_path = output_dir / sys_filename
            
            session.add_file('microphone', str(mic_path))
            session.add_file('system', str(sys_path))
            
            # Aufnahme-Buffer
            mic_buffer = []
            sys_buffer = []
            
            def audio_callback(indata, outdata, frames, time, status):
                """Callback fu00fcr den Audiostream."""
                if status:
                    logger.warning(f"Status: {status}")
                
                if session.status == RecordingStatus.RECORDING:
                    # Mikrofon-Daten (Kanal 0)
                    mic_data = indata[:, 0]
                    mic_buffer.append(mic_data.copy())
                    
                    # System-Daten von BlackHole (Kanal 0)
                    sys_data = outdata[:, 0] if outdata is not None else np.zeros_like(mic_data)
                    sys_buffer.append(sys_data.copy())
                    
                    # Progress-Callback
                    duration = len(mic_buffer) * frames / config.sample_rate
                    self._trigger_callbacks('on_progress', 
                                           session=session,
                                           duration=duration,
                                           status=session.status.value)
            
            # Stream starten
            input_device = int(config.input_device_id)
            output_device = int(config.output_device_id)
            
            # Geräteinfos abrufen, um Kanalkapazitäten zu prüfen
            try:
                input_info = sd.query_devices(input_device)
                output_info = sd.query_devices(output_device)
                
                # Sichere Kanaleinstellungen bestimmen
                input_channels = min(input_info['max_input_channels'], 2)  # Maximal 2 Kanäle, aber nicht mehr als das Gerät unterstützt
                output_channels = min(output_info['max_output_channels'], 2)
                
                # Die niedrigere Anzahl von Kanälen verwenden, um Kompatibilität sicherzustellen
                safe_channels = min(input_channels, output_channels, config.channels)
                
                if safe_channels < 1:
                    raise ValueError(f"Geräte unterstützen keine ausreichende Kanalanzahl: Input={input_channels}, Output={output_channels}")
                    
                logger.info(f"Angepasste Kanal-Konfiguration: {safe_channels} (original: {config.channels})")
                
                with sd.Stream(device=(input_device, output_device),
                               samplerate=config.sample_rate,
                               blocksize=1024,
                               channels=safe_channels,  # Verwende die sichere Kanalanzahl
                               callback=audio_callback):
                    logger.info(f"Aufnahme gestartet: {session.session_id}")
                    
                    while not self.stop_event.is_set():
                        time.sleep(0.1)
                        
                        # Prüfen, ob maximale Dauer erreicht
                        if config.max_duration_sec > 0:
                            current_duration = len(mic_buffer) * 1024 / config.sample_rate
                            if current_duration >= config.max_duration_sec:
                                logger.info(f"Maximale Aufnahmedauer erreicht: {config.max_duration_sec}s")
                                break
            except Exception as e:
                logger.error(f"Fehler beim Setup des Audio-Streams: {e}")
                session.set_error(str(e))
                raise
            
            # Aufgenommene Daten speichern
            if mic_buffer and session.status != RecordingStatus.ERROR:
                mic_data = np.concatenate(mic_buffer)
                sys_data = np.concatenate(sys_buffer) if sys_buffer else np.zeros_like(mic_data)
                
                # Als WAV speichern
                def save_to_wav(data, filepath, sample_rate, bit_depth):
                    """Speichert Audiodaten als WAV-Datei."""
                    if bit_depth == 24:
                        # 24-bit WAV wird nicht direkt unterstu00fctzt, Konvertierung notwendig
                        data = (data * (2**23-1)).astype(np.int32)
                        bytes_per_sample = 3
                    elif bit_depth == 16:
                        data = (data * (2**15-1)).astype(np.int16)
                        bytes_per_sample = 2
                    else:  # 32-bit float
                        bytes_per_sample = 4
                    
                    with wave.open(str(filepath), 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(bytes_per_sample)
                        wf.setframerate(sample_rate)
                        if bit_depth == 24:
                            # 24-bit Daten aus 32-bit extrahieren
                            packed_data = b''
                            for sample in data:
                                packed_data += sample.tobytes()[:3]
                            wf.writeframes(packed_data)
                        else:
                            wf.writeframes(data.tobytes())
                
                # Dateien speichern
                save_to_wav(mic_data, mic_path, config.sample_rate, config.bit_depth)
                save_to_wav(sys_data, sys_path, config.sample_rate, config.bit_depth)
                
                logger.info(f"Aufnahme gespeichert: {mic_path}, {sys_path}")
                session.complete()
            else:
                logger.warning("Keine Daten aufgenommen oder Fehler aufgetreten")
                if session.status != RecordingStatus.ERROR:
                    session.set_error("Keine Audiodaten aufgenommen")
        
        except Exception as e:
            logger.error(f"Fehler bei der Aufnahme: {e}")
            session.set_error(str(e))
            self._trigger_callbacks('on_error', session=session, error=str(e))
        finally:
            # Aufru00e4umen
            self.active_session_id = None
            self._trigger_callbacks('on_stop', session=session)
    
    def stop_recording(self) -> bool:
        """Stoppt die aktuelle Aufnahme.
        
        Returns:
            bool: True, wenn erfolgreich gestoppt
        """
        if not self.active_session_id:
            logger.warning("Keine aktive Aufnahme")
            return False
        
        session = self.get_session(self.active_session_id)
        if not session:
            logger.error(f"Aktive Sitzung {self.active_session_id} nicht gefunden")
            return False
        
        # Signal zum Stoppen senden
        self.stop_event.set()
        
        # Auf Thread-Ende warten
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5.0)
        
        return True
    
    def pause_recording(self) -> bool:
        """Pausiert die aktuelle Aufnahme.
        
        Returns:
            bool: True, wenn erfolgreich pausiert
        """
        if not self.active_session_id:
            logger.warning("Keine aktive Aufnahme")
            return False
        
        session = self.get_session(self.active_session_id)
        if not session:
            logger.error(f"Aktive Sitzung {self.active_session_id} nicht gefunden")
            return False
        
        session.pause()
        self._trigger_callbacks('on_pause', session=session)
        return True
    
    def resume_recording(self) -> bool:
        """Setzt die pausierte Aufnahme fort.
        
        Returns:
            bool: True, wenn erfolgreich fortgesetzt
        """
        if not self.active_session_id:
            logger.warning("Keine aktive Aufnahme")
            return False
        
        session = self.get_session(self.active_session_id)
        if not session:
            logger.error(f"Aktive Sitzung {self.active_session_id} nicht gefunden")
            return False
        
        if session.status != RecordingStatus.PAUSED:
            logger.warning(f"Sitzung {self.active_session_id} ist nicht pausiert")
            return False
        
        session.resume()
        self._trigger_callbacks('on_resume', session=session)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Lu00f6scht eine Aufnahmesitzung.
        
        Args:
            session_id: ID der Sitzung
            
        Returns:
            bool: True, wenn erfolgreich gelu00f6scht
        """
        if session_id == self.active_session_id:
            self.stop_recording()
        
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Dateien lu00f6schen
        for file_path in session.file_paths.values():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Fehler beim Lu00f6schen der Datei {file_path}: {e}")
        
        # Sitzung entfernen
        del self.sessions[session_id]
        return True
