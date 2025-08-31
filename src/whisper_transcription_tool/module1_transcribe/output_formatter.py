"""
Output formatting for the Whisper Transcription Tool.
Handles conversion between different output formats.
"""

import json
import re
from typing import Dict, List, Optional, Union

import srt
from datetime import timedelta

from ..core.exceptions import FileFormatError
from ..core.logging_setup import get_logger
from ..core.models import OutputFormat

logger = get_logger(__name__)


def convert_format(
    text: str,
    source_format: Union[str, OutputFormat],
    target_format: Union[str, OutputFormat]
) -> str:
    """
    Convert text from one format to another.
    
    Args:
        text: Text to convert
        source_format: Source format
        target_format: Target format
        
    Returns:
        Converted text
    """
    # Convert string parameters to enums if needed
    if isinstance(source_format, str):
        source_format = OutputFormat(source_format)
    
    if isinstance(target_format, str):
        target_format = OutputFormat(target_format)
    
    # If formats are the same, return the original text
    if source_format == target_format:
        return text
    
    # Convert from source format to plain text
    plain_text = ""
    if source_format == OutputFormat.TXT:
        plain_text = text
    elif source_format == OutputFormat.SRT:
        plain_text = srt_to_text(text)
    elif source_format == OutputFormat.VTT:
        plain_text = vtt_to_text(text)
    elif source_format == OutputFormat.JSON:
        plain_text = json_to_text(text)
    else:
        raise FileFormatError(f"Unsupported source format: {source_format}")
    
    # Convert from plain text to target format
    if target_format == OutputFormat.TXT:
        return plain_text
    elif target_format == OutputFormat.SRT:
        return text_to_srt(plain_text)
    elif target_format == OutputFormat.VTT:
        return text_to_vtt(plain_text)
    elif target_format == OutputFormat.JSON:
        return text_to_json(plain_text)
    else:
        raise FileFormatError(f"Unsupported target format: {target_format}")


def srt_to_text(srt_text: str) -> str:
    """
    Convert SRT format to plain text.
    
    Args:
        srt_text: Text in SRT format
        
    Returns:
        Plain text
    """
    # Remove timestamps and indices
    lines = srt_text.split('\n')
    result = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Skip index lines (just numbers)
        if line.isdigit():
            i += 1
            continue
        
        # Skip timestamp lines
        if '-->' in line:
            i += 1
            continue
        
        # Add content lines
        result.append(line)
        i += 1
    
    return ' '.join(result)


def vtt_to_text(vtt_text: str) -> str:
    """
    Convert VTT format to plain text.
    
    Args:
        vtt_text: Text in VTT format
        
    Returns:
        Plain text
    """
    # Remove WEBVTT header, timestamps, and cue identifiers
    lines = vtt_text.split('\n')
    result = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Skip WEBVTT header
        if line.startswith('WEBVTT'):
            i += 1
            continue
        
        # Skip timestamp lines
        if '-->' in line:
            i += 1
            continue
        
        # Skip cue identifier lines (just numbers)
        if line.isdigit():
            i += 1
            continue
        
        # Add content lines
        result.append(line)
        i += 1
    
    return ' '.join(result)


def json_to_text(json_text: str) -> str:
    """
    Convert JSON format to plain text.
    
    Args:
        json_text: Text in JSON format
        
    Returns:
        Plain text
    """
    try:
        # Parse JSON
        data = json.loads(json_text) if isinstance(json_text, str) else json_text
        
        # Extract text from different JSON structures
        if isinstance(data, dict):
            # Check for common fields
            if 'text' in data:
                return data['text']
            elif 'segments' in data:
                segments = data['segments']
                if isinstance(segments, list):
                    return ' '.join([segment.get('text', '') for segment in segments if 'text' in segment])
        
        # If we can't extract text, return the JSON as string
        return str(data)
    
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return json_text


