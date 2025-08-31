#!/bin/bash

# Whisper Transcription Tool Installer
# Version 0.5.0

echo "=================================================="
echo "        Whisper Transcription Tool Installer     "
echo "=================================================="
echo "Dieses Skript installiert das Whisper Transcription Tool"
echo "und alle notwendigen Abhängigkeiten."
echo ""

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Fehler: Python 3 ist nicht installiert."
    echo "Bitte installieren Sie Python 3.11 oder höher."
    exit 1
fi

# Prüfe Python-Version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
python_version_major=$(echo $python_version | cut -d. -f1)
python_version_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_version_major" -lt 3 ] || ([ "$python_version_major" -eq 3 ] && [ "$python_version_minor" -lt 11 ]); then
    echo "Fehler: Python 3.11 oder höher wird benötigt."
    echo "Aktuell installierte Version: $python_version"
    exit 1
fi

echo "Python-Version: $python_version [OK]"

# Prüfe, ob FFmpeg installiert ist
if ! command -v ffmpeg &> /dev/null; then
    echo "Hinweis: FFmpeg wurde nicht gefunden."
    echo "FFmpeg wird für die Verarbeitung von Videodateien benötigt."
    echo "FFmpeg wird automatisch installiert..."
    
    # Betriebssystem erkennen und entsprechende Installation durchführen
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS - Installation über Homebrew
        if ! command -v brew &> /dev/null; then
            echo "Homebrew wird benötigt. Installation..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        echo "Installiere FFmpeg über Homebrew..."
        brew install ffmpeg
    elif [[ "$(uname)" == "Linux" ]]; then
        # Linux - verschiedene Paketmanager prüfen
        if command -v apt-get &> /dev/null; then
            echo "Installiere FFmpeg über apt..."
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            echo "Installiere FFmpeg über dnf..."
            sudo dnf install -y ffmpeg
        elif command -v pacman &> /dev/null; then
            echo "Installiere FFmpeg über pacman..."
            sudo pacman -S --noconfirm ffmpeg
        else
            echo "Warnung: Konnte keinen bekannten Paketmanager finden."
            echo "Bitte installieren Sie FFmpeg manuell: https://ffmpeg.org/download.html"
        fi
    else
        echo "Warnung: Ihr Betriebssystem wird nicht automatisch unterstützt."
        echo "Bitte installieren Sie FFmpeg manuell: https://ffmpeg.org/download.html"
    fi
    
    # Prüfe, ob die Installation erfolgreich war
    if command -v ffmpeg &> /dev/null; then
        echo "FFmpeg wurde erfolgreich installiert."
    else
        echo "Warnung: FFmpeg konnte nicht automatisch installiert werden."
        echo "Einige Funktionen zur Videoverarbeitung werden nicht verfügbar sein."
        echo "Bitte installieren Sie FFmpeg manuell: https://ffmpeg.org/download.html"
    fi
else
    echo "FFmpeg ist bereits installiert [OK]"
    ffmpeg_version=$(ffmpeg -version | head -n 1)
    echo "$ffmpeg_version"
fi

# Prüfe, ob Whisper.cpp installiert ist
whisper_path=""

# Überprüfe gängige Pfade für das Whisper.cpp-Binary
paths_to_check=("./whisper" "/usr/local/bin/whisper" "/usr/bin/whisper" "$HOME/whisper.cpp/main" "$HOME/whisper.cpp/whisper")

for path in "${paths_to_check[@]}"; do
    if [ -x "$path" ]; then
        whisper_path="$path"
        break
    fi
done

if [ -z "$whisper_path" ]; then
    echo "Hinweis: Whisper.cpp wurde nicht gefunden."
    echo "Whisper.cpp wird automatisch installiert..."

    # Erstelle ein temporäres Verzeichnis für die Installation
    temp_dir=$(mktemp -d)
    cd "$temp_dir" || exit

    echo "Klone das Whisper.cpp-Repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp || exit

    echo "Kompiliere Whisper.cpp..."
    make

    echo "Lade das Medium-Modell herunter..."
    ./models/download-ggml-model.sh medium

    echo "Kopiere das whisper-Binary nach $HOME/whisper.cpp/"
    mkdir -p "$HOME/whisper.cpp"
    cp main "$HOME/whisper.cpp/whisper"

    whisper_path="$HOME/whisper.cpp/whisper"

    echo "Whisper.cpp wurde erfolgreich installiert."
else
    echo "Whisper.cpp gefunden: $whisper_path [OK]"
fi

# Erstelle virtuelle Umgebung
echo "Erstelle virtuelle Python-Umgebung..."

if [ -d "venv" ]; then
    echo "Virtuelle Umgebung existiert bereits."
    echo "Möchten Sie die vorhandene Umgebung aktualisieren? (j/n)"
    read -r update_venv
    
    if [[ $update_venv != "j" ]] && [[ $update_venv != "J" ]]; then
        echo "Installation abgebrochen."
        exit 0
    fi
else
    python3 -m venv venv
fi

# Aktiviere virtuelle Umgebung
source venv/bin/activate

# Aktualisiere pip
echo "Aktualisiere pip..."
python -m pip install --upgrade pip

# Installiere Abhängigkeiten
echo "Installiere Abhängigkeiten..."
python -m pip install -e .

# Erstelle Konfigurationsdatei
echo "Konfiguriere das Tool..."

config_dir="$HOME/.whisper_transcription_tool"
config_file="$config_dir/config.yaml"

if [ ! -d "$config_dir" ]; then
    mkdir -p "$config_dir"
fi

if [ ! -f "$config_file" ]; then
    echo "Erstelle Konfigurationsdatei: $config_file"
    
    cat > "$config_file" << EOF
whisper:
  binary_path: "$whisper_path"
  model_path: "$HOME/whisper_models"
  threads: 4

output:
  default_directory: "$HOME/transcriptions"
  temp_directory: "/tmp/whisper_transcription_tool"

logging:
  level: "INFO"
  file: "$config_dir/whisper_tool.log"
EOF

else
    echo "Konfigurationsdatei existiert bereits: $config_file"
fi

# Erstelle Ausgabe- und Temp-Verzeichnisse
mkdir -p "$HOME/transcriptions"
mkdir -p "/tmp/whisper_transcription_tool"

echo ""
echo "Installation abgeschlossen!"
echo ""
echo "Sie können das Whisper Transcription Tool jetzt mit WhisperStarter.applescript starten:"
echo ""
echo "  $(pwd)/WhisperStarter.applescript"
echo ""

script_path="$(pwd)/WhisperStarter.applescript"

# Prüfe, ob die Datei existiert und ausführbar ist
if [ -f "$script_path" ]; then
    # Mache das Skript ausführbar
    chmod +x "$script_path"
    
    echo "Doppelklicken Sie einfach auf WhisperStarter.applescript, um das Tool zu starten."
else
    echo "HINWEIS: WhisperStarter.applescript konnte nicht gefunden werden."
    echo "Sie können das Tool dennoch manuell starten mit:"
    echo "1. Aktivieren Sie die virtuelle Umgebung: source venv/bin/activate"
    echo "2. Starten Sie die Web-Oberfläche: python -m src.whisper_transcription_tool.main web"
    echo "3. Öffnen Sie Ihren Browser und navigieren Sie zu: http://localhost:8000"
fi

echo ""
echo "================================================"
