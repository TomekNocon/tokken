"""RunWare API service for video generation."""

import asyncio
import base64
import time
import uuid
from typing import List, Tuple
import requests

from config import config
from exceptions import RunWareAPIError, ConfigurationError
from logging_config import get_logger
from utils import resize_image_for_video

logger = get_logger(__name__)


class RunWareService:
    """Service for interacting with RunWare API."""
    
    def __init__(self):
        if not config.RUNWARE_API_KEY:
            raise ConfigurationError("RunWare API key not configured")
        
        self.api_key = config.RUNWARE_API_KEY
        self.api_url = config.RUNWARE_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def upload_image(self, image_path: str, target_width: int, target_height: int) -> str:
        """Upload an image to RunWare and return the image ID."""
        try:
            logger.info(f"Uploading image: {image_path}")
            
            # Resize image
            image_data = resize_image_for_video(image_path, target_width, target_height)
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare upload payload
            upload_payload = [{
                "taskType": "imageUpload",
                "taskUUID": str(uuid.uuid4()),
                "image": "data:image/png;base64," + image_base64
            }]
            
            # Make API request
            response = requests.post(self.api_url, headers=self.headers, json=upload_payload)
            
            if response.status_code != 200:
                logger.error(f"Image upload failed: {response.status_code} - {response.text}")
                raise RunWareAPIError(f"Image upload failed: {response.text}")
            
            result = response.json()
            
            # Extract image ID
            if "data" in result and len(result["data"]) > 0:
                task_result = result["data"][0]
                
                for field_name in ["imageId", "id", "imageUUID", "uuid"]:
                    if field_name in task_result:
                        image_id = task_result[field_name]
                        logger.info(f"Image uploaded successfully with ID: {image_id}")
                        return image_id
                
                logger.error(f"No image ID found in upload response: {result}")
                raise RunWareAPIError("No image ID returned by upload API")
            else:
                raise RunWareAPIError("No data returned by upload API")
                
        except RunWareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise RunWareAPIError(f"Failed to upload image: {str(e)}")
    
    async def generate_video(
        self, 
        image_ids: List[str], 
        character_name: str,
        prompt: str = None,
        width: int = None,
        height: int = None,
        duration: float = None
    ) -> str:
        """Generate video from images using RunWare API."""
        try:
            # Use config defaults if not provided
            width = width or config.DEFAULT_VIDEO_WIDTH
            height = height or config.DEFAULT_VIDEO_HEIGHT
            duration = duration or config.DEFAULT_VIDEO_DURATION
            
            # Use custom prompt or default
            if prompt:
                video_prompt = prompt
            else:
                video_prompt = config.DEFAULT_VIDEO_PROMPT.format(character_name=character_name)
            
            logger.info(f"Starting video generation for character: {character_name}")
            logger.info(f"Video dimensions: {width}x{height}, Duration: {duration}s")
            logger.info(f"Using {len(image_ids)} images for video generation")
            
            if not image_ids:
                raise RunWareAPIError("No images provided for video generation")
            
            # Prepare frame images - use all uploaded images
            frame_images = []
            
            if len(image_ids) == 1:
                # Single image - use as first frame
                frame_images.append({
                    "inputImage": image_ids[0],
                    "frame": "first"
                })
            else:
                # Multiple images - use first and last for 2-frame animation
                frame_images.append({
                    "inputImage": image_ids[0],
                    "frame": "first"
                })
                
                # If we have more than one image, use the last one as the final frame
                if len(image_ids) > 1:
                    frame_images.append({
                        "inputImage": image_ids[-1],
                        "frame": "last"
                    })
            
            logger.info(f"Frame images configuration: {len(frame_images)} frames")
            for i, frame in enumerate(frame_images):
                logger.info(f"Frame {i+1}: {frame['frame']} position")
            
            # Prepare video generation payload
            task_uuid = str(uuid.uuid4())
            payload = [{
                "taskType": "videoInference",
                "duration": duration,
                "model": config.DEFAULT_VIDEO_MODEL,
                "height": height,
                "width": width,
                "numberResults": 1,
                "providerSettings": {
                    "google": {
                        "generateAudio": True,
                        "enhancePrompt": True
                    }
                },
                "frameImages": frame_images,
                "positivePrompt": video_prompt,
                "taskUUID": task_uuid
            }]
            
            # Submit video generation task
            logger.info(f"Submitting video generation task: {task_uuid}")
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Video generation submission failed: {response.status_code} - {response.text}")
                raise RunWareAPIError(f"Video generation failed: {response.text}")
            
            result = response.json()
            logger.info(f"Video generation task submitted successfully: {result}")
            
            # Check for immediate errors
            if "errors" in result and result["errors"]:
                error_msg = result["errors"][0].get("message", "Unknown error")
                raise RunWareAPIError(f"Video generation error: {error_msg}")
            
            # Poll for completion
            logger.info("Waiting for video generation to complete...")
            video_url = await self._poll_for_completion(task_uuid)
            
            logger.info(f"Video generation completed: {video_url}")
            return video_url
            
        except RunWareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise RunWareAPIError(f"Failed to generate video: {str(e)}")
    
    async def _poll_for_completion(self, task_uuid: str) -> str:
        """Poll RunWare API for task completion."""
        start_time = time.time()
        
        for attempt in range(config.MAX_POLLING_ATTEMPTS):
            try:
                # Query for task status
                status_payload = [{
                    "taskType": "getResponse",
                    "taskUUID": task_uuid
                }]
                
                response = requests.post(self.api_url, headers=self.headers, json=status_payload)
                
                # Log response details for debugging on first few attempts
                if attempt < 3:
                    logger.debug(f"Polling response status: {response.status_code}")
                    if response.status_code != 200:
                        logger.debug(f"Non-200 response: {response.text[:500]}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check for errors
                    if "errors" in result and result["errors"]:
                        error_msg = result["errors"][0].get("message", "Unknown error")
                        logger.error(f"RunWare error: {error_msg}")
                        raise RunWareAPIError(f"RunWare error: {error_msg}")
                    
                    if "data" in result and len(result["data"]) > 0:
                        task_result = result["data"][0]
                        
                        # Log task details on first few attempts
                        if attempt < 2:
                            logger.debug(f"Task result fields: {list(task_result.keys())}")
                            if attempt == 0:
                                logger.debug(f"Full task result: {task_result}")
                        
                        # Check if video URL is present
                        video_url_fields = ["videoURL", "outputVideoURL", "videoPath", "video", "url"]
                        for field_name in video_url_fields:
                            if field_name in task_result and task_result[field_name]:
                                elapsed = int(time.time() - start_time)
                                logger.info(f"Video generation completed after {elapsed} seconds ({attempt + 1} attempts)")
                                return task_result[field_name]
                        
                        # Log task status and progress
                        if "status" in task_result:
                            status = task_result['status']
                            progress = task_result.get('progress', 'unknown')
                            logger.debug(f"Task status: {status} | Progress: {progress}")
                    else:
                        # No data returned yet
                        if attempt < 5:
                            logger.debug(f"No data in response yet. Full response: {result}")
                
                # Calculate elapsed time and delay
                elapsed = int(time.time() - start_time)
                elapsed_mins = elapsed // 60
                elapsed_secs = elapsed % 60
                
                # Adaptive delay
                delay = min(config.INITIAL_POLLING_DELAY + (attempt // 30) * 0.2, config.MAX_POLLING_DELAY)
                
                # Log progress periodically
                if attempt % 5 == 0 or attempt < 10:
                    logger.info(f"Polling attempt {attempt + 1}/{config.MAX_POLLING_ATTEMPTS} - {elapsed_mins}m {elapsed_secs}s elapsed - video still generating... (delay: {delay:.1f}s)")
                
                await asyncio.sleep(delay)
                
            except RunWareAPIError:
                raise
            except Exception as e:
                logger.error(f"Error polling RunWare: {e}")
                if attempt == config.MAX_POLLING_ATTEMPTS - 1:
                    raise
                await asyncio.sleep(config.INITIAL_POLLING_DELAY)
        
        elapsed = int(time.time() - start_time)
        raise RunWareAPIError(f"Video generation timeout - task took longer than {elapsed} seconds to complete. This usually means the video generation failed or is stuck.")
    
    async def download_video(self, video_url: str, output_path: str) -> None:
        """Download generated video from URL."""
        try:
            logger.info(f"Downloading video from: {video_url}")
            
            response = requests.get(video_url)
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"Video downloaded successfully: {output_path}")
                logger.info(f"Video size: {len(response.content)} bytes")
            else:
                raise RunWareAPIError(f"Failed to download video: HTTP {response.status_code}")
                
        except RunWareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise RunWareAPIError(f"Failed to download video: {str(e)}")