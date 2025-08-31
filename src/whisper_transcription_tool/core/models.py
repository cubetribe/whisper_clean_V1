"""
Data models for the Whisper Transcription Tool.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union


class OutputFormat(str, Enum):
    """Supported output formats for transcription."""
    TXT = "txt"
    SRT = "srt"
    VTT = "vtt"
    JSON = "json"


class WhisperModel(str, Enum):
    """Supported Whisper models."""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V3 = "large-v3"
    LARGE_V3_TURBO = "large-v3-turbo"  # Default model as specified by user


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""
    success: bool
    text: Optional[str] = None
    output_file: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None
    stderr: Optional[str] = None
    segments: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ExtractionResult:
    """Result of an audio extraction operation."""
    success: bool
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    error: Optional[str] = None
    stderr: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class PhoneProcessingResult:
    """Result of a phone call processing operation."""
    success: bool
    output_file: Optional[str] = None
    track_a: Optional[str] = None
    track_b: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class TranscriptionRequest:
    """Request for transcription."""
    audio_path: Union[str, Path]
    output_format: OutputFormat = OutputFormat.TXT
    language: Optional[str] = None
    model: WhisperModel = WhisperModel.LARGE_V3_TURBO
    output_path: Optional[Union[str, Path]] = None


@dataclass
class ExtractionRequest:
    """Request for audio extraction."""
    video_path: Union[str, Path]
    output_path: Optional[Union[str, Path]] = None


@dataclass
class PhoneProcessingRequest:
    """Request for phone call processing."""
    track_a_path: Union[str, Path]
    track_b_path: Union[str, Path]
    output_path: Optional[Union[str, Path]] = None
