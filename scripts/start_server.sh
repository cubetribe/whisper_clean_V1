#!/bin/bash

# Farbdefinitionen
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner anzeigen
echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}        Whisper Transkriptionstool Starter${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Aktuelles Verzeichnis feststellen (wo das Skript liegt)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Gehe zum Hauptverzeichnis (eine Ebene höher)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Setze die DYLD_LIBRARY_PATH Umgebungsvariable für dynamische Bibliotheken
echo -e "${YELLOW}Konfiguriere Bibliothekspfade...${NC}"

# Stelle sicher, dass wir die dyn. Bibliotheken im neuen Pfad finden können
export DYLD_LIBRARY_PATH="$PROJECT_DIR/deps/whisper.cpp/build/src:$PROJECT_DIR/deps/whisper.cpp/build/ggml/src:$PROJECT_DIR/deps/whisper.cpp/build/ggml/src/ggml-blas:$PROJECT_DIR/deps/whisper.cpp/build/ggml/src/ggml-metal:$DYLD_LIBRARY_PATH"

# Workaround entfernt - nicht mehr benötigt da lokale Pfade verwendet werden

# Funktion, um bestehende Whisper-Server zu beenden
close_running_servers() {
    echo -e "${YELLOW}Überprüfe auf bereits laufende Whisper-Server...${NC}"
    # Suche nach laufenden Python-Prozessen, die den Whisper-Server ausführen
    RUNNING_SERVERS=$(ps aux | grep "[p]ython -m src.whisper_transcription_tool.main web" | awk '{print $2}')
    
    if [ -n "$RUNNING_SERVERS" ]; then
        echo -e "${RED}Gefundene laufende Server-Instanzen:${NC}"
        # Zeige Informationen zu den laufenden Servern an
        for PID in $RUNNING_SERVERS; do
            # Extrahiere den Port
            SERVER_PORT=$(ps -p $PID -o args | grep -o "--port [0-9]*" | cut -d' ' -f2)
            echo -e "${YELLOW}  • Server auf Port $SERVER_PORT (PID: $PID)${NC}"
        done
        
        echo -e "${YELLOW}Möchtest du alle laufenden Server beenden? (j/n)${NC}"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Jj]$ ]]; then
            for PID in $RUNNING_SERVERS; do
                kill $PID 2>/dev/null
                echo -e "${GREEN}Server mit PID $PID beendet.${NC}"
            done
        else
            echo -e "${YELLOW}Bestehende Server werden weiter ausgeführt.${NC}"
        fi
    else
        echo -e "${GREEN}Keine laufenden Whisper-Server gefunden.${NC}"
    fi
}

# Funktion zur Prüfung, ob ein Port frei ist
check_port() {
    local port=$1
    # Prüfe, ob der Port bereits in Benutzung ist (unter macOS)
    if lsof -i :$port > /dev/null 2>&1; then
        return 1  # Port ist belegt
    else
        return 0  # Port ist frei
    fi
}

# Funktion zum Finden eines freien Ports
find_free_port() {
    local start_port=$DEFAULT_PORT
    local end_port=$((start_port + 100))
    local port
    
    for ((port=start_port; port<=end_port; port++)); do
        if ! lsof -i :$port >/dev/null 2>&1; then
            SELECTED_PORT=$port
            echo -e "${GREEN}Port $port ist frei und wurde ausgewählt.${NC}"
            return 0
        fi
    done
    
    echo -e "${RED}Kein freier Port im Bereich $start_port-$end_port gefunden.${NC}"
    return 1
}

# Bestehende Server schließen
close_running_servers

# Standardport
DEFAULT_PORT=8090
SELECTED_PORT=$DEFAULT_PORT

# Überprüfen, ob die virtuelle Umgebung existiert
echo -e "${YELLOW}Überprüfe virtuelle Umgebung...${NC}"
# Prüfe zuerst auf venv_new, dann auf venv
if [ -d "venv_new" ]; then
    VENV_DIR="venv_new"
    echo -e "${GREEN}Virtuelle Umgebung 'venv_new' gefunden.${NC}"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
    echo -e "${GREEN}Virtuelle Umgebung 'venv' gefunden.${NC}"
else
    echo -e "${RED}Keine virtuelle Umgebung gefunden.${NC}"
    echo -e "${YELLOW}Erstelle neue virtuelle Umgebung 'venv_new'...${NC}"
    python3 -m venv venv_new
    if [ $? -ne 0 ]; then
        echo -e "${RED}Fehler beim Erstellen der virtuellen Umgebung.${NC}"
        echo "Drücke eine beliebige Taste, um fortzufahren..."
        read -n 1
        exit 1
    fi
    VENV_DIR="venv_new"
    echo -e "${GREEN}Virtuelle Umgebung erstellt.${NC}"
