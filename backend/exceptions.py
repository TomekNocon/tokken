"""Custom exceptions for the Character Duel API."""

from typing import Optional


class CharacterDuelException(Exception):
    """Base exception for Character Duel API."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConfigurationError(CharacterDuelException):
    """Configuration related errors."""
    pass


class RunWareAPIError(CharacterDuelException):
    """RunWare API related errors."""
    pass


class ImageProcessingError(CharacterDuelException):
    """Image processing related errors."""
    pass


class VideoGenerationError(CharacterDuelException):
    """Video generation related errors."""
    pass


class CharacterNotFoundError(CharacterDuelException):
    """Character not found errors."""
    pass


class FileOperationError(CharacterDuelException):
    """File operation related errors."""
    pass


class ValidationError(CharacterDuelException):
    """Validation related errors."""
    pass