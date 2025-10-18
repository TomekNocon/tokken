# AI Property Video Generator

An AI-powered application that transforms property photos into engaging videos with the ability to add yourself to the scene. Perfect for real estate marketing, Airbnb listings, and property showcases.

## 🎯 What It Does

- **Upload Property Photos**: Drag & drop 1-3 property images
- **Add Yourself**: Combine your photo with property images using AI
- **Generate Videos**: Create professional property tour videos
- **Multiple Variations**: Generate multiple video versions with different styles
- **Platform Optimization**: Tailor videos for Airbnb, Instagram, TikTok, Facebook, etc.

## 🏗️ Architecture

**Backend (Python/FastAPI)**
- Character generation and video creation
- AI image combination using RunWare API
- File-based storage for simplicity
- RESTful API endpoints

**Frontend (React/Next.js)**
- Modern UI with drag & drop uploads
- Real-time progress tracking
- Multiple video comparison view
- Responsive design with dark/light themes

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- RunWare API key

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/{characters,duels}

# Set up environment variables
cp .env.example .env
# Edit .env and add your RunWare API key:
# RUN_WARE_API_KEY=your_api_key_here

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
tokken/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── models.py              # Data models
│   ├── requirements.txt       # Python dependencies
│   ├── services/
│   │   ├── character_service.py      # Character management
│   │   ├── runware_service.py        # AI video generation
│   │   └── image_combination_service.py  # Image combining
│   └── data/
│       ├── characters/        # Generated content storage
│       └── duels/            # Future feature
├── frontend/
│   ├── app/
│   │   └── dashboard/
│   │       └── page.tsx      # Main application UI
│   ├── components/           # Reusable UI components
│   └── package.json         # Node.js dependencies
└── README.md               # This file
```

## 🎨 Features

### Core Features
- **Property Photo Upload**: Support for 1-3 images with drag & drop
- **AI Video Generation**: Convert static photos to dynamic videos
- **Style Customization**: Choose from luxury, fun, business, or family vibes
- **Platform Targeting**: Optimize for different social media platforms

### Advanced Features
- **"Add Yourself" Mode**: AI-powered person insertion into property scenes
- **Multiple Video Generation**: Create and compare multiple video variations
- **Real-time Progress**: Live generation status with progress bars
- **Responsive Layout**: Optimized for desktop and mobile devices

### Video Customization
- Opening text overlays
- Color mood settings (warm, cool, natural, vibrant)
- Music mood options
- Custom call-to-action text
- Transition speed control

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
RUN_WARE_API_KEY=your_runware_api_key

# Optional (defaults provided)
RUNWARE_API_URL=https://api.runware.ai/tasks
DEFAULT_VIDEO_WIDTH=1280
DEFAULT_VIDEO_HEIGHT=720
DEFAULT_VIDEO_DURATION=15
```

### API Endpoints
- `POST /characters/` - Create character and generate video
- `GET /characters/{id}` - Get character details
- `GET /characters/{id}/video` - Download character video
- `POST /combine-images/` - Combine person with property image
- `GET /combinations/{id}/image` - Get combined image

## 📱 Usage

1. **Upload Photos**: Add 1-3 property images
2. **Set Details**: Enter property name and select type
3. **Choose Style**: Pick platform and vibe
4. **Add Yourself** (Optional): Upload your photo to be added to the scene
5. **Generate**: Create your first video
6. **Generate More**: Create additional variations
7. **Download & Share**: Export videos for your marketing needs

## 🛠️ Development

### Adding New Features
- Backend services in `backend/services/`
- Frontend components in `frontend/components/`
- API routes in `backend/main.py`

### Running Tests
```bash
# Backend tests (when available)
cd backend
pytest

# Frontend tests (when available)
cd frontend
npm test
```

## 📋 Requirements

### System Requirements
- 4GB+ RAM recommended
- Stable internet connection for AI processing
- Modern web browser

### API Dependencies
- RunWare API account and key
- Sufficient API credits for video generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and development purposes. Please ensure you have proper licensing for any AI services used in production.

## 🆘 Troubleshooting

### Common Issues

**"RunWare API Error"**
- Check your API key in `.env`
- Verify sufficient API credits
- Ensure stable internet connection

**"Video Generation Timeout"**
- Large images may take longer to process
- Check RunWare service status
- Try with smaller image files

**"Port Already in Use"**
- Change backend port: `uvicorn main:app --port 8001`
- Change frontend port: `npm run dev -- --port 3001`

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Check RunWare API status and documentation
