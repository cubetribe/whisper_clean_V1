# Whisper Transcription Tool - TODO Liste

Diese TODO-Liste verfolgt alle Aufgaben für die Entwicklung des modularen Python-Transkriptionstools mit Whisper.cpp für Apple Silicon. Die Liste ist nach Modulen und Entwicklungsphasen organisiert.

## Legende
- [ ] Offen
- [x] Erledigt
- [~] In Bearbeitung
- [!] Hohe Priorität
- [?] Benötigt Entscheidung

## Projektsetup und Grundstruktur

- [x] Repository-Struktur erstellen
- [x] Grundlegende Dokumentation (README.md, CONTRIBUTING.md, etc.) erstellen
- [x] Konfigurationssystem implementieren
- [~] Entwicklungsumgebung einrichten
- [ ] CI/CD-Pipeline einrichten (GitHub Actions)
- [ ] Automatisierte Tests einrichten
- [ ] Versionierungsstrategie festlegen
- [ ] Pre-commit-Hooks konfigurieren

## Modul 1: Lokale Audio-Transkription

### Whisper.cpp-Integration
- [x] Whisper.cpp für Apple Silicon (M4) kompilieren
- [x] Binärdateien für verschiedene Plattformen bereitstellen
- [x] Wrapper-Funktionen für Whisper.cpp implementieren
- [x] Fehlerbehandlung für Whisper.cpp-Aufrufe implementieren
- [x] "large-v3-turbo" als Standard-Modell verwenden
- [x] Automatische Audio-Extraktion aus Videodateien implementieren

### Modellverwaltung
- [x] Modelldownload-Funktionalität implementieren
- [x] Modellcache-System implementieren
- [x] Modellauswahl-Logik implementieren
- [~] Anzeige der heruntergeladenen Modelle in der GUI verbessert
- [x] Korrekte Pfadauflösung für Modellverzeichnis implementiert (whisper.model_path)
- [x] Löschfunktion für lokale Modelle implementiert
- [!] Download-Geschwindigkeit optimieren (aktuell sehr langsam, ca. 0,08 MB/s)
- [!] WebSocket-Aktualisierung für Download-Fortschritt:
  - [x] Fehlende Imports hinzugefügt
  - [x] WebSocket-Endpunkt implementiert
  - [x] Verbesserte Fehlerbehandlung
  - [~] Problem identifiziert (Verbindungen aber keine Updates)
  - [ ] Lösung verschoben auf Version 0.6.0
- [ ] Speicherprüfung vor Modellladung implementieren

### Transkriptionsfunktionen
- [x] Haupttranskriptionsfunktion implementieren
- [x] Spracherkennung implementieren
- [x] Fortschrittsanzeige für lange Transkriptionen hinzufügen
- [x] Multithreading-Unterstützung optimieren

### Ausgabeformatierung
- [x] TXT-Ausgabeformat implementieren
- [x] SRT-Untertitelformat implementieren
- [x] SRT-Dateien gemäß offiziellem Standard mit korrekten Zeitangaben erstellen (JSON-basierte Generierung)
- [x] Verbesserte SRT-Segmentierung mit optimalen Untertitelblöcken (1-3 Sek.)
- [x] GUI-Erweiterung für SRT-Exporteinstellungen (max. Zeichen/Zeile, max. Dauer/Segment) implementieren
- [x] Implementierung von Text-Formatierung mit Zeilenbegrenzungen (gemäß SRT-INFO.md)
- [ ] Unit-Tests für `segments_to_srt` hinzufügen
- [ ] Integrationstest für `--format srt` mit JSON-Fallback
- [x] VTT-Untertitelformat implementieren
- [x] JSON-Ausgabeformat für Weiterverarbeitung implementieren
- [!] JSON-Kontroll-Export implementieren:
  * [ ] Funktion export_json_control erstellen
  * [ ] Speicherung im Unterordner JSON-Exporter
  * [ ] Automatische Erstellung des Unterordners, falls nicht vorhanden
  * [ ] Integration in die bestehende Export-Logik
  * [ ] Tests zur Verifikation der Funktionalität

