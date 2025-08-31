# Backup-Strategie für das Whisper Transkriptionstool

## Übersicht

Dieses Dokument beschreibt die offizielle Backup-Strategie und den Release-Prozess für das Whisper Transkriptionstool. Es dient als Leitfaden, um konsistente Sicherungen zu erstellen, Versionen zu verwalten und einen reibungslosen Übergang zwischen Entwicklungsphasen zu gewährleisten.

## Versionierung

Das Projekt folgt einem semantischen Versionierungsschema (SemVer) in der Form `X.Y.Z`:

- **X** (Major): Inkompatible API-Änderungen, grundlegende Umstrukturierungen
- **Y** (Minor): Neue Funktionen bei Erhaltung der Rückwärtskompatibilität
- **Z** (Patch): Bug-Fixes und kleinere Verbesserungen

## Backup-Prozess

### Vollständiges Backup vor jedem Release

```bash
# 1. Aktuelle Version ermitteln (aus constants.py)
CURRENT_VERSION=$(grep "VERSION =" src/whisper_transcription_tool/core/constants.py | cut -d '"' -f 2)

# 2. Backup-Verzeichnis erstellen
BACKUP_DIR="Backups/whisper_v${CURRENT_VERSION}_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 3. Aktuellen Codestand kopieren (mit allen erforderlichen Ausschlüssen)
rsync -av \
  --exclude="venv/" \
  --exclude=".env/" \
  --exclude="env/" \
  --exclude="virtualenv/" \
  --exclude="__pycache__/" \
  --exclude="*.pyc" \
  --exclude=".DS_Store" \
  --exclude="Trance/" \
  --exclude="trance/" \
  --exclude="scripts/temp/" \
  --exclude="temp/" \
  --exclude="tmp/" \
  --exclude="*.tmp" \
  --exclude="Recordings/" \
  --exclude="recordings/" \
  --exclude="logs/" \
  --exclude="*.log" \
  . "$BACKUP_DIR/"

# 4. Metadaten zum Backup hinzufügen
echo "Backup-Datum: $(date)" > "$BACKUP_DIR/BACKUP_INFO.md"
echo "Version: $CURRENT_VERSION" >> "$BACKUP_DIR/BACKUP_INFO.md"
echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo 'Nicht in Git')" >> "$BACKUP_DIR/BACKUP_INFO.md"
```

### Inkrementelle Backups während der Entwicklung

Zusätzlich zu vollständigen Backups vor jedem Release sollten regelmäßige inkrementelle Backups kritischer Dateien durchgeführt werden:

```bash
# Kritische Konfigurationen und Datendateien sichern
BACKUP_INCR="Backups/incremental_$(date +%Y%m%d_%H%M)"
mkdir -p "$BACKUP_INCR"

# Hauptkonfigurationsdateien
cp src/whisper_transcription_tool/core/constants.py "$BACKUP_INCR/"
cp src/whisper_transcription_tool/core/config.py "$BACKUP_INCR/"

# Dokumentationsdateien
cp README.md CHANGELOG.md TODO.md PROBLEMS.md "$BACKUP_INCR/"
```

## Release-Prozess

Wenn ein neues Release erstellt werden soll, folgen Sie diesen Schritten:

1. **Vollständiges Backup erstellen** (siehe oben)

2. **Versionen aktualisieren**:
   ```bash
   # Haupt-Versionsnummer in constants.py aktualisieren
   sed -i '' "s/VERSION = \"[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\?\"/VERSION = \"NEUE_VERSION\"/g" src/whisper_transcription_tool/core/constants.py
   
   # GUI-Versionsnummer in base.html (falls vorhanden)
   sed -i '' 's/<span class="version">v[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\?<\/span>/<span class="version">vNEUE_VERSION<\/span>/' src/whisper_transcription_tool/web/templates/base.html
   ```

3. **Dokumentation aktualisieren**:
   * `CHANGELOG.md`: Release-Informationen und Liste der Änderungen
   * `TODO.md`: Erledigte Aufgaben abhaken, neue Aufgaben hinzufügen
   * `README.md`: Bei Bedarf aktualisieren

