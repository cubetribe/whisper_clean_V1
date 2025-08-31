"""Hilfsfunktionen für den Vergleich von Transkriptionsdateien (SRT vs JSON)."""

import re
import json
import difflib
from typing import Dict, List

def parse_srt_file(content: str) -> List[Dict]:
    """
    Parst den Inhalt einer SRT-Datei und gibt eine Liste von Segmenten zurück.
    
    Args:
        content: Inhalt der SRT-Datei als String
        
    Returns:
        Liste von Segment-Dictionaries mit Index, Start, Ende und Text
    """
    segments = []
    
    # Regex-Muster für SRT-Parsing
    pattern = r'(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n([\s\S]*?)(?=\n\s*\n\s*\d+\s*\n|$)'
    matches = re.finditer(pattern, content)
    
    for match in matches:
        index = int(match.group(1))
        start_time = match.group(2)
        end_time = match.group(3)
        text = match.group(4).strip()
        
        # Konvertiere Zeitstempel in Millisekunden
        start_ms = time_to_milliseconds(start_time)
        end_ms = time_to_milliseconds(end_time)
        
        segments.append({
            "index": index,
            "start": start_time,
            "end": end_time,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": text
        })
    
    return segments


def time_to_milliseconds(time_str: str) -> int:
    """
    Konvertiert einen Zeitstempel im Format HH:MM:SS,mmm in Millisekunden.
    
    Args:
        time_str: Zeitstempel im Format HH:MM:SS,mmm
        
    Returns:
        Zeit in Millisekunden
    """
    # Ersetze Komma durch Punkt für einfachere Verarbeitung
    time_str = time_str.replace(',', '.')
    
    # Stunden, Minuten, Sekunden extrahieren
    h, m, s = time_str.split(':')
    
    # Berechne Gesamtmillisekunden
    total_ms = int(float(h) * 3600 * 1000 + float(m) * 60 * 1000 + float(s) * 1000)
    
    return total_ms


def compare_segments(srt_segments: List[Dict], json_segments: List[Dict], time_tolerance: int = 300) -> List[Dict]:
    """
    Vergleicht SRT- und JSON-Segmente und gibt eine Liste mit Vergleichsergebnissen zurück.
    
    Args:
        srt_segments: Liste von SRT-Segmenten
        json_segments: Liste von JSON-Segmenten
        time_tolerance: Toleranz für Zeitabweichungen in Millisekunden (Standard: 300ms)
        
    Returns:
        Liste von Vergleichsergebnissen
    """
    results = []
    
    # Maximal so viele Segmente vergleichen, wie im kürzeren Array vorhanden sind
    min_segments = min(len(srt_segments), len(json_segments))
    
    for i in range(min_segments):
        srt_segment = srt_segments[i]
        json_segment = json_segments[i]
        
        # Zeitdifferenzen berechnen
        start_diff = abs(srt_segment["start_ms"] - json_segment["start_ms"])
        end_diff = abs(srt_segment["end_ms"] - json_segment["end_ms"])
        time_diff = max(start_diff, end_diff)
        
        # Textähnlichkeit mit difflib berechnen
        text_similarity = difflib.SequenceMatcher(None, srt_segment["text"], json_segment["text"]).ratio()
        
        # Status bestimmen
        status = "OK"
        if time_diff > time_tolerance and text_similarity < 0.8:
            status = "Fehler"
        elif time_diff > time_tolerance or text_similarity < 0.8:
            status = "Warnung"
        
        results.append({
            "index": i + 1,
            "time_diff_ms": time_diff,
            "text_similarity": text_similarity,
            "status": status,
            "srt_text": srt_segment["text"],
            "json_text": json_segment["text"]
        })
    
    return results