### Für Version 0.3.5
- [x] Exportpfad-Auswahlmöglichkeit in der Web-UI implementieren
- [x] Download-Button-Funktionalität korrigieren
- [x] SRT-Anzeige mit Zeitstempeln in der Weboberfläche hinzufügen
- [x] Interaktiven Verzeichnisbrowser für die Pfadauswahl entwickeln
- [x] Weitere Tests für SRT-Generierung entwickeln
- [x] Installer-Skript erstellen

### Für Version 0.4.0 (Aktuelle Version)
- [x] JavaScript-Fehler in der Promise-Verkettung beheben (falsche Klammersetzung im fetch-Promise)
- [x] Fehlende schließende Klammer im jQuery-Document-Ready-Handler ergänzen
- [x] Gesamte JavaScript-Struktur überprüfen und optimieren
- [x] Dokumentation der Fehler und Lösungen in PROBLEMS.md
- [x] Versionsnummer auf 0.4.0 aktualisieren in allen relevanten Dateien
- [x] Sichern der stabilen Version 0.3.5 als Backup

### Für Version 0.4.1 (Aktuelle Version)
- [x] GUI-Erweiterung für Batch-Verarbeitung von Dateien
  * [x] multiple-Attribut zum Dateiauswahl-Element hinzufügen
  * [x] Sequentielle Verarbeitung mehrerer Dateien implementieren
  * [x] Fortschrittsanzeige für die gesamte Batch und einzelne Dateien
  * [x] Fehlerbehandlung bei teilweisem Batch-Fehlschlag
  * [x] Zusammenfassende Statistik nach Batch-Abschluss
- [x] ~~Echtzeit-Fortschrittsanzeige implementieren~~ (nicht erforderlich - aktuelle Anzeige ausreichend)
- [x] ~~Verbesserte Fehlerbehandlung in der Weboberfläche~~ (nicht erforderlich - aktuelle Fehlerbehandlung robust)
- [x] ~~Mobile Optimierung der Weboberfläche~~ (nicht erforderlich - Basis-Responsivität vorhanden)

### Für Version 0.4.2 (Wenn Bedarf besteht)
- [x] Echtzeit-Fortschrittsanzeige mit WebSocket-Events
- [ ] Erweiterte Fehlerbehandlung mit spezifischen Empfehlungen
- [ ] Vollständige mobile Optimierung

## Version 0.5.0: Video-Audioextraktion (Aktuell)
- [x] FFmpeg-Integration
- [x] Grundlegende Videoformat-Unterstützung
- [~] Batch-Verarbeitung
- [ ] Automatische Codec-Erkennung
- [x] BlackHole-basierte Aufnahmefunktion:
   - [x] Device-Auswahl für Systemaudio und Mikrofon
   - [x] Parallelaufnahme auf getrennten Kanälen
   - [x] Automatische Sample Rate Anpassung
   - [x] Integration in Transkriptions-Pipeline

## Version 0.5.1: Bugfixes und Stabilisierung
### Kritische Fehler
- [x] Whisper-Modellfehler beheben
  * Modelldatei "ggml-tiny.bin" überprüfen und reparieren
  * Fehler "not all tensors loaded from model file - expected 167, got 1" diagnostizieren
  * Beschädigte Modelldatei identifizieren und neu herunterladen
  * Integritätscheck für Modelle nach Download implementieren
- [ ] GUI-Status beim Stoppen der Aufnahme aktualisieren und Buttons zurücksetzen
  * `on_stop`-Callback von `stop_recording()` an das Frontend senden
  * Frontend-Buttons nach Stop zurücksetzen und Status auf "Bereit" setzen
  * Fehlerbehandlung für wiederholtes Stoppen implementieren

