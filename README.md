# Whisper Transcription Tool v0.9.2

Ein modulares Python-Tool zur Transkription und Auswertung von Audio- und Videodaten mit Whisper.cpp, vollständig portabel und plattformunabhängig mit automatischer Audioextraktion.

## 🚀 Schnellstart

### Direkte Ausführung (empfohlen)
```bash
cd "/Users/denniswestermann/Desktop/Coding Projekte/whisper_clean"
source venv_new/bin/activate
python -m src.whisper_transcription_tool.main web --port 8090
```

### Mit Startskript
```bash
cd "/Users/denniswestermann/Desktop/Coding Projekte/whisper_clean"
./scripts/start_server.sh
```

### Mit Launcher (GUI)
Doppelklick auf: `scripts/QuickLauncher.command`

Dann öffnen: http://localhost:8090

## 📁 Projektstruktur

```
whisper_clean/
├── src/                          # Hauptquellcode
│   └── whisper_transcription_tool/
├── scripts/                      # Alle Skripte und Launcher
├── documentation/                # Vollständige Dokumentation
├── requirements.txt              # Python-Abhängigkeiten
├── setup.py                     # Python-Paket-Setup
└── README.md                    # Diese Datei
```

## 🔧 Installation

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. Entwicklungsmodus installieren
pip install -e ".[web]"

# 3. Whisper-Binary ausführbar machen
chmod +x deps/whisper.cpp/build/bin/whisper-cli
```

## 📖 Dokumentation

Vollständige Dokumentation in `documentation/`:
- `README.md` - Detaillierte Anleitung
- `CLAUDE.md` - Claude Code Spezifikationen
- `INSTALLATION.md` - Setup-Anleitung
- `DEPLOYMENT_STATUS.md` - Aktueller Status

## 🎯 Features

- ✅ **Lokale Transkription** mit Whisper.cpp (Apple Silicon optimiert)
- ✅ **Video-Extraktion** mit FFmpeg
- ✅ **Web-Interface** mit Echtzeit-Updates
- ✅ **Modulare Architektur** mit 4 Hauptmodulen
- ✅ **Batch-Verarbeitung** für mehrere Dateien
- ✅ **Mehrere Ausgabeformate** (TXT, SRT, VTT)

## 📞 Support

- GitHub Issues: [whisper_clean_V1](https://github.com/cubetribe/whisper_clean_V1)
- Dokumentation: `documentation/` Verzeichnis

---

**Version:** 0.9.2 | **Status:** Production Ready ✅