"""Datenmodelle fu00fcr Telefonaufnahmen.

Enthu00e4lt die Datenklassen fu00fcr Konfiguration und Sitzungsdaten.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import os
import uuid


class RecordingStatus(Enum):
    """Status einer Aufnahme-Sitzung."""
    NOT_STARTED = "not_started"
    RECORDING = "recording"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class RecordingConfig:
    """Konfiguration fu00fcr eine Audioaufnahme."""
    input_device_id: str
    output_device_id: str
    sample_rate: int = 44100
    channels: int = 2
    filename_prefix: str = "call"
    output_directory: str = "recordings"
    format: str = "wav"  # wav, flac, mp3
    bit_depth: int = 24
    # Maximale Gru00f6u00dfe in MB, 0 = unbegrenzt
    max_file_size_mb: int = 0
    # Maximale Lu00e4nge in Sekunden, 0 = unbegrenzt
    max_duration_sec: int = 0
    
    def __post_init__(self):
        """Validiere und normalisiere die Konfiguration."""
        if self.channels < 1:
            self.channels = 2
        
        if self.sample_rate not in (8000, 16000, 22050, 44100, 48000):
            self.sample_rate = 44100

        if self.format not in ("wav", "flac", "mp3"):
            self.format = "wav"
            
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory, exist_ok=True)


@dataclass
class RecordingSession:
    """Details einer Aufnahme-Sitzung."""
    config: RecordingConfig
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: RecordingStatus = RecordingStatus.NOT_STARTED
    duration_seconds: float = 0.0
    file_paths: Dict[str, str] = field(default_factory=dict)
    notes: str = ""
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def start(self) -> None:
        """Startet die Aufnahmesitzung."""
        self.start_time = datetime.now()
        self.status = RecordingStatus.RECORDING
    
    def pause(self) -> None:
        """Pausiert die Aufnahmesitzung."""
        self.status = RecordingStatus.PAUSED
    
    def resume(self) -> None:
        """Setzt die Aufnahmesitzung fort."""
        self.status = RecordingStatus.RECORDING
    
    def complete(self) -> None:
        """Beendet die Aufnahmesitzung."""
        self.end_time = datetime.now()
        self.status = RecordingStatus.COMPLETED
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def add_file(self, channel_name: str, file_path: str) -> None:
        """Fu00fcgt einen Audiodatei-Pfad hinzu."""
        self.file_paths[channel_name] = file_path
    
    def set_error(self, error_message: str) -> None:
        """Markiert die Sitzung als fehlerhaft."""
        self.status = RecordingStatus.ERROR
        self.metadata["error"] = error_message
    
    def to_dict(self) -> Dict:
        """Konvertiert die Sitzung in ein Dictionary."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "file_paths": self.file_paths,
            "notes": self.notes,
            "metadata": self.metadata
        }