### Hohe Priorität
- [x] BlackHole-Audiogeräte-Erkennung reparieren
  * API-Endpunkt `/api/phone/devices` funktioniert jetzt korrekt
  * Dropdown-Menüs werden mit erkannten Geräten befüllt
  * Problem lag an fehlendem Zugriff auf das `sounddevice`-Modul - Server muss mit aktivierter virtueller Umgebung gestartet werden
- [x] Audioaufnahme-Funktion mit BlackHole reparieren
  * Fehler bei Stream-Erstellung mit dynamischer Kanalanpassung behoben
  * Unterstützung für Geräte mit unterschiedlichen Kanalanzahlen implementiert
  * Verbesserte Fehlerbehandlung und Logging hinzugefügt
- [x] Automatische Übergabe der Audiodateien an das Transkriptionsformular implementieren
  * URL-Parameter anstelle von LocalStorage (analog zur Videoextraktion)
  * Dateiauswahl-Felder bei Seitenaufruf vorbefüllen
  * Pfadkorrekturen für lokale Dateien überprüfen

### Mittlere Priorität
- [x] UTF-8-Kodierungsprobleme in der Web-Oberfläche beheben
  * Escapesequenzen in Umlauten korrigiert ("Geräteauswahl" wird korrekt als "Geräteauswahl" angezeigt)
  * Template-Dateien auf korrekte Kodierung geprüft
- [x] Projektbereinigung durchführen
  * Entfernen von nicht benötigten Dateien und Codefragmenten
  * Konsolidierung von Funktionen und Klassen
  * Verbesserung der Code-Struktur und -Lesbarkeit
- [ ] Spracheinstellung für Transkription erzwingen
  * `language='de'` in API-Aufruf standardmäßig setzen
  * Parameterweiterleitung in Endpunkt prüfen
  * Tests für Sprachparameter implementieren

## Version 0.7.0 (Aktuell) - Speichermanagement und verbesserte Stapelverarbeitung

### Höchste Priorität
- [x] Festplattenmanagement für temporäre Dateien
  - [x] Automatische Bereinigung der temporären Ordner nach Transkriptionen
  - [x] Löschung von nicht mehr benötigten Videodateien nach der Verarbeitung
  - [x] Implementierung einer Überwachungsfunktion für Speicherplatzverbrauch
  - [x] Konfigurierbare Aufbewahrungsrichtlinien für temporäre Dateien
  - [x] Integration in die Web-Benutzeroberfläche mit eigener Speicherseite
  - [x] Anzeige von Speicherstatistiken und Verwaltungsoptionen im UI
  - [x] Automatische Bereinigung bei niedrigem Speicherplatz
  - [x] Konfigurierbare Speicherplatzgrenzen
  - [x] Warnmeldungen bei Stapelverarbeitung, wenn nicht genügend Speicherplatz verfügbar ist

- [!] Automatische Konvertierung von WAV zu MP3
  - [ ] Implementierung einer automatischen WAV-zu-MP3-Konvertierung nach der Extraktion
  - [ ] Sofortige Löschung der WAV-Dateien nach der Konvertierung
  - [ ] Prüfung der MP3-Dateien auf Integrität vor Löschung der Originale
  - [ ] Konfigurierbare MP3-Qualitätseinstellungen in der Benutzeroberfläche

- [!] Gleichzeitiger Export von TXT und SRT
  - [ ] Implementierung einer neuen Funktion für simultanen Export beider Formate
  - [ ] Anpassung der Benutzeroberfläche für Multiple-Format-Auswahl
  - [ ] Backend-Erweiterung für parallele Formatverarbeitung
  - [ ] Konsistente Benennung für zusammengehörige Ausgabedateien

- [!] Verbesserte Stapelverarbeitung
  - [ ] Stabilisierung der Batch-Funktionalität für über 30 Videos
  - [ ] Optimierung der Speichernutzung während der Stapelverarbeitung
  - [ ] Verbesserte Fortschrittsanzeige und Fehlerbehandlung
  - [ ] Möglichkeit zur Wiederaufnahme unterbrochener Stapelverarbeitungen
  - [ ] Protokollierung der Verarbeitungsergebnisse für Fehlernachverfolgung

