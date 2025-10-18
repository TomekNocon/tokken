"""Character service for managing character operations."""

import os
from typing import List, Tuple
from fastapi import UploadFile

from config import config
from exceptions import ValidationError, FileOperationError
from logging_config import get_logger
from models import Character, CreateCharacterResponse
from services.runware_service import RunWareService
from utils import (
    generate_id, 
    get_current_timestamp, 
    validate_image_file, 
    process_uploaded_image,
    save_character_data,
    load_character_data,
    load_all_characters,
    get_file_path
)

logger = get_logger(__name__)


class CharacterService:
    """Service for managing character operations."""
    
    def __init__(self):
        self.runware_service = RunWareService()
    
    async def create_character(self, images: List[UploadFile], name: str) -> CreateCharacterResponse:
        """Create a new character from uploaded images."""
        try:
            logger.info(f"Creating character '{name}' with {len(images)} images")
            
            # Validate inputs
            self._validate_character_creation(images, name)
            
            # Generate character ID
            char_id = generate_id()
            
            # Save uploaded images
            image_paths = await self._save_uploaded_images(char_id, images)
            
            # Generate character video
            generated_video_path = await self._generate_character_video(char_id, image_paths, name)
            
            # Create character data
            character_data = self._create_character_data(char_id, name, image_paths, generated_video_path)
            
            # Save character data
            save_character_data(character_data)
            
            logger.info(f"Character '{name}' created successfully with ID: {char_id}")
            
            return CreateCharacterResponse(
                character_id=char_id,
                name=name,
                status="completed",
                message="Character created successfully!"
            )
            
        except Exception as e:
            logger.error(f"Error creating character '{name}': {e}")
            raise
    
    def get_character(self, char_id: str) -> Character:
        """Get character by ID."""
        try:
            logger.debug(f"Getting character: {char_id}")
            character_data = load_character_data(char_id)
            return Character(**character_data)
            
        except Exception as e:
            logger.error(f"Error getting character {char_id}: {e}")
            raise
    
    def list_characters(self) -> List[Character]:
        """List all characters."""
        try:
            logger.debug("Listing all characters")
            characters_data = load_all_characters()
            return [Character(**data) for data in characters_data]
            
        except Exception as e:
            logger.error(f"Error listing characters: {e}")
            raise
    
    def get_character_image_path(self, char_id: str, image_index: int) -> str:
        """Get character image file path."""
        image_path = get_file_path(char_id, "image", image_index)
        
        if not os.path.exists(image_path):
            raise FileOperationError(f"Image not found: {image_path}")
        
        return image_path
    
    def get_character_video_path(self, char_id: str) -> str:
        """Get character video file path."""
        video_path = get_file_path(char_id, "video")
        
        if not os.path.exists(video_path):
            raise FileOperationError(f"Video not found: {video_path}")
        
        return video_path
    
    def _validate_character_creation(self, images: List[UploadFile], name: str) -> None:
        """Validate character creation inputs."""
        if len(images) == 0:
            raise ValidationError("At least one image is required")
        
        if not name or len(name.strip()) == 0:
            raise ValidationError("Character name is required")
        
        if len(name.strip()) > 100:
            raise ValidationError("Character name must be 100 characters or less")
        
        for image in images:
            validate_image_file(image.content_type)
    
    async def _save_uploaded_images(self, char_id: str, images: List[UploadFile]) -> List[str]:
        """Save uploaded images and return their paths."""
        image_paths = []
        
        for i, image_file in enumerate(images):
            image_path = get_file_path(char_id, "image", i)
            
            # Read and process the image
            image_content = await image_file.read()
            process_uploaded_image(image_content, image_path)
            
            image_paths.append(image_path)
            logger.debug(f"Saved image {i}: {image_path}")
        
        return image_paths
    
    async def _generate_character_video(self, char_id: str, image_paths: List[str], name: str) -> str:
        """Generate character video using AI."""
        try:
            logger.info(f"Generating video for character: {name}")
            
            # Upload images to RunWare
            uploaded_image_ids = []
            for image_path in image_paths:
                image_id = await self.runware_service.upload_image(
                    image_path, 
                    config.DEFAULT_VIDEO_WIDTH, 
                    config.DEFAULT_VIDEO_HEIGHT
                )
                uploaded_image_ids.append(image_id)
            
            # Generate video
            video_url = await self.runware_service.generate_video(uploaded_image_ids, name)
            
            # Download generated video
            video_path = get_file_path(char_id, "video")
            await self.runware_service.download_video(video_url, video_path)
            
            logger.info(f"Video generated successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error generating video for character {name}: {e}")
            raise
    
    def _create_character_data(self, char_id: str, name: str, image_paths: List[str], video_path: str) -> dict:
        """Create character data dictionary."""
        # Convert absolute paths to relative paths for storage
        image_paths_relative = [f"characters/{char_id}_image_{i}.png" for i in range(len(image_paths))]
        video_path_relative = f"characters/{char_id}_generated.mp4"
        
        return {
            "id": char_id,
            "name": name.strip(),
            "image_paths": image_paths_relative,
            "generated_path": video_path_relative,
            "health": config.DEFAULT_CHARACTER_HEALTH,
            "wins": 0,
            "losses": 0,
            "created_at": get_current_timestamp(),
            "status": "ready"
        }