"""
Setup and initialization instructions for FraudShield AI
"""

# Backend Setup
## Prerequisites
- Python 3.9+
- pip or conda
- Virtual environment (venv or conda)

## Steps

1. Navigate to backend directory
   cd backend

2. Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies
   pip install -r requirements.txt

4. Create necessary directories
   mkdir -p app/storage/{uploads,reports,chromadb} data

5. Copy environment file
   cp .env.example .env
   # Edit .env with your configuration

6. Run migrations (when Alembic is set up)
   alembic upgrade head

7. Start backend server
   python main.py
   # API will be available at http://localhost:8000

---

# Frontend Setup
## Prerequisites
- Node.js 18+
- npm or yarn

## Steps

1. Navigate to frontend directory
   cd frontend

2. Install dependencies
   npm install

3. Create environment file
   cp .env.example .env.local
   # Ensure NEXT_PUBLIC_API_URL matches backend URL

4. Start development server
   npm run dev
   # Frontend will be available at http://localhost:3000

---

# Docker Setup
## Prerequisites
- Docker and Docker Compose

## Steps

1. From root directory
   docker-compose up --build

2. Access services
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

---

# Database Setup
## SQLite (Development)
Database file will be created automatically at: backend/data/fraudshield.db

## PostgreSQL (Production)
1. Update DATABASE_URL in .env:
   DATABASE_URL=postgresql://user:password@localhost:5432/fraudshield

2. Run migrations:
   alembic upgrade head

---

# API Documentation
Once backend is running, visit:
http://localhost:8000/api/docs (Swagger UI)
http://localhost:8000/api/redoc (ReDoc)

---

# Configuration Files to Update

1. backend/.env
   - OPENAI_API_KEY: Add your OpenAI API key
   - DATABASE_URL: Set database connection
   - JWT_SECRET_KEY: Change to secure value

2. frontend/.env.local
   - NEXT_PUBLIC_API_URL: Backend URL

3. docker-compose.yml (if using Docker)
   - Environment variables
   - Port mappings
   - Volume mappings
