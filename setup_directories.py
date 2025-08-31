#!/usr/bin/env python3

"""
Dieses Skript erstellt alle erforderlichen Verzeichnisse für die Whisper Transkriptions-App.
"""

import os
import sys
from pathlib import Path

def color_text(text, color_code):
    """Gibt Text in einer bestimmten Farbe aus."""
    return f"\033[{color_code}m{text}\033[0m"

def red(text):
    return color_text(text, '91')

def green(text):
    return color_text(text, '92')

def yellow(text):
    return color_text(text, '93')

def blue(text):
    return color_text(text, '94')

def create_directory(path):
    """Erstellt ein Verzeichnis, wenn es nicht existiert."""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"{green('✓')} Verzeichnis erstellt/überprüft: {blue(path)}")
        return True
    except Exception as e:
        print(f"{red('✗')} Fehler beim Erstellen von {path}: {e}")
        return False

def main():
    # Banner anzeigen
    print("\n" + "=" * 60)
    print(yellow("  Whisper Transkriptionstool - Verzeichnisstruktur Setup"))
    print("=" * 60 + "\n")
    
    # Aktuelles Verzeichnis (Projektverzeichnis)
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Projektverzeichnis: {blue(project_dir)}\n")
    
    # Liste der zu erstellenden Verzeichnisse
    directories = [
        os.path.join(project_dir, "models"),
        os.path.join(project_dir, "recordings"),
        os.path.join(project_dir, "transcriptions"),
        os.path.join(project_dir, "transcriptions", "temp"),
        os.path.join(project_dir, "deps"),
    ]
    
    # Erstelle alle Verzeichnisse
    all_created = True
    for directory in directories:
        if not create_directory(directory):
            all_created = False
    
    # Abschlussmeldung
    print("\n" + "-" * 60)
    if all_created:
        print(green("Alle erforderlichen Verzeichnisse wurden erfolgreich erstellt!"))
    else:
        print(yellow("Es sind Fehler aufgetreten. Bitte überprüfen Sie die Fehlermeldungen oben."))
    print("-" * 60 + "\n")
    
    # Hinweise für den nächsten Schritt
    print(f"Starten Sie die App jetzt mit:\n{yellow('./QuickLauncher.command')}")
    print("\n")

if __name__ == "__main__":
    main()
