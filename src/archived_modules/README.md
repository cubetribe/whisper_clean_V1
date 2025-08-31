# Archivierte Module

## Übersicht

Dieses Verzeichnis enthält archivierte Module und Dateien, die aus der aktiven Projektstruktur entfernt wurden, aber für Referenzzwecke aufbewahrt werden.

## Hintergrund

Während der Entwicklung des Whisper Transcription Tools wurde die Projektstruktur reorganisiert. Dabei wurden einige Module von ihrer ursprünglichen Position unter `/src/` in eine strukturiertere Paketorganisation unter `/src/whisper_transcription_tool/` verschoben.

Anstatt die ursprünglichen Dateien zu löschen, wurden sie in dieses Archivverzeichnis verschoben, um bei Bedarf auf den ursprünglichen Code zurückgreifen zu können.

## Inhalt

Dieses Verzeichnis enthält:

### Modulverzeichnisse mit Inhalt:
- **/module3_phone**: Module für die Telefon-Aufnahmefunktionalität in ihrer ursprünglichen Struktur
  - `__init__.py`: Modul-Initialisierung (427 Bytes)
  - `cli.py`: Kommandozeilen-Interface (7239 Bytes)
  - `models.py`: Datenmodelle für Telefonaufnahmen (3578 Bytes)
  - `recorder.py`: Audio-Aufnahme-Implementierung (17684 Bytes)

### Leere Modulverzeichnisse (zur Vollständigkeit):
- **/module1_transcribe**: Leeres Verzeichnis für Transkriptionsmodul
- **/module2_extract**: Leeres Verzeichnis für Extraktionsmodul
- **/module4_chatbot**: Leeres Verzeichnis für Chatbot-Modul
- **/core**: Leeres Verzeichnis für Kernfunktionalität

Die Analyse ergab, dass bei der Projektreorganisation nur das `module3_phone`-Verzeichnis tatsächlich duplizierte Inhalte enthält, während die anderen Modulverzeichnisse zwar angelegt, aber nie mit Dateien gefüllt wurden.

## Zeitpunkt der Archivierung

Die Archivierung wurde am 20. April 2025 durchgeführt, während der Behebung von Problemen mit der Audiogeräte-Erkennung und Audiokanal-Konfiguration in Version 0.5.1.

## Wichtiger Hinweis

Die in diesem Verzeichnis enthaltenen Dateien sollten **nicht mehr verwendet oder importiert** werden. Sie dienen ausschließlich als Referenz oder für Notfälle, falls in der aktiven Struktur Fehler auftreten.

Für die aktive Entwicklung verwenden Sie bitte ausschließlich die Module in der Hauptstruktur unter:
```
/src/whisper_transcription_tool/
```

## Verantwortlicher für die Archivierung

Diese Archivierung wurde vom Cascade AI-Assistenten im Auftrag von Dennis Westermann durchgeführt.
