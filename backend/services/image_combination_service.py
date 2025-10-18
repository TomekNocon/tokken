"""Image combination service for combining two images using AI."""

import base64
import os
import uuid
from typing import Tuple

from config import config
from exceptions import RunWareAPIError, FileOperationError
from logging_config import get_logger
from utils import generate_id, get_current_timestamp
import requests

logger = get_logger(__name__)


class ImageCombinationService:
    """Service for combining two images using RunWare API."""
    
    def __init__(self):
        if not config.RUNWARE_API_KEY:
            raise RunWareAPIError("RunWare API key not configured")
        
        self.api_key = config.RUNWARE_API_KEY
        self.api_url = config.RUNWARE_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def combine_images(
        self, 
        background_image_path: str, 
        person_image_path: str, 
        prompt: str = None
    ) -> Tuple[str, str]:
        """
        Combine two images: fit a person into a background scene.
        
        Args:
            background_image_path: Path to the background/room image
            person_image_path: Path to the person image
            prompt: Custom prompt for the combination
            
        Returns:
            Tuple of (generated_image_path, combination_id)
        """
        try:
            logger.info("Starting image combination process")
            
            # Read and encode the background image (seed image)
            with open(background_image_path, "rb") as image_file:
                background_data = image_file.read()
                background_base64 = base64.b64encode(background_data).decode('utf-8')
            
            # Read and encode the person image (control image)
            with open(person_image_path, "rb") as image_file:
                person_data = image_file.read()
                person_base64 = base64.b64encode(person_data).decode('utf-8')
            
            # Generate task UUID and combination ID
            task_uuid = str(uuid.uuid4())
            combination_id = generate_id()
            
            # Use custom prompt or default
            if prompt:
                combination_prompt = prompt
            else:
                combination_prompt = "A person naturally placed in this room environment, realistic lighting, seamless integration, photorealistic, high quality, natural pose"
            
            logger.info(f"Using prompt: {combination_prompt}")
            
            # Prepare RunWare API payload for image combination
            payload = [
            {
                "taskType": "imageInference",
                "taskUUID": task_uuid,
                "numberResults": 1,
                "outputFormat": "JPEG",
                "width": 1024,
                "height": 1024,
                "includeCost": True,
                "outputType": [
                "URL"
                ],
                "referenceImages": [background_base64, person_base64],
                "model": "google:4@1",
                "positivePrompt": combination_prompt
            }
            ]
            
            logger.info(f"Submitting image combination task: {task_uuid}")
            
            # Make API request to RunWare
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"RunWare API error: {response.status_code} - {response.text}")
                raise RunWareAPIError(f"RunWare API error: {response.text}")
            
            result = response.json()
            logger.info(f"RunWare response: {result}")
            
            # Check for immediate errors
            if "errors" in result and result["errors"]:
                error_msg = result["errors"][0].get("message", "Unknown error")
                raise RunWareAPIError(f"RunWare error: {error_msg}")
            
            # Extract the generated image URL
            if "data" in result and len(result["data"]) > 0:
                task_result = result["data"][0]
                
                # Check various possible field names for the image URL
                image_url = None
                for field_name in ["imageURL", "outputImageURL", "imagePath", "image", "url"]:
                    if field_name in task_result:
                        image_url = task_result[field_name]
                        break
                
                if not image_url:
                    logger.error(f"RunWare response structure: {result}")
                    raise RunWareAPIError(f"No image URL found in RunWare response. Available fields: {list(task_result.keys())}")
                
                # Download the generated image
                logger.info(f"Downloading combined image from: {image_url}")
                img_response = requests.get(image_url)
                
                if img_response.status_code == 200:
                    # Save the combined image
                    generated_path = os.path.join(config.CHARACTERS_DIR, f"{combination_id}_combined.png")
                    
                    with open(generated_path, "wb") as f:
                        f.write(img_response.content)
                    
                    logger.info(f"Combined image saved: {generated_path}")
                    return generated_path, combination_id
                else:
                    raise RunWareAPIError("Failed to download generated image")
            else:
                raise RunWareAPIError("No image generated by RunWare API")
                
        except RunWareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error combining images: {e}")
            raise RunWareAPIError(f"Failed to combine images: {str(e)}")
    
    def save_combination_metadata(
        self, 
        combination_id: str, 
        background_path: str, 
        person_path: str, 
        generated_path: str,
        prompt: str = None
    ) -> None:
        """Save combination metadata to JSON file."""
        try:
            metadata = {
                "id": combination_id,
                "background_image": background_path,
                "person_image": person_path,
                "combined_image": generated_path,
                "prompt": prompt,
                "created_at": get_current_timestamp(),
                "status": "completed"
            }
            
            metadata_path = os.path.join(config.CHARACTERS_DIR, f"{combination_id}_combination.json")
            
            import json
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"Combination metadata saved: {metadata_path}")
            
        except Exception as e:
            logger.error(f"Error saving combination metadata: {e}")
            raise FileOperationError(f"Failed to save combination metadata: {str(e)}")