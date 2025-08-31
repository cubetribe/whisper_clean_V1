# Installation des Whisper Transcription Tools

## Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)
2. [Installation auf macOS/Linux](#installation-auf-macoslinux)
3. [Installation auf Windows](#installation-auf-windows)
4. [Manuelle Installation](#manuelle-installation)
5. [Konfiguration](#konfiguration)
6. [Fehlerbehebung](#fehlerbehebung)

## Voraussetzungen

Fu00fcr die Installation des Whisper Transcription Tools benu00f6tigen Sie:

- Python 3.11 oder hu00f6her
- Whisper.cpp (wird automatisch installiert oder kann manuell installiert werden)
- Fu00fcr Windows: Ein C++-Compiler (z.B. Visual Studio mit Desktop Development with C++)

## Installation auf macOS/Linux

1. u00d6ffnen Sie ein Terminal-Fenster
2. Navigieren Sie zum Projektverzeichnis:
   ```bash
   cd /pfad/zum/whisper_clean
   ```
3. Fu00fchren Sie das Installationsskript aus:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
4. Folgen Sie den Anweisungen auf dem Bildschirm

Das Skript wird automatisch:
- Python-Version u00fcberpru00fcfen
- Whisper.cpp erkennen oder installieren (wenn gewu00fcnscht)
- Eine virtuelle Umgebung erstellen
- Alle Abhu00e4ngigkeiten installieren
- Eine Konfigurationsdatei erstellen

## Installation auf Windows

1. u00d6ffnen Sie eine Kommandozeile (cmd.exe) oder PowerShell
2. Navigieren Sie zum Projektverzeichnis:
   ```cmd
   cd C:\pfad\zum\whisper_clean
   ```
3. Fu00fchren Sie das Installationsskript aus:
   ```cmd
   install.bat
   ```
4. Folgen Sie den Anweisungen auf dem Bildschirm

**Hinweis:** Auf Windows muss Whisper.cpp manuell installiert werden, bevor Sie das Skript ausfu00fchren. Das Skript wird Sie durch den Prozess fu00fchren.

## Manuelle Installation

Wenn Sie das Tool manuell installieren mu00f6chten:

1. Virtuelle Umgebung erstellen:
   ```bash
   python -m venv venv
   ```

2. Virtuelle Umgebung aktivieren:
   - Unter Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - Unter Windows:
     ```cmd
     venv\Scripts\activate.bat
     ```

3. Abhu00e4ngigkeiten installieren:
   ```bash
   pip install -e .
   ```

4. Whisper.cpp installieren:
   - Folgen Sie der Anleitung unter: https://github.com/ggerganov/whisper.cpp

5. Konfigurationsdatei erstellen:
   ```bash
   mkdir -p ~/.whisper_transcription_tool
   ```
   Erstellen Sie `~/.whisper_transcription_tool/config.yaml` mit folgendem Inhalt:
   ```yaml
   whisper:
     binary_path: "/pfad/zu/whisper"
     model_path: "~/whisper_models"
     threads: 4
   
   output:
     default_directory: "~/transcriptions"
     temp_directory: "/tmp/whisper_transcription_tool"
   
   logging:
     level: "INFO"
     file: "~/.whisper_transcription_tool/whisper_tool.log"
   ```

## Konfiguration

Die Konfigurationsdatei befindet sich unter:
- Linux/macOS: `~/.whisper_transcription_tool/config.yaml`
- Windows: `%USERPROFILE%\.whisper_transcription_tool\config.yaml`

Wichtige Einstellungen:

- `whisper.binary_path`: Pfad zum Whisper.cpp-Binary
- `whisper.model_path`: Pfad zum Whisper-Modellverzeichnis
- `output.default_directory`: Standardverzeichnis fu00fcr generierte Transkriptionen

## Fehlerbehebung

### Whisper.cpp wird nicht gefunden

Stellen Sie sicher, dass das Whisper.cpp-Binary im PATH ist oder geben Sie den vollstu00e4ndigen Pfad in der Konfigurationsdatei an.

### Python-Version nicht unterstu00fctzt

Installieren Sie Python 3.11 oder hu00f6her und stellen Sie sicher, dass es als `python3` (Linux/macOS) oder `python` (Windows) verfu00fcgbar ist.

### Keine Audiodateien werden verarbeitet

u00dcberpru00fcfen Sie, ob Whisper.cpp korrekt installiert ist und ob die Modell-Datei heruntergeladen wurde.
