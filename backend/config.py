"""Configuration settings for the Character Duel API."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Keys
    RUNWARE_API_KEY: Optional[str] = os.getenv("RUN_WARE_API_KEY")
    
    # API URLs
    RUNWARE_API_URL: str = "https://api.runware.ai/v1"
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True
    TIMEOUT_KEEP_ALIVE: int = 7200
    
    # Data directories
    DATA_DIR: str = "data"
    CHARACTERS_DIR: str = os.path.join(DATA_DIR, "characters")
    DUELS_DIR: str = os.path.join(DATA_DIR, "duels")
    
    # Video generation settings
    DEFAULT_VIDEO_WIDTH: int = 720
    DEFAULT_VIDEO_HEIGHT: int = 1280
    DEFAULT_VIDEO_DURATION: float = 8.0
    DEFAULT_VIDEO_MODEL: str = "google:3@3"
    
    # Polling settings
    MAX_POLLING_ATTEMPTS: int = 300
    INITIAL_POLLING_DELAY: float = 0.5
    MAX_POLLING_DELAY: float = 2.0
    
    # Character settings
    DEFAULT_CHARACTER_HEALTH: int = 1000
    
    # Default video generation prompt
    DEFAULT_VIDEO_PROMPT: str = "create a virtual tour video of this living room as if real estate agent walked around and recorded it"
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        if not cls.RUNWARE_API_KEY:
            raise ValueError("RUN_WARE_API_KEY environment variable is required")
        
        # Ensure directories exist
        os.makedirs(cls.CHARACTERS_DIR, exist_ok=True)
        os.makedirs(cls.DUELS_DIR, exist_ok=True)


# Global config instance
config = Config()