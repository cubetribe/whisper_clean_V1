# Universelle Audioformat-Unterstützung und Verarbeitung

## Übersicht

Das Whisper Transkriptionstool unterstützt ab Version 0.8.3 nicht nur eine umfangreiche Palette an Audio- und Videoformaten, sondern bietet auch fortschrittliche Funktionen wie Audio-Chunking für lange Dateien und GPU-beschleunigte Verarbeitung für alle Formate. Durch diese intelligente Audio-Verarbeitungspipeline können praktisch alle gängigen Medienformate effizient verarbeitet werden.

## Unterstützte Formate

### Audioformate

- WAV (Waveform Audio)
- MP3 (MPEG Audio Layer III)
- OGG/OGA (Ogg Vorbis Audio)
- FLAC (Free Lossless Audio Codec)
- AAC (Advanced Audio Coding)
- M4A (MPEG-4 Audio)
- WMA (Windows Media Audio)
- OPUS (Opus Interactive Audio Codec) - ideal für WhatsApp-Sprachnachrichten
- AMR (Adaptive Multi-Rate Audio)
- AIFF (Audio Interchange File Format)
- AU (Sun/NeXT Audio)
- 3GP Audio
- RA/RM (RealAudio)
- VOC (Creative Voice)
- DSS (Digital Speech Standard)
- MSV (Sony Memory Stick Voice)
- DVF (Sony Digital Voice)
- MPC (Musepack)
- SPX (Speex)
- GSM (Global System for Mobile Audio)

### Videoformate

- MP4 (MPEG-4 Part 14)
- AVI (Audio Video Interleave)
- MOV (QuickTime Movie)
- MKV (Matroska Video)
- WEBM (Web Media)
- FLV (Flash Video)
- WMV (Windows Media Video)
- MPG/MPEG (Moving Picture Experts Group)
- M4V (MPEG-4 Video)
- 3GP/3G2 (3GPP Multimedia)
- MTS/M2TS (MPEG Transport Stream)
- TS (Transport Stream)
- DIVX (DivX Video)
- ASF (Advanced Systems Format)
- OGV (Ogg Video)
- VOB (DVD Video Object)
- RMVB (RealMedia Variable Bitrate)

## Arbeitsweise der Konvertierung

### Automatisierter Prozess

1. **Formaterkennung**: Das System erkennt automatisch das Format der hochgeladenen Datei
2. **Medientyp-Bestimmung**: Unterscheidung zwischen Audio- und Videodateien
3. **Konvertierungsprozess**:
   - Bei Videodateien: Extraktion des Audiostreams und Konvertierung zu MP3
   - Bei Audiodateien: Direkte Konvertierung ins optimierte Format
4. **Audiooptimierung**:
   - Konvertierung zu MP3 mit 128 kbps Bitrate (guter Kompromiss aus Qualität und Dateigröße)
   - Sample-Rate-Anpassung auf 16 kHz (optimal für Whisper)
   - Konvertierung zu Mono-Audio (1 Kanal)
   - Lautstärkenormalisierung für verbesserte Transkriptionsqualität
5. **Transkription**: Verarbeitung des optimierten Audioformats
6. **Automatische Bereinigung**: Löschung temporärer Mediendateien nach erfolgreicher Transkription

### Vorteile

- **Zeitersparnis**: Keine manuelle Vorkonvertierung mehr nötig
- **Platzersparnis**: Optimierte Audiodateien sind kompakter
- **Verbessertes Timing**: Präzisere Zeitstempel durch konsistente Audioformate
- **Höhere Erfolgsquote**: Robustere Verarbeitung durch standardisiertes Format
- **Schnellere Transkription**: Optimierte Dateien werden schneller verarbeitet
- **Skalierbarkeit**: Auch sehr große Audiodateien werden effizient verarbeitet
- **GPU-Beschleunigung**: Konsistent schnelle Verarbeitung durch optimierte GPU-Nutzung

## Fortschrittliche Audio-Verarbeitung (ab v0.8.3)

### Audio-Chunking für lange Dateien

Lange Audiodateien (über 30 Minuten) werden automatisch in kleinere, überlappende Segmente aufgeteilt, um folgende Vorteile zu bieten:

- **Zuverlässigkeit**: Vermeidung von Abstürzen oder Hängern bei sehr langen Dateien
- **Effizienz**: Optimale Ressourcennutzung durch angepasste Segmentgrößen (30 Minuten)
- **Präzision**: 5-Sekunden-Überlappung zwischen Segmenten für nahtlose Übergänge
- **Robustheit**: Teilweise Fehler beeinträchtigen nicht die gesamte Transkription
- **Organisation**: Automatisches Zusammenführen der Segmente mit korrekten Zeitstempeln

Die Implementierung funktioniert vollständig im Hintergrund und erfordert keine Benutzerinteraktion.

### Metal-GPU-Beschleunigung

Ab Version 0.8.3 unterstützt das Tool eine konsistente GPU-Beschleunigung für alle Formate:

- **Format-Agnostik**: Sowohl Video- als auch alle Audiodateien nutzen die GPU
- **Optimierte Batch-Größe**: Einstellung von 1024 MB für Metal-Batch-Verarbeitung
- **Apple Silicon-Optimierung**: Volle Ausnutzung der M-Serie-GPUs (M1/M2/M3/M4)
- **Überwachung**: Automatisches Monitoring von Prozess-Timeouts und GPU-Ressourcen
- **Fallback-Mechanismus**: Elegantes Zurückfallen auf CPU bei Problemen

## Technische Details

Die Konvertierung nutzt FFmpeg mit folgenden Parametern für optimale Ergebnisse:

```bash
ffmpeg -i EINGABEDATEI -c:a libmp3lame -b:a 128k -ar 16000 -ac 1 -y -vn -sn -dn \
       -map_metadata -1 -af "loudnorm=I=-16:TP=-1:LRA=11" AUSGABEDATEI.mp3
```

Parameter-Erklärung:
- `-c:a libmp3lame`: MP3-Encoder verwenden
- `-b:a 128k`: Bitrate auf 128 kbps setzen
- `-ar 16000`: Sample-Rate auf 16 kHz setzen (ideal für Spracherkennung)
- `-ac 1`: Mono-Audio verwenden (1 Kanal)
- `-y`: Ausgabedateien ohne Nachfrage überschreiben
- `-vn`: Keine Videoausgabe
- `-sn`: Keine Untertitelausgabe
- `-dn`: Keine Datenausgabe
- `-map_metadata -1`: Keine Metadaten übernehmen
- `-af "loudnorm=I=-16:TP=-1:LRA=11"`: Lautstärke normalisieren für verbesserte Erkennbarkeit

## Konfigurationsmöglichkeiten

In zukünftigen Versionen werden weitere Konfigurationsmöglichkeiten hinzugefügt, um die Transkriptionsqualität und Verarbeitungsgeschwindigkeit noch feiner steuern zu können.
