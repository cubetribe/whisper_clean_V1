"""Modul 3: Telefonanruf-Aufnahme und Verarbeitung

Dieses Modul stellt Funktionen zur Aufnahme von Telefonaten mit getrennten
Audiokanälen für Mikrofon und Systemton bereit.

Erfordert BlackHole als virtuelle Audioschnittstelle.
"""

from .recorder import AudioRecorder, DeviceManager
from .models import RecordingSession, RecordingConfig

__all__ = ['AudioRecorder', 'DeviceManager', 'RecordingSession', 'RecordingConfig']
