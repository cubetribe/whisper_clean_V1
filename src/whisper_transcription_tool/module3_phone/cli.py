"""Kommandozeilen-Interface für Audioaufnahme.

Dieses Modul stellt eine einfache CLI zum Testen der Audioaufnahme bereit.
"""

import argparse
import time
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

from .recorder import AudioRecorder, DeviceManager
from .models import RecordingConfig, RecordingSession

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def list_devices_cmd():
    """Listet alle verfügbaren Audiogeräte auf."""
    devices = DeviceManager.list_devices()
    
    print("\nVerfügbare Audiogeräte:")
    print("-" * 80)
    print(f"{'ID':^4} | {'Ein':^5} | {'Aus':^5} | {'Name':<40} | {'Sample Rate':>10}")
    print("-" * 80)
    
    for device in devices:
        print(f"{device['id']:4d} | {device['channels_in']:^5d} | {device['channels_out']:^5d} | "
              f"{device['name']:<40} | {device['default_samplerate']:10.0f}")
    
    print("\nStandardgeräte:")
    default_in = DeviceManager.get_default_input_device()
    default_out = DeviceManager.get_default_output_device()
    
    if default_in:
        print(f"Standard-Eingabe: {default_in.get('id', 'N/A')} - {default_in.get('name', 'N/A')}")
    else:
        print("Kein Standard-Eingabegerät gefunden.")
        
    if default_out:
        print(f"Standard-Ausgabe: {default_out.get('id', 'N/A')} - {default_out.get('name', 'N/A')}")
    else:
        print("Kein Standard-Ausgabegerät gefunden.")
    
    blackhole = DeviceManager.find_blackhole_device()
    if blackhole:
        print(f"\nBlackHole gefunden: {blackhole['id']} - {blackhole['name']}")
    else:
        print("\nKein BlackHole-Gerät gefunden. Bitte installieren Sie BlackHole:")
        print("brew install --cask blackhole-2ch")


def check_setup_cmd():
    """Überprüft die Aufnahme-Konfiguration."""
    setup = DeviceManager.recommend_setup()
    
    if setup['status'] == 'error':
        print(f"Fehler: {setup['message']}")
        print(f"Installation: {setup.get('installation_guide', '')}")
        return 1
    
    recommended = setup['recommended_setup']
    print("\nEmpfohlene Konfiguration:")
    print(f"Eingabegerät: {recommended['input_device']['id']} - {recommended['input_device']['name']}")
    print(f"Ausgabegerät: {recommended['output_device']['id']} - {recommended['output_device']['name']}")
    print(f"Sample Rate: {recommended['sample_rate']}")
    return 0


def record_cmd(args):
    """Führt eine Audioaufnahme durch."""
    # BlackHole prüfen
    blackhole = DeviceManager.find_blackhole_device()
    if not blackhole:
        print("Kein BlackHole-Gerät gefunden. Bitte installieren Sie BlackHole:")
        print("brew install --cask blackhole-2ch")
        return 1
    
    # Wenn keine Geräte-IDs angegeben wurden, Empfehlungen verwenden
    setup = DeviceManager.recommend_setup()
    if setup['status'] == 'error':
        print(f"Fehler: {setup['message']}")
        return 1
    
    recommended = setup['recommended_setup']
    input_device_id = args.input or recommended['input_device']['id']
    output_device_id = args.output or recommended['output_device']['id']
    sample_rate = args.rate or recommended['sample_rate']
    
    # Ausgabeverzeichnis
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Aufnahme-Konfiguration
    config = RecordingConfig(
        input_device_id=str(input_device_id),
        output_device_id=str(output_device_id),
        sample_rate=int(sample_rate),
        channels=2,
        filename_prefix=args.prefix,
        output_directory=str(output_dir),
        format="wav",
        max_duration_sec=args.duration
    )
    
    recorder = AudioRecorder()
    
    # Callbacks registrieren
    def on_start(session):
        print(f"\nAufnahme gestartet. Session ID: {session.session_id}")
        print(f"Drücken Sie Strg+C, um die Aufnahme zu beenden...")
    
    def on_pause(session):
        print("Aufnahme pausiert.")
    
    def on_resume(session):
        print("Aufnahme fortgesetzt.")
    
    def on_stop(session):
        print("\nAufnahme beendet.")
        print("Aufgenommene Dateien:")
        for channel, path in session.file_paths.items():
            print(f"  - {channel}: {path}")
        
        # Dauer berechnen
        duration = session.duration_seconds
        minutes, seconds = divmod(duration, 60)
        print(f"Dauer: {int(minutes)}:{seconds:05.2f}")
    
    def on_error(session, error):
        print(f"\nFehler: {error}")
    
    def on_progress(session, duration, status):
        if duration % 1 < 0.1:  # Nur alle ~1 Sekunde aktualisieren
            minutes, seconds = divmod(duration, 60)
            sys.stdout.write(f"\rAufnahme läuft: {int(minutes)}:{int(seconds):02d} - Status: {status}")
            sys.stdout.flush()
    
    recorder.register_callback('on_start', on_start)
    recorder.register_callback('on_pause', on_pause)
    recorder.register_callback('on_resume', on_resume)
    recorder.register_callback('on_stop', on_stop)
    recorder.register_callback('on_error', on_error)
    recorder.register_callback('on_progress', on_progress)
    
    # Sitzung erstellen und Aufnahme starten
    session = recorder.create_session(config)
    recorder.start_recording(session.session_id)
    
    try:
        # Auf Benutzerinteraktion warten
        while recorder.active_session_id:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nBenutzerabbruch...")
        recorder.stop_recording()
    
    return 0


def main():
    """Haupteinstiegspunkt für die CLI."""
    parser = argparse.ArgumentParser(description='Audiomanager für getrennte Aufnahme')
    subparsers = parser.add_subparsers(dest='command', help='Befehle')
    
    # Geräteliste
    list_parser = subparsers.add_parser('devices', help='Audiogeräte auflisten')
    
    # Setup-Check
    check_parser = subparsers.add_parser('check', help='Aufnahmekonfiguration prüfen')
    
    # Aufnahme
    record_parser = subparsers.add_parser('record', help='Aufnahme starten')
    record_parser.add_argument('--input', '-i', type=int, help='ID des Eingabegeräts')
    record_parser.add_argument('--output', '-o', type=int, help='ID des Ausgabegeräts')
    record_parser.add_argument('--rate', '-r', type=int, help='Sample-Rate')
    record_parser.add_argument('--duration', '-d', type=int, default=0, 
                              help='Maximale Aufnahmedauer in Sekunden (0=unbegrenzt)')
    record_parser.add_argument('--output-dir', default='recordings', 
                              help='Ausgabeverzeichnis')
    record_parser.add_argument('--prefix', default='call', 
                              help='Dateiname-Präfix')
    
    args = parser.parse_args()
    
    if args.command == 'devices':
        return list_devices_cmd()
    elif args.command == 'check':
        return check_setup_cmd()
    elif args.command == 'record':
        return record_cmd(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
