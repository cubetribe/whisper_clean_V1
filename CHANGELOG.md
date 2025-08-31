# Changelog

## Version 0.9.5 (2025-08-31)

### 🎯 Major Updates
- **Neues Repository**: Sauberes Repository ohne Git-History erstellt
  - GitHub: https://github.com/cubetribe/Whisper-Transcription-Tool
  - Keine persönlichen Pfade mehr in der History
  - Professionelle Präsentation für öffentliche Nutzung

### 📄 Lizenz & Dokumentation
- **Neue Lizenz**: "Free to Use" statt MIT
  - Copyright © 2025 Dennis Westermann - aiEX Academy
  - Website: www.goaiex.com
  - Kostenlos für persönliche und kommerzielle Nutzung
  - Attribution erforderlich

- **Umfassend erweitertes README**:
  - Detaillierte Erklärung der App-Funktionalität
  - Anwendungsfälle für verschiedene Nutzergruppen
  - Technische Architektur und Performance-Details
  - Professionelles Branding mit aiEX Academy

### 🔒 Sicherheit & Datenschutz
- **Persönliche Daten entfernt**:
  - Alle Pfade anonymisiert (/Users/denniswestermann → /path/to/project)
  - E-Mail-Adressen entfernt
  - Scripts verwenden relative Pfade (funktionieren weiterhin)

## Version 0.9.4.2 (2025-08-31)

### ❌ FEHLGESCHLAGENER VERSUCH - Terminal Output Display
- **Was versucht wurde**: Terminal-Output im Frontend anzeigen
- **Problem**: WebSocket-Buffering verhindert Echtzeit-Anzeige
- **Status**: Funktioniert nicht - alle Nachrichten kommen erst nach Abschluss
- **Dokumentiert in**: GitHub Issue #1

## Version 0.9.4.1 (2025-08-31)

### ✅ Features
- **Terminal Debug Output**: Detaillierte Fortschrittsanzeige in der Konsole
- **Verbesserte Scripts**: 
  - WhisperTool.command als Hauptlauncher
  - Aufgeräumte scripts/ Struktur
  - Alte Versionen archiviert

### 🐛 Bugfixes
- Start-Script Pfade korrigiert
- DYLD_LIBRARY_PATH richtig gesetzt

## Version 0.9.4 (2025-08-31)

### 📝 Dokumentation
- **GitHub Issue #1**: WebSocket-Problem ausführlich dokumentiert
  - Async/Sync Context-Konflikt identifiziert
  - Subprocess hat keinen asyncio Event-Loop
  - Events werden gepuffert statt in Echtzeit gesendet

### 🔧 Debug Features
- Terminal-Ausgabe mit print() statements
- [WHISPER PROGRESS] und [PROGRESS UPDATE] Nachrichten
- Funktioniert zumindest in der Server-Konsole

## Version 0.9.3 (2025-08-31)

### ✅ Neue Features
- **Cleanup-Manager**: Automatische Bereinigung des Temp-Verzeichnisses nach erfolgreicher Transkription
  - Löscht Audio-Chunks nach Verarbeitung
  - Konfigurierbare Aufbewahrungsrichtlinien
  - Reduziert Speicherplatzverbrauch erheblich (von 9.3 GB auf 0.0001 GB in Tests)

### 🐛 Bugfixes
- **TranscriptionResult metadata Fehler behoben**: Entfernte das nicht unterstützte `metadata` Argument
- **Doppelte WebSocket-Endpoints entfernt**: Konflikt zwischen zwei `/ws/progress` Routen behoben
- **EventType.STATUS_UPDATE ersetzt**: Durch PROGRESS_UPDATE ersetzt, da STATUS_UPDATE nicht definiert war

### 🔧 Technische Verbesserungen
- Zurück zur bewährten async Event-Handler Implementierung (v0.9.2)
- Entfernung der überkomplexen Queue-Bridge-Systeme
- Bereinigung des Event-Systems

### ⚠️ Bekannte Probleme

#### WebSocket Progress Updates
**Problem**: Fortschrittsbalken und Statusanzeigen werden möglicherweise nicht korrekt angezeigt.

**Ursache**: 
- Async/Sync Konflikt zwischen Subprocess-Events und WebSocket-Kommunikation
- Events aus dem Whisper-Subprocess (sync) müssen an WebSocket-Clients (async) gesendet werden

**Lösungsansatz**:
```python
# Funktionierender Ansatz (v0.9.2):
async def progress_event_handler(event: Event):  # ASYNC Handler
    await websocket.send_json(event.data)
    
# Problematischer Ansatz (vermeiden):
def sync_progress_handler(event: Event):  # SYNC Handler
    thread_safe_queue.put(event_dict)  # Führt zu Thread-Boundary-Problemen
```

#### Cancel-Funktion
**Problem**: Die Abbruch-Funktion reagiert möglicherweise nicht sofort.

**Ursache**: 
- Der Whisper-Prozess läuft als Subprocess
- Signale werden nicht immer korrekt weitergeleitet

**Temporäre Lösung**: Server-Neustart bei hängenden Prozessen

### 📝 Lessons Learned

1. **Async/Await Konsistenz**: Bei WebSockets immer im async Context bleiben
2. **Event-System Einfachheit**: Direkte async Handler sind robuster als komplexe Queue-Bridges
3. **FastAPI Route-Konflikte**: Doppelte WebSocket-Endpoints führen zu unvorhersehbarem Verhalten
4. **Type Safety**: Sicherstellen, dass alle Event-Types in der Enum definiert sind

## Version 0.9.2 (2025-08-30)
- Audio Chunking für große Dateien implementiert
- Automatische Aufteilung von Dateien >20 Minuten
- 20-Minuten-Segmente mit 10 Sekunden Überlappung

## Version 0.9.1 (2025-08-30)
- Initial release mit grundlegenden Features
- Web-Interface mit Drag & Drop
- Whisper.cpp Integration
- FFmpeg Video-Extraktion