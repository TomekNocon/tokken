from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
import os
import base64
from datetime import datetime
from typing import List, Optional
import requests
from PIL import Image
import io
from dotenv import load_dotenv
import asyncio
import time

# Load environment variables
load_dotenv()

app = FastAPI(title="Character Duel API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RunWare API key
RUNWARE_API_KEY = os.getenv("RUN_WARE_API_KEY")
if not RUNWARE_API_KEY:
    print("Warning: RUN_WARE_API_KEY not found in environment variables")

# Data directories
DATA_DIR = "data"
CHARACTERS_DIR = os.path.join(DATA_DIR, "characters")
DUELS_DIR = os.path.join(DATA_DIR, "duels")

# Ensure directories exist
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(DUELS_DIR, exist_ok=True)


def generate_id() -> str:
    """Generate a short unique ID"""
    return str(uuid.uuid4())[:8]


def save_character_data(character_data: dict) -> None:
    """Save character data to JSON file"""
    char_id = character_data["id"]
    file_path = os.path.join(CHARACTERS_DIR, f"{char_id}.json")
    with open(file_path, "w") as f:
        json.dump(character_data, f, indent=2)


def load_character_data(char_id: str) -> dict:
    """Load character data from JSON file"""
    file_path = os.path.join(CHARACTERS_DIR, f"{char_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Character not found")
    
    with open(file_path, "r") as f:
        return json.load(f)


def load_all_characters() -> List[dict]:
    """Load all character data"""
    characters = []
    for filename in os.listdir(CHARACTERS_DIR):
        if filename.endswith(".json"):
            char_id = filename[:-5]  # Remove .json extension
            try:
                character = load_character_data(char_id)
                characters.append(character)
            except:
                continue
    
    # Sort by creation date (newest first)
    characters.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return characters


async def upload_image_to_runware(image_path: str, target_width: int = 1920, target_height: int = 1080) -> str:
    """
    Upload an image to RunWare and return the image ID
    Resizes image to target dimensions before uploading
    """
    try:
        if not RUNWARE_API_KEY:
            raise HTTPException(status_code=500, detail="RunWare API key not configured")
        
        # Open the image and resize it to target dimensions
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
            image_data = img_byte_arr.read()
            
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare RunWare API request for image upload
        runware_url = "https://api.runware.ai/v1"
        
        headers = {
            "Authorization": f"Bearer {RUNWARE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Generate a UUID for this upload task
        upload_uuid = str(uuid.uuid4())
        
        upload_payload = [{
            "taskType": "imageUpload",
            "taskUUID": upload_uuid,
            "image": "data:image/png;base64," + image_base64
        }]
        
        # Make API request to upload image
        response = requests.post(runware_url, headers=headers, json=upload_payload)
        
        if response.status_code != 200:
            print(f"RunWare image upload error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"RunWare image upload error: {response.text}")
        
        result = response.json()
        
        # Extract the image ID from the response
        if "data" in result and len(result["data"]) > 0:
            task_result = result["data"][0]
            
            # Check for image ID in various possible field names
            image_id = None
            for field_name in ["imageId", "id", "imageUUID", "uuid"]:
                if field_name in task_result:
                    image_id = task_result[field_name]
                    break
            
            if not image_id:
                print(f"RunWare upload response structure: {result}")
                raise HTTPException(status_code=500, detail=f"No image ID found in RunWare upload response. Available fields: {list(task_result.keys())}")
            
            return image_id
        else:
            raise HTTPException(status_code=500, detail="No image ID returned by RunWare upload API")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading image to RunWare: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


async def poll_runware_result(task_uuid: str, max_attempts: int = 300, initial_delay: float = 0.5) -> dict:
    """
    Poll RunWare API for task completion
    Returns the completed task result
    Max attempts: 300 with 0.5-2 second delays = up to 4-5 minutes timeout
    """
    runware_url = "https://api.runware.ai/v1"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    
    for attempt in range(max_attempts):
        try:
            # Query for task status using getResponse
            status_payload = [{
                "taskType": "getResponse",
                "taskUUID": task_uuid
            }]
            
            response = requests.post(runware_url, headers=headers, json=status_payload)
            
            # Log response details for debugging
            if attempt < 3:
                print(f"🔍 Polling response status: {response.status_code}")
                if response.status_code != 200:
                    print(f"🔍 Non-200 response: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for errors at the top level
                if "errors" in result and result["errors"]:
                    error_msg = result["errors"][0].get("message", "Unknown error")
                    print(f"❌ RunWare error: {error_msg}")
                    raise HTTPException(status_code=500, detail=f"RunWare error: {error_msg}")
                
                if "data" in result and len(result["data"]) > 0:
                    task_result = result["data"][0]
                    
                    # Log detailed response on first few attempts only
                    if attempt < 2:
                        print(f"🔍 Task result fields: {list(task_result.keys())}")
                        if attempt == 0:
                            print(f"🔍 Full task result: {task_result}")
                    
                    # Check if video URL is present (task completed)
                    video_url_fields = ["videoURL", "outputVideoURL", "videoPath", "video", "url"]
                    for field_name in video_url_fields:
                        if field_name in task_result and task_result[field_name]:
                            elapsed = int(time.time() - start_time)
                            print(f"✓ Video generation completed after {elapsed} seconds ({attempt + 1} attempts)")
                            return task_result
                    
                    # Log task status and progress if available
                    if "status" in task_result:
                        status = task_result['status']
                        progress = task_result.get('progress', 'unknown')
                        print(f"📈 Task status: {status} | Progress: {progress}")
                else:
                    # No data returned yet - log the full response for debugging
                    if attempt < 5:
                        print(f"🔍 No data in response yet. Full response: {result}")
                        print(f"🔍 Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Calculate elapsed time
            elapsed = int(time.time() - start_time)
            elapsed_mins = elapsed // 60
            elapsed_secs = elapsed % 60
            
            # Adaptive delay: start with shorter delays, gradually increase but cap at 2 seconds
            delay = min(initial_delay + (attempt // 30) * 0.2, 2.0)
            
            # Print status more frequently for better feedback
            if attempt % 5 == 0 or attempt < 10:
                print(f"⏳ Polling attempt {attempt + 1}/{max_attempts} - {elapsed_mins}m {elapsed_secs}s elapsed - video still generating... (delay: {delay:.1f}s)")
            
            await asyncio.sleep(delay)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error polling RunWare: {e}")
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(initial_delay)
    
    elapsed = int(time.time() - start_time)
    raise HTTPException(status_code=504, detail=f"Video generation timeout - task took longer than {elapsed} seconds to complete. This usually means the video generation failed or is stuck.")


async def process_images_to_video(image_paths: List[str], character_name: str) -> str:
    """
    Process uploaded images and generate character video using RunWare FLUX model
    Returns the path to the generated character video and character ID
    """
    try:
        if not RUNWARE_API_KEY:
            raise HTTPException(status_code=500, detail="RunWare API key not configured")
        
        # Define target video dimensions (supported by Kling 1.6 Pro)
        # Supported: 1920x1080 (16:9), 1080x1920 (9:16), 1080x1080 (1:1)
        target_width = 1280
        target_height = 720
        
        print(f"🎯 Using video dimensions: {target_width}x{target_height}")
        
        # Upload images to RunWare and get image IDs
        uploaded_image_ids = []
        for image_path in image_paths:
            # First upload each image to get an image ID (resized to target dimensions)
            upload_response = await upload_image_to_runware(image_path, target_width, target_height)
            uploaded_image_ids.append(upload_response)
        
        # Prepare RunWare API request
        runware_url = "https://api.runware.ai/v1"
        
        headers = {
            "Authorization": f"Bearer {RUNWARE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Generate a UUID for this task
        task_uuid = str(uuid.uuid4())
        
        # Create frame images array (API expects exactly 1 frame image)
        if len(uploaded_image_ids) == 0:
            raise HTTPException(status_code=400, detail="No images were successfully uploaded to RunWare")
        
        frame_images = [{
            "inputImage": uploaded_image_ids[0],
            "frame": "first"
        }]
        
        print(f"📁 Frame images array: {frame_images}")
        print(f"🆔 Using image ID: {uploaded_image_ids[0]}")
        print(f"📐 Video dimensions: {target_width}x{target_height}")
        print(f"⏱️ Duration: 5.0 seconds")
        print(f"🤖 Model: klingai:3@2")
        
        payload = [{
            "taskType": "videoInference",
            "duration": 4.0,
            "model": "google:3@3",
            "height": target_height,
            "width": target_width,
            "numberResults": 1,
            "providerSettings": {
            "google": {
                "generateAudio": True,
                "enhancePrompt": True
            }
            },
            "frameImages": frame_images,
            "positivePrompt": f"A detailed anime-style character named {character_name} in action, dynamic movement, professional character animation, vibrant colors, clean lines, fantasy RPG character",
            "taskUUID": task_uuid
        }]

        
        # Make API request to RunWare to start video generation
        print(f"🚀 Starting video generation with task UUID: {task_uuid}")
        print(f"📤 Sending payload to RunWare API...")
        
        start_request_time = time.time()
        response = requests.post(runware_url, headers=headers, json=payload)
        request_duration = time.time() - start_request_time
        
        print(f"📡 API request completed in {request_duration:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"RunWare API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"RunWare API error: {response.text}")
        
        result = response.json()
        print(f"📋 API Response: {result}")
        
        if response.status_code == 200:
            print(f"✅ Video generation task submitted successfully!")
        else:
            print(f"❌ API request failed with status {response.status_code}")
        
        # Check for immediate errors
        if "errors" in result and result["errors"]:
            error_msg = result["errors"][0].get("message", "Unknown error")
            raise HTTPException(status_code=500, detail=f"RunWare error: {error_msg}")
        
        # Poll for completion
        print(f"⏳ Waiting for video generation to complete...")
        print(f"🔄 Starting aggressive polling for task: {task_uuid}")
        print(f"📊 Expected completion time: 30-120 seconds (optimized)")
        
        polling_start_time = time.time()
        task_result = await poll_runware_result(task_uuid)
        polling_duration = time.time() - polling_start_time
        
        print(f"🎉 Video generation completed after {polling_duration:.2f} seconds of polling!")
        print(f"⚡ Total generation time: {(time.time() - start_request_time):.2f} seconds")
        
        # Extract video URL from completed task
        video_url = None
        for field_name in ["videoURL", "outputVideoURL", "videoPath", "video", "url"]:
            if field_name in task_result:
                video_url = task_result[field_name]
                break
        
        if not video_url:
            print(f"RunWare response structure: {task_result}")
            raise HTTPException(status_code=500, detail=f"No video URL found in completed task. Available fields: {list(task_result.keys())}")
        
        # Download the generated video
        print(f"⬇️ Downloading video from: {video_url}")
        
        download_start_time = time.time()
        video_response = requests.get(video_url)
        download_duration = time.time() - download_start_time
        
        print(f"📥 Video download completed in {download_duration:.2f} seconds")
        print(f"📊 Video download status: {video_response.status_code}")
        print(f"📦 Video size: {len(video_response.content)} bytes")
        if video_response.status_code == 200:
            # Generate character ID and save path
            char_id = generate_id()
            generated_path = os.path.join(CHARACTERS_DIR, f"{char_id}_generated.mp4")
            
            with open(generated_path, "wb") as f:
                f.write(video_response.content)
            
            print(f"Video saved successfully: {generated_path}")
            return generated_path, char_id
        else:
            raise HTTPException(status_code=500, detail="Failed to download generated video")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating character: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate character: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Character Duel API is running!"}


@app.get("/test_multiple_upload.html")
async def serve_test_page():
    """Serve the multiple upload test page"""
    return FileResponse("test_multiple_upload.html", media_type="text/html")


@app.post("/characters/")
async def create_character(
    images: List[UploadFile] = File(...),
    name: str = Form(...)
):
    """
    Upload multiple images and generate an AI character video
    """
    try:
        # Validate file types and minimum count
        if len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")
        
        for image in images:
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="All files must be images")
        
        print(f"Processing {len(images)} uploaded images for character '{name}'")
        
        # Generate character ID
        char_id = generate_id()
        
        # Save uploaded images
        image_paths = []
        for i, image_file in enumerate(images):
            image_path = os.path.join(CHARACTERS_DIR, f"{char_id}_image_{i}.png")
            
            # Read and save the image
            image_content = await image_file.read()
            
            # Convert to PNG if needed
            image = Image.open(io.BytesIO(image_content))
            image = image.convert("RGB")  # Ensure RGB format
            image.save(image_path, "PNG")
            image_paths.append(image_path)
        
        # Generate character video using AI
        generated_path, _ = await process_images_to_video(image_paths, name)
        
        # Create character data
        image_paths_relative = [f"characters/{char_id}_image_{i}.png" for i in range(len(images))]
        character_data = {
            "id": char_id,
            "name": name,
            "image_paths": image_paths_relative,
            "generated_path": f"characters/{char_id}_generated.mp4",
            "health": 1000,  # Default health
            "wins": 0,
            "losses": 0,
            "created_at": datetime.now().isoformat(),
            "status": "ready"
        }
        
        # Save character data
        save_character_data(character_data)
        
        return {
            "character_id": char_id,
            "name": name,
            "status": "completed",
            "message": "Character created successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating character: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create character: {str(e)}")


@app.get("/characters/")
async def list_characters():
    """Get all characters"""
    try:
        characters = load_all_characters()
        return {"characters": characters}
    except Exception as e:
        print(f"Error listing characters: {e}")
        raise HTTPException(status_code=500, detail="Failed to load characters")


@app.get("/characters/{char_id}")
async def get_character(char_id: str):
    """Get specific character details"""
    character = load_character_data(char_id)
    return character


@app.get("/characters/{char_id}/image/{image_index}")
async def get_character_image(char_id: str, image_index: int):
    """
    Get character image by index
    """
    image_path = os.path.join(CHARACTERS_DIR, f"{char_id}_image_{image_index}.png")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path, media_type="image/png")


@app.get("/characters/{char_id}/video")
async def get_character_video(char_id: str):
    """
    Get generated character video
    """
    video_path = os.path.join(CHARACTERS_DIR, f"{char_id}_generated.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(video_path, media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, timeout_keep_alive=7200)

