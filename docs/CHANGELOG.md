# Whisper Transkriptionstool Changelog

## [Unreleased]
- Zukünftige Verbesserungen und Funktionen werden hier aufgeführt

## [0.9] - 2025-05-24

### Implementierte Funktionen
- WebSocket-Implementierung mit verbesserter Event-Übertragung
- Fortschrittsanzeige während der Videokonvertierung
- Automatische Installation von FFmpeg im Setup-Skript
- Verbesserter Datei-Download aus benutzerdefinierten Verzeichnissen

## [0.8.0] - 2025-05-14

### Implementierte Funktionen
- Vollständige App-Portabilität erreicht
  - Dynamische Pfadfindung auf Betriebssystemebene implementiert
  - Automatische Audioextraktion aus Videodateien
  - Vereinfachter App-Start mit QuickLauncher.command
  - Symbolische Links für Rückwärtskompatibilität
- Verbesserte Konfiguration
  - Relative Pfade in der gesamten Codebasis
  - Automatisches Setup der benötigten Verzeichnisse
  - Standard-Modellauswahl auf 'large-v3-turbo' gesetzt
- Robuste Fehlerbehandlung
  - DYLD_LIBRARY_PATH Konfiguration automatisiert
  - Fehlerbehandlung bei fehlenden Ausgabedateien
  - Erweiterte Logging-Funktionalität

## [0.7.1] - 2025-05-14

### Implementierte Funktionen
- App-Portabilität implementiert
  - Dynamische Pfadfindung für alle Komponenten (python-basiert)
  - Automatische Konfigurationsanpassung beim Programmstart
  - Plattformunabhängige Pfaderkennung für FFmpeg und andere Abhängigkeiten
  - Korrektur aller hartcodierten Pfade im gesamten Codebase
  - Verbesserte Whisper Transkriptionstool.app mit dynamischer Pfaderkennung
- Projektstruktur verbessert
  - Dokumentationsordner (docs) mit zentralem Inhaltsverzeichnis
  - Bessere Organisation von Dokumentationsdateien
  - Einheitliche Backup-Strategie implementiert

### Stabilität und Wartbarkeit
- Fehlerkorrektur in Logging-Funktionen (`get_logger` Parameter korrigiert)
- Plattformunabhängige Pfade in wichtigen Kernmodulen:
  - FFmpeg-Wrapper
  - Web-Interface
  - Modell-Management
- Dynamische Verzeichniserkennung für Dateiauswahldialoge (OS-spezifisch)
- Allgemeine Code-Wartung und Aufräumarbeiten

## [0.7.0] - 2025-05-11

### Implementierte Funktionen
- Verbessertes Festplattenmanagement für temporäre Dateien
  - Automatische Bereinigung der temporären Ordner nach Transkriptionen implementiert
  - Löschung von nicht mehr benötigten Videodateien nach der Verarbeitung implementiert
  - Überwachungsfunktion für Speicherplatzverbrauch mit Notfallbereinigung hinzugefügt
  - Konfigurierbare Aufbewahrungsrichtlinien für temporäre Dateien implementiert
  - Neue Speicherverwaltungsseite in der Web-Oberfläche zur Überwachung und manuellen Bereinigung
  - Automatische Bereinigung bei kritisch niedrigem Speicherplatz
  - Regelmäßige Überwachung des Festplattenspeichers im Hintergrund
  - Konfigurierbare Speicherplatzlimits (maximale Nutzung in %, Mindestplatz, Stapelverarbeitungsschwelle)
  - Warnhinweise bei der Stapelverarbeitung, wenn der Speicherplatz knapp wird
  - Benutzerobserfläche zur Anpassung aller Speicherverwaltungseinstellungen

### Geplante Funktionen
- Automatische Konvertierung von WAV zu MP3
  - WAV-zu-MP3-Konvertierung nach der Extraktion
  - Sofortige Löschung der WAV-Dateien nach der Konvertierung
  - Konfigurierbare MP3-Qualitätseinstellungen
- Gleichzeitiger Export von TXT und SRT
  - Simultaner Export beider Formate
  - Multiple-Format-Auswahl in der Benutzeroberfläche
- Stabilisierte Stapelverarbeitung für große Datenmengen
  - Unterstützung für über 30 Videos in einem Durchgang
  - Optimierte Speichernutzung während der Stapelverarbeitung
  - Verbesserte Fehlerbehandlung und Protokollierung

### Änderungen
- Website-URL im Footer von omgol.de auf goaiex.de aktualisiert