fi

# Virtuelle Umgebung aktivieren
source "$VENV_DIR/bin/activate"

# Überprüfen, ob alle Pakete installiert sind
echo -e "${YELLOW}Überprüfe Abhängigkeiten...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}requirements.txt nicht gefunden.${NC}"
    echo "Drücke eine beliebige Taste, um fortzufahren..."
    read -n 1
    exit 1
fi

# Installiere fehlende Pakete
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler beim Installieren der Abhängigkeiten.${NC}"
    echo "Drücke eine beliebige Taste, um fortzufahren..."
    read -n 1
    exit 1
fi

# Überprüfen, ob Whisper-Konfigurationsdatei existiert
echo -e "${YELLOW}Überprüfe Whisper-Konfigurationsdatei...${NC}"
if [ ! -f "$HOME/.whisper_tool.json" ]; then
    echo -e "${RED}Whisper-Konfigurationsdatei nicht gefunden.${NC}"
    echo -e "${YELLOW}Möchtest du eine Standard-Konfigurationsdatei erstellen? (j/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        # Standard-Konfiguration erstellen
        cat > "$HOME/.whisper_tool.json" << EOL
{
    "whisper": {
        "binary_path": "$PROJECT_DIR/deps/whisper.cpp/build/bin/whisper-cli",
        "model_path": "$PROJECT_DIR/models",
        "threads": 4
    },
    "output": {
        "default_directory": "$PROJECT_DIR/transcriptions",
        "temp_directory": "$PROJECT_DIR/transcriptions/temp"
    },
    "ffmpeg": {
        "binary_path": "/usr/local/bin/ffmpeg"
    }
}
EOL
        mkdir -p "$PROJECT_DIR/models"
        mkdir -p "$PROJECT_DIR/transcriptions/temp"
        echo -e "${GREEN}Standard-Konfigurationsdatei erstellt.${NC}"
    else
        echo -e "${RED}Ohne Konfigurationsdatei kann das Tool nicht gestartet werden.${NC}"
        echo "Drücke eine beliebige Taste, um fortzufahren..."
        read -n 1
        exit 1
    fi
else
    echo -e "${GREEN}Whisper-Konfigurationsdatei gefunden.${NC}"
fi

# Abfrage für Debug-Modus
echo -e "${YELLOW}Möchtest du den Server im Debug-Modus starten? (j/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    DEBUG="WHISPER_LOG_LEVEL=DEBUG"
    echo -e "${GREEN}Debug-Modus aktiviert.${NC}"
else
    DEBUG=""
    echo -e "${GREEN}Normaler Modus aktiviert.${NC}"
fi

# Port auswählen
if ! check_port $SELECTED_PORT; then
    echo -e "${RED}Der Port $SELECTED_PORT ist bereits belegt!${NC}"
    find_free_port
    if [ $? -ne 0 ]; then
        echo -e "${RED}Kein freier Port gefunden. Programm wird beendet.${NC}"
        exit 1
    fi
fi

# Server starten
echo -e "${GREEN}Starte Server auf Port $SELECTED_PORT...${NC}"
echo -e "${YELLOW}Drücke STRG+C, um den Server zu beenden.${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Funktion zum Öffnen des Browsers
open_browser() {
    # Warte kurz, bis der Server gestartet ist
    sleep 2
    
    # Öffne den Browser mit der entsprechenden URL
    echo -e "${GREEN}Öffne Browser mit URL: http://localhost:$SELECTED_PORT${NC}"
    
    # Je nach Betriebssystem den entsprechenden Befehl ausführen
    # Da wir auf macOS sind, nutzen wir den 'open' Befehl
    open "http://localhost:$SELECTED_PORT"
}

# Starte Browser im Hintergrund
open_browser &

# Server mit den entsprechenden Optionen starten
if [[ -n "$DEBUG" ]]; then
    env $DEBUG python -m src.whisper_transcription_tool.main web --port $SELECTED_PORT
else
    python -m src.whisper_transcription_tool.main web --port $SELECTED_PORT
fi

# Wenn wir hierher kommen, wurde der Server beendet
echo -e "\n${YELLOW}Server wurde beendet.${NC}"
echo "Drücke eine beliebige Taste, um das Fenster zu schließen..."
read -n 1
