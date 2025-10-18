# Character Duel Backend

FastAPI backend for the AI character dueling platform.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. Run the development server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

## API Endpoints

- `GET /` - Health check
- `POST /characters/` - Upload sketch and create character
- `GET /characters/` - List all characters  
- `GET /characters/{id}` - Get character details
- `GET /characters/{id}/image/{type}` - Get character images (sketch/generated)

## Testing the API

You can test the character creation endpoint using curl:

```bash
curl -X POST "http://localhost:8000/characters/" \
  -F "sketch=@your_sketch.png" \
  -F "name=Fire Dragon"
```

Or visit http://localhost:8000/docs for the interactive API documentation.

## Data Storage

Characters are stored as:
- `data/characters/{char_id}.json` - Character metadata
- `data/characters/{char_id}_sketch.png` - Original sketch
- `data/characters/{char_id}_generated.png` - AI-generated character