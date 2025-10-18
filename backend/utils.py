"""Utility functions for the Character Duel API."""

import json
import os
import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException
from PIL import Image
import io

from config import config
from models import Character
from exceptions import CharacterNotFoundError, FileOperationError


def generate_id() -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4())[:8]


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def save_character_data(character_data: dict) -> None:
    """Save character data to JSON file."""
    try:
        char_id = character_data["id"]
        file_path = os.path.join(config.CHARACTERS_DIR, f"{char_id}.json")
        
        with open(file_path, "w") as f:
            json.dump(character_data, f, indent=2)
            
    except Exception as e:
        raise FileOperationError(f"Failed to save character data: {str(e)}")


def load_character_data(char_id: str) -> dict:
    """Load character data from JSON file."""
    try:
        file_path = os.path.join(config.CHARACTERS_DIR, f"{char_id}.json")
        
        if not os.path.exists(file_path):
            raise CharacterNotFoundError(f"Character {char_id} not found")
        
        with open(file_path, "r") as f:
            return json.load(f)
            
    except CharacterNotFoundError:
        raise
    except Exception as e:
        raise FileOperationError(f"Failed to load character data: {str(e)}")


def load_all_characters() -> List[dict]:
    """Load all character data."""
    try:
        characters = []
        
        if not os.path.exists(config.CHARACTERS_DIR):
            return characters
            
        for filename in os.listdir(config.CHARACTERS_DIR):
            if filename.endswith(".json"):
                char_id = filename[:-5]  # Remove .json extension
                try:
                    character = load_character_data(char_id)
                    characters.append(character)
                except Exception:
                    # Skip corrupted character files
                    continue
        
        # Sort by creation date (newest first)
        characters.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return characters
        
    except Exception as e:
        raise FileOperationError(f"Failed to load characters: {str(e)}")


def validate_image_file(content_type: str) -> None:
    """Validate image file type."""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")


def process_uploaded_image(image_content: bytes, output_path: str) -> None:
    """Process and save uploaded image."""
    try:
        # Convert to PNG format
        image = Image.open(io.BytesIO(image_content))
        image = image.convert("RGB")  # Ensure RGB format
        image.save(output_path, "PNG")
        
    except Exception as e:
        raise FileOperationError(f"Failed to process image: {str(e)}")


def resize_image_for_video(image_path: str, target_width: int, target_height: int) -> bytes:
    """Resize image for video generation."""
    try:
        with Image.open(image_path) as img:
            # Ensure dimensions are within valid range (300-2048 for width)
            width = max(300, min(2048, target_width))
            height = max(300, min(2048, target_height))
            
            # Resize the image maintaining aspect ratio if needed
            img = img.convert("RGB")
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.read()
            
    except Exception as e:
        raise FileOperationError(f"Failed to resize image: {str(e)}")


def get_file_path(char_id: str, file_type: str, index: int = 0) -> str:
    """Get file path for character assets."""
    if file_type == "image":
        return os.path.join(config.CHARACTERS_DIR, f"{char_id}_image_{index}.png")
    elif file_type == "video":
        return os.path.join(config.CHARACTERS_DIR, f"{char_id}_generated.mp4")
    else:
        raise ValueError(f"Unknown file type: {file_type}")


def file_exists(file_path: str) -> bool:
    """Check if file exists."""
    return os.path.exists(file_path)