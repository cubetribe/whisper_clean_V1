#!/bin/bash

# ======================================================
# Whisper Transkriptionstool - Automatisches Backup-Skript
# ======================================================
#
# Dieses Skript erstellt automatisch Backups mit den korrekten
# Ausschlussregeln gemu00e4u00df den Vorgaben in docs/BACKUP.md.
#
# Verwendung:
#   ./create_backup.sh         # Vollstu00e4ndiges Release-Backup
#   ./create_backup.sh dev     # Inkrementelles Entwicklungs-Backup
#
# ======================================================

# Farbdefinitionen fu00fcr bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner anzeigen
echo -e "\n${BLUE}=========================================================${NC}"
echo -e "${BLUE}        Whisper Transkriptionstool - Backup-Tool${NC}"
echo -e "${BLUE}=========================================================${NC}\n"

# Aktuelle Version aus constants.py ermitteln
echo -e "${YELLOW}Aktuelle Version wird ermittelt...${NC}"
CURRENT_VERSION=$(grep "VERSION =" src/whisper_transcription_tool/core/constants.py | cut -d '"' -f 2)

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}FEHLER: Version konnte nicht ermittelt werden!${NC}"
    echo -e "${RED}Bitte stellen Sie sicher, dass die Datei 'src/whisper_transcription_tool/core/constants.py' existiert.${NC}"
    exit 1
fi

echo -e "${GREEN}Erkannte Version: ${CURRENT_VERSION}${NC}\n"

# Backup-Typ bestimmen (Release oder Dev)
BACKUP_TYPE="release"
if [ "$1" = "dev" ]; then
    BACKUP_TYPE="dev"
    BACKUP_DIR="Backups/whisper_dev_$(date +%Y%m%d_%H%M)"
    echo -e "${YELLOW}Inkrementelles Entwicklungs-Backup wird erstellt...${NC}"
else
    BACKUP_DIR="Backups/whisper_v${CURRENT_VERSION}_$(date +%Y%m%d)"
    echo -e "${YELLOW}Vollstu00e4ndiges Release-Backup wird erstellt...${NC}"
fi

# Sicherstellen, dass das Backup-Verzeichnis existiert
mkdir -p "$BACKUP_DIR"

# Gru00f6u00dfe des Projekts vor dem Backup ermitteln (ohne ausgeschlossene Dateien)
PROJECT_SIZE=$(du -hs --exclude="venv" --exclude="models" --exclude="whisper_models" --exclude="Backups" . | cut -f1)

echo -e "${BLUE}Backup-Verzeichnis: ${BACKUP_DIR}${NC}"
echo -e "${BLUE}Projektgru00f6u00dfe (ohne ausgeschlossene Dateien): ${PROJECT_SIZE}${NC}\n"

# Bestu00e4tigung einholen
echo -e "${YELLOW}Mu00f6chten Sie das Backup jetzt durchfu00fchren? (j/n): ${NC}"
read -r confirm
if [[ ! "$confirm" =~ ^[jJyY]$ ]]; then
    echo -e "${RED}Backup wurde abgebrochen.${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Backup wird erstellt...${NC}"

# Aktuellen Codestand kopieren mit ALLEN Ausschlussregeln
rsync -av \
  --exclude="Backups/" \
  --exclude="venv/" \
  --exclude=".env/" \
  --exclude="env/" \
  --exclude="virtualenv/" \
  --exclude="__pycache__/" \
  --exclude="*.pyc" \
  --exclude=".DS_Store" \
  --exclude="models/" \
  --exclude="whisper_models/" \
  --exclude="temp/" \
  --exclude="tmp/" \
  --exclude="transcriptions/temp/" \
  --exclude="*.wav" \
  --exclude="*.mp3" \
  --exclude="*.mp4" \
  --exclude="*.ogg" \
  --exclude="*.flac" \
  --exclude="*.log" \
  --exclude="recordings/" \
  --exclude="Recordings/" \
  . "$BACKUP_DIR/"

