"""
Exception handling for the Whisper Transcription Tool.
"""

class WhisperToolError(Exception):
    """Base exception class for Whisper Transcription Tool."""
    pass


class ConfigError(WhisperToolError):
    """Exception raised for configuration errors."""
    pass


class ModelError(WhisperToolError):
    """Exception raised for model-related errors."""
    pass


class TranscriptionError(WhisperToolError):
    """Exception raised for transcription errors."""
    pass


class ExtractionError(WhisperToolError):
    """Exception raised for audio extraction errors."""
    pass


class PhoneProcessingError(WhisperToolError):
    """Exception raised for phone call processing errors."""
    pass


class ChatbotError(WhisperToolError):
    """Exception raised for chatbot-related errors."""
    pass


class DependencyError(WhisperToolError):
    """Exception raised for missing dependencies."""
    pass


class FileFormatError(WhisperToolError):
    """Exception raised for unsupported file formats."""
    pass


class APIError(WhisperToolError):
    """Exception raised for API-related errors."""
    pass