### Zusätzliche Verbesserungen
- [ ] Anpassbares Ausgabeverzeichnis für Transkriptionsergebnisse
- [ ] Zusätzliche Fehlerbehebung für den Download der erzeugten Dateien
- [ ] Automatische Modellintegritätsprüfung
- [ ] Verbesserte Fehlerbericht-Funktion

### App-Portabilität und Multiplattform-Unterstützung
- [x] Dynamische Pfadfindung für die Anwendung implementieren
  * [x] Lösung für hardcodierte Pfade in AppleScript/Shell-Skripten entwickelt
  * [x] Relativen Pfad zur Anwendung selbst ermittelt (mit BASH_SOURCE und Python-basierter Pfadermittlung)
  * [x] Automatische Pfadanpassung bei Start der App implementiert
  * [x] Konfigurationsdatei im Home-Verzeichnis des Nutzers aktualisiert und genutzt
- [x] Portable App-Version erstellt
  * [x] Automatische Erkennung und Einrichtung der Arbeitsumgebung
  * [x] Konfiguration für verschiedene Benutzerverzeichnisse
  * [x] Installations-/Setup-Wizard für Erstnutzer implementiert (setup_directories.py)
- [x] Pfadunabhängige Starter-App
  * [x] Standalone-Launcher entwickelt (QuickLauncher.command)
  * [x] Automatische Projektpfad-Erkennung implementiert
  * [x] Robuste Fehlerbehandlung bei fehlenden Dateien/Pfaden
- [x] Plattformunabhängige Implementierung
  * [x] Windows-Pfadunterstützung in FFmpeg-Wrapper und Extraktionsmodulen
  * [x] Betriebssystemspezifische Pfade in Dateiauswahldialogen
  * [x] Dynamische Anpassung an verschiedene Umgebungen
  * [x] Automatische Audio-Extraktion aus verschiedenen Videoformaten
  * [x] Dynamische DYLD_LIBRARY_PATH-Konfiguration für macOS
  * [x] Symbolische Links für Rückwärtskompatibilität

### Geplant für Version 0.8.1
- [ ] Performance-Optimierung bei der Transkription
- [ ] Verbesserte Videovorschau in der Web-UI
- [ ] Cross-Plattform-Tests auf verschiedenen Betriebssystemen durchführen
- [ ] Installationsanleitung für Linux und Windows erstellen

### Geplant für Version 0.9.0
- [ ] Eigene Desktop-App mit Benutzerfreundlichem UI (Electron/PyQt)
- [ ] Stapelverarbeitung-UI verbessern
- [ ] Unterschiedliche Transkriptionsqualität-Profile erstellen (schnell, standard, genau)

### Verschobene Aufgaben
- [ ] Unterstützung für Transkriptvergleich zwischen verschiedenen Modellen
- [ ] Neue WebSocket-Implementierung
- [ ] Redis-PubSub-Integration

## Modul 2: Video-Audioextraktion

### FFmpeg-Integration
- [x] FFmpeg-Verfügbarkeit prüfen (in `module2_extract/ffmpeg_wrapper.py` als `detect_ffmpeg()`)
- [ ] Installationsanleitung für FFmpeg verbessern
- [ ] Automatische Installation von FFmpeg im Installationsskript integrieren
- [x] Wrapper-Funktionen für FFmpeg implementieren (in `ffmpeg_wrapper.py`)
- [x] Optimale Kommandozeilenparameter für verschiedene Formate
- [x] Fehlerbehandlung für FFmpeg-Aufrufe implementieren

### Audioextraktion
- [x] Funktionen zur Audioextraktion implementieren (in `__init__.py` als `extract_audio()`)
- [x] Unterstützung für verschiedene Videoformate (MP4, MOV, etc.)
- [ ] ~~Audio-Optimierung für Whisper implementieren~~ (nicht notwendig)
- [ ] Fortschrittsanzeige für lange Extraktionen in Web-UI integrieren
- [ ] Benutzereinstellungen für Videokonvertierung in Web-UI hinzufügen

