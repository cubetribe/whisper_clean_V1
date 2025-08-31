# Whisper Transcription Tool - Scripts

## 🚀 Schnellstart

### Hauptlauncher
**`WhisperTool.command`** - Doppelklicken Sie diese Datei, um das Tool zu starten!

## 📁 Dateiübersicht

### Aktive Scripts
- **`WhisperTool.command`** - Hauptlauncher für macOS (doppelklickbar)
- **`start_server.sh`** - Server-Startscript mit allen Optionen
- **`install.sh`** - Installationsscript für Abhängigkeiten
- **`create_backup.sh`** - Backup-Erstellung
- **`restore_backup.sh`** - Backup-Wiederherstellung

### Python-Hilfsskripte
- **`clean_temp.py`** - Bereinigung temporärer Dateien
- **`setup_directories.py`** - Verzeichnisstruktur einrichten
- **`dynamic_path_finder.py`** - Dynamische Pfadfindung

### Archivierte Dateien (old_versions/)
Alte Launcher-Versionen wurden archiviert und befinden sich im `old_versions` Ordner.

## 💡 Verwendung

### macOS (empfohlen)
1. Öffnen Sie den Finder
2. Navigieren Sie zu diesem Ordner
3. Doppelklicken Sie auf **`WhisperTool.command`**
4. Der Browser öffnet sich automatisch mit der Weboberfläche

### Terminal
```bash
cd "/Users/denniswestermann/Desktop/Coding Projekte/whisper_clean/scripts"
./start_server.sh
```

## ⚙️ Optionen

Das `start_server.sh` Script bietet:
- Automatische Port-Verwaltung
- Debug-Modus Option
- Server-Verwaltung
- Abhängigkeitsprüfung

## 🛠️ Fehlerbehebung

Falls die .command Datei nicht startet:
1. Rechtsklick → "Öffnen mit" → "Terminal"
2. Oder im Terminal: `chmod +x WhisperTool.command`

## 📝 Version
Aktuelle Version: 0.9.4