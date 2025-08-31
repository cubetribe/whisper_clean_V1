# Whisper Transkriptionstool - Kurzanleitung für Apple M4

Diese Anleitung hilft dir, das Whisper Transkriptionstool auf deinem Apple M4 Mac zu installieren und zu verwenden. Das Tool ermöglicht die Transkription von Audio- und Videodateien mit Hilfe von Whisper.cpp, optimiert für Apple Silicon.

## Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)
2. [Installation](#installation)
3. [Erste Schritte](#erste-schritte)
4. [Funktionen](#funktionen)
5. [Fehlerbehebung](#fehlerbehebung)

## Voraussetzungen

- Ein Mac mit Apple Silicon (M1, M2, M3 oder M4 Chip)
- macOS Ventura (13) oder neuer
- Mindestens 8 GB RAM (16 GB empfohlen)
- Mindestens 10 GB freier Speicherplatz
- Internetverbindung für die Installation

## Installation

### Schritt 1: Homebrew installieren

Öffne das Terminal (du findest es unter Programme > Dienstprogramme > Terminal) und führe folgenden Befehl aus:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Folge den Anweisungen auf dem Bildschirm. Nach der Installation musst du möglicherweise dein Terminal neu starten.

### Schritt 2: Python installieren

Installiere Python mit Homebrew:

```bash
brew install python@3.11
```

### Schritt 3: FFmpeg installieren

FFmpeg wird für die Verarbeitung von Videodateien benötigt:

```bash
brew install ffmpeg
```

### Schritt 4: Whisper Transkriptionstool herunterladen

1. Lade die ZIP-Datei von der Projektwebsite herunter
2. Entpacke die ZIP-Datei in deinem Benutzerordner
3. Öffne das Terminal und navigiere zum entpackten Ordner:

```bash
cd ~/whisper_transcription_tool
```

### Schritt 5: Virtuelle Umgebung erstellen und Abhängigkeiten installieren

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Schritt 6: Whisper.cpp kompilieren

```bash
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make clean
WHISPER_COREML=1 make -j
```

Die Option `WHISPER_COREML=1` aktiviert die Metal-Beschleunigung für Apple Silicon.

## Erste Schritte

### Starten des Tools

1. Öffne das Terminal
2. Navigiere zum Projektordner:

```bash
cd ~/whisper_transcription_tool
```

3. Aktiviere die virtuelle Umgebung:

```bash
source venv/bin/activate
```

4. Starte das Tool:

```bash
python -m src.whisper_transcription_tool.main
```

5. Öffne deinen Webbrowser und gehe zu: http://localhost:8000

### Modell herunterladen

Beim ersten Start musst du ein Whisper-Modell herunterladen:

1. Klicke auf der Startseite auf "Modelle verwalten"
2. Wähle "large-v3-turbo" aus der Liste
3. Klicke auf "Herunterladen"
4. Warte, bis der Download abgeschlossen ist (ca. 3-4 GB)

## Funktionen

### Audio transkribieren

1. Klicke auf "Transkription" im Hauptmenü
2. Klicke auf "Datei auswählen" und wähle eine Audiodatei aus
3. Wähle das Modell "large-v3-turbo" aus dem Dropdown-Menü
4. Klicke auf "Transkribieren"
5. Nach Abschluss kannst du die Transkription herunterladen

### Video transkribieren

1. Klicke auf "Video extrahieren" im Hauptmenü
2. Klicke auf "Datei auswählen" und wähle eine Videodatei aus
3. Klicke auf "Audio extrahieren und transkribieren"
4. Warte, bis die Extraktion und Transkription abgeschlossen sind
5. Nach Abschluss kannst du die Transkription herunterladen

### Telefonaufnahmen verarbeiten

1. Klicke auf "Telefonaufnahmen" im Hauptmenü
2. Lade die beiden Audiospuren hoch (Anrufer und Empfänger)
3. Klicke auf "Verarbeiten"
4. Nach Abschluss erhältst du eine kombinierte Transkription

### Chatbot verwenden

1. Klicke auf "Chatbot" im Hauptmenü
2. Wähle eine vorhandene Transkription aus
3. Stelle Fragen zum Inhalt der Transkription
4. Der Chatbot analysiert die Transkription und beantwortet deine Fragen

## Fehlerbehebung

### Modell wird nicht geladen

Wenn das Modell nicht geladen werden kann:

1. Überprüfe, ob genügend Speicherplatz vorhanden ist
2. Stelle sicher, dass du die virtuelle Umgebung aktiviert hast
3. Versuche, das Modell manuell herunterzuladen:

```bash
cd ~/whisper_models
curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin -o ggml-large-v3-turbo.bin
```

### Transkription funktioniert nicht

Wenn die Transkription nicht funktioniert:

1. Überprüfe, ob FFmpeg installiert ist:

```bash
which ffmpeg
```

2. Stelle sicher, dass die Audiodatei in einem unterstützten Format vorliegt (WAV, MP3, M4A)
3. Versuche, eine kürzere Audiodatei zu transkribieren

### Programm startet nicht

Wenn das Programm nicht startet:

1. Überprüfe, ob alle Abhängigkeiten installiert sind:

```bash
pip install -r requirements.txt
```

2. Stelle sicher, dass Python 3.11 oder neuer verwendet wird:

```bash
python --version
```

3. Überprüfe, ob der Port 8000 bereits verwendet wird:

```bash
lsof -i :8000
```

Falls der Port belegt ist, kannst du einen anderen Port verwenden:

```bash
python -m src.whisper_transcription_tool.main --port 8080
```

### Weitere Hilfe

Wenn du weitere Hilfe benötigst, besuche die Projektwebsite oder erstelle ein Issue auf GitHub.

---

Viel Erfolg mit dem Whisper Transkriptionstool auf deinem Apple M4!
