# Whisper Transkriptionstool - Probleme und Fehler

## Aktuelle Probleme (Stand: 2025-05-14)

### 2025-05-11: Internal Server Error auf der Speicherverwaltungsseite

- **Datum:** 2025-05-11
- **Betroffene Komponente:** Speicherverwaltung / Web-Oberfläche
- **Fehlerbeschreibung:** Beim Aufruf der Speicherverwaltungsseite (http://localhost:8096/disk) tritt ein Internal Server Error auf.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung
  2. Navigiere zur Seite http://localhost:8096/disk
- **Erwartetes Verhalten:** Die Speicherverwaltungsseite wird korrekt angezeigt
- **Tatsächliches Verhalten:** Ein Internal Server Error wird angezeigt
- **Lösungsansatz:** 
  1. Behebung der Inkompatibilität zwischen Flask- und FastAPI-Routen. API-Endpunkte wurden von `app.route()` auf FastAPI-konforme Dekoratoren (`app.get()`, `app.post()`) umgestellt.
  2. Ersetzung von `render_template()` durch FastAPI-konforme `templates.TemplateResponse()`
  3. Anpassung der Parametertrennung in den Funktionsaufrufen
  4. Korrektur der Formularverarbeitung durch Verwendung von `await request.form()`
  5. Hinzufügen fehlender Importe für `RedirectResponse` und Pydantic-Klassen
- **Status:** Gelöst

### 2025-05-14: Download-Fortschritt wird nicht in der Web-UI angezeigt

- **Datum:** 2025-05-14
- **Betroffene Komponente:** Web-UI / WebSocket / Modell-Download
- **Fehlerbeschreibung:** Der Fortschritt beim Herunterladen von Modellen wird nur im Terminal angezeigt, nicht aber in der Weboberfläche, obwohl die Fortschrittsdaten an die WebSockets gesendet werden.
- **Priorität:** Niedrig
- **Reproduktionsschritte:** 
  1. Starte die Anwendung
  2. Navigiere zur Modell-Verwaltungsseite
  3. Starte den Download eines Modells
- **Erwartetes Verhalten:** Der Download-Fortschritt sollte in der Web-UI durch eine Fortschrittsleiste oder prozentuale Anzeige sichtbar sein
- **Tatsächliches Verhalten:** Der Fortschritt ist nur im Terminal sichtbar, obwohl die Logs zeigen, dass die Daten an die WebSockets gesendet werden ("Broadcasting to active websockets")
- **Lösungsansatz:** 
  1. Überprüfen der Frontend-JavaScript-Implementierung für die WebSocket-Verarbeitung
  2. Sicherstellen, dass die empfangenen Fortschrittsdaten korrekt in der UI angezeigt werden
  3. Testen der WebSocket-Verbindung und des Event-Formats
- **Status:** Offen (Niedrige Priorität)

### 2025-05-14: Videotranskription erzeugt keine Ausgabedateien

- **Datum:** 2025-05-14
- **Betroffene Komponente:** Transkriptionsmodul / Whisper-Integration
- **Fehlerbeschreibung:** Bei der direkten Transkription von Videodateien (MP4, etc.) werden keine Ausgabedateien erzeugt, was zu der Fehlermeldung "Output file not found" führt.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung
  2. Lade eine Videodatei (MP4) zur Transkription hoch
  3. Wähle Modell und Format und starte die Transkription
- **Erwartetes Verhalten:** Die Videodatei sollte transkribiert werden und eine Ausgabedatei im gewünschten Format sollte erstellt werden
- **Tatsächliches Verhalten:** Der Transkriptionsprozess wird gestartet, aber es werden keine Ausgabedateien erzeugt, was zu einem Fehler führt
- **Lösungsansatz:** 
  1. Implementierung einer automatischen Audioextraktion aus Videodateien vor der Transkription
  2. Verwendung von FFmpeg zur Konvertierung von Video zu Audio (WAV, 16kHz, Mono)
  3. Übergabe der extrahierten Audiodatei an Whisper anstelle der Videodatei
  4. Robuste Fehlerbehandlung für verschiedene Dateiformate
- **Status:** Gelöst in Version 0.8.0

### Template für neue Probleme

- **Datum:** 
- **Betroffene Komponente:**
- **Fehlerbeschreibung:**
- **Priorität:** (kritisch/hoch/mittel/niedrig)
- **Reproduktionsschritte:**
- **Erwartetes Verhalten:**
- **Tatsächliches Verhalten:**
- **Lösungsansatz:**
- **Status:**

### 2025-04-20: Extrem langsame Download-Geschwindigkeit bei Modellen

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Modell-Download
- **Fehlerbeschreibung:** Die Download-Geschwindigkeit beim Herunterladen von Whisper-Modellen ist extrem langsam (ca. 0,08 MB/s), wodurch selbst kleine Modelle (wie das 75 MB 'tiny'-Modell) unverhältnismäßig lange zum Herunterladen benötigen.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Wähle ein Modell zum Download aus.
  3. Beobachte die Download-Geschwindigkeit.
- **Erwartetes Verhalten:** Die Download-Geschwindigkeit sollte im Bereich von MB/s liegen.
- **Tatsächliches Verhalten:** Die Download-Geschwindigkeit liegt bei ca. 0,08 MB/s.
- **Lösungsansatz:** 
  - Implementierung größerer Chunk-Sizes beim Download (1 MB statt 8 KB)
  - Entfernung korrupter Modelldateien und Neuinitialisierung
  - Verbessertes Fehlerhandling und Integritätsprüfung
- **Status:** Gelöst
- **Ergebnis:** Download-Geschwindigkeit nun bei über 100 MB/s statt 0,08 MB/s

### 2025-04-20: GUI zeigt Download-Fortschritt nicht an, obwohl er im Terminal sichtbar ist

- **Datum:** 2025-04-20
- **Betroffene Komponente:** GUI, Download-Fortschritt
- **Fehlerbeschreibung:** Obwohl im Terminal der Download-Fortschritt korrekt angezeigt wird (Prozent, aktuelle MB, gesamt MB, Geschwindigkeit), erscheint diese Information nicht in der Benutzeroberfläche. Der Fortschrittsbalken und die zugehörigen Informationen werden nicht aktualisiert.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Wähle ein Modell zum Download aus.
  3. Beobachte den Download-Fortschritt im Terminal und in der GUI.
- **Erwartetes Verhalten:** Der Download-Fortschritt sollte sowohl im Terminal als auch in der GUI korrekt angezeigt werden.
- **Tatsächliches Verhalten:** Der Download-Fortschritt wird nur im Terminal korrekt angezeigt.
- **Lösungsansatz:** 
  - WebSocket-Verbindung überprüfen
  - Event-System überprüfen
  - GUI-Update-Mechanismus überprüfen
- **Status:** In Bearbeitung - Verbindung wird korrekt hergestellt, aber Nachrichten werden nicht empfangen

### 2025-04-20: Fortschrittsanzeige beim Modell-Download nicht korrekt

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Modell-Download, Fortschrittsanzeige
- **Fehlerbeschreibung:** Die Fortschrittsanzeige beim Download von Whisper-Modellen zeigt zwar an, dass ein Download gestartet wird, aktualisiert aber nicht den tatsächlichen Fortschritt. Es werden keine Informationen zu Geschwindigkeit, heruntergeladener Menge oder verbleibender Zeit angezeigt.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Wähle ein Modell zum Download aus.
  3. Beobachte die Fortschrittsanzeige.
- **Erwartetes Verhalten:** Die Fortschrittsanzeige sollte den tatsächlichen Fortschritt korrekt anzeigen.
- **Tatsächliches Verhalten:** Die Fortschrittsanzeige zeigt nur an, dass ein Download gestartet wurde.
- **Lösungsansatz:** 
  - WebSocket-Verbindung überprüfen
  - Event-System überprüfen
  - Fortschrittsanzeige-Mechanismus überprüfen
- **Status:** In Bearbeitung - UI aktualisiert Status richtig, aber nicht den Fortschritt

### 2025-04-20: WebSocket-Kommunikation für Echtzeit-Updates

- **Datum:** 2025-04-20
- **Betroffene Komponente:** WebSocket-Kommunikation
- **Fehlerbeschreibung:** Obwohl WebSocket-Verbindungen erfolgreich hergestellt werden, werden Events vom Server nicht an den Client übertragen. Das Terminal zeigt "No active websockets, skipping broadcast", obwohl eine aktive Verbindung in den Logs angezeigt wird.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Überprüfe die WebSocket-Verbindung.
  3. Überprüfe die Event-Übertragung.
- **Erwartetes Verhalten:** Events sollten korrekt vom Server an den Client übertragen werden.
- **Tatsächliches Verhalten:** Events werden nicht übertragen.
- **Lösungsansatz:** 
  - WebSocket-Verbindung überprüfen
  - Event-System überprüfen
  - Broadcast-Mechanismus überprüfen
- **Status:** Zurückgestellt

### 2025-04-19: JavaScript-Fehler in der Weboberfläche

- **Datum:** 2025-04-19
- **Betroffene Komponente:** Weboberfläche, JavaScript
- **Fehlerbeschreibung:** 
  1. Transkriptionsergebnisse werden nicht in der Weboberfläche angezeigt, obwohl die Transkription im Hintergrund erfolgreich durchgeführt wird.
  2. Die Verarbeitung von Server-Antworten funktioniert nicht korrekt.
  3. Die Fortschrittsanzeige wird nicht richtig aktualisiert.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Führe eine Transkription durch.
  3. Beobachte die Ergebnisse in der Weboberfläche.
- **Erwartetes Verhalten:** Die Ergebnisse sollten korrekt in der Weboberfläche angezeigt werden.
- **Tatsächliches Verhalten:** Die Ergebnisse werden nicht angezeigt.
- **Lösungsansatz:** 
  1. Korrektur der Promise-Verkettung im fetch-Aufruf
  2. Ergänzung der fehlenden schließenden Klammer
  3. Überprüfung und Korrektur der gesamten JavaScript-Struktur
- **Status:** Gelöst

### 2025-04-20: Stoppen der Aufnahme-Status nicht in GUI übertragen
- **Datum:** 2025-04-20
- **Betroffene Komponente:** AudioRecorder, Web-UI
- **Fehlerbeschreibung:** Stoppen der Aufnahme wird im Terminal geloggt, aber die GUI aktualisiert den Aufnahme-Status nicht. Ein erneuter Stop-Versuch führt zu einer Fehlermeldung, obwohl die Datei korrekt gespeichert wurde.
- **Priorität:** Hoch
- **Reproduktionsschritte:**  
  1. Live-Aufnahme über die Web UI starten  
  2. Aufnahme beenden  
  3. GUI bleibt im Aufnahmemodus und zeigt weiterhin aktive Controls  
  4. Erneut "Beenden" klicken ergibt Fehler, Datei ist aber vorhanden  
- **Erwartetes Verhalten:** GUI wechselt nach dem Stoppen in den Status "Bereit" und aktiviert/deaktiviert Buttons korrekt  
- **Tatsächliches Verhalten:** GUI bleibt im Aufnahmemodus, Buttons lassen sich erneut klicken und führen zu Fehlern  
- **Lösungsansatz:**  
  1. `stop_recording()` Methode setzt `active_session_id = None` und löst `on_stop`-Callback aus  
  2. Frontend setzt Buttons immer zurück, auch wenn `success = false`  
  3. API-Endpunkt gibt immer 200 OK zurück mit `success`-Flag statt 500-Fehler  
- **Status:** Gelöst

### 2025-04-20: Fehlende automatische Übergabe der Audiodateien an Transkriptionsmodul
- **Datum:** 2025-04-20
- **Betroffene Komponente:** Web-UI, Transkriptionsseite
- **Fehlerbeschreibung:** Nach erfolgreicher Aufnahme werden die generierten Audiodateien nicht automatisch in das Transkriptionsfenster geladen; müssen manuell ausgewählt werden.
- **Priorität:** Mittel
- **Reproduktionsschritte:**  
  1. Live-Aufnahme durchführen und beenden  
  2. Auf "Zur Transkription senden" klicken  
  3. Transkriptionsseite öffnet sich ohne vorab geladene Dateien  
- **Erwartetes Verhalten:** Alle beiden Audiodateien (Mikrofon + System) werden in das Transkriptionsformular übernommen  
- **Tatsächliches Verhalten:** Formular bleibt leer, Dateien müssen manuell nachgeladen werden  
- **Lösung:**  
  1. URL-Parameter-Übergabe statt LocalStorage, analog zur Videoextraktion  
  2. Mikrofon- und System-Audio als separate Parameter übergeben (`audio` und `system_audio`)  
  3. In `transcribe.html` die übergebenen Parameter auslesen und anzeigen  
- **Status:** Gelöst

### 2025-04-20: Falsche Spracheinsatz bei Transkription
- **Datum:** 2025-04-20
- **Betroffene Komponente:** Transkriptions-Engine, Sprachparameter
- **Fehlerbeschreibung:** Teile deutsche Audiospuren werden im Ergebnis auf Englisch transkribiert, obwohl Sprache Deutsch sein sollte.
- **Priorität:** Mittel
- **Reproduktionsschritte:**  
  1. Deutsche Telefonaufzeichnung transkribieren  
  2. Teilweise englische Begriffe im Ergebnis bemerken  
- **Erwartetes Verhalten:** Vollständige Transkription im korrekten Sprachmodus (Deutsch)  
- **Tatsächliches Verhalten:** Mischung aus Deutsch und Englisch  
- **Lösungsansatz:**  
  1. Sprachparameter (`language=de`) wird jetzt standardmäßig bei der Telefon-zu-Transkription-Übergabe mitgesendet  
  2. Parameter erscheint in der URL (`/transcribe?audio=...&language=de`)  
  3. `transcribe.html` setzt Sprachparameter automatisch in das Formularfeld  
- **Status:** Gelöst

## Gelöste Probleme

### 2025-04-20: Falsche URL-Generierung für Whisper-Modell-Downloads

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Modell-Download, URL-Generierung
- **Fehlerbeschreibung:** Beim Versuch, das Modell 'large' herunterzuladen, trat der Fehler "HTTP 404 Not Found" auf, weil die generierte URL nicht korrekt war. Die Anwendung versuchte, die Datei "ggml-large.bin" herunterzuladen, die auf Hugging Face nicht existiert.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Wähle das Modell 'large' zum Download aus.
  3. Beobachte die URL-Generierung.
- **Erwartetes Verhalten:** Die URL sollte korrekt generiert werden.
- **Tatsächliches Verhalten:** Die URL wurde nicht korrekt generiert.
- **Lösungsansatz:** 
  1. Implementierung eines Mappingsystems, das einfache Modellnamen auf aktuelle Dateinamen abbildet
  2. Fokussierung auf die wichtigsten und aktuellsten Modelle
  3. Hinzufügen detaillierter Modellinformationen (Größe, Empfehlungen)
  4. Verbesserung der Fehlerbehandlung bei HTTP-Anfragen
- **Status:** Gelöst

### 2025-04-20: UnboundLocalError bei HTTP-Fehler während des Modell-Downloads

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Modell-Download, HTTP-Fehler
- **Fehlerbeschreibung:** Bei einem HTTP-Fehler (z.B. 404 Not Found) trat ein `UnboundLocalError` auf, weil im Fehlerfall auf Variablen wie `total_size_mb` zugegriffen wurde, die nicht initialisiert waren.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Wähle ein Modell zum Download aus.
  3. Simuliere einen HTTP-Fehler.
- **Erwartetes Verhalten:** Der Fehler sollte korrekt behandelt werden.
- **Tatsächliches Verhalten:** Ein `UnboundLocalError` trat auf.
- **Lösungsansatz:** 
  1. Initialisierung aller relevanten Variablen am Anfang der Funktion
  2. Neustrukturierung der try-except-Blöcke für bessere Fehlerbehandlung
  3. Korrekte Verwendung von nested try-except für HTTP-spezifische Fehler
- **Status:** Gelöst

### 2025-04-19: Export-Pfadauswahl und Download-Button fehlerhaft

- **Datum:** 2025-04-19
- **Betroffene Komponente:** Export-Pfadauswahl, Download-Button
- **Fehlerbeschreibung:** 
  1. Der Exportpfad für transkribierte Dateien kann nicht vom Benutzer ausgewählt werden.
  2. Der in der Weboberfläche vorhandene Download-Button funktioniert nicht richtig.
  3. SRT-Dateien werden in der Weboberfläche ohne Zeitstempel angezeigt.
  4. Es fehlt die Möglichkeit, mehrere Audiodateien gleichzeitig zu verarbeiten.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Führe eine Transkription durch.
  3. Versuche, den Exportpfad auszuwählen.
  4. Versuche, den Download-Button zu verwenden.
- **Erwartetes Verhalten:** Der Exportpfad sollte ausgewählt werden können und der Download-Button sollte funktionieren.
- **Tatsächliches Verhalten:** Der Exportpfad konnte nicht ausgewählt werden und der Download-Button funktionierte nicht.
- **Lösungsansatz:** 
  1. Hinzufügen einer Exportpfad-Auswahlmöglichkeit in der Web-UI
  2. Korrekte Implementierung des Download-Buttons
  3. Sicherstellen, dass der Download-Button die transkribierte Datei korrekt vom Server abruft
  4. Implementierung einer speziellen SRT-Anzeige mit Zeitstempeln
  5. Erweiterung des Formulars zur Unterstützung von Mehrfachauswahl und sequentieller Verarbeitung
- **Status:** Gelöst

### 2025-04-11: Fehlerhafte Spracherkennung und gemischte Transkription

- **Datum:** 2025-04-11
- **Betroffene Komponente:** Spracherkennung, Transkription
- **Fehlerbeschreibung:** Transkriptionen enthielten eine Mischung aus Englisch und Deutsch, weil die Spracherkennung nicht korrekt funktionierte. Das führte zu fehlerhaften und inkonsistenten Ergebnissen.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Führe eine Transkription durch.
  3. Beobachte die Ergebnisse.
- **Erwartetes Verhalten:** Die Ergebnisse sollten korrekt sein.
- **Tatsächliches Verhalten:** Die Ergebnisse waren fehlerhaft.
- **Lösungsansatz:** 
  - Bei der Weiterleitung von der Extraktionsseite wird jetzt automatisch `language=de` als Parameter übergeben
  - Die Transkriptionsseite erkennt diesen Parameter und stellt das Sprachfeld auf Deutsch ein
  - Dadurch verwendet Whisper durchgehend Deutsch für die Transkription
- **Status:** Gelöst

### 2025-04-11: Unterbrochener Workflow bei Videoextraktion

- **Datum:** 2025-04-11
- **Betroffene Komponente:** Videoextraktion, Workflow
- **Fehlerbeschreibung:** Bei der Videoextraktion musste der Nutzer die extrahierte Audiodatei manuell in der Transkriptionsseite auswählen, was den Workflow unterbrach.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Führe eine Videoextraktion durch.
  3. Beobachte den Workflow.
- **Erwartetes Verhalten:** Der Workflow sollte nicht unterbrochen werden.
- **Tatsächliches Verhalten:** Der Workflow wurde unterbrochen.
- **Lösungsansatz:** 
  - Implementierung einer URL-Parameterübergabe von der Extraktionsseite zur Transkriptionsseite
  - Anpassung der Transkriptionsseite, um Audiodateien aus dem URL-Parameter zu erkennen und automatisch zu laden
  - Anpassung der Transkriptions-API, um sowohl hochgeladene Dateien als auch Dateipfade zu unterstützen
- **Status:** Gelöst

### 2025-04-11: Falscher Import-Pfad zum Logger-Modul

- **Datum:** 2025-04-11
- **Betroffene Komponente:** Logger-Modul, Import-Pfad
- **Fehlerbeschreibung:** Nach der Behebung des Problems mit den fehlenden Konstanten trat ein neuer Fehler auf: `No module named 'src.whisper_transcription_tool.core.logger'`. Die Anwendung konnte immer noch keine Modelle laden und keine Transkriptionen durchführen.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Beobachte die Fehlermeldung.
- **Erwartetes Verhalten:** Die Anwendung sollte korrekt funktionieren.
- **Tatsächliches Verhalten:** Die Anwendung funktionierte nicht korrekt.
- **Lösungsansatz:** 
  - Korrektur des Import-Pfads in `module1_transcribe/__init__.py` zu: `from ..core.logging_setup import get_logger`.
- **Status:** Gelöst

### 2025-04-11: Fehlende constants.py im core-Modul

- **Datum:** 2025-04-11
- **Betroffene Komponente:** core-Modul, constants.py
- **Fehlerbeschreibung:** Beim Start des Servers trat ein Fehler auf: `No module named 'src.whisper_transcription_tool.core.constants'`. Die Anwendung konnte keine Modelle laden und keine Transkriptionen durchführen.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Beobachte die Fehlermeldung.
- **Erwartetes Verhalten:** Die Anwendung sollte korrekt funktionieren.
- **Tatsächliches Verhalten:** Die Anwendung funktionierte nicht korrekt.
- **Lösungsansatz:** 
  - Erstellen der fehlenden Datei `constants.py` mit allen notwendigen Konstanten wie:
    - URL für Whisper.cpp-Modelle
    - Standardverzeichnisse
    - Unterstützte Audio- und Videoformate
    - Unterstützte Ausgabeformate
    - Konfigurationsdateiname
    - Log-Dateiname
    - Versionsangabe
- **Status:** Gelöst

## Behobene Probleme

### 2025-04-19: SRT-Export erzeugt weiterhin nur reinen Text

- **Datum:** 2025-04-19
- **Betroffene Komponente:** SRT-Export
- **Fehlerbeschreibung:** Trotz Korrekturen im Backend (`module1_transcribe/__init__.py`), die explizit die Funktion `text_to_srt` zur Erzeugung standardkonformer SRT-Dateien aufrufen sollen, enthalten die exportierten `.srt`-Dateien weiterhin nur den reinen transkribierten Text ohne SRT-Formatierung (Nummern, Zeitstempel).
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Führe eine Transkription durch.
  3. Exportiere die Ergebnisse als SRT-Datei.
- **Erwartetes Verhalten:** Die SRT-Datei sollte korrekt formatiert sein.
- **Tatsächliches Verhalten:** Die SRT-Datei war nicht korrekt formatiert.
- **Lösungsansatz:** 
  - Implementierung der JSON-basierten Segment-Erzeugung mit `segments_to_srt` und CLI-Optionen zur Segmentsteuerung
- **Status:** Gelöst

### 2025-04-19: SRT-Segmente sind zu groß und nicht optimal lesbar

- **Datum:** 2025-04-19
- **Betroffene Komponente:** SRT-Segmente
- **Fehlerbeschreibung:** Die erzeugten SRT-Dateien haben zwar jetzt das korrekte Format mit Zeitstempeln, aber die Segmente sind zu groß (5 Sekunden) und die Textmenge pro Segment ist nicht optimal für die Lesbarkeit von Untertiteln.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Führe eine Transkription durch.
  3. Exportiere die Ergebnisse als SRT-Datei.
- **Erwartetes Verhalten:** Die SRT-Segmente sollten optimal lesbar sein.
- **Tatsächliches Verhalten:** Die SRT-Segmente waren nicht optimal lesbar.
- **Lösungsansatz:** 
  1. Verbesserung der `segments_to_srt`-Funktion mit intelligenteren Aufteilungsalgorithmen
  2. Hinzufügen von GUI-Steuerelementen für SRT-Parameter
  3. Implementierung von Text-Formatierung mit Zeilenbegrenzungen
  4. Einhaltung der Standards gemäß SRT-INFO.md
- **Status:** Gelöst

### 2025-04-11: Fehler mit '-metal' Parameter

- **Datum:** 2025-04-11
- **Betroffene Komponente:** '-metal' Parameter
- **Fehlerbeschreibung:** Die Whisper-CLI akzeptierte den Parameter `-metal` nicht, obwohl Whisper.cpp mit Metal-Unterstützung kompiliert wurde.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Versuche, den `-metal` Parameter zu verwenden.
- **Erwartetes Verhalten:** Der Parameter sollte korrekt funktionieren.
- **Tatsächliches Verhalten:** Der Parameter funktionierte nicht korrekt.
- **Lösungsansatz:** 
  - Entfernen des Parameters aus dem Code, da die Metal-Unterstützung automatisch erkannt wird, wenn sie vorhanden ist.
- **Status:** Gelöst

### 2025-04-20: Diverse `ImportError` beim Start nach Modulintegration

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Modulintegration, ImportError
- **Fehlerbeschreibung:** Nach der Integration der Modellverwaltungs-API und der `httpx`-Bibliothek trat beim Starten des Webservers (`python -m src.whisper_transcription_tool.main web`) eine Kette von `ImportError`-Fehlern auf.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Beobachte die Fehlermeldungen.
- **Erwartetes Verhalten:** Die Anwendung sollte korrekt funktionieren.
- **Tatsächliches Verhalten:** Die Anwendung funktionierte nicht korrekt.
- **Lösungsansatz:** 
  1. Die Importe für `WhisperModel` und `OutputFormat` in `web/__init__.py` und `core/model_manager.py` wurden korrigiert, um auf `core/models.py` zu verweisen.
  2. Der fehlerhafte Import der nicht existierenden Funktionen aus `core/utils.py` wurde aus `web/__init__.py` entfernt.
- **Status:** Gelöst

### 2025-04-20: Hilfestellung zur BlackHole-Installation und Konfiguration

- **Datum:** 2025-04-20
- **Betroffene Komponente:** BlackHole Audio-Routing
- **Fehlerbeschreibung:** Bei der Nutzung der BlackHole-Aufnahmefunktion kann es zu Problemen mit der Geräteerkennung oder dem Audio-Routing kommen.
- **Priorität:** Mittel
- **Reproduktionsschritte:** 
  1. Installation von BlackHole
  2. Verwendung der Aufnahmefunktion ohne vorherige Systemkonfiguration
- **Erwartetes Verhalten:** Nahtlose Erkennnung und Nutzung von BlackHole
- **Tatsächliches Verhalten:** Fehlende Erkennnung von BlackHole oder kein Ton in der Aufnahme
- **Lösungsansätze:** 
  1. **Neustart nach Installation:** Nach der Installation von BlackHole einen Neustart durchführen
  2. **Systemeinstellungen überprüfen:** Sicherstellen, dass BlackHole in den Systemeinstellungen unter 'Ton' als Ausgabegerät erscheint
  3. **Audio-MIDI-Setup:** Im Audio-MIDI-Setup (Dienstprogramme) ein Multi-Output-Gerät erstellen, das sowohl auf die normalen Lautsprecher als auch auf BlackHole ausgibt
  4. **Kommunikationsanwendungen:** In Teams/Discord/Zoom sicherstellen, dass die Eingangs-/Ausgabegeräte korrekt gesetzt sind
  5. **Berechtigungen:** Systemeinstellungen → Sicherheit → Mikrofonzugriff für die Anwendung erlauben
- **Status:** Dokumentiert

### 2025-04-20: `await` außerhalb von `async` Funktion im WebSocket Event Handler

- **Datum:** 2025-04-20
- **Betroffene Komponente:** WebSocket Event Handler, await
- **Fehlerbeschreibung:** Der Linter meldete einen Fehler (`await is only valid in async function`) in der Funktion `progress_event_handler` in `web/__init__.py`, nachdem `await websocket.send_text(...)` hinzugefügt wurde.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Starte die Anwendung.
  2. Beobachte die Fehlermeldung.
- **Erwartetes Verhalten:** Die Funktion sollte korrekt funktionieren.
- **Tatsächliches Verhalten:** Die Funktion funktionierte nicht korrekt.
- **Lösungsansatz:** 
  1. Die Funktion `progress_event_handler` wurde als `async def` deklariert.
- **Status:** Gelöst

### 2025-04-20: Abhängigkeitskonflikt nach BlackHole-Integration

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Paketabhängigkeiten, setup.py
- **Fehlerbeschreibung:** Nach der Integration der BlackHole-Aufnahmefunktion startete der Server nicht mehr und gab die Fehlermeldung `Web dependencies not installed. Install with pip install 'whisper_transcription_tool[web]'` aus.
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Installation von `sounddevice` über requirements.txt
  2. Versuch, den Webserver zu starten
- **Erwartetes Verhalten:** Server startet ohne Fehler
- **Tatsächliches Verhalten:** Fehler `Web dependencies not installed`
- **Lösungsansatz:** 
  1. Die neue `sounddevice`-Abhängigkeit wurde zu `extras_require` in den Kategorien `web` und `full` in der `setup.py` hinzugefügt
  2. Neuinstallation des Pakets mit `pip install -e ".[web]"` erforderlich
- **Ursachenanalyse:** Das Projekt verwendet ein modulares Abhängigkeitssystem mit optionalen Features. Neue Abhängigkeiten müssen sowohl in `requirements.txt` als auch in den entsprechenden `extras_require`-Abschnitten in `setup.py` eingetragen werden.
- **Status:** Gelöst
  2. Die `publish`-Funktion im Event-System (`core/events.py`) wurde angepasst, um `asyncio.iscoroutinefunction` zu prüfen und asynchrone Handler mittels `asyncio.create_task(handler(event))` im Hintergrund zu starten, ohne den synchronen `publish`-Aufruf zu blockieren.
- **Status:** Gelöst

### 2025-04-20: Probleme mit UTF-8 Kodierung in der Web-Oberfläche

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Web-Oberfläche, Templates
- **Fehlerbeschreibung:** Nach der Integration der BlackHole-Komponente werden UTF-8-Zeichen in der Weboberfläche falsch angezeigt (z.B. "Gerü00e4teauswahl" statt "Geräteauswahl")
- **Priorität:** Mittel
- **Reproduktionsschritte:** 
  1. Server starten
  2. Telefonaufnahmen-Tab öffnen und auf "Live-Aufnahme" wechseln
  3. Fehlerhafte Umlaute in der GUI beobachten
- **Erwartetes Verhalten:** Korrekte Anzeige von Umlauten und Sonderzeichen
- **Tatsächliches Verhalten:** Escapesequenzen werden anstelle der Umlaute angezeigt
- **Lösungsansatz:** 
  1. Manuelle Korrektur der falsch kodierten Umlaute in den Template-Dateien:
     - Korrektur in phone.html (14 Stellen)
     - Korrektur in extract.html (1 Stelle)
  2. Systematische Überprüfung aller Template-Dateien auf Kodierungsprobleme
- **Status:** Gelöst

### 2025-04-20: Keine Audiogeräte werden in der Geräteauswahl angezeigt

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Telefonaufnahme-Modul, Audio-Geräte-Erkennung
- **Fehlerbeschreibung:** Beim Öffnen der Telefonaufnahme-Funktion werden keine Audiogeräte in den Dropdown-Menüs angezeigt
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Server starten
  2. Telefonaufnahmen-Tab öffnen und auf "Live-Aufnahme" wechseln
  3. Die Dropdown-Menüs für Mikrofon und Ausgabe bleiben leer oder zeigen nur "Wird geladen..."
- **Erwartetes Verhalten:** Anzeige aller verfügbaren Audio-Ein- und Ausgabegeräte in den Dropdown-Menüs
- **Tatsächliches Verhalten:** Keine Geräte werden angezeigt, API-Endpunkt /api/phone/devices liefert keine Daten
- **Lösungsansatz:** 
  1. Server mit aktivierter virtueller Umgebung starten, um Zugriff auf das `sounddevice`-Modul zu gewährleisten
  2. Korrekte Startbefehle: `source venv/bin/activate && cd src && python -m whisper_transcription_tool.main web`
  3. Verifiziert, dass der API-Endpunkt `/api/phone/devices` jetzt korrekt alle Geräte zurückliefert
- **Status:** Gelöst

### 2025-04-20: Whisper-Modellfehler beim Laden der Tensoren

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Whisper-Modellinitialisierung, Modelldateien
- **Fehlerbeschreibung:** Beim Initialisieren des Whisper-Modells tritt ein kritischer Fehler auf: `whisper_model_load: ERROR not all tensors loaded from model file - expected 167, got 1`
- **Priorität:** Kritisch
- **Reproduktionsschritte:** 
  1. Server starten
  2. Transkription durchführen
  3. Fehlermeldung im Ergebnis beobachten
- **Erwartetes Verhalten:** Whisper-Modell wird korrekt geladen mit allen Tensoren
- **Tatsächliches Verhalten:** Fehlercode 3 von Whisper.cpp mit Meldung: `whisper_model_load: ERROR not all tensors loaded from model file - expected 167, got 1`
- **Lösungsansatz:** 
  1. Beschädigte Modelldatei "ggml-tiny.bin" identifiziert und entfernt
  2. Implementierung einer Integritätsprüfung nach dem Download in `model_manager.py`
  3. Automatisches Löschen von Dateien, die die Integritätsprüfung nicht bestehen
- **Status:** Gelöst

### 2025-04-20: Transkriptionsmodul funktioniert nicht mehr

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Hauptmodul zur Transkription
- **Fehlerbeschreibung:** Das Hauptmodul "Transkription" generiert keine Ausgabedateien mehr
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Server starten
  2. Transkription durchführen
  3. Beobachten, dass keine Ausgabedateien generiert werden
- **Erwartetes Verhalten:** Generierung und Speicherung von Transkriptionsdateien
- **Tatsächliches Verhalten:** Keine Ausgabedateien werden erzeugt
- **Lösungsansatz:** 
  1. Noch kein Lösungsansatz implementiert
- **Status:** Offen

### 2025-04-20: Fehler bei Audioaufnahme mit BlackHole

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Telefonaufnahme-Modul, Audio-Stream-Erstellung
- **Fehlerbeschreibung:** Trotz erkannter Audiogeräte und BlackHole kann die Aufnahme nicht gestartet werden
- **Priorität:** Hoch
- **Reproduktionsschritte:** 
  1. Server starten
  2. Telefonaufnahmen-Tab öffnen und auf "Live-Aufnahme" wechseln
  3. Mikrofon und BlackHole auswählen
  4. Auf "Aufnahme starten" klicken
- **Erwartetes Verhalten:** Aufnahme startet, Timer läuft und Buttons zum Pausieren/Stoppen werden aktiviert
- **Tatsächliches Verhalten:** Fehler "Error opening Stream: Invalid number of channels [PaErrorCode -9998]" im Log, Aufnahme kann nicht gestoppt oder pausiert werden
- **Lösungsansatz:** 
  1. Feste Kanalanzahl (2) durch dynamische Anpassung an Gerätefähigkeiten ersetzt
  2. Abfrage der tatsächlich unterstützten Kanalanzahl jedes Geräts
  3. Verwendung der niedrigeren Kanalanzahl für optimale Kompatibilität
  4. Verbesserte Fehlerbehandlung mit detailliertem Logging
- **Status:** Gelöst

### 2025-04-20: Doppelte Dateistruktur im Projekt führt zu Bearbeitungsfehlern

- **Datum:** 2025-04-20
- **Betroffene Komponente:** Projektstruktur, Modul-Organisation
- **Fehlerbeschreibung:** Gleiche Module existieren in zwei verschiedenen Verzeichnisstrukturen, was zu Verwirrung bei der Bearbeitung führt
- **Priorität:** Mittel
- **Reproduktionsschritte:** 
  1. Suche nach Dateien wie `recorder.py` im Projekt
  2. Beobachten, dass dieselbe Datei sowohl unter `/src/module3_phone/` als auch unter `/src/whisper_transcription_tool/module3_phone/` existiert
- **Erwartetes Verhalten:** Eine klare, einheitliche Verzeichnisstruktur ohne Duplikate
- **Tatsächliches Verhalten:** Zwei parallele Strukturen existieren:
  * `/src/module3_phone/` (veraltet, wird nicht verwendet)
  * `/src/whisper_transcription_tool/module3_phone/` (aktiv, wird vom Programm verwendet)
- **Lösungsansatz:** 
  1. Identifizierung der tatsächlich verwendeten Struktur (`/src/whisper_transcription_tool/`)
  2. Änderungen nur in den aktiven Dateien vornehmen
  3. Langfristig: Entfernung der duplizierten, nicht verwendeten Dateien
  4. Diesen Fehler in der Dokumentation festhalten, um zukünftige Verwirrung zu vermeiden
- **Status:** Identifiziert, Lösung implementiert