### Weiterentwicklung in der Web-UI
- [ ] Videoformate in der Dateiauswahl explizit unterstützen (`accept` Attribut anpassen)
- [x] Nahtlose Übergabe von extrahiertem Audio an Transkriptionsmodul (bereits in `web/__init__.py`)
- [ ] Feedback zum Extraktionsfortschritt während der Videokonvertierung
- [ ] Verbesserung der Fehlerbehandlung bei problematischen Videos
- [ ] **GUI-Verbesserungen (Allgemein):**
  - [ ] **Modellverwaltung:**
    - [ ] Eigene Sektion (Home/Settings) zur Auswahl, Download und Verwaltung von Whisper-Modellen.
    - [ ] Möglichkeit zur Festlegung des Speicherorts für Modelle.
  - [ ] **Versionsanzeige:**
    - [x] Aktuelle Anwendungsversion (z.B. 0.5.0) in der UI anzeigen (z.B. im Footer).

## Modul 3: Audio-Konverter (hohe Priorität)

### Audio-Formatunterstützung
- [ ] Integration von pydub + ffmpeg für Audio-Konvertierung
- [ ] Unterstützung für .opus-Dateien (WhatsApp Sprachnachrichten) hinzufügen
- [ ] Nahtlose Integration in den Transkriptionsprozess
- [ ] Überprüfen und erweitern der Formatunterstützung (.wav, .mp3, .opus, etc.)
- [ ] Fehlerbehandlung für nicht unterstützte oder korrupte Audioformate

### UI-Integration
- [ ] Separate Seite/Tab für Audio-Konvertierung implementieren
- [ ] Benutzerfreundliches Interface für Formatauswahl
- [ ] Batch-Konvertierung mehrerer Dateien ermöglichen
- [ ] Fortschrittsanzeige für Konvertierungsprozesse

### Transkriptions-Integration
- [ ] Erweiterung der Transkriptionsfunktion zur Unterstützung aller konvertierbaren Formate
- [ ] Automatische Konvertierung vor der Transkription bei Bedarf
- [ ] Zwischenspeicherung von konvertierten Audiodateien für bessere Performance

## Zukünftige Module (geplant für spätere Versionen)

## Modul 4: Telefonaufnahme-Verarbeitung (verschoben, niedrige Priorität)

### Audiospurverwaltung
- [ ] Funktionen zur Verwaltung mehrerer Audiospuren implementieren
- [ ] Metadaten-Extraktion und -Verwaltung implementieren
- [ ] Unterstützung für verschiedene Audioformate testen

### Transkriptionskoordination
- [ ] Koordination der Transkription mehrerer Spuren implementieren
- [ ] Zeitstempelbasierte Zusammenführung implementieren
- [ ] Parallelisierung der Transkription implementieren

### Dialogformatierung
- [ ] Dialogartige Formatierung der Transkripte implementieren
- [ ] Sprecherzuordnung implementieren
- [ ] Verschiedene Ausgabeformate für Dialoge unterstützen

## Modul 5: Chatbot zur Transkriptanalyse (verschoben, niedrige Priorität)

### Vektordatenbank
- [ ] Vektordatenbank-Integration (ChromaDB oder FAISS) implementieren
- [ ] Chunking-Strategien für Transkripte implementieren
- [ ] Effiziente Indizierung und Suche implementieren

### LLM-Anbindung
- [ ] Lokale LLM-Anbindung über Ollama implementieren
- [ ] Optionale OpenAI-API-Anbindung implementieren
- [ ] Prompt-Engineering für Transkriptanalyse optimieren

### Abfrage-Engine
- [ ] Semantische Abfragefunktionen implementieren
- [ ] Kontextfenster-Management implementieren
- [ ] Relevanz-Ranking implementieren

