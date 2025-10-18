"""Data models for the Character Duel API."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Character data model."""
    
    id: str = Field(..., description="Unique character identifier")
    name: str = Field(..., description="Character name")
    image_paths: List[str] = Field(..., description="Paths to character images")
    generated_path: str = Field(..., description="Path to generated character video")
    health: int = Field(default=1000, description="Character health points")
    wins: int = Field(default=0, description="Number of wins")
    losses: int = Field(default=0, description="Number of losses")
    created_at: str = Field(..., description="Creation timestamp")
    status: str = Field(default="ready", description="Character status")


class Duel(BaseModel):
    """Duel data model."""
    
    id: str = Field(..., description="Unique duel identifier")
    char1_id: str = Field(..., description="First character ID")
    char2_id: str = Field(..., description="Second character ID")
    char1_prompt: str = Field(..., description="First character battle prompt")
    char2_prompt: str = Field(..., description="Second character battle prompt")
    winner: Optional[str] = Field(None, description="Winner character ID")
    video_path: Optional[str] = Field(None, description="Path to battle video")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")


class CreateCharacterRequest(BaseModel):
    """Request model for creating a character."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Character name")


class CreateCharacterResponse(BaseModel):
    """Response model for character creation."""
    
    character_id: str = Field(..., description="Created character ID")
    name: str = Field(..., description="Character name")
    status: str = Field(..., description="Creation status")
    message: str = Field(..., description="Status message")


class ListCharactersResponse(BaseModel):
    """Response model for listing characters."""
    
    characters: List[Character] = Field(..., description="List of characters")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class RunWareTask(BaseModel):
    """RunWare API task model."""
    
    task_type: str = Field(..., description="Task type")
    task_uuid: str = Field(..., description="Task UUID")
    status: Optional[str] = Field(None, description="Task status")
    progress: Optional[str] = Field(None, description="Task progress")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    error: Optional[str] = Field(None, description="Error message if any")