# Pru00fcfen, ob rsync erfolgreich war
if [ $? -ne 0 ]; then
    echo -e "\n${RED}FEHLER: Backup konnte nicht erstellt werden!${NC}"
    exit 1
fi

# Metadaten zum Backup hinzufu00fcgen
echo "Backup-Datum: $(date)" > "$BACKUP_DIR/BACKUP_INFO.md"
echo "Version: $CURRENT_VERSION" >> "$BACKUP_DIR/BACKUP_INFO.md"

# Gru00f6u00dfe des Backups ermitteln
BACKUP_SIZE=$(du -hs "$BACKUP_DIR" | cut -f1)

echo -e "\n${GREEN}Backup-Verzeichnis wurde erfolgreich erstellt!${NC}"
echo -e "${GREEN}Backup-Größe: ${BACKUP_SIZE}${NC}"
echo -e "${GREEN}Speicherort: ${BACKUP_DIR}${NC}"

# ZIP-Archiv erstellen mit Fortschrittsanzeige
echo -e "\n${YELLOW}Erstelle ZIP-Archiv für zusätzliche Sicherheit...${NC}"
ZIP_FILE="${BACKUP_DIR}.zip"

if [ -f "$ZIP_FILE" ]; then
    echo -e "${YELLOW}ZIP-Datei existiert bereits und wird ersetzt.${NC}"
    rm "$ZIP_FILE"
fi

# ZIP-Archiv erstellen
zip -r "$ZIP_FILE" "$BACKUP_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}FEHLER: ZIP-Archiv konnte nicht erstellt werden!${NC}"
else
    # ZIP-Datei auf Integrität prüfen
    echo -e "${YELLOW}\nPrüfe ZIP-Integrität...${NC}"
    zip -T "$ZIP_FILE"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}WARNUNG: ZIP-Integritätsprüfung fehlgeschlagen!${NC}"
    else
        # Prüfe die Dateianzahl im Backup und in der ZIP
        BACKUP_FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)
        ZIP_FILE_COUNT=$(unzip -l "$ZIP_FILE" | tail -n 1 | awk '{print $2}')
        ZIP_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
        
        echo -e "${GREEN}ZIP-Archiv wurde erfolgreich erstellt und verifiziert!${NC}"
        echo -e "${GREEN}ZIP-Größe: ${ZIP_SIZE}${NC}"
        echo -e "${GREEN}ZIP-Speicherort: ${ZIP_FILE}${NC}"
        echo -e "${GREEN}Dateien im Backup: ${BACKUP_FILE_COUNT}${NC}"
        echo -e "${GREEN}Dateien in ZIP: ${ZIP_FILE_COUNT}${NC}"
        
        if [ "$BACKUP_FILE_COUNT" -ne "$ZIP_FILE_COUNT" ]; then
            echo -e "${RED}WARNUNG: Anzahl der Dateien im Backup und in der ZIP stimmen nicht überein!${NC}"
        else
            echo -e "${GREEN}Anzahl der Dateien im Backup und in der ZIP stimmen überein.${NC}"
        fi
    fi
fi

# Verify-Anweisung ausgeben
echo -e "${YELLOW}Wichtig: Pru00fcfen Sie das Backup auf Vollstu00e4ndigkeit${NC}"
echo -e "${YELLOW}  ls -la ${BACKUP_DIR}${NC}\n"

# Bei Release-Backup an die Checkliste erinnern
if [ "$BACKUP_TYPE" = "release" ]; then
    echo -e "${BLUE}Bitte die Release-Checkliste in docs/BACKUP.md durchgehen:${NC}"
    echo -e "${BLUE}  - Version in base.html aktualisiert?${NC}"
    echo -e "${BLUE}  - CHANGELOG.md aktualisiert?${NC}"
    echo -e "${BLUE}  - TODO.md aktualisiert?${NC}"
    echo -e "${BLUE}  - README.md aktualisiert?${NC}\n"
fi

echo -e "${GREEN}Backup-Vorgang abgeschlossen.${NC}\n"
