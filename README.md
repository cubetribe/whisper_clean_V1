# Whisper Transcription Tool

🎙️ **Ein leistungsstarkes, modulares Tool zur Audio- und Video-Transkription mit Whisper.cpp**

[![Version](https://img.shields.io/badge/version-0.9.4.2-blue.svg)](https://github.com/cubetribe/Whisper-Transcription-Tool)
[![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Free%20to%20Use-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/author-Dennis%20Westermann-orange.svg)](https://www.goaiex.com)

---

## 👨‍💻 Über den Entwickler

**Dennis Westermann** | aiEX Academy | [www.goaiex.com](https://www.goaiex.com)

Copyright © 2025 - Alle Rechte vorbehalten | Free to Use License

---

## 🎯 Was ist das Whisper Transcription Tool?

Das **Whisper Transcription Tool** ist eine professionelle Desktop-Anwendung zur automatischen Transkription von Audio- und Videodateien. Es wurde speziell entwickelt, um die Leistungsfähigkeit von OpenAIs Whisper-Modell lokal auf Ihrem Computer zu nutzen - ohne Cloud, ohne API-Kosten, ohne Datenschutzbedenken.

### 🤔 Warum wurde dieses Tool entwickelt?

In der modernen digitalen Welt fallen täglich unzählige Audio- und Videoinhalte an:
- **Meetings & Konferenzen** - Stundenlange Zoom/Teams-Aufzeichnungen
- **Podcasts & Interviews** - Content-Erstellung und Dokumentation
- **Vorlesungen & Schulungen** - Bildungsinhalte zugänglich machen
- **Videos & Filme** - Untertitel und Barrierefreiheit
- **Sprachnotizen** - Persönliche Aufzeichnungen in Text umwandeln

Die meisten Transkriptionsdienste sind entweder:
- ❌ **Teuer** (Cloud-APIs kosten pro Minute)
- ❌ **Datenschutz-problematisch** (Ihre Daten verlassen Ihren Computer)
- ❌ **Langsam** (Upload, Wartezeit, Download)
- ❌ **Begrenzt** (Dateigröße, Formate, Sprachen)

### ✨ Die Lösung: Lokale KI-Transkription

Dieses Tool löst all diese Probleme durch:
- ✅ **100% lokal** - Ihre Daten bleiben auf Ihrem Computer
- ✅ **Kostenlos** - Keine API-Gebühren oder Abonnements
- ✅ **Schnell** - Optimiert für Apple Silicon (M1/M2/M3)
- ✅ **Unbegrenzt** - Keine Limits bei Dateigröße oder Anzahl
- ✅ **Professionell** - Broadcast-Qualität mit Zeitstempeln

---

## 🚀 Hauptfunktionen

### 1. 🎙️ **Audio-Transkription**
- Unterstützt alle gängigen Formate (MP3, WAV, M4A, FLAC, etc.)
- Batch-Verarbeitung für mehrere Dateien gleichzeitig
- Automatische Spracherkennung (99+ Sprachen)
- Verschiedene Ausgabeformate:
  - **TXT** - Reiner Text für Dokumente
  - **SRT** - Untertitel mit Zeitstempeln
  - **VTT** - Web-Video-Untertitel
  - **JSON** - Strukturierte Daten mit Metadaten

### 2. 🎬 **Video-Verarbeitung**
- Automatische Audio-Extraktion aus Videos
- Unterstützt MP4, MOV, AVI, MKV, WebM
- Direkte Untertitel-Generierung für Videos
- Perfekt für YouTube, Vimeo, Social Media

### 3. 🌐 **Web-Interface**
- Moderne, intuitive Benutzeroberfläche
- Drag & Drop für Dateien
- Echtzeit-Fortschrittsanzeige
- Vorschau und Download der Ergebnisse
- Läuft im Browser (localhost:8090)

### 4. 🎯 **Intelligente Features**
- **Chunk-Processing**: Große Dateien werden automatisch in Segmente aufgeteilt
- **Auto-Cleanup**: Temporäre Dateien werden nach Verarbeitung gelöscht
- **Modell-Management**: Automatischer Download und Verwaltung der KI-Modelle
- **Multi-Threading**: Nutzt alle CPU-Kerne für maximale Geschwindigkeit

### 5. 📱 **Phone Recording Module** (Experimental)
- Dual-Track-Aufnahme (Mikrofon + System-Audio)
- Perfekt für Telefon-Interviews
- Automatische Synchronisation der Tracks

---

## 💡 Anwendungsfälle

### Für **Content Creator** 📹
- YouTube-Videos automatisch untertiteln
- Podcast-Transkripte für SEO erstellen
- Social Media Clips barrierefrei machen

### Für **Journalisten** 📰
- Interviews schnell verschriftlichen
- Recherche-Material durchsuchbar machen
- Zitate exakt dokumentieren

### Für **Studenten & Forscher** 🎓
- Vorlesungen in durchsuchbare Notizen verwandeln
- Forschungsinterviews transkribieren
- Fremdsprachige Inhalte übersetzen

### Für **Unternehmen** 💼
- Meeting-Protokolle automatisch erstellen
- Kundengespräche dokumentieren
- Schulungsvideos untertiteln

### Für **Barrierefreiheit** ♿
- Videos für Gehörlose zugänglich machen
- Untertitel in mehreren Sprachen
- Screenreader-kompatible Texte

---

## 🛠️ Technische Details

### Architektur
- **Backend**: Python 3.8+ mit FastAPI
- **Frontend**: HTML5, JavaScript, WebSockets
- **KI-Engine**: Whisper.cpp (C++ Implementation)
- **Audio-Processing**: FFmpeg
- **Optimierung**: Apple Silicon Native (Metal)

### Modelle
- **Tiny** (39 MB) - Schnell, für Entwürfe
- **Base** (74 MB) - Gute Balance
- **Small** (244 MB) - Hohe Qualität
- **Medium** (769 MB) - Professionell
- **Large** (1550 MB) - Broadcast-Qualität
- **Large-v3-turbo** - Neuestes Modell, beste Ergebnisse

### Performance
- **Geschwindigkeit**: Bis zu 10x Echtzeit auf M1/M2
- **Speicher**: 2-8 GB RAM je nach Modell
- **Genauigkeit**: 95-99% je nach Audioqualität

---

## 📦 Installation

### Voraussetzungen
- macOS (optimiert für Apple Silicon M1/M2/M3)
- Python 3.8 oder höher
- 4 GB freier Speicherplatz
- FFmpeg (wird automatisch installiert)

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/cubetribe/Whisper-Transcription-Tool.git
cd Whisper-Transcription-Tool

# Abhängigkeiten installieren
pip install -r requirements.txt

# Web-Server starten
./scripts/start_server.sh
```

Öffnen Sie dann http://localhost:8090 in Ihrem Browser.

### Erste Schritte
1. Wählen Sie ein Whisper-Modell (empfohlen: large-v3-turbo)
2. Laden Sie eine Audio- oder Videodatei hoch
3. Wählen Sie das Ausgabeformat
4. Klicken Sie auf "Transkribieren"
5. Laden Sie das Ergebnis herunter

---

## 📖 Dokumentation

Ausführliche Dokumentation finden Sie im `documentation/` Verzeichnis:
- [Vollständige Anleitung](documentation/README.md)
- [Installation & Setup](documentation/INSTALL.md)
- [Kurzanleitung](documentation/KURZANLEITUNG.md)

---

## 🤝 Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Pull Request oder öffnen Sie ein Issue.

### Entwicklung
```bash
# Entwicklungsmodus
pip install -e ".[dev]"

# Tests ausführen
pytest

# Code formatieren
black src/
```

---

## 📄 Lizenz

**Copyright © 2025 Dennis Westermann - aiEX Academy**

Dieses Tool ist **Free to Use** - kostenlos für persönliche und kommerzielle Nutzung.
Details siehe [LICENSE](LICENSE) Datei.

Bei Verwendung bitte Namensnennung:
> "Powered by Whisper Transcription Tool - Dennis Westermann / aiEX Academy"

---

## 🔗 Links

- **GitHub**: [github.com/cubetribe/Whisper-Transcription-Tool](https://github.com/cubetribe/Whisper-Transcription-Tool)
- **aiEX Academy**: [www.goaiex.com](https://www.goaiex.com)
- **Support**: Erstellen Sie ein Issue auf GitHub

---

## 🙏 Danksagung

- OpenAI für das Whisper-Modell
- Georgi Gerganov für Whisper.cpp
- Die Open-Source-Community

---

**Made with ❤️ by Dennis Westermann | aiEX Academy | www.goaiex.com**

*Transforming Audio into Knowledge - One Transcription at a Time*