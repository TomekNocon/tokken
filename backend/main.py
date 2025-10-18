"""
Character Duel API - Main application module.

A FastAPI-based backend for an AI-powered character dueling platform.
Users can upload sketches, generate AI characters, and create battles.
"""

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import config
from exceptions import (
    CharacterDuelException, 
    ConfigurationError, 
    CharacterNotFoundError,
    FileOperationError,
    ValidationError
)
from logging_config import setup_logging, get_logger
from models import Character, CreateCharacterResponse, ListCharactersResponse
from services import CharacterService

# Set up logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Character Duel API...")
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Character Duel API...")


# Create FastAPI application
app = FastAPI(
    title="Character Duel API",
    description="AI-powered character dueling platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
character_service = CharacterService()


# Exception handlers
@app.exception_handler(CharacterNotFoundError)
async def character_not_found_handler(request, exc: CharacterNotFoundError):
    """Handle character not found errors."""
    logger.warning(f"Character not found: {exc.message}")
    raise HTTPException(status_code=404, detail=exc.message)


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.message}")
    raise HTTPException(status_code=400, detail=exc.message)


@app.exception_handler(FileOperationError)
async def file_operation_error_handler(request, exc: FileOperationError):
    """Handle file operation errors."""
    logger.error(f"File operation error: {exc.message}")
    raise HTTPException(status_code=500, detail=exc.message)


@app.exception_handler(CharacterDuelException)
async def general_character_duel_error_handler(request, exc: CharacterDuelException):
    """Handle general character duel errors."""
    logger.error(f"Character duel error: {exc.message}")
    raise HTTPException(status_code=500, detail=exc.message)


# API Routes

@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "message": "Character Duel API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/test_multiple_upload.html", tags=["Development"])
async def serve_test_page():
    """Serve the multiple upload test page for development."""
    return FileResponse("test_multiple_upload.html", media_type="text/html")


@app.post("/characters/", response_model=CreateCharacterResponse, tags=["Characters"])
async def create_character(
    images: List[UploadFile] = File(..., description="Character images to upload"),
    name: str = Form(..., description="Character name")
) -> CreateCharacterResponse:
    """
    Create a new AI character from uploaded images.
    
    - **images**: List of image files (PNG, JPG, etc.)
    - **name**: Character name (1-100 characters)
    
    Returns the created character ID and status.
    """
    try:
        logger.info(f"Creating character '{name}' with {len(images)} images")
        result = await character_service.create_character(images, name)
        logger.info(f"Character created successfully: {result.character_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        raise


@app.get("/characters/", response_model=ListCharactersResponse, tags=["Characters"])
async def list_characters() -> ListCharactersResponse:
    """
    Get all characters.
    
    Returns a list of all created characters with their metadata.
    """
    try:
        logger.debug("Listing all characters")
        characters = character_service.list_characters()
        return ListCharactersResponse(characters=characters)
        
    except Exception as e:
        logger.error(f"Error listing characters: {e}")
        raise


@app.get("/characters/{char_id}", response_model=Character, tags=["Characters"])
async def get_character(char_id: str) -> Character:
    """
    Get specific character details.
    
    - **char_id**: Unique character identifier
    
    Returns detailed character information.
    """
    try:
        logger.debug(f"Getting character: {char_id}")
        character = character_service.get_character(char_id)
        return character
        
    except Exception as e:
        logger.error(f"Error getting character {char_id}: {e}")
        raise


@app.get("/characters/{char_id}/image/{image_index}", tags=["Characters"])
async def get_character_image(char_id: str, image_index: int):
    """
    Get character image by index.
    
    - **char_id**: Unique character identifier
    - **image_index**: Image index (starting from 0)
    
    Returns the character image file.
    """
    try:
        logger.debug(f"Getting image {image_index} for character {char_id}")
        image_path = character_service.get_character_image_path(char_id, image_index)
        return FileResponse(image_path, media_type="image/png")
        
    except Exception as e:
        logger.error(f"Error getting image for character {char_id}: {e}")
        raise


@app.get("/characters/{char_id}/video", tags=["Characters"])
async def get_character_video(char_id: str):
    """
    Get generated character video.
    
    - **char_id**: Unique character identifier
    
    Returns the generated character video file.
    """
    try:
        logger.debug(f"Getting video for character {char_id}")
        video_path = character_service.get_character_video_path(char_id)
        return FileResponse(video_path, media_type="video/mp4")
        
    except Exception as e:
        logger.error(f"Error getting video for character {char_id}: {e}")
        raise


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server...")
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        timeout_keep_alive=config.TIMEOUT_KEEP_ALIVE
    )