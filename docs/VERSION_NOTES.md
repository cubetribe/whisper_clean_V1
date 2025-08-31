# Whisper Transkriptionstool - Versionshinweise

## Versionsempfehlungen

### Version v0.8.0 (14. Mai 2025)

Diese Version wird für folgende Anwendungsfälle besonders empfohlen:

- **Batch-Verarbeitung großer Dateimengen**: Version v0.8.0 ermöglicht eine zuverlässige, fehlerfreie Stapelverarbeitung mehrerer Dateien, was in späteren Versionen (v0.8.2 - v0.8.8) Probleme verursachen kann.
- **Korrekte SRT-Dateigenerierung**: Alle Transkriptionsdateien werden korrekt und vollständig generiert, ohne dass unterschiedliche Videodateien die gleiche Transkription erhalten.

### Version v0.8.8 (22. Mai 2025)

Diese Version hat folgende Vorteile:

- **Verbesserte Benutzeroberfläche**: Moderneres UI mit besserer Statusanzeige für einzelne Transkriptionen
- **Optimierte Speicherverwaltung**: Verbesserter Umgang mit Arbeitsspeicher und Festplattenspeicher

Aber auch folgende bekannte Probleme:

- **Probleme mit Stapelverarbeitung**: Bei der Transkription mehrerer Dateien werden Mediendateien vorzeitig gelöscht
- **Identische Transkriptionen**: Manchmal werden für unterschiedliche Videodateien identische Transkriptionen ausgegeben

## Versionshistorie und Besonderheiten

### Wichtige Hinweise zu bestimmten Versionen

#### Version v0.8.0 (14. Mai 2025)

- **Empfohlene Produktionsversion** für Batch-Verarbeitung und zuverlässige Transkriptionen
- Stabile Transkription von Video- und Audiodateien
- Zuverlässige Stapelverarbeitung auch großer Dateimengen
- Alle SRT-Dateien werden korrekt generiert

#### Version v0.8.2 - v0.8.8 (15. Mai - 22. Mai 2025)

- Einführung neuer Features und UI-Verbesserungen
- Leider auch Einführung von Problemen bei der Stapelverarbeitung
- Problem mit wiederverwendeten Transkriptionsdateien bei unterschiedlichen Videos

## Empfehlungen für spezifische Anwendungsfälle

1. **Für Massentranskription mehrerer Dateien**: Verwenden Sie Version v0.8.0
2. **Für einzelne Transkriptionen mit verbesserter UI**: Verwenden Sie Version v0.8.8

## Wie führe ich ein Downgrade/Upgrade durch?

Verwenden Sie das Wiederherstellungsskript, um zwischen verschiedenen Versionen zu wechseln:

```bash
# Erstellen Sie einen symbolischen Link zum gewünschten Backup-Verzeichnis
ln -sf /Users/denniswestermann/Library/CloudStorage/GoogleDrive-cubetribe@googlemail.com/Meine\ Ablage/aiEX\ Software\ Dev/Transriber\ App\ -\ Mac\ -\ BEAT/whisper_clean/Backups/whisper_v0.8.0_20250514/restore_backup.sh .

# Führen Sie das Wiederherstellungsskript aus
./restore_backup.sh
```

## Wartungs- und Entwicklungshinweise

Bei zukünftigen Entwicklungen sollte besonders auf folgende Aspekte geachtet werden:

1. **Stapelverarbeitung**: Sicherstellen, dass temporäre Dateien nicht vorzeitig gelöscht werden
2. **Sprachcode-Handling**: Korrekte Umwandlung von "deutsch" zu "de" für die Whisper-API
3. **Temporäre Dateien**: Verbesserte Verwaltung der temporären Ausgabedateien (output.srt, output.txt)

---

*Letzte Aktualisierung: 22. Mai 2025*
