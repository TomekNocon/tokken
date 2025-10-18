# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered character dueling platform where users:
1. Upload hand-drawn sketches of characters
2. AI converts sketches to animated characters
3. Users create duels between characters with text prompts
4. LLM judges creativity of prompts and determines winner
5. Sora 2 API generates battle video showing the fight

## MVP Architecture (Simplified)

**No database, no Docker, no complex setup** - Using file-based storage and API-only AI services.

### Tech Stack

**Backend (Python)**:
- FastAPI - API endpoints
- File system storage (JSON + images)
- API integrations: Replicate (character generation), OpenAI (prompt judging), Sora 2 (videos)

**Frontend (React)**:
- React + Vite
- Axios for API calls
- React Dropzone for file uploads
- Local state management (no Redux)

### Project Structure
```
character-duel-mvp/
├── backend/
│   ├── main.py              # Single FastAPI file with all endpoints
│   ├── requirements.txt     # Python dependencies
│   └── data/
│       ├── characters/      # Character JSON + images
│       └── duels/          # Duel JSON + videos
└── frontend/
    ├── src/
    │   ├── App.jsx         # Main app component
    │   ├── pages/
    │   │   ├── Upload.jsx  # Character creation
    │   │   ├── Gallery.jsx # Character gallery
    │   │   ├── Duel.jsx    # Duel creation
    │   │   └── Result.jsx  # Battle results
    │   └── components/
    │       └── CharacterCard.jsx
    └── package.json
```

## Backend Implementation

### Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
replicate==0.15.0
openai==1.3.0
requests==2.31.0
Pillow==10.1.0
```

### API Endpoints
```python
POST   /characters/           # Upload sketch + generate character
GET    /characters/           # List all characters
GET    /characters/{id}/image # Serve character images
POST   /duels/               # Create duel with prompts
GET    /duels/{id}           # Get duel result + video
```

### Data Models (JSON Files)
```python
# Character: data/characters/{char_id}.json
{
    "id": "char_001",
    "name": "Fire Dragon",
    "sketch_path": "characters/char_001_sketch.png",
    "generated_path": "characters/char_001_generated.png",
    "health": 850,
    "wins": 3,
    "losses": 1,
    "created_at": "2024-01-01T12:00:00Z"
}

# Duel: data/duels/{duel_id}.json
{
    "id": "duel_001",
    "char1_id": "char_001",
    "char2_id": "char_002",
    "char1_prompt": "Breathes massive fire blast",
    "char2_prompt": "Creates ice shield and counters",
    "winner": "char_002",
    "video_path": "duels/duel_001_video.mp4",
    "completed_at": "2024-01-01T12:30:00Z"
}
```

### Backend Commands
```bash
# Setup
cd backend
pip install -r requirements.txt
mkdir -p data/{characters,duels}

# Run development server
uvicorn main:app --reload --port 8000
```

## Frontend Implementation

### Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0", 
    "axios": "^1.6.0",
    "react-dropzone": "^14.2.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.1.0",
    "vite": "^4.5.0"
  }
}
```

### Pages Required
1. **Upload.jsx** - Drag/drop sketch upload + character naming
2. **Gallery.jsx** - Grid view of all generated characters
3. **Duel.jsx** - Select 2 characters + enter battle prompts
4. **Result.jsx** - Show winner + battle video

### Frontend Commands
```bash
# Setup
npx create-vite frontend --template react
cd frontend
npm install axios react-dropzone

# Run development server
npm run dev
```

## Implementation Timeline (2-3 weeks)

### Week 1: Core Setup
**Backend**: Setup FastAPI + character creation endpoint
**Frontend**: Setup React + upload page

### Week 2: Character System  
**Backend**: Character generation via Replicate API
**Frontend**: Gallery page + character display

### Week 3: Battle System
**Backend**: Duel endpoints + OpenAI judging + Sora 2 videos
**Frontend**: Duel creation + result pages

## AI Integration Patterns

### Character Generation (Replicate)
```python
response = await replicate_client.run(
    "stability-ai/stable-diffusion:db21e45d",
    input={
        "image": sketch_file,
        "prompt": "anime character, detailed, colorful game art",
        "controlnet": "lineart"
    }
)
```

### Prompt Judging (OpenAI)
```python
response = await openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": f"""Judge these battle prompts (1-10 creativity):
        Player 1: {prompt1}
        Player 2: {prompt2}
        Return JSON: {{"winner": 1 or 2, "score1": X, "score2": Y}}"""
    }]
)
```

### Video Generation (Sora 2)
```python
response = await sora2_client.generate(
    prompt=f"Epic anime battle: {char1_name} vs {char2_name}. {winner_prompt} wins. 15 seconds.",
    duration=15
)
```

## MVP Scope

**Included**:
- Character upload & AI generation
- Text-based battles with prompt judging
- Video generation of battle results
- Simple file-based storage

**NOT in MVP**:
- User accounts/authentication
- Rankings/leaderboards
- Health system mechanics
- Multiple arenas
- Real-time updates
- Database
- Complex animations

## Development Notes

- Start with backend character creation endpoint first
- Use hardcoded API keys for MVP (move to env vars later)
- Focus on core flow: sketch → character → duel → video
- Deploy backend/frontend separately (Railway/Vercel)
- Estimated cost: $50-100/month for API calls