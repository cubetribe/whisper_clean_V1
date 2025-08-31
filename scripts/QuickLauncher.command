#!/bin/bash

# Farbdefinitionen fu00fcr visuelle Hinweise
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner anzeigen
echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}        Whisper Transkriptionstool Launcher${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Ermittle den Pfad zum Skript selbst, unabhu00e4ngig vom Ausfu00fchrungsort
SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${GREEN}Script Path: $SCRIPT_PATH${NC}"

# Pru00fcfe, ob dynamic_path_finder.py existiert
if [ ! -f "$SCRIPT_PATH/dynamic_path_finder.py" ]; then
    echo -e "${RED}Fehler: dynamic_path_finder.py nicht gefunden in $SCRIPT_PATH${NC}"
    echo -e "${YELLOW}Pru00fcfe alternative Pfade...${NC}"
    
    # Pru00fcfe einige mu00f6gliche Orte
    if [ -f "$SCRIPT_PATH/Contents/MacOS/dynamic_path_finder.py" ]; then
        SCRIPT_PATH="$SCRIPT_PATH/Contents/MacOS"
        echo -e "${GREEN}Datei gefunden in: $SCRIPT_PATH${NC}"
    else
        echo -e "${RED}Konnte dynamic_path_finder.py nicht finden. Bitte stellen Sie sicher, dass die Datei existiert.${NC}"
        read -n 1 -s -r -p "Dru00fccken Sie eine Taste, um zu beenden..."
        exit 1
    fi
fi

# Fu00fchre dynamic_path_finder.py aus
echo -e "${YELLOW}Fu00fchre dynamic_path_finder.py aus...${NC}"
python3 "$SCRIPT_PATH/dynamic_path_finder.py"
if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler beim Ausfu00fchren von dynamic_path_finder.py${NC}"
    read -n 1 -s -r -p "Dru00fccken Sie eine Taste, um zu beenden..."
    exit 1
fi

# Starte start_server.sh
echo -e "${GREEN}Starte Whisper Transkriptionstool...${NC}"

# Setze Ausfu00fchrungsrechte
chmod +x "$SCRIPT_PATH/start_server.sh"

# Setze die DYLD_LIBRARY_PATH Umgebungsvariable für dynamische Bibliotheken
echo -e "${YELLOW}Konfiguriere Bibliothekspfade...${NC}"

export DYLD_LIBRARY_PATH="$SCRIPT_PATH/deps/whisper.cpp/build/src:$SCRIPT_PATH/deps/whisper.cpp/build/ggml/src:$SCRIPT_PATH/deps/whisper.cpp/build/ggml/src/ggml-blas:$SCRIPT_PATH/deps/whisper.cpp/build/ggml/src/ggml-metal:$DYLD_LIBRARY_PATH"

echo -e "${GREEN}Bibliothekspfade konfiguriert:${NC}"
echo -e "${BLUE}$DYLD_LIBRARY_PATH${NC}"

# Führe start_server.sh aus mit den neuen Umgebungsvariablen
"$SCRIPT_PATH/start_server.sh"
