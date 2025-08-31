#!/bin/bash

# Farbdefinitionen für visuelle Hinweise
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Terminal-Titel setzen
echo -ne "\033]0;Whisper Transcription Tool\007"

# Banner anzeigen
clear
echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}        🎙️  Whisper Transcription Tool v0.9.4 🎙️${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo

# Ermittle den Pfad zum Script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}✓ Projektverzeichnis: $PROJECT_DIR${NC}"

# Wechsle zum Projektverzeichnis
cd "$PROJECT_DIR"

# Prüfe, ob start_server.sh existiert
if [ ! -f "$SCRIPT_DIR/start_server.sh" ]; then
    echo -e "${RED}✗ Fehler: start_server.sh nicht gefunden!${NC}"
    echo -e "${YELLOW}Bitte stellen Sie sicher, dass alle Dateien vorhanden sind.${NC}"
    echo
    echo "Drücken Sie eine beliebige Taste zum Beenden..."
    read -n 1
    exit 1
fi

# Setze Ausführungsrechte
chmod +x "$SCRIPT_DIR/start_server.sh"

# Starte den Server
echo -e "${YELLOW}⏳ Starte Whisper Transcription Tool...${NC}"
echo

# Führe start_server.sh aus
"$SCRIPT_DIR/start_server.sh"

# Wenn das Script beendet wird
echo
echo -e "${YELLOW}Server wurde beendet.${NC}"
echo "Drücken Sie eine beliebige Taste, um das Fenster zu schließen..."
read -n 1