## [0.6] - 2025-05-11

### Added
- Updated version number to 0.6 in all relevant files and GUI.

## [0.5.1] - 2025-04-20

### Behoben
- Whisper-Modellfehler beim Laden der Tensoren behoben
  - Implementierung von Integritätsprüfungen für heruntergeladene Modelle
  - Automatische Erkennung und Entfernung beschädigter Modelldateien
  - Verbesserte Fehlerbehandlung beim Modell-Download
- UTF-8-Kodierungsprobleme in der Web-Oberfläche korrigiert
  - Fehlerhaft angezeigte Umlaute (ä, ö, ü) in den Templates behoben
  - Konsistente Zeichenkodierung im gesamten Projekt sichergestellt
- BlackHole-Audiogeräte-Erkennung repariert
  - API-Endpunkt `/api/phone/devices` funktioniert jetzt korrekt
  - Dropdown-Menüs werden mit erkannten Geräten befüllt
- Audioaufnahme-Funktion mit dynamischer Kanalanpassung verbessert
  - Fehler "Invalid number of channels" bei Stream-Erstellung behoben
  - Automatische Anpassung an tatsächliche Gerätekapazitäten
  - Verbesserte Fehlerbehandlung und Logging

### Verbessert
- Projektstruktur bereinigt und optimiert
  - Veraltete und nicht verwendete Module archiviert
  - Klare Trennung zwischen aktiver und archivierter Codebasis
  - Ausführliche Dokumentation der Projektorganisation
- Download-Geschwindigkeit von Whisper-Modellen deutlich erhöht
  - Steigerung von 0,08 MB/s auf über 100 MB/s
  - Chunk-Größe für Downloads von 8 KB auf 1 MB erhöht

## [0.5.0] - 2025-04-20

### Added
- Display application version (`0.5.0`) in the web UI footer on all pages.
- BlackHole-basierte Aufnahmefunktion für Konferenzsysteme
  - Parallele Aufnahme von Mikrofon und Systemton auf getrennten Kanälen
  - Echtzeit-Device-Erkennung mit BlackHole-Integration
  - Unterstützung für Teams, Discord, Zoom und andere Kommunikationsanwendungen
  - Vollständige GUI-Integration mit Tab-basierter Aufnahmesteuerung

### Changed
- Updated copyright notice in the web UI footer to ' 2025 Dennis Westermann / www.omgol.de'.
- WebSocket-Implementierung vorläufig pausiert
- Dokumentation vollständig überarbeitet
- Modellverwaltungs-GUI stabilisiert

### Behoben
- JavaScript-Fehler in der Model-Übersicht
- Falsche Pfadangaben in der Konfiguration

## [0.4.1] - 2025-04-19

### Hinzugefügt
- Batch-Verarbeitung für die gleichzeitige Transkription mehrerer Audiodateien
- Counter für ausgewählte Dateien in der Weboberfläche
- Sequentielle Verarbeitung mehrerer Dateien mit gemeinsamen Einstellungen
- Tabellarische Ergebnisdarstellung mit Einzeldatei-Downloads
- Zusammenfassende Statistik nach Abschluss der Batch-Verarbeitung

### Verbessert
- Robustere JavaScript-Struktur mit dedizierter Batch-Logik
- Klare Trennung zwischen Einzel- und Batch-Verarbeitung
- Verbesserte Fehlerbehandlung bei teilweisem Batch-Fehlschlag

## [0.4.0] - 2025-04-19

### Hinzugefügt
- Umfassende Fehlerbehebung im JavaScript-Code der Weboberfläche
- Verbesserte Benutzeroberfläche mit optimierter Fehlerbehandlung
- Robustere Ausführung und Anzeige der Transkriptionsergebnisse

### Behoben
- JavaScript-Fehler in der Promise-Verkettung behoben
- Schließende Klammern im DOM-Ready-Handler ergänzt
- Ergebnisanzeige wird nun korrekt aktualisiert

### Geplante Verbesserungen
- Batch-Verarbeitung für die Transkription mehrerer Audiodateien
- Verbesserte Fortschrittsanzeige mit Echtzeit-Status
- Optimierung der Benutzeroberfläche für mobile Geräte

## [0.3.5] - 2025-04-19

