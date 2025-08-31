Wichtige Informationen zu SRT-Dateien (SubRip Subtitle)
Was ist eine SRT-Datei?

SRT steht für SubRip Subtitle und ist das am weitesten verbreitete Untertitelformat für Videos auf Plattformen wie YouTube, Netflix, Vimeo und Amazon.

SRT-Dateien sind reine Textdateien mit der Endung .srt und enthalten keine eingebetteten Medien oder komplexe Formatierungen.

Struktur einer SRT-Datei

Eine SRT-Datei besteht aus wiederholten Blöcken mit folgendem Aufbau:

Nummerierung: Fortlaufende Nummer jeder Untertitelzeile.

Zeitstempel: Start- und Endzeitpunkt, wann der Untertitel angezeigt wird, im Format Stunden:Minuten:Sekunden,Millisekunden --> Stunden:Minuten:Sekunden,Millisekunden.

Untertiteltext: Der eigentliche Text, der angezeigt werden soll (eine oder mehrere Zeilen).

Leerzeile: Trennt die Untertitelblöcke voneinander.

Beispiel:

text
1
00:00:01,000 --> 00:00:04,000
Hallo, das ist ein Beispiel.

2
00:00:05,000 --> 00:00:08,000
Noch ein Untertiteltext.
Formatierungsoptionen

SRT unterstützt grundlegende Textformatierungen, die von HTML-Tags abgeleitet sind:

Fett: <b>Text</b> oder {b}Text{/b}

Kursiv: <i>Text</i> oder {i}Text{/i}

Unterstrichen: <u>Text</u> oder {u}Text{/u}

Farbe: <font color="#code">Text</font>

Positionierung (je nach Player): z. B. {\a3} für Zeilenposition

Die Unterstützung dieser Tags hängt vom verwendeten Mediaplayer ab. Nicht alle Player interpretieren Formatierungen oder Positionsangaben korrekt.

Standards und Kompatibilität

Es gibt keinen offiziellen Standard für SRT-Dateien; das Format hat sich durch breite Nutzung etabliert.

Die Kodierung ist meist UTF-8, aber nicht explizit vorgeschrieben. Bei Problemen mit Sonderzeichen sollte die Kodierung geprüft werden.

Die maximale Zeilenlänge liegt typischerweise bei 32 Zeichen, und pro Untertitelblock sollten nicht mehr als zwei Zeilen Text verwendet werden.

Die Kompatibilität und Darstellung von Formatierungen ist plattformabhängig; vor dem Einsatz sollte die SRT-Datei auf dem Ziel-Mediaplayer getestet werden.

Erstellung und Bearbeitung

SRT-Dateien können mit jedem Texteditor (z. B. Notepad, Wordpad, TextEdit) erstellt und bearbeitet werden.

Für größere Projekte oder komfortableres Arbeiten gibt es spezialisierte Software wie:

Aegisub

Premiere Pro

SubRip

YouTube Untertitel-Editor (bietet automatische Spracherkennung und Zeitsynchronisation)

Auch automatische Transkriptionsdienste können SRT-Dateien generieren.

Programmierung und Integration in Software

Um SRT-Dateien in einer eigenen Software zu verarbeiten, ist folgendes Vorgehen üblich:

Einlesen: Die Datei zeilenweise einlesen.

Parsen:

Nummerierung erkennen (Integer).

Zeitstempel extrahieren und in ein Zeitformat umwandeln.

Untertiteltext bis zur nächsten Leerzeile sammeln.

Verarbeiten: Die Untertitel mit den Zeitstempeln synchron zum Video anzeigen.

Exportieren: Beim Schreiben einer SRT-Datei die oben beschriebene Struktur einhalten.

Beispiel für einen einfachen Parser (Pseudocode):

python
with open('untertitel.srt', 'r', encoding='utf-8') as file:
    while not end_of_file:
        nummer = read_line()
        zeiten = read_line()  # z.B. "00:00:01,000 --> 00:00:04,000"
        text = []
        while (line := read_line()) != "":
            text.append(line)
        # Speichern oder weiterverarbeiten
Zusammenfassung
SRT ist ein einfaches, weit verbreitetes Untertitelformat mit klarer, textbasierter Struktur und minimalen Formatierungsmöglichkeiten.

Es gibt keinen offiziellen Standard, aber eine de-facto-Konvention für Aufbau und Kodierung.

Die Erstellung ist mit jedem Texteditor oder spezialisierten Tools möglich.

Für die Programmierung reicht das Parsen von Textdateien nach festen Regeln; Formatierungen und Sonderfunktionen hängen vom Ziel-Mediaplayer ab.

Tipp: Immer die fertige SRT-Datei mit dem Zielplayer testen, um Darstellungsprobleme zu vermeiden.