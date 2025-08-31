#!/bin/bash

# Ermittle den eigenen Pfad, unabhängig vom Ausführungsort
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Starte Terminal und führe dort den dynamischen Pfadfinder und das Whisper-Tool aus
osascript -e 'tell application "Terminal"' \
  -e 'activate' \
  -e 'do script ""' \
  -e "do script \"cd '$SCRIPT_DIR' && python3 ./dynamic_path_finder.py && chmod +x ./start_server.sh && ./start_server.sh\" in front window" \
  -e 'activate' \
  -e 'end tell'
