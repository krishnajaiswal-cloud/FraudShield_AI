# FraudShield AI - Complete Setup & Installation Guide

## System Requirements

- Node.js 16+ (recommended 18+)
- npm 8+ or yarn
- Python 3.10+ (for backend)
- SQLite3

## Project Structure

```
FraudShield-AI/
├── backend/           # FastAPI backend (Python)
├── frontend/          # React frontend (Node.js)
└── README.md         # This file
```

## Step 1: Backend Setup

### Prerequisites

- Python 3.10+
- pip package manager
- Virtual environment tool

### Installation

```bash
# Navigate to backend
cd FraudShield-AI/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if needed)
python scripts/init_db.py
```

### Running Backend

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Step 2: Frontend Setup

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
# Navigate to frontend
cd FraudShield-AI/frontend

# Install dependencies
npm install

# or with yarn
yarn install
```

### Environment Configuration

Create `.env` file in `frontend/` directory:

```
VITE_API_URL=http://localhost:8000
```

### Running Frontend

```bash
# Start development server
npm run dev

# or with yarn
yarn dev
```

Frontend will be available at: `http://localhost:5173`

## Step 3: Full Application Setup (One Command)

### Using npm scripts (from root)

```bash
# Install all dependencies
npm install

# Run both backend and frontend simultaneously
npm run dev
```

This requires the following setup in the root `package.json`:

```json
{
  "scripts": {
    "dev": "concurrently \"cd backend && python -m uvicorn app.main:app --reload\" \"cd frontend && npm run dev\""
  }
}
```

## Development Workflow

### Terminal 1 - Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

Now you can access the application at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Building for Production

### Backend Build

```bash
# No build step needed, but you can create a Docker image
docker build -t fraudshield-backend .
docker run -p 8000:8000 fraudshield-backend
```

### Frontend Build

```bash
cd frontend
npm run build
npm run preview
```

Production build output will be in `frontend/dist/`

## API Endpoints Reference

### Upload & Analysis

- `POST /api/v1/upload` - Upload APK file
- `POST /api/v1/analysis` - Create analysis record
- `POST /api/v1/analysis/{id}/run` - Run analysis
- `GET /api/v1/analysis/{id}` - Get analysis status and results

### Chat

- `POST /api/v1/chat` - Send chat message
- `GET /api/v1/chat/{analysisId}` - Get chat history

## Frontend Routes

- `/` - Landing page
- `/scan` - Upload page
- `/analysis/:id` - Analysis progress
- `/dashboard/:analysisId` - Results dashboard
- `/chat/:analysisId` - AI chat interface

## Database

### SQLite Setup

Backend uses SQLite by default. Database file location:

```
backend/app/data/fraudshield.db
```

To reset database:

```bash
rm backend/app/data/fraudshield.db
python backend/scripts/init_db.py
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests (Optional)

```bash
cd frontend
npm run test
```

## Troubleshooting

### Issue: CORS errors in browser console

**Solution**: Ensure backend is running on port 8000 and frontend CORS config is correct.

Check `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

### Issue: "Connection refused" errors

**Solution**: Backend might not be running. Check:
- Backend terminal shows `Uvicorn running on http://0.0.0.0:8000`
- Port 8000 is not blocked by firewall

### Issue: Node modules errors

**Solution**: Clear cache and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Python import errors in backend

**Solution**: Ensure virtual environment is activated:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Performance Optimization

### Frontend

- Code splitting enabled
- React Query caching configured
- Image optimization
- CSS minification

### Backend

- Database connection pooling
- Request caching headers
- Async processing for APK analysis

## Security Considerations

1. **API Key** (if implemented): Store securely in environment variables
2. **File Upload**: Validate file types and sizes
3. **HTTPS**: Use HTTPS in production
4. **CORS**: Configure appropriate CORS policies
5. **Database**: Use environment variables for connection strings

## Docker Deployment (Optional)

### Backend Dockerfile

```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Getting Help

### Check Logs

Backend: Look at terminal running `uvicorn`
Frontend: Check browser console (F12)

### API Documentation

Visit: `http://localhost:8000/docs` (when backend is running)

### Common Commands

```bash
# Clear frontend cache
rm -rf frontend/.next frontend/node_modules frontend/.dist

# Reset backend
rm -rf backend/app/data
python backend/scripts/init_db.py

# Kill port 8000 (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# Kill port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Run backend and frontend
3. ✅ Access dashboard at http://localhost:5173
4. ✅ Upload an APK for analysis
5. ✅ Review security report
6. ✅ Chat with AI analyst

Enjoy analyzing APKs with FraudShield AI! 🛡️