### Benutzeroberfläche
- [ ] CLI-Schnittstelle implementieren
- [ ] Web-Schnittstelle mit Gradio implementieren
- [ ] Datei-Upload-Funktionalität implementieren
- [ ] Ergebnisanzeige und -download implementieren

## Dokumentation und Tests

### Dokumentation
- [ ] Installationsanleitung vervollständigen
- [ ] Benutzerhandbuch erstellen
- [ ] API-Dokumentation erstellen
- [ ] Entwicklerdokumentation erstellen

### Tests
- [ ] Unit-Tests für alle Module schreiben
- [ ] Integrationstests schreiben
- [ ] End-to-End-Tests schreiben
- [ ] Performance-Tests schreiben

## Optimierung und Verfeinerung

### Performance
- [ ] Flaschenhälse identifizieren und beheben
- [ ] Parallelisierung wo sinnvoll implementieren
- [ ] Speicherverbrauch optimieren
- [ ] Startzeit optimieren

### Audio-Visualisierung (Version 0.7.0)
- [ ] Implementierung von Echtzeit-Lautstärke-Visualisierung
  * Anzeige der aktuellen Lautstärke während der Aufnahme
  * Farbkodierte Pegelanzeige (grün, gelb, rot)
  * Anpassbare Empfindlichkeit und Schwellenwerte
- [ ] Wellenform-Visualisierung der aufgenommenen Audiodaten
  * DAW-ähnliche Darstellung der Audiowellenformen
  * Zoom- und Scroll-Funktionalität in der Wellenansicht
  * Möglichkeit zur visuellen Auswahl von Audioabschnitten
- [ ] Erweitertes Audio-Monitoring
  * Spektrum-Analyse für fortgeschrittene Audiodiagnostik
  * Clipping-Warnung bei Übersteuerten Audiospuren
  * Anpassbare Visualisierungsparameter (Farben, Auflösung, etc.)

### Fehlerbehandlung
- [ ] Umfassende Fehlerbehandlung implementieren
- [ ] Wiederherstellungsmechanismen für unterbrochene Prozesse
- [ ] Validierung von Eingaben und Ausgaben
- [ ] Logging-System verbessern

### Benutzerfreundlichkeit
- [ ] Benutzeroberfläche verfeinern
- [ ] Hilfetexte und Tooltips hinzufügen
- [ ] Beispiele und Tutorials erstellen
- [ ] Feedback von Benutzern einholen und umsetzen

## Modul 5: Live-Telefonat mit Echtzeit-Aufzeichnung (Geplant)

### Telefonat-Aufzeichnung
- [ ] Schnittstelle für Telefongespräche über das Internet (VoIP) implementieren
- [ ] Live-Aufzeichnung von Telefonaten ermöglichen
- [ ] Automatische Trennung der Gesprächsteilnehmer in separate Audiospuren
- [ ] Sichere Speicherung der Aufnahmen mit Verschlüsselung

### Automatische Transkription
- [ ] Direkte Übergabe der Telefonataufzeichnung an das Transkriptionsmodul
- [ ] Automatische Sprechererkennung und -kennzeichnung (Person 1, Person 2)
- [ ] Formatierung als Dialog mit Zeitstempeln
- [ ] Optionale Echtzeit-Transkription während des Gesprächs

### Chatbot-Integration
- [ ] Nahtlose Übergabe des Transkripts an das Chatbot-Modul
- [ ] Automatische Analyse und Zusammenfassung des Gesprächs
- [ ] Extraktion von wichtigen Punkten und Aufgaben aus dem Telefonat
- [ ] Erstellung von Follow-up-E-Mails basierend auf dem Gesprächsinhalt

## Zukünftige Erweiterungen

- [ ] Sprecheridentifikation integrieren
- [ ] Mehrsprachige Unterstützung erweitern
- [ ] Batch-Verarbeitung für große Mengen von Dateien implementieren
- [ ] GUI-Anwendung für macOS entwickeln
- [ ] Cloud-Synchronisationsfunktionen implementieren
- [ ] Echtzeit-Transkription implementieren
