#!/usr/bin/env python3

"""
Dieses Skript bereinigt temporu00e4re Dateien des Whisper Transkriptionstools.
Es u00fcberpru00fcft den temp-Ordner und entfernt Mediendateien, behu00e4lt aber wichtige Konfigurations- und Ausgabedateien.
"""

import os
import sys
import shutil
from pathlib import Path
import datetime
import argparse

# Farbdefinitionen fu00fcr visuelle Hinweise
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
NC = '\033[0m' # No Color

def get_dir_size(path):
    """Ermittelt die Gru00f6u00dfe eines Verzeichnisses in Bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def human_readable_size(size_bytes):
    """Wandelt Bytes in menschenlesbare Gru00f6u00dfenangabe um."""
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names)-1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"

def file_age_days(filepath):
    """Ermittelt das Alter einer Datei in Tagen."""
    modified_time = os.path.getmtime(filepath)
    current_time = datetime.datetime.now().timestamp()
    age_seconds = current_time - modified_time
    return age_seconds / (60 * 60 * 24)  # Umrechnung in Tage

def clean_temp_dir(temp_dir, max_age_days=None, force=False):
    """Bereinigt das temp-Verzeichnis von alten Mediendateien."""
    if not os.path.exists(temp_dir):
        print(f"{RED}Fehler: Das Verzeichnis {temp_dir} existiert nicht.{NC}")
        return False
        
    # Speicherplatz vor der Bereinigung ermitteln
    initial_size = get_dir_size(temp_dir)
    print(f"{BLUE}Belegter Speicherplatz: {human_readable_size(initial_size)}{NC}")
    
    # Zu lu00f6schende Dateiendungen (Medien und extrahierte Audiodateien)
    media_extensions = ['.mp4', '.wav', '.mp3', '.avi', '.mov', '.mkv', '.flac', '.ogg', '.webm']
    
    # Dateien im temp-Verzeichnis durchsuchen
    files_to_delete = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Pru00fcfe, ob es sich um eine Mediendatei handelt
            if file_ext in media_extensions:
                # Wenn ein Altersfilter gesetzt ist, nur alte Dateien lu00f6schen
                if max_age_days is None or file_age_days(file_path) >= max_age_days:
                    files_to_delete.append(file_path)
    
    if not files_to_delete:
        print(f"{GREEN}Keine zu bereinigenden Dateien gefunden.{NC}")
        return True
    
    # Gesamtgru00f6u00dfe der zu lu00f6schenden Dateien berechnen
    delete_size = sum(os.path.getsize(f) for f in files_to_delete)
    
    # Liste der Dateien anzeigen
    print(f"{YELLOW}Folgende Mediendateien werden gelu00f6scht ({human_readable_size(delete_size)}){NC}:")
    for i, file_path in enumerate(files_to_delete, 1):
        age = file_age_days(file_path)
        size = human_readable_size(os.path.getsize(file_path))
        print(f"{i}. {os.path.basename(file_path)} - {size} - {age:.1f} Tage alt")
    
    # Bestu00e4tigung einholen, sofern nicht erzwungen
    if not force:
        confirm = input(f"\n{YELLOW}Mu00f6chten Sie diese Dateien lu00f6schen? (j/n): {NC}").lower()
        if confirm != 'j' and confirm != 'y':
            print(f"{BLUE}Bereinigung abgebrochen.{NC}")
            return False
    
    # Dateien lu00f6schen
    deleted_count = 0
    try:
        for file_path in files_to_delete:
            os.remove(file_path)
            deleted_count += 1
            
        # Speicherplatz nach der Bereinigung ermitteln
        final_size = get_dir_size(temp_dir)
        saved_space = initial_size - final_size
        
        print(f"{GREEN}\nBereinigung abgeschlossen!{NC}")
        print(f"{GREEN}{deleted_count} Dateien gelu00f6scht.{NC}")
        print(f"{GREEN}Freigegebener Speicherplatz: {human_readable_size(saved_space)}{NC}")
        print(f"{GREEN}Neuer belegter Speicherplatz: {human_readable_size(final_size)}{NC}")
        return True
    except Exception as e:
        print(f"{RED}Fehler beim Lu00f6schen der Dateien: {e}{NC}")
        return False

def main():
    # Kommandozeilenargumente definieren
    parser = argparse.ArgumentParser(description="Bereinigt temporu00e4re Mediendateien des Whisper Transkriptionstools.")
    parser.add_argument("--age", type=int, default=None, help="Nur Dateien lu00f6schen, die u00e4lter als X Tage sind")
    parser.add_argument("--force", "-f", action="store_true", help="Lu00f6schen ohne Bestu00e4tigung erzwingen")
    args = parser.parse_args()
    
    # Banner anzeigen
    print(f"\n{BLUE}========================================================={NC}")
    print(f"{BLUE}        Whisper Transkriptionstool - Temp Cleanup{NC}")
    print(f"{BLUE}========================================================={NC}\n")
    
    # Projektverzeichnis ermitteln
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(current_dir, "transcriptions", "temp")
    
    print(f"{YELLOW}Temp-Verzeichnis: {temp_dir}{NC}")
    
    if args.age:
        print(f"{YELLOW}Bereinige Dateien u00e4lter als {args.age} Tage{NC}")
    else:
        print(f"{YELLOW}Bereinige alle Mediendateien{NC}")
    
    # Temp-Verzeichnis bereinigen
    clean_temp_dir(temp_dir, max_age_days=args.age, force=args.force)

if __name__ == "__main__":
    main()
