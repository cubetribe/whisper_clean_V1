#!/bin/bash

# Farbdefinitionen für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner anzeigen
echo -e "\n${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Whisper Transkriptionstool - Wiederherstellungstool${NC}"
echo -e "${BLUE}=========================================================${NC}\n"

# Backup-Quelle festlegen
BACKUP_SOURCE="/Users/denniswestermann/Desktop/Coding Projekte/whisper_clean/Backups/whisper_v0.8.0_20250514"
TARGET_DIR="/Users/denniswestermann/Desktop/Coding Projekte/whisper_clean"

# Prüfen, ob das Backup-Verzeichnis existiert
if [ ! -d "$BACKUP_SOURCE" ]; then
    echo -e "${RED}FEHLER: Backup-Verzeichnis nicht gefunden: $BACKUP_SOURCE${NC}"
    exit 1
fi

echo -e "${YELLOW}Quelle: $BACKUP_SOURCE${NC}"
echo -e "${YELLOW}Ziel: $TARGET_DIR${NC}\n"

# Fragen, ob wirklich wiederhergestellt werden soll
echo -e "${YELLOW}WARNUNG: Diese Aktion wird Dateien im Zielverzeichnis überschreiben!${NC}"
echo -e "${YELLOW}Möchten Sie wirklich fortfahren? (j/n): ${NC}"
read -r answer

if [[ $answer != "j" && $answer != "J" ]]; then
    echo -e "${RED}Wiederherstellung wurde abgebrochen.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Stoppe laufende Server...${NC}"
pkill -f "python.*whisper.*web" || true

# Zu erhaltende Verzeichnisse
echo -e "\n${YELLOW}Sichere wichtige Verzeichnisse...${NC}"

# Temporäres Verzeichnis für wichtige Daten
TEMP_DIR="/tmp/whisper_restore_temp"
mkdir -p "$TEMP_DIR"

# Sichere models-Verzeichnis (falls vorhanden)
if [ -d "$TARGET_DIR/models" ]; then
    echo -e "${GREEN}Sichere models-Verzeichnis...${NC}"
    cp -R "$TARGET_DIR/models" "$TEMP_DIR/"
fi

# Sichere transcriptions-Verzeichnis (falls vorhanden)
if [ -d "$TARGET_DIR/transcriptions" ]; then
    echo -e "${GREEN}Sichere transcriptions-Verzeichnis...${NC}"
    cp -R "$TARGET_DIR/transcriptions" "$TEMP_DIR/"
fi

# Sichere Konfigurationsdatei (falls vorhanden)
if [ -f "$HOME/.whisper_tool.json" ]; then
    echo -e "${GREEN}Sichere Konfigurationsdatei...${NC}"
    cp "$HOME/.whisper_tool.json" "$TEMP_DIR/"
fi

# Kopiere src-Verzeichnis (Programmcode)
echo -e "\n${YELLOW}Kopiere Programmcode aus Backup...${NC}"
rsync -av --exclude="__pycache__" "$BACKUP_SOURCE/src/" "$TARGET_DIR/src/"

# Kopiere Skripte und Dokumentation
echo -e "\n${YELLOW}Kopiere Skripte und Dokumentation...${NC}"
rsync -av "$BACKUP_SOURCE/docs/" "$TARGET_DIR/docs/"
cp "$BACKUP_SOURCE/"*.{sh,py,md} "$TARGET_DIR/" 2>/dev/null || true
cp "$BACKUP_SOURCE/Whisper Transkriptionstool"* "$TARGET_DIR/" 2>/dev/null || true

# Stelle wichtige Daten wieder her
echo -e "\n${YELLOW}Stelle wichtige Daten wieder her...${NC}"

# Stelle models-Verzeichnis wieder her (falls gesichert)
if [ -d "$TEMP_DIR/models" ]; then
    echo -e "${GREEN}Stelle models-Verzeichnis wieder her...${NC}"
    rsync -av "$TEMP_DIR/models/" "$TARGET_DIR/models/"
fi

# Stelle transcriptions-Verzeichnis wieder her (falls gesichert)
if [ -d "$TEMP_DIR/transcriptions" ]; then
    echo -e "${GREEN}Stelle transcriptions-Verzeichnis wieder her...${NC}"
    rsync -av "$TEMP_DIR/transcriptions/" "$TARGET_DIR/transcriptions/"
fi

# Stelle Konfigurationsdatei wieder her (falls gesichert)
if [ -f "$TEMP_DIR/.whisper_tool.json" ]; then
    echo -e "${GREEN}Stelle Konfigurationsdatei wieder her...${NC}"
    cp "$TEMP_DIR/.whisper_tool.json" "$HOME/"
fi

# Bereinige temporäres Verzeichnis
rm -rf "$TEMP_DIR"

# Setze Ausführungsrechte für Skripte
echo -e "\n${YELLOW}Setze Ausführungsrechte für Skripte...${NC}"
chmod +x "$TARGET_DIR/"*.sh 2>/dev/null || true
chmod +x "$TARGET_DIR/QuickLauncher.command" 2>/dev/null || true

echo -e "\n${GREEN}Wiederherstellung abgeschlossen!${NC}"
echo -e "${YELLOW}Möchten Sie den Server jetzt starten? (j/n): ${NC}"
read -r start_server

if [[ $start_server == "j" || $start_server == "J" ]]; then
    echo -e "\n${YELLOW}Starte Server...${NC}"
    cd "$TARGET_DIR" && ./start_server.sh &
else
    echo -e "\n${YELLOW}Server wurde nicht gestartet. Sie können ihn später mit './start_server.sh' starten.${NC}"
fi

echo -e "\n${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Wiederherstellung erfolgreich abgeschlossen!${NC}"
echo -e "${BLUE}=========================================================${NC}\n"
