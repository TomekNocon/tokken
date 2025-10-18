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


async def process_sketch_to_character(sketch_path: str, character_name: str) -> str:
    """
    Process uploaded sketch and generate character using RunWare FLUX model
    Returns the path to the generated character image and character ID
    """
    try:
        if not RUNWARE_API_KEY:
            raise HTTPException(status_code=500, detail="RunWare API key not configured")
        
        # Read and encode the sketch image
        with open(sketch_path, "rb") as image_file:
            image_data = image_file.read()
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare RunWare API request
        runware_url = "https://api.runware.ai/v1"
        
        headers = {
            "Authorization": f"Bearer {RUNWARE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Generate a UUID for this task
        task_uuid = str(uuid.uuid4())
        
        payload = [{
            "taskType": "imageInference",
            "taskUUID": task_uuid,
            "model": "runware:101@1",
            "positivePrompt": f"A detailed anime-style character named {character_name}, full body, professional character design, vibrant colors, clean lines, fantasy RPG character",
            "negativePrompt": "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, signature, draft, sketch lines",
            "seedImage": "data:image/png;base64," + image_base64,
            "strength": 0.85,
            "CFGScale": 7.5,
            "steps": 30,
            "width": 1024,
            "height": 1024
        }]

        
        # Make API request to RunWare
        response = requests.post(runware_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"RunWare API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"RunWare API error: {response.text}")
        
        result = response.json()
        
        # Extract the generated image URL
        if "data" in result and len(result["data"]) > 0:
            # RunWare returns the image URL in the first task result
            task_result = result["data"][0]
            
            # Check various possible field names for the image URL
            image_url = None
            for field_name in ["imageURL", "outputImageURL", "imagePath", "image", "url"]:
                if field_name in task_result:
                    image_url = task_result[field_name]
                    break
            
            if not image_url:
                print(f"RunWare response structure: {result}")
                raise HTTPException(status_code=500, detail=f"No image URL found in RunWare response. Available fields: {list(task_result.keys())}")
            
            # Download the generated image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                # Generate character ID and save path
                char_id = generate_id()
                generated_path = os.path.join(CHARACTERS_DIR, f"{char_id}_generated.png")
                
                with open(generated_path, "wb") as f:
                    f.write(img_response.content)
                
                return generated_path, char_id
            else:
                raise HTTPException(status_code=500, detail="Failed to download generated image")
        else:
            raise HTTPException(status_code=500, detail="No image generated by RunWare API")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating character: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate character: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Character Duel API is running!"}


@app.post("/characters/")
async def create_character(
    sketch: UploadFile = File(...),
    name: str = Form(...)
):
    """
    Upload a sketch and generate an AI character
    """
    try:
        # Validate file type
        if not sketch.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate character ID
        char_id = generate_id()
        
        # Save uploaded sketch
        sketch_path = os.path.join(CHARACTERS_DIR, f"{char_id}_sketch.png")
        
        # Read and save the sketch
        sketch_content = await sketch.read()
        
        # Convert to PNG if needed
        image = Image.open(io.BytesIO(sketch_content))
        image = image.convert("RGB")  # Ensure RGB format
        image.save(sketch_path, "PNG")
        
        # Generate character using AI
        generated_path, _ = await process_sketch_to_character(sketch_path, name)
        
        # Create character data
        character_data = {
            "id": char_id,
            "name": name,
            "sketch_path": f"characters/{char_id}_sketch.png",
            "generated_path": f"characters/{char_id}_generated.png",
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


@app.get("/characters/{char_id}/image/{image_type}")
async def get_character_image(char_id: str, image_type: str):
    """
    Get character image (sketch or generated)
    image_type: 'sketch' or 'generated'
    """
    if image_type not in ["sketch", "generated"]:
        raise HTTPException(status_code=400, detail="image_type must be 'sketch' or 'generated'")
    
    image_path = os.path.join(CHARACTERS_DIR, f"{char_id}_{image_type}.png")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

