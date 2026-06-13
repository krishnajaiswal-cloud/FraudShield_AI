# FraudShield AI - Backend Foundation Implementation Guide

## Overview

Complete FastAPI backend foundation for FraudShield AI with production-grade setup including:

- ✅ FastAPI application with lifespan management
- ✅ Structured logging (JSON + rotating files)
- ✅ Security utilities (JWT, password hashing)
- ✅ Exception handling middleware
- ✅ CORS and Trusted Host middleware
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Session management
- ✅ Dependency injection
- ✅ API versioning (v1)
- ✅ 5 router endpoints (health, upload, analysis, report, chat)
- ✅ Startup/shutdown events
- ✅ Configuration management (Pydantic Settings)

---

## File Locations & Purposes

### Core Configuration

#### `backend/app/core/config.py`
**Purpose**: Application settings and environment variables

- Loads settings from `.env` file using Pydantic
- Supports multiple environments (development, staging, production)
- Centralized configuration management
- Database, storage, API, security, RAG, and email settings
- Helper methods: `is_production()`, `is_development()`, etc.

**Key Classes**:
- `Settings`: Main configuration class with all environment variables

**Usage**:
```python
from app.core.config import settings
print(settings.APP_NAME)  # FraudShield AI
print(settings.DEBUG)     # True/False based on ENVIRONMENT
```

---

#### `backend/app/core/logger.py`
**Purpose**: Structured logging configuration

- JSON formatted logs for production
- Console + file handlers
- Rotating file handler (max 10MB)
- Separate error and access logs
- Configurable log levels

**Key Functions**:
- `setup_logging()`: Initialize logging system (called on startup)
- `get_logger()`: Get logger for a module

**Log Files Created**:
- `logs/app.log` - Main application logs (JSON)
- `logs/errors.log` - Error logs (detailed format)
- `logs/access.log` - HTTP access logs (JSON)

**Usage**:
```python
from app.core.logger import get_logger
logger = get_logger(__name__)
logger.info("Application started")
```

---

#### `backend/app/core/security.py`
**Purpose**: JWT and password security utilities

- JWT token creation and verification
- Password hashing with bcrypt
- HTTP Bearer token extraction
- Dependency for current user authentication

**Key Functions**:
- `hash_password()`: Hash passwords with bcrypt
- `verify_password()`: Verify password against hash
- `create_access_token()`: Generate JWT access token
- `create_refresh_token()`: Generate JWT refresh token
- `verify_token()`: Verify and decode JWT
- `get_current_user()`: FastAPI dependency for auth

**Usage**:
```python
from app.core.security import hash_password, verify_password
hashed = hash_password("password123")
if verify_password("password123", hashed):
    print("Password correct!")
```

---

#### `backend/app/core/exceptions.py`
**Purpose**: Custom exception classes for error handling

- Structured exception hierarchy
- HTTP status codes attached to exceptions
- Proper error responses with context

**Exception Classes**:
- `FraudShieldException` - Base exception
- `ValidationException` - 422 Unprocessable Entity
- `AuthenticationException` - 401 Unauthorized
- `AuthorizationException` - 403 Forbidden
- `ResourceNotFoundException` - 404 Not Found
- `ConflictException` - 409 Conflict
- `APKProcessingException` - 400 Bad Request
- `AnalysisException` - 500 Internal Server Error
- `StorageException` - 500 Internal Server Error
- `DatabaseException` - 500 Internal Server Error
- `ExternalServiceException` - 502 Bad Gateway

**Usage**:
```python
from app.core.exceptions import ResourceNotFoundException
raise ResourceNotFoundException("User", 123)
```

---

#### `backend/app/core/dependencies.py`
**Purpose**: FastAPI dependency injection utilities

- Database session dependency
- Query parameter validation
- Centralized dependency management

**Key Functions**:
- `get_db()`: FastAPI dependency for database session
- `get_query_params()`: Validate pagination parameters

**Usage**:
```python
from fastapi import Depends
from app.core.dependencies import get_db
from sqlalchemy.orm import Session

@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

---

### Database Layer

#### `backend/app/database/database.py`
**Purpose**: Database engine and session factory setup

- SQLAlchemy engine creation
- SQLite-specific optimizations (foreign keys, pragma)
- Session factory (`SessionLocal`)
- Database initialization and cleanup
- Automatic directory creation

**Key Functions**:
- `get_engine()`: Create database engine with optimizations
- `create_db_engine()`: Wrapper for engine creation
- `init_db()`: Create all tables from models
- `drop_db()`: Drop all tables (warning: data loss!)
- `get_db()`: Generator dependency for sessions

**Global Variables**:
- `engine`: SQLAlchemy engine instance
- `SessionLocal`: Session factory
- `Base`: declarative base for all models

**Usage**:
```python
from app.database.database import init_db, get_db
# Initialize database on startup
init_db()

