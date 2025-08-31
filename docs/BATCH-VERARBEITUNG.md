# Batch-Verarbeitung im Whisper Transkriptionstool

## Überblick

Die Batch-Verarbeitung ermöglicht es, mehrere Audiodateien in einem Durchlauf zu transkribieren, ohne jede Datei manuell einzeln hochladen zu müssen. Diese Funktion ist besonders nützlich für Benutzer, die regelmäßig größere Mengen an Audiomaterial verarbeiten müssen.

## Funktionsweise

### 1. Auswahl mehrerer Dateien

In der Weboberfläche können Sie nun mehrere Audiodateien gleichzeitig auswählen:

1. Klicken Sie auf "Audiodateien auswählen"
2. Halten Sie die Strg-Taste (Windows/Linux) oder Cmd-Taste (macOS) gedrückt, um mehrere Dateien auszuwählen
3. Alternativ können Sie auch eine Dateiauswahl durch Ziehen mit der Maus treffen
4. Die Anzahl der ausgewählten Dateien wird unter dem Auswahlfeld angezeigt

### 2. Gemeinsame Einstellungen

Alle ausgewählten Dateien werden mit denselben Einstellungen transkribiert:

- Gleiches Whisper-Modell
- Gleiche Spracheinstellung
- Gleiches Ausgabeformat
- Gleiches Ausgabeverzeichnis
- Bei SRT-Format: Gleiche SRT-Parameter (maximale Zeichenzahl, maximale Dauer)

### 3. Verarbeitungsprozess

Wenn Sie das Formular absenden, geschieht Folgendes:

1. Das System erkennt automatisch, dass mehrere Dateien ausgewählt wurden
2. Es wird eine Batch-Verarbeitung gestartet
3. Die Dateien werden nacheinander (sequentiell) verarbeitet
4. Für jede Datei wird ein separater API-Aufruf durchgeführt
5. Der Fortschritt wird in Echtzeit angezeigt

### 4. Ergebnisdarstellung

Nach Abschluss der Verarbeitung werden die Ergebnisse übersichtlich dargestellt:

- Eine Tabelle mit allen verarbeiteten Dateien
- Status jeder Datei (erfolgreich/fehlgeschlagen)
- Download-Buttons für jede erfolgreich transkribierte Datei
- Zusammenfassende Statistik (Anzahl erfolgreicher/fehlgeschlagener Transkriptionen)

## Technische Implementierung

### Frontend (JavaScript)

Die Batch-Verarbeitung wurde vollständig clientseitig implementiert, um den Server zu entlasten. Das bedeutet:

- Die Dateien werden nacheinander an den Server gesendet
- Der Client verwaltet den Gesamtprozess
- Der Server verarbeitet jede Anfrage einzeln und unabhängig

### Prozessfluss

1. Benutzer wählt mehrere Dateien aus und sendet das Formular ab
2. JavaScript erkennt die Mehrfachauswahl und startet die `processBatchFiles()`-Funktion
3. Die Funktion extrahiert die gemeinsamen Parameter aus dem Formular
4. Die erste Datei wird zusammen mit den Parametern per AJAX an den Server gesendet
5. Nach Erhalt der Antwort wird die nächste Datei gesendet
6. Die Ergebnisse werden in einer Tabelle gesammelt und angezeigt

### Fehlerbehandlung

Die Implementierung enthält umfassende Fehlerbehandlung:

- Jede Datei wird unabhängig verarbeitet
- Ein Fehler bei einer Datei stoppt nicht die gesamte Batch-Verarbeitung
- Fehlerdetails werden für jede fehlgeschlagene Datei angezeigt
- Die Verarbeitung wird selbst bei Netzwerkproblemen fortgesetzt

## Einschränkungen

- Da die Dateien sequentiell verarbeitet werden, kann die Verarbeitung vieler großer Dateien einige Zeit in Anspruch nehmen
- Alle Dateien müssen denselben Einstellungen entsprechen (kein individuelles Ausgabeformat pro Datei)
- Sehr große Dateien können zu Timeouts führen, abhängig von den Servereinstellungen

## Zukünftige Erweiterungen

Für zukünftige Versionen sind folgende Erweiterungen geplant:

- Parallelverarbeitung mehrerer Dateien für schnellere Resultate
- Individuelle Einstellungen pro Datei
- Speicherung und Wiederverwendung von Batch-Konfigurationen
- Drag-and-Drop-Unterstützung für Dateien
- Fortgesetzte Verarbeitung nach Browserneustart