### Hinzugefügt
- Exportpfad-Auswahlmöglichkeit in der Web-UI mit interaktivem Verzeichnisbrowser implementiert
- Anzeige der SRT-Untertitel mit Zeitstempeln in der Weboberfläche
- Batch-Verarbeitung für die gleichzeitige Transkription mehrerer Audiodateien
- Neuer API-Endpunkt `/api/download` für direkten Dateidownload
- Neuer API-Endpunkt `/api/browse-directories` zum Durchsuchen der Verzeichnisstruktur
- Parameter `output_dir` in transcribe_audio-Funktion für benutzerdefinierte Ausgabeverzeichnisse
- Installationsskripte für macOS/Linux (`install.sh`) und Windows (`install.bat`)

### Behoben
- Download-Button funktioniert jetzt korrekt für generierte Dateien
- SRT-Anzeige zeigt vollständige Untertitel mit Zeitstempeln
- Fehlendes Sprachen-Modul durch Liste von gängigen Sprachen ersetzt

### Geplante Verbesserungen
- Unit-Tests für SRT-Generierung
- Weitere Verbesserungen der Benutzeroberfläche
- Generierung eines Installationspakets

## [0.3.2] - 2025-04-19

### Hinzugefügt
- Verbesserte SRT-Generierung mit optimaler Segmentgröße (1-3 Sek.)
- GUI-Steuerelemente für SRT-Parameter (max. Zeichen, max. Dauer)
- Intelligente Textaufteilung für bessere Lesbarkeit
- text_to_srt-Funktion erweitert mit Zeitdauerberechnung und Segmentierung

## [0.3.1] - 2025-04-19

### Hinzugefügt
- JSON-basierte SRT-Erzeugung via `segments_to_srt` und CLI-Flags `--srt-max-chars`/`--srt-max-duration`.

### Behoben
- SRT-Export generiert nun korrekte Untertiteldateien mit Nummerierung und Zeitstempeln.

## [0.3.0] - 2025-04-19

### Fehlerbehebungen
- SRT-Export korrigiert: Gewährleistet nun die Erstellung standardkonformer SRT-Dateien durch konsequente Nutzung des `srt`-Pakets, auch wenn Whisper.cpp keine SRT-Datei liefert.
- Logging im SRT-Exportpfad hinzugefügt zur besseren Fehlersuche.

## [0.2.3] - 2025-04-11

### Hinzugefügt
- Automatische Vorauswahl der deutschen Sprache bei der Transkription

### Fehlerbehebungen
- Problem mit gemischter Sprache (Deutsch/Englisch) in Transkriptionen behoben

### Geplant
- Verbesserung der SRT-Ausgabe gemäß offiziellem Standard mit der pysrt-Bibliothek
- Neues Modul 5: Live-Telefonat-Aufzeichnung mit automatischer Transkription und Sprechererkennung
- Integration des Telefonie-Moduls mit dem Chatbot zur automatischen Gesprächsanalyse

## [0.2.2] - 2025-04-11

### Hinzugefügt
- Nahtlose Integration des Video-Extraktions- und Transkriptionsworkflows
- Automatische Übernahme der extrahierten Audiodatei in die Transkription

## [0.2.1] - 2025-04-11

### Hinzugefügt
- Automatisches Öffnen des Browsers beim Serverstart
- Portüberprüfung und automatische Suche nach freien Ports
- Erkennung und optionales Beenden bestehender Server-Instanzen

## [0.2.0] - 2025-04-11

### Hinzugefügt
- Speicherprüfung vor Modellladung implementiert
- Fortschrittsanzeige für lange Transkriptionen via WebSockets
- Start-Skript für einfachen Server-Start
- Desktop-App für One-Click-Start des Servers
- Debug-Modus in Start-Skript integriert

## [0.1.0] - 2025-04-11

### Hinzugefügt
- Whisper.cpp für Apple Silicon (M4) kompiliert und integriert
- Konfigurationssystem mit JSON-Datei implementiert
- Wrapper-Funktionen für Whisper.cpp
- Fehlerbehandlung für Whisper.cpp-Aufrufe
- "large-v3-turbo" als Standard-Modell konfiguriert
- Modelldownload-Funktionalität
- Modellcache-System implementiert
- Modellauswahl-Logik
- Transkriptionsfunktionen für verschiedene Audioformate
- Spracherkennung implementiert
- Multithreading-Unterstützung für Transkriptionen
- Ausgabeformate: TXT, SRT, VTT und JSON

### Fehlerbehebungen
- Problem mit -metal Parameter in Whisper CLI behoben
- Probleme mit temporären Verzeichnissen und Ausgabedateien behoben
