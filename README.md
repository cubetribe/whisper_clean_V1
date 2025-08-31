# Whisper Transcription Tool v0.9.3

Ein modulares Python-Tool zur Transkription und Auswertung von Audio- und Videodaten mit Whisper.cpp, vollständig portabel und plattformunabhängig mit automatischer Audioextraktion.

## 🎯 Neue Features in v0.9.3
- **Automatische Cleanup-Funktion**: Temp-Verzeichnis wird nach erfolgreicher Transkription automatisch bereinigt
- **Bugfixes**: WebSocket-Konflikte und Event-System-Probleme behoben
- **Verbesserte Stabilität**: Rückkehr zur bewährten async Event-Handler Implementierung

## 🚀 Schnellstart

### Direkte Ausführung (empfohlen)
```bash
# Im Projektverzeichnis:
source venv_new/bin/activate
python -m src.whisper_transcription_tool.main web --port 8090
```

### Mit Startskript
```bash
# Im Projektverzeichnis:
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

## 🔧 Troubleshooting & Bekannte Probleme

### WebSocket Progress Updates
**Problem**: Fortschrittsbalken wird nicht angezeigt  
**Lösung**: Server neu starten, Browser-Cache leeren

### Cancel-Funktion
**Problem**: Abbruch-Button reagiert nicht sofort  
**Temporäre Lösung**: Server-Neustart bei hängenden Prozessen

### Technische Details für Entwickler
Die WebSocket-Implementierung nutzt async Event-Handler. Bei Problemen:
1. Prüfen ob nur ein `/ws/progress` Endpoint existiert
2. Sicherstellen dass `progress_event_handler` async ist
3. Keine sync/async Bridge-Worker verwenden

Details siehe [CHANGELOG.md](CHANGELOG.md)

## 📞 Support

- GitHub Issues: [whisper_clean_V1](https://github.com/cubetribe/whisper_clean_V1)
- Dokumentation: `documentation/` Verzeichnis
- Changelog: [CHANGELOG.md](CHANGELOG.md)

---

**Version:** 0.9.3 | **Status:** Production Ready ✅