# Use in routes
@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    ...
```

---

#### `backend/app/database/session.py`
**Purpose**: Database session management utilities

- Session manager class for context management
- Context manager for automatic commit/rollback
- Global session manager instance

**Key Classes**:
- `SessionManager`: Manages database sessions

**Key Functions**:
- `get_session()`: Get new database session

**Usage**:
```python
from app.database.session import session_manager

# Context manager usage
with session_manager.session_scope() as session:
    user = session.query(User).first()
    # Automatically commits on success, rolls back on error
```

---

### API Routes

#### `backend/app/api/v1/__init__.py`
**Purpose**: API v1 router aggregator

- Combines all v1 endpoint routers
- Applies `/api/v1` prefix to all routes
- Central router configuration

**Structure**:
```
/api/v1/
├── /health         -> health.py
├── /upload         -> upload.py
├── /analysis       -> analysis.py
├── /report         -> report.py
└── /chat           -> chat.py
```

---

#### `backend/app/api/v1/endpoints/health.py`
**Purpose**: Health check and status endpoints

**Endpoints**:
- `GET /api/v1/health` - Service health status
- `GET /api/v1/ready` - Readiness check
- `GET /api/v1/info` - API information

**Response Example**:
```json
{
  "status": "healthy",
  "service": "FraudShield AI",
  "version": "1.0.0",
  "environment": "development"
}
```

---

#### `backend/app/api/v1/endpoints/upload.py`
**Purpose**: APK file upload handling

**Endpoints**:
- `POST /api/v1/upload` - Upload APK file
- `GET /api/v1/upload/{file_id}` - Get upload status

**Response Example**:
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "app.apk",
  "size_bytes": 5242880,
  "upload_timestamp": "2024-01-15T10:30:45Z",
  "status": "received"
}
```

---

#### `backend/app/api/v1/endpoints/analysis.py`
**Purpose**: APK analysis task management

**Endpoints**:
- `POST /api/v1/analysis` - Create analysis task
- `GET /api/v1/analysis/{analysis_id}` - Get analysis results
- `GET /api/v1/analysis` - List analyses (with pagination)
- `DELETE /api/v1/analysis/{analysis_id}` - Delete analysis

**Response Example**:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "queued",
  "created_at": "2024-01-15T10:30:45Z",
  "estimated_duration_seconds": 60
}
```

---

#### `backend/app/api/v1/endpoints/report.py`
**Purpose**: Report generation and retrieval

**Endpoints**:
- `POST /api/v1/report/{analysis_id}` - Generate report
- `GET /api/v1/report/{report_id}` - Get report metadata
- `GET /api/v1/report/{report_id}/download` - Download report
- `GET /api/v1/report` - List reports (with pagination)
- `DELETE /api/v1/report/{report_id}` - Delete report

**Supported Formats**: JSON, PDF, HTML

---

#### `backend/app/api/v1/endpoints/chat.py`
**Purpose**: RAG-powered conversational analysis

**Endpoints**:
- `POST /api/v1/chat` - Chat about analysis with RAG
- `GET /api/v1/chat/history/{analysis_id}` - Get chat history
- `DELETE /api/v1/chat/history/{analysis_id}` - Clear chat history

**Request Example**:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "What are the main security risks?"
    }
  ],
  "top_k_results": 5
}
```

---

### Main Application

#### `backend/app/main.py`
**Purpose**: FastAPI application entry point

**Features**:
- Application factory with lifespan management
- CORS and TrustedHost middleware
- Exception handlers for all error types
- Database initialization on startup
- Storage directory creation
- Comprehensive logging
- Startup/shutdown events
- Root endpoints (/, /health)
- API v1 router inclusion

**Middleware Stack**:
1. TrustedHostMiddleware - Security
2. CORSMiddleware - Cross-origin requests

**Exception Handlers**:
1. FraudShieldException - Custom exceptions
2. RequestValidationError - Pydantic validation
3. General Exception - Catch-all handler

**Startup Tasks**:
1. Initialize database
2. Create storage directories
3. Log startup information

**Shutdown Tasks**:
1. Log shutdown information
2. Cleanup resources

---

## How to Run the Backend

### 1. Setup Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings
# At minimum, set:
# - OPENAI_API_KEY (for fraud detection agent)
# - DATABASE_URL (if not using default SQLite)
# - ENVIRONMENT (development/production)
```

### 3. Run Backend Server

```bash
# Development with auto-reload
python main.py

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access API

- **API Docs**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

---

## Environment Variables Reference

```env
# Application
APP_NAME=FraudShield AI
APP_VERSION=1.0.0
ENVIRONMENT=development          # development, staging, production
DEBUG=True

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_TITLE=FraudShield AI API
API_DESCRIPTION=AI-powered Android APK fraud detection system
API_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_DIR=logs

# Database
DATABASE_URL=sqlite:///./data/fraudshield.db
DATABASE_ECHO=False              # Enable SQL query logging

# Storage
UPLOAD_DIR=./app/storage/uploads
REPORT_DIR=./app/storage/reports
CHROMA_DB_PATH=./app/storage/chromadb
APK_TEMP_DIR=./app/storage/uploads/temp
APK_MAX_FILE_SIZE=104857600      # 100MB

# Security
SECRET_KEY=change-this-in-production
JWT_SECRET_KEY=change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# RAG
RAG_MODEL_NAME=all-MiniLM-L6-v2
RAG_EMBEDDING_DIMENSION=384
RAG_SIMILARITY_THRESHOLD=0.7
```

---

## Database Schema

Default: SQLite at `./data/fraudshield.db`

**Features**:
- Automatic initialization via `init_db()`
- Foreign key constraints enabled
- Created on startup if doesn't exist

**Models to Add** (ready for implementation):
- User
- APKFile
- Analysis
- AnalysisResult
- Report
- ChatMessage
- RiskIndicator

---

## Logging

**Log Directory**: `./logs/`

**Files**:
- `app.log` - Main application logs (JSON)
- `errors.log` - Error traces (detailed)
- `access.log` - HTTP requests (JSON)

**Log Levels**:
- DEBUG - Detailed diagnostic info
- INFO - General informational messages
- WARNING - Warning messages
- ERROR - Error messages
- CRITICAL - Critical failures

---

## Error Handling

All errors return standardized JSON responses:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "error_type"
}
```

**Exception Mapping**:
- `400 Bad Request` - APK Processing, Validation
- `401 Unauthorized` - Authentication failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - External service error

---

## Security Features

1. **JWT Authentication** - Token-based auth (ready to implement)
2. **Password Hashing** - Bcrypt hashing with salt
3. **CORS** - Cross-origin request control
4. **TrustedHost** - Host header validation
5. **Input Validation** - Pydantic model validation
6. **SQL Injection Prevention** - SQLAlchemy ORM
7. **Rate Limiting** - Ready to implement
8. **Error Handling** - No internal error exposure in production

---

## API Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload APK
```bash
curl -X POST \
  -F "file=@app.apk" \
  http://localhost:8000/api/v1/upload
```

### Create Analysis
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_id":"550e8400-e29b-41d4-a716-446655440000"}' \
  http://localhost:8000/api/v1/analysis
```

### Get Analysis Results
```bash
curl http://localhost:8000/api/v1/analysis/550e8400-e29b-41d4-a716-446655440000
```

---

## Next Steps - What's Ready to Build

1. **Database Models** - Create SQLAlchemy models in `app/models/`
2. **Services** - Implement business logic in `app/services/`
3. **Agents** - Build AI agents in `app/agents/`
4. **Endpoint Logic** - Complete endpoint implementations
5. **Authentication** - Implement login/register endpoints
6. **Testing** - Add unit and integration tests

---

## Project Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── health.py       ✅ Complete
│   │   │   ├── upload.py       ✅ Complete
│   │   │   ├── analysis.py     ✅ Complete
│   │   │   ├── report.py       ✅ Complete
│   │   │   └── chat.py         ✅ Complete
│   │   └── __init__.py         ✅ Complete
│   ├── core/
│   │   ├── config.py           ✅ Complete
│   │   ├── logger.py           ✅ Complete
│   │   ├── security.py         ✅ Complete
│   │   ├── exceptions.py       ✅ Complete
│   │   └── dependencies.py     ✅ Complete
│   ├── database/
│   │   ├── database.py         ✅ Complete
│   │   ├── session.py          ✅ Complete
│   │   └── __init__.py         ✅ Complete
│   ├── main.py                 ✅ Complete
│   └── __init__.py             ✅ Complete
├── requirements.txt            ✅ Updated
└── README.md                   ✅ This file
```

---

## Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY` and `JWT_SECRET_KEY` to secure random values
- [ ] Configure `OPENAI_API_KEY`
- [ ] Migrate database to PostgreSQL (for production)
- [ ] Setup S3 for file storage (instead of local filesystem)
- [ ] Configure monitoring and error tracking (Sentry)
- [ ] Setup log aggregation (ELK, CloudWatch)
- [ ] Enable rate limiting
- [ ] Configure backups
- [ ] Setup CI/CD pipeline
- [ ] Deploy with proper SSL/TLS certificates

---

## Support & Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Python-Jose Docs](https://python-jose.readthedocs.io/)