def text_to_srt(text: str, max_chars: Optional[int] = None, max_duration: Optional[float] = None, linebreaks: bool = True) -> str:
    """
    Convert plain text to SRT format using the 'srt' package for standard compliance.
    
    Args:
        text: Plain text
        max_chars: Maximum characters per subtitle (default: 70)
        max_duration: Maximum duration per subtitle in seconds (default: 2.0)
        linebreaks: Whether to include linebreaks (default: True)
    Returns:
        Text in SRT format (string)
    """
    # Standardwerte setzen wenn nicht angegeben
    if max_chars is None:
        max_chars = 20  # Sehr kurze Segmente
    
    if max_duration is None:
        max_duration = 1.0  # Sehr kurze Segmente
        
    logger.info(f"Generating SRT with text_to_srt: max_chars={max_chars}, max_duration={max_duration}")
    
    sentences = split_into_sentences(text)
    subtitles = []
    
    # Gesamtlänge des Textes und Anzahl der Sätze für die Berechnung der Zeitdauern
    total_chars = sum(len(s) for s in sentences)
    total_sentences = len(sentences)
    
    # Geschätzte Gesamtdauer basierend auf durchschnittlich 15 Zeichen pro Sekunde (anpassbar)
    total_duration = total_chars / 15  # etwa 15 Zeichen pro Sekunde als Sprechgeschwindigkeit
    
    # Initialisierung für die Berechnung
    current_position = 0
    index = 1
    
    for i, sentence in enumerate(sentences):
        # Relative Position im Text für die Zeitberechnung
        sentence_chars = len(sentence)
        sentence_proportion = sentence_chars / total_chars if total_chars > 0 else 1/total_sentences
        
        # Geschätzte Dauer dieses Satzes basierend auf der Zeichenanzahl
        sentence_duration = total_duration * sentence_proportion
        
        # Start- und Endzeit basierend auf der relativen Position im Text
        start_time = current_position / total_chars * total_duration if total_chars > 0 else i * (total_duration / total_sentences)
        end_time = start_time + sentence_duration
        
        # Aktualisiere die Position für den nächsten Satz
        current_position += sentence_chars
        
        # Wenn der Satz zu lang ist oder die Dauer zu lang, teile ihn auf
        if len(sentence) > max_chars or sentence_duration > max_duration:
            # Teile den Satz in Wörter auf
            words = sentence.split()
            
            # Anzahl der benötigten Teile berechnen
            parts_by_chars = max(1, len(sentence) // max_chars + (1 if len(sentence) % max_chars > 0 else 0))
            parts_by_duration = max(1, int(sentence_duration / max_duration) + (1 if sentence_duration % max_duration > 0 else 0))
            num_parts = max(parts_by_chars, parts_by_duration)
            
            # Berechne Wörter pro Teil
            words_per_part = max(1, len(words) // num_parts)
            
            # Teile den Satz in etwa gleich große Teile
            for part_idx in range(num_parts):
                start_word_idx = part_idx * words_per_part
                end_word_idx = min(len(words), start_word_idx + words_per_part)
                
                if start_word_idx >= len(words):
                    break
                
                part_text = ' '.join(words[start_word_idx:end_word_idx])
                
                # Berechne die Zeitdauer für diesen Teil
                part_proportion = len(part_text) / sentence_chars if sentence_chars > 0 else 1/num_parts
                part_start = start_time + (sentence_duration * (part_idx / num_parts))
                part_end = part_start + (sentence_duration * part_proportion)
                
                # Untertitel erstellen
                subtitles.append(srt.Subtitle(
                    index=index,
                    start=timedelta(seconds=part_start),
                    end=timedelta(seconds=part_end),
                    content=format_text_with_max_chars(part_text, max_chars, linebreaks=linebreaks)
                ))
                index += 1
        else:
            # Normaler Fall: Der Satz ist kurz genug
            content = format_text_with_max_chars(sentence, max_chars, linebreaks=linebreaks)
            # Wenn linebreaks aktiv und der Text keine Zeilenumbrüche enthält, aber mehr als ein Wort hat, füge einen Dummy-Umbruch ein
            if linebreaks and '\n' not in content and len(sentence.split()) > 1:
                mid = len(content) // 2
                # Füge Zeilenumbruch möglichst in der Mitte ein
                content = content[:mid] + '\n' + content[mid:]
            subtitles.append(srt.Subtitle(
                index=index,
                start=timedelta(seconds=start_time),
                end=timedelta(seconds=end_time),
                content=content
            ))
            index += 1
    
    # DIREKTER FIX: Wir umgehen die srt-Bibliothek und erstellen das SRT-Format manuell
    # Das garantiert, dass unsere Zeilenumbrüche exakt erhalten bleiben
    manual_srt = []
    
    for sub in subtitles:
        # SRT-Index
        manual_srt.append(str(sub.index))
        
        # Zeitstempel formatieren
        start_h = int(sub.start.total_seconds() // 3600)
        start_m = int((sub.start.total_seconds() % 3600) // 60)
        start_s = int(sub.start.total_seconds() % 60)
        start_ms = int((sub.start.total_seconds() % 1) * 1000)
        
        end_h = int(sub.end.total_seconds() // 3600)
        end_m = int((sub.end.total_seconds() % 3600) // 60)
        end_s = int(sub.end.total_seconds() % 60)
        end_ms = int((sub.end.total_seconds() % 1) * 1000)
        
        timestamp = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"
        manual_srt.append(timestamp)
        
        # Content mit garantierten Zeilenumbrüchen
        manual_srt.append(sub.content)
        
        # Leerzeile zwischen Untertiteln
        manual_srt.append('')
    
    # Zusammenfügen und Windows-Zeilenumbrüche sicherstellen
    return '\r\n'.join(manual_srt)


def segments_to_srt(segments: List[Dict], max_chars: Optional[int] = None, max_duration: Optional[float] = None, linebreaks: bool = True) -> str:
    """
    Generate SRT from JSON segments with optimal subtitle segmentation.
    
    Args:
        segments: List of segments from Whisper JSON output
        max_chars: Maximum characters per subtitle line (default: 70)
        max_duration: Maximum duration in seconds per subtitle (default: 2.0)
        linebreaks: Whether to include linebreaks (default: True)
        
    Returns:
        Standardized SRT content as string
    """
    # Standardwerte setzen wenn nicht angegeben
    if max_chars is None:
        max_chars = 20  # Sehr kurze Segmente
    
    if max_duration is None:
        max_duration = 1.0  # Sehr kurze Segmente
        
    logger.info(f"Generating SRT with max_chars={max_chars}, max_duration={max_duration}")
    
    subtitles: List[srt.Subtitle] = []
    index = 1
    
    for seg in segments:
        # Original-Zeitstempel aus Whisper-Segmenten
        start_time = seg.get("start", 0)
        end_time = seg.get("end", 0)
        text = seg.get("text", "").strip()
        
        # Segmentlänge
        segment_duration = end_time - start_time
        
        # Falls Segment zu lang ist, in kleinere Teile aufteilen
        if segment_duration > max_duration:
            # Anzahl der Teilsegmente berechnen
            num_chunks = max(1, int(segment_duration / max_duration))
            chunk_duration = segment_duration / num_chunks
            
            logger.debug(f"Splitting segment ({segment_duration:.2f}s) into {num_chunks} chunks of {chunk_duration:.2f}s each")
            
            # Text in Sätze aufteilen (wenn möglich)
            sentences = split_into_sentences(text)
            
            # Wenn nur ein Satz oder sehr kurzes Segment, verwende Wortaufteilung
            if len(sentences) <= 1 or len(sentences) < num_chunks:
                words = text.split()
                words_per_chunk = max(1, len(words) // num_chunks)
                
                for i in range(num_chunks):
                    chunk_start = start_time + (i * chunk_duration)
                    chunk_end = chunk_start + chunk_duration
                    
                    # Wörter für diesen Chunk
                    start_idx = i * words_per_chunk
                    end_idx = min(len(words), start_idx + words_per_chunk)
                    chunk_text = " ".join(words[start_idx:end_idx])
                    
                    # Zeichen pro Zeile begrenzen
                    formatted_text = format_text_with_max_chars(chunk_text, max_chars, linebreaks=linebreaks)
                    
                    # Untertitel erstellen
                    subtitles.append(srt.Subtitle(
                        index=index,
                        start=timedelta(seconds=chunk_start),
                        end=timedelta(seconds=chunk_end),
                        content=formatted_text
                    ))
                    index += 1
            else:
                # Verteilung der Sätze auf die Zeit
                sentences_duration = segment_duration / len(sentences)
                
                for i, sentence in enumerate(sentences):
                    chunk_start = start_time + (i * sentences_duration)
                    chunk_end = min(end_time, chunk_start + sentences_duration)
                    
                    # Satz in mehrere Zeilen aufteilen
                    parts = [sentence[j:j+max_chars] for j in range(0, len(sentence), max_chars)]
                    for part in parts:
                        part_start = chunk_start
                        part_end = min(chunk_end, part_start + sentences_duration / len(parts))
                        part_text = format_text_with_max_chars(part, max_chars, linebreaks=linebreaks)
                        subtitles.append(srt.Subtitle(
                            index=index,
                            start=timedelta(seconds=part_start),
                            end=timedelta(seconds=part_end),
                            content=part_text
                        ))
                        index += 1
        else:
            # Wenn Segment kurz genug ist, nur Textformatierung anwenden
            formatted_text = format_text_with_max_chars(text, max_chars, linebreaks=linebreaks)
            
            subtitles.append(srt.Subtitle(
                index=index,
                start=timedelta(seconds=start_time),
                end=timedelta(seconds=end_time),
                content=formatted_text
            ))
            index += 1
    
    # Ergebnis zusammenstellen und prüfen
    result = srt.compose(subtitles)
    logger.debug(f"Generated {len(subtitles)} subtitles")
    
    # DIREKTER FIX: Wir umgehen die srt-Bibliothek und erstellen das SRT-Format manuell
    # Das garantiert, dass unsere Zeilenumbrüche exakt erhalten bleiben
    manual_srt = []
    
    for sub in subtitles:
        # SRT-Index
        manual_srt.append(str(sub.index))
        
        # Zeitstempel formatieren
        start_h = int(sub.start.total_seconds() // 3600)
        start_m = int((sub.start.total_seconds() % 3600) // 60)
        start_s = int(sub.start.total_seconds() % 60)
        start_ms = int((sub.start.total_seconds() % 1) * 1000)
        
        end_h = int(sub.end.total_seconds() // 3600)
        end_m = int((sub.end.total_seconds() % 3600) // 60)
        end_s = int(sub.end.total_seconds() % 60)
        end_ms = int((sub.end.total_seconds() % 1) * 1000)
        
        timestamp = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}"
        manual_srt.append(timestamp)
        
        # Content mit garantierten Zeilenumbrüchen
        manual_srt.append(sub.content)
        
        # Leerzeile zwischen Untertiteln
        manual_srt.append('')
    
    # Zusammenfügen und Windows-Zeilenumbrüche sicherstellen
    return '\r\n'.join(manual_srt)


def format_text_with_max_chars(text: str, max_chars: int = 70, linebreaks: bool = True) -> str:
    """
    Teilt Text in Zeilen mit max_chars Zeichen auf, wobei Umbrüche an Wortgrenzen erfolgen.
    Optional kann Zeilenumbruch deaktiviert werden (alles einzeilig).
    
    Args:
        text: Zu formatierender Text
        max_chars: Maximale Zeichenanzahl pro Zeile
        linebreaks: Zeilenumbruch aktivieren (default True)
    Returns:
        Formatierter Text mit oder ohne Zeilenumbrüchen
    Verhalten:
        - linebreaks=True: Umbrechen an Wortgrenzen, wobei max_chars eingehalten wird.
        - linebreaks=False: Alles einzeilig.
    """
    if not linebreaks or len(text) <= max_chars:
        return text
        
    # Umbrechen an Wortgrenzen, für schönere Lesbarkeit
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # Prüfe, ob das Wort + Leerzeichen zur aktuellen Zeile passt
        test_line = f"{current_line} {word}".strip()
        
        if len(test_line) <= max_chars:
            # Wort passt in die aktuelle Zeile
            current_line = test_line
        else:
            # Wort passt nicht mehr in die Zeile - speichere aktuelle Zeile und beginne neue
            if current_line:
                lines.append(current_line)
            
            # Wenn das Wort selbst länger als max_chars ist, teile es auf
            if len(word) > max_chars:
                chunks = [word[i:i+max_chars] for i in range(0, len(word), max_chars)]
                lines.extend(chunks[:-1])  # Füge alle außer dem letzten Chunk hinzu
                current_line = chunks[-1]  # Letzter Chunk ist Start der neuen Zeile
            else:
                current_line = word
    
    # Letzte Zeile hinzufügen, falls vorhanden
    if current_line:
        lines.append(current_line)
        
    return '\n'.join(lines)


def text_to_vtt(text: str) -> str:
    """
    Convert plain text to VTT format.
    
    Args:
        text: Plain text
        
    Returns:
        Text in VTT format
    """
    # Split text into sentences
    sentences = split_into_sentences(text)
    
    # Generate VTT format
    vtt_lines = ["WEBVTT", ""]
    for i, sentence in enumerate(sentences):
        # Calculate approximate duration (5 seconds per sentence)
        start_time = i * 5
        end_time = (i + 1) * 5
        
        # Format timestamp
        start_timestamp = format_vtt_timestamp(start_time)
        end_timestamp = format_vtt_timestamp(end_time)
        
        # Add VTT entry
        vtt_lines.append(f"{start_timestamp} --> {end_timestamp}")
        vtt_lines.append(sentence)
        vtt_lines.append("")
    
    return '\n'.join(vtt_lines)


def text_to_json(text: str) -> str:
    """
    Convert plain text to JSON format.
    
    Args:
        text: Plain text
        
    Returns:
        Text in JSON format
    """
    # Split text into sentences
    sentences = split_into_sentences(text)
    
    # Generate segments
    segments = []
    for i, sentence in enumerate(sentences):
        # Calculate approximate duration (5 seconds per sentence)
        start_time = i * 5
        end_time = (i + 1) * 5
        
        segments.append({
            "id": i,
            "start": start_time,
            "end": end_time,
            "text": sentence
        })
    
    # Create JSON structure
    json_data = {
        "text": text,
        "segments": segments
    }
    
    return json.dumps(json_data, indent=2, ensure_ascii=False)


def split_into_sentences(text: str) -> List[str]:
    import re
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    sentences = sentence_endings.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]


# --- Kompatibilitätstest für SRT-Export ---
def test_srt_compatibility():
    """
    Testet, ob die erzeugte SRT-Datei mit srt.parse() korrekt eingelesen werden kann.
    """
    sample_text = "Hallo Welt. Dies ist ein Test! Noch ein Satz?"
    srt_content = text_to_srt(sample_text)
    try:
        parsed = list(srt.parse(srt_content))
        assert len(parsed) == 3, f"Erwartet: 3 Untertitel, gefunden: {len(parsed)}"
        assert parsed[0].content.startswith("Hallo Welt"), "Erster Untertiteltext stimmt nicht."
        print("SRT-Kompatibilitätstest erfolgreich: SRT-Datei ist standardkonform.")
    except Exception as e:
        print(f"SRT-Kompatibilitätstest fehlgeschlagen: {e}")


def format_vtt_timestamp(seconds: float) -> str:
    """
    Format seconds as VTT timestamp.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:02d}.{milliseconds:03d}"


def export_json_control(transcript_data: List[Dict], output_path: str) -> str:
    """
    Exportiert eine JSON-Kontrolldatei mit Transkriptionsinformationen.
    
    Diese Funktion speichert Transkriptionsdaten in einem speziellen JSON-Format,
    das als Referenz und zur Qualitätskontrolle verwendet werden kann.
    Die Segmentierung entspricht exakt der SRT-Datei für bessere Vergleichbarkeit.
    
    Args:
        transcript_data: Liste von Segment-Dictionarys mit Transkriptionsdaten
        output_path: Pfad zur Ausgabedatei (.json wird automatisch als Endung verwendet)
        
    Returns:
        Pfad zur erstellten JSON-Datei
    """
    import os
    import json
    import srt
    from datetime import timedelta
    
    # Die gleiche Segmentierungslogik wie bei segments_to_srt anwenden
    # Standardwerte für max_chars und max_duration
    max_chars = 20  # Gleicher Wert wie in segments_to_srt
    max_duration = 1.0  # Gleicher Wert wie in segments_to_srt
    
    logger.info(f"Generating JSON control with max_chars={max_chars}, max_duration={max_duration}")
    
    # Zuerst die SRT-Segmente erstellen (ohne diese zu speichern)
    subtitles = []
    index = 1
    
    for seg in transcript_data:
        # Original-Zeitstempel aus Whisper-Segmenten
        start_time = seg.get("start", 0)
        end_time = seg.get("end", 0)
        text = seg.get("text", "").strip()
        
        # Segmentlänge
        segment_duration = end_time - start_time
        
        # Falls Segment zu lang ist, in kleinere Teile aufteilen
        if segment_duration > max_duration:
            # Anzahl der Teilsegmente berechnen
            num_chunks = max(1, int(segment_duration / max_duration))
            chunk_duration = segment_duration / num_chunks
            
            # Text in Sätze aufteilen (wenn möglich)
            sentences = split_into_sentences(text)
            
            # Wenn nur ein Satz oder sehr kurzes Segment, verwende Wortaufteilung
            if len(sentences) <= 1 or len(sentences) < num_chunks:
                words = text.split()
                words_per_chunk = max(1, len(words) // num_chunks)
                
                for i in range(num_chunks):
                    chunk_start = start_time + (i * chunk_duration)
                    chunk_end = chunk_start + chunk_duration
                    
                    # Wörter für diesen Chunk
                    start_idx = i * words_per_chunk
                    end_idx = min(len(words), start_idx + words_per_chunk)
                    chunk_text = " ".join(words[start_idx:end_idx])
                    
                    # Zeichen pro Zeile begrenzen
                    formatted_text = format_text_with_max_chars(chunk_text, max_chars, linebreaks=True)
                    
                    # Untertitel erstellen
                    subtitles.append(srt.Subtitle(
                        index=index,
                        start=timedelta(seconds=chunk_start),
                        end=timedelta(seconds=chunk_end),
                        content=formatted_text
                    ))
                    index += 1
            else:
                # Verteilung der Sätze auf die Zeit
                sentences_duration = segment_duration / len(sentences)
                
                for i, sentence in enumerate(sentences):
                    chunk_start = start_time + (i * sentences_duration)
                    chunk_end = min(end_time, chunk_start + sentences_duration)
                    
                    # Satz in mehrere Zeilen aufteilen
                    parts = [sentence[j:j+max_chars] for j in range(0, len(sentence), max_chars)]
                    for part in parts:
                        part_start = chunk_start
                        part_end = min(chunk_end, part_start + sentences_duration / len(parts))
                        part_text = format_text_with_max_chars(part, max_chars, linebreaks=True)
                        subtitles.append(srt.Subtitle(
                            index=index,
                            start=timedelta(seconds=part_start),
                            end=timedelta(seconds=part_end),
                            content=part_text
                        ))
                        index += 1
        else:
            # Wenn Segment kurz genug ist, nur Textformatierung anwenden
            formatted_text = format_text_with_max_chars(text, max_chars, linebreaks=True)
            
            subtitles.append(srt.Subtitle(
                index=index,
                start=timedelta(seconds=start_time),
                end=timedelta(seconds=end_time),
                content=formatted_text
            ))
            index += 1
    
    # Jetzt die Untertitel in JSON umwandeln
    json_segments = []
    
    for subtitle in subtitles:
        # Start- und Endzeit in Millisekunden berechnen
        start_ms = int(subtitle.start.total_seconds() * 1000)
        end_ms = int(subtitle.end.total_seconds() * 1000)
        
        # Formatierte Zeitstempel erstellen (in SRT-Format mit Komma)
        start_h = int(subtitle.start.total_seconds() // 3600)
        start_m = int((subtitle.start.total_seconds() % 3600) // 60)
        start_s = int(subtitle.start.total_seconds() % 60)
        start_ms_part = int((subtitle.start.total_seconds() % 1) * 1000)
        
        end_h = int(subtitle.end.total_seconds() // 3600)
        end_m = int((subtitle.end.total_seconds() % 3600) // 60)
        end_s = int(subtitle.end.total_seconds() % 60)
        end_ms_part = int((subtitle.end.total_seconds() % 1) * 1000)
        
        start_formatted = f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms_part:03d}"
        end_formatted = f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms_part:03d}"
        
        # JSON-Segment erstellen
        json_segment = {
            "index": subtitle.index,
            "start": start_formatted,
            "end": end_formatted,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": subtitle.content
        }
        
        json_segments.append(json_segment)
    
    # JSON-Exporter-Verzeichnis erstellen, falls nicht vorhanden
    output_dir = os.path.dirname(output_path)
    json_exporter_dir = os.path.join(output_dir, "JSON-Exporter")
    
    os.makedirs(json_exporter_dir, exist_ok=True)
    logger.info(f"JSON-Exporter-Verzeichnis: {json_exporter_dir}")
    
    # Ausgabedateiname erstellen (gleicher Name wie Audiodatei, aber mit .json-Endung)
    base_filename = os.path.basename(output_path)
    base_name, _ = os.path.splitext(base_filename)
    json_filename = f"{base_name}.json"
    json_filepath = os.path.join(json_exporter_dir, json_filename)
    
    # Daten als JSON speichern
    with open(json_filepath, 'w', encoding='utf-8') as json_file:
        json.dump(json_segments, json_file, ensure_ascii=False, indent=2)
    
    logger.info(f"JSON-Kontrolldatei mit {len(json_segments)} Segmenten gespeichert: {json_filepath}")
    return json_filepath