4. **Startdatei mit neuer Version erstellen**:
   ```bash
   # Kopie der Startdatei mit neuer Versionsnummer
   cp src/whisper_transcription_tool/main.py whisper_transcription_tool_vNEUE_VERSION.py
   ```

5. **Tests ausführen**:
   ```bash
   # Alle Tests ausführen
   cd tests && python -m unittest discover
   ```

6. **Release-ZIP erstellen** (für Distribution):
   ```bash
   # Release-Paket erstellen
   zip -r whisper_transcription_tool_vNEUE_VERSION.zip . -x "*venv*" "*.git*" "*__pycache__*" "*.pyc" "*.DS_Store" "Backups/*"
   ```

## Wiederherstellung

Um ein Backup wiederherzustellen, folgen Sie diesen Schritten:

```bash
# 1. In das Projektverzeichnis wechseln
cd /pfad/zum/whisper_transkriptionstool

# 2. Aktuelle Codebasis sichern (falls erforderlich)
mkdir -p Backups/pre_restore_$(date +%Y%m%d)
rsync -av --exclude="venv/" --exclude="__pycache__/" . Backups/pre_restore_$(date +%Y%m%d)/

# 3. Backup-Version auswählen und wiederherstellen
rsync -av --exclude="venv/" Backups/whisper_vX.Y.Z_DATUM/ .
```

## Best Practices

1. **Regelmäßige Backups**: Führen Sie vollständige Backups vor jeder größeren Änderung durch.

2. **Dokumentation pflegen**: Halten Sie die Dokumentationsdateien (CHANGELOG.md, TODO.md, etc.) stets aktuell.

3. **Kritische Ausschlüsse beachten**: Folgende Elemente dürfen NIEMALS in Backups enthalten sein:
   - Virtuelle Umgebungen (venv, .env, env, virtualenv)
   - Trance-Dateien und -Verzeichnisse
   - Temporäre Skripte und Dateien (tmp, temp, *.tmp)
   - Recordings und große Audiodateien
   - Cache-Verzeichnisse und -Dateien (__pycache__, .cache, *.pyc)
   - Log-Dateien (logs/, *.log) - diese sollten separat archiviert werden
   - Große Binärdateien und Modelle (ggf. in einem separaten Artefakt-Repository sichern)

4. **Konfiguration trennen**: Trennen Sie Anwendungscode von Benutzerkonfigurationen, damit diese bei Updates erhalten bleiben.

5. **Testlaufstrategie**: Führen Sie nach jeder Wiederherstellung einen einfachen Testlauf durch, um die Funktionsfähigkeit zu verifizieren.

6. **Speicherplatzmanagement**: Überwachen Sie den verfügbaren Speicherplatz regelmäßig und richten Sie eine automatische Bereinigung älterer Backups ein, um Platz zu sparen.

7. **Verschlüsselung**: Verschlüsseln Sie sensible Backups, insbesondere wenn diese externe Server oder Cloud-Speicher verwenden.

8. **Multi-Standort-Strategie**: Bewahren Sie Kopien kritischer Backups an unterschiedlichen physischen Standorten auf.

9. **Automatisierung**: Verwenden Sie CI/CD-Pipelines oder geplante Aufgaben, um den Backup-Prozess zu automatisieren.

10. **Backup-Rotation**: Implementieren Sie eine Rotationsstrategie (z.B. Großvater-Vater-Sohn-Prinzip) für langfristige Aufbewahrung.

11. **Backup-Verifizierung**: Automatisieren Sie Tests zur Überprüfung der Backup-Integrität.

12. **Dokumentation**: Dokumentieren Sie jeden Backup-Vorgang mit Datum, Version und verantwortlicher Person.

## Checkliste für jeden Release

- [ ] Vollständiges Backup erstellt
- [ ] Version in constants.py aktualisiert
- [ ] Version in base.html (GUI) aktualisiert
- [ ] CHANGELOG.md aktualisiert
- [ ] TODO.md aktualisiert 
- [ ] README.md (falls nötig) aktualisiert
- [ ] Startdatei mit neuer Versionsnummer erstellt
- [ ] Tests ausgeführt und bestanden
- [ ] Release-ZIP erstellt (falls für Distribution benötigt)
- [ ] Testlauf der neuen Version durchgeführt
