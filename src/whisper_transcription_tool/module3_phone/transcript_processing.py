"""
Transcript processing utilities for phone call recordings.
Handles transcript formatting, speaker identification, and other transcript-related tasks.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.logging_setup import get_logger
from ..core.models import OutputFormat

logger = get_logger(__name__)


def parse_json_transcript(json_text: str) -> List[Dict]:
    """
    Parse a JSON transcript into segments.
    
    Args:
        json_text: JSON transcript text
        
    Returns:
        List of transcript segments
    """
    try:
        # Parse JSON
        data = json.loads(json_text) if isinstance(json_text, str) else json_text
        
        # Extract segments
        if isinstance(data, dict) and "segments" in data:
            return data["segments"]
        
        return []
    
    except Exception as e:
        logger.error(f"Error parsing JSON transcript: {e}")
        return []


def merge_transcripts_with_timestamps(
    transcript_a_json: str,
    transcript_b_json: str,
    speaker_a_name: str = "Speaker A",
    speaker_b_name: str = "Speaker B",
    output_format: str = "txt"
) -> str:
    """
    Merge two JSON transcripts into a conversation format with timestamps.
    
    Args:
        transcript_a_json: JSON transcript from first audio track
        transcript_b_json: JSON transcript from second audio track
        speaker_a_name: Name for speaker A
        speaker_b_name: Name for speaker B
        output_format: Output format (txt, md, json)
        
    Returns:
        Merged transcript
    """
    # Parse JSON transcripts
    segments_a = parse_json_transcript(transcript_a_json)
    segments_b = parse_json_transcript(transcript_b_json)
    
    # Add speaker information to segments
    for segment in segments_a:
        segment["speaker"] = speaker_a_name
    
    for segment in segments_b:
        segment["speaker"] = speaker_b_name
    
    # Combine and sort segments by start time
    all_segments = segments_a + segments_b
    all_segments.sort(key=lambda x: x.get("start", 0))
    
    # Format output based on requested format
    if output_format == "json":
        return json.dumps({
            "segments": all_segments
        }, indent=2)
    
    elif output_format == "md":
        return format_transcript_markdown(all_segments, speaker_a_name, speaker_b_name)
    
    else:  # Default to txt
        return format_transcript_text(all_segments, speaker_a_name, speaker_b_name)


def format_transcript_text(
    segments: List[Dict],
    speaker_a_name: str,
    speaker_b_name: str
) -> str:
    """
    Format transcript segments as plain text.
    
    Args:
        segments: List of transcript segments
        speaker_a_name: Name for speaker A
        speaker_b_name: Name for speaker B
        
    Returns:
        Formatted transcript
    """
    lines = []
    lines.append("Telefongesprächstranskript")
    lines.append("=========================")
    lines.append("")
    lines.append(f"Teilnehmer: {speaker_a_name}, {speaker_b_name}")
    lines.append("")
    lines.append("Transkript:")
    lines.append("")
    
    current_speaker = None
    
    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "").strip()
        start_time = segment.get("start", 0)
        
        # Format timestamp
        timestamp = format_timestamp(start_time)
        
        # Add speaker change
        if speaker != current_speaker:
            lines.append("")
            lines.append(f"{speaker} [{timestamp}]:")
            current_speaker = speaker
        
        # Add text
        lines.append(f"  {text}")
    
    return "\n".join(lines)


def format_transcript_markdown(
    segments: List[Dict],
    speaker_a_name: str,
    speaker_b_name: str
) -> str:
    """
    Format transcript segments as Markdown.
    
    Args:
        segments: List of transcript segments
        speaker_a_name: Name for speaker A
        speaker_b_name: Name for speaker B
        
    Returns:
        Formatted transcript
    """
    lines = []
    lines.append("# Telefongesprächstranskript")
    lines.append("")
    lines.append("## Teilnehmer")
    lines.append(f"- {speaker_a_name}")
    lines.append(f"- {speaker_b_name}")
    lines.append("")
    lines.append("## Transkript")
    lines.append("")
    
    current_speaker = None
    
    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "").strip()
        start_time = segment.get("start", 0)
        
        # Format timestamp
        timestamp = format_timestamp(start_time)
        
        # Add speaker change
        if speaker != current_speaker:
            lines.append("")
            lines.append(f"### {speaker} [{timestamp}]")
            current_speaker = speaker
        
        # Add text
        lines.append(text)
    
    return "\n".join(lines)


def format_timestamp(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    
    return f"{minutes:02d}:{seconds:02d}"


def identify_speakers(
    transcript_a: str,
    transcript_b: str
) -> Tuple[str, str]:
    """
    Attempt to identify speakers based on transcript content.
    
    Args:
        transcript_a: Transcript from first audio track
        transcript_b: Transcript from second audio track
        
    Returns:
        Tuple of (speaker_a_name, speaker_b_name)
    """
    # This is a placeholder for a more advanced implementation
    # that would use NLP to identify speakers based on content
    
    # For now, we'll use simple heuristics
    
    # Default names
    speaker_a_name = "Anrufer"
    speaker_b_name = "Empfänger"
    
    # Check for common greeting patterns
    if re.search(r'\b(hallo|guten tag|grüß|grüss|servus|moin)\b', transcript_a.lower()):
        # First speaker is likely the caller
        speaker_a_name = "Anrufer"
        speaker_b_name = "Empfänger"
    
    if re.search(r'\b(hallo|guten tag|grüß|grüss|servus|moin)\b', transcript_b.lower()):
        # Second speaker is likely the caller
        speaker_a_name = "Empfänger"
        speaker_b_name = "Anrufer"
    
    return speaker_a_name, speaker_b_name


def extract_key_information(transcript: str) -> Dict:
    """
    Extract key information from a transcript.
    
    Args:
        transcript: Transcript text
        
    Returns:
        Dictionary with extracted information
    """
    info = {
        "names": [],
        "phone_numbers": [],
        "email_addresses": [],
        "dates": [],
        "key_topics": []
    }
    
    # Extract phone numbers
    phone_pattern = r'\b(\+?[\d\s\(\)-]{8,})\b'
    info["phone_numbers"] = re.findall(phone_pattern, transcript)
    
    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    info["email_addresses"] = re.findall(email_pattern, transcript)
    
    # Extract dates
    date_pattern = r'\b(\d{1,2}[./]\d{1,2}[./]\d{2,4})\b'
    info["dates"] = re.findall(date_pattern, transcript)
    
    # This is a placeholder for more advanced NLP-based extraction
    # In a real implementation, we would use NLP to extract names and key topics
    
    return info
