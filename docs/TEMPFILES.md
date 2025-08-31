# Verwaltung der temporären Dateien

## Übersicht

Die Whisper Transkriptions-App erzeugt verschiedene temporäre Dateien während des Transkriptionsprozesses. Diese Dateien können über Zeit erheblichen Speicherplatz belegen, insbesondere bei der Verarbeitung von Videos und hochauflösenden Audiodateien.

## Aktueller Speicherbedarf

Das temporäre Verzeichnis (`transcriptions/temp/`) enthält aktuell **4,4 GB** an Daten, hauptsächlich:

- Kopien der ursprünglichen Mediendateien (Videos, Audios)
- Extrahierte Audiodateien aus Videos
- Temporäre Verarbeitungsdateien

## Speichermanagement

Das Tool speichert temporäre Dateien aus mehreren Gründen:

1. **Schnellzugriff** bei erneuter Transkription der gleichen Datei
2. **Fehleranalyse** bei Problemen mit der Transkription
3. **Wiederverwendbarkeit** von extrahierten Audiodaten

Dadurch vermeiden wir wiederholte Extraktionen und Konvertierungen der gleichen Datei und verbessern die Leistung bei wiederholten Transkriptionen.

## Bereinigungsoptionen

### 1. Manuelle Bereinigung mit dem Clean-Up-Tool

Mit dem neu erstellten `clean_temp.py` Skript können Sie temporäre Mediendateien einfach bereinigen:

```bash
# Alle temporären Mediendateien bereinigen (interaktiv)  
./clean_temp.py

# Nur Dateien löschen, die älter als 7 Tage sind
./clean_temp.py --age 7

# Automatische Bereinigung ohne Bestätigung
./clean_temp.py --force
```

### 2. Automatische Bereinigung

Sie können einen regelmäßigen Bereinigungsjob einrichten, um alte temporäre Dateien automatisch zu entfernen:

```bash
# Beispiel für einen Cron-Job (täglich um 2 Uhr nachts)
0 2 * * * cd /Pfad/zum/whisper_clean && ./clean_temp.py --age 5 --force >> cleanup.log 2>&1
```

## Richtlinien für den Umgang mit temporären Dateien

1. **Regelmäßige Bereinigung**: Führen Sie eine Bereinigung alle 1-2 Wochen durch, oder wenn der freie Speicherplatz knapp wird.

2. **Bei Bedarf**: Nach umfangreichen Stapelverarbeitungen großer Videodateien sollten Sie das Clean-Up-Tool ausführen.

3. **Behalten Sie wichtige Daten**: Das Tool löscht nur Mediendateien (Videos, Audios), nicht aber Transkriptionsergebnisse oder Konfigurationsdateien.

4. **Bevor Sie ein Backup erstellen**: Bereinigen Sie zuerst temporäre Dateien, um die Backup-Größe zu minimieren.

## Speicheroptimierung für zukünftige Versionen

Für Version 0.8.1 sind folgende Verbesserungen geplant:

- [ ] Automatische Bereinigung nach erfolgreicher Transkription (optional)
- [ ] Konfigurierbare Speichergrenze für den temp-Ordner
- [ ] Web-UI zur Speicherverwaltung mit Statistiken und manueller Bereinigung
- [ ] Priorisierte Bereinigung von Dateien nach Typ (zuerst Videos, dann Audios)
