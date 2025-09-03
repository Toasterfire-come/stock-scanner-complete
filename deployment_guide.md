# Stock Scanner Deployment Guide

## Current Status ✅
- Frontend: Built and ready for static deployment
- Backend: Running on port 8000
- Database: Using in-memory fallback (MongoDB optional)

## Quick Start

### 1. Backend Server
```bash
cd backend
source venv/bin/activate  # If using virtual environment
python server.py
```
The backend will run on http://localhost:8000

### 2. Frontend (Static Files)
The frontend has been built and is located in `/workspace/frontend/build/`

To serve with any static server:
```bash
cd frontend/build
python3 -m http.server 3001  # Or use nginx, apache, etc.
```

## Configuration

### Backend Environment Variables
- `MONGO_URL`: MongoDB connection string (optional)
- `EXTERNAL_API_URL`: https://api.retailtradescanner.com (default)
- `CORS_ORIGINS`: Allowed origins (default: *)

### Frontend Environment Variables
- `REACT_APP_BACKEND_URL`: Backend API URL (currently: http://localhost:8000)
- `REACT_APP_API_PASSWORD`: API password for authentication
- `REACT_APP_PAYPAL_CLIENT_ID`: PayPal integration (optional)

## API Endpoints

### Working Endpoints
- `GET /api/health` - Health check endpoint ✅
- `GET /api/platform-stats` - Platform statistics ✅
- `GET /api/stocks` - Stock data (uses external API)
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration

## Deployment Options

### Option 1: Local Development
- Backend: `python server.py` (port 8000)
- Frontend: `npm start` (port 3000) or serve build files

### Option 2: Production with Static Server
1. Backend: Deploy to any Python hosting (Heroku, AWS, etc.)
2. Frontend: Deploy build folder to any static hosting (Netlify, Vercel, S3, etc.)

### Option 3: Docker (Optional)
Create Dockerfile for backend and serve frontend with nginx

## Troubleshooting

### Issue: "Backend temporarily unavailable"
**Solution**: Fixed by correcting the backend URL in `.env` file from `.con` to `.com` and pointing to local backend

### Issue: Global variable syntax errors
**Solution**: Fixed by moving `global db_disabled` declarations to the beginning of functions

### Issue: Backend not binding to port
**Solution**: Added uvicorn.run() in main block of server.py

## Current Architecture
```
Frontend (React) --> Backend (FastAPI) --> External API / Local DB
   Port 3000/3001      Port 8000         api.retailtradescanner.com
```

## Security Notes
- CORS is configured to allow all origins (adjust for production)
- API password is included in environment variables
- HTTPS redirect middleware is available but disabled for local development