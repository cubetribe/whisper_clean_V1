-- WhisperStarter.applescript
-- Startet das Whisper Transkriptionstool im Terminal

tell application "Terminal"
    activate
    -- Öffne ein neues Terminal-Fenster
    do script ""
    
    -- Wechsle in das richtige Verzeichnis und führe das Skript aus
    do script "cd /Users/denniswestermann/Desktop/Coding\ Projekte/whisper_clean && chmod +x ./start_server.sh && ./start_server.sh" in front window
    
    -- Stelle sicher, dass das Terminal-Fenster aktiv bleibt
    activate
end tell
