# FraudShield AI - Quick Reference Guide

## Project Overview
A production-ready fraud detection system for mobile applications using AI agents, APK analysis, and RAG.

---

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js, React, TypeScript | Modern web UI |
| | Tailwind CSS | Styling |
| **Backend** | FastAPI, Python | REST API server |
| **Database** | SQLite/PostgreSQL, SQLAlchemy | Data persistence |
| **AI/ML** | OpenAI API | LLM-powered fraud detection |
| **APK Analysis** | Androguard | Android package analysis |
| **Vector DB** | ChromaDB | Vector storage for RAG |
| **Embeddings** | Sentence Transformers | Text embeddings |

---

## Key Architectural Patterns

### 1. **Clean Architecture**
- **API Layer**: HTTP request/response handling
- **Service Layer**: Business logic
- **Model Layer**: Database entities
- **Agent Layer**: AI/ML operations

### 2. **Agent-Based Design**
```
User Request
    ↓
API Endpoint
    ↓
Service Layer
    ↓
Multiple Agents (parallel):
    - APK Analyzer Agent (Androguard)
    - RAG Agent (ChromaDB + Sentence Transformers)
    - Fraud Detector Agent (OpenAI)
    ↓
Combined Results
    ↓
Response to User
```

### 3. **Separation of Concerns**
- Frontend handles UI/UX
- Backend handles business logic
- Agents handle AI/ML operations
- Database handles persistence

---

## Critical Folders & Their Purposes

### Frontend

| Folder | Purpose |
|--------|---------|
| `src/app/` | Page routing (Next.js App Router) |
| `src/components/` | Reusable React components |
| `src/hooks/` | Custom React hooks for logic |
| `src/lib/api/` | API client functions |
| `src/types/` | TypeScript type definitions |
| `src/contexts/` | Global state management |

### Backend

| Folder | Purpose |
|--------|---------|
| `app/api/v1/endpoints/` | RESTful API route handlers |
| `app/services/` | Business logic & orchestration |
| `app/agents/` | AI agents (APK, RAG, Fraud) |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic validation schemas |
| `app/database/` | Database connection & migrations |
| `app/storage/` | File uploads, reports, vector DB |
| `app/utils/` | Helper functions & analyzers |

---

## Data Flow

```
User Interface (Next.js)
        ↓
API Request (HTTP)
        ↓
FastAPI Endpoint (app/api/v1/endpoints/)
        ↓
Service Layer (app/services/)
        ↓
AI Agents (parallel):
  ├─ APK Analyzer (Androguard) → Permissions, Manifest, Behavior
  ├─ RAG Agent (ChromaDB) → Contextual Knowledge
  └─ Fraud Detector (OpenAI) → Risk Score & Recommendations
        ↓
Models & Database (SQLAlchemy)
        ↓
Storage (uploads, reports, chromadb)
        ↓
Response Data (JSON)
        ↓
React Components
        ↓
User Interface Display
```

---

## API Endpoints (Examples)

```
POST   /api/v1/auth/login              - User login
POST   /api/v1/apk/upload              - Upload APK file
POST   /api/v1/analysis                - Start analysis
GET    /api/v1/analysis/{id}           - Get analysis results
GET    /api/v1/reports                 - List reports
GET    /api/v1/reports/{id}            - Download report
GET    /api/v1/health                  - Health check
```

---

## Development Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev             # Start dev server (localhost:3000)
npm run build           # Production build
npm run lint            # Lint code
npm run type-check      # TypeScript check
```

### Backend
```bash
cd backend
python -m venv venv     # Create virtual environment
source venv/bin/activate  # Activate (Windows: venv\Scripts\activate)
pip install -r requirements.txt  # Install dependencies
python main.py          # Start server (localhost:8000)
python -m pytest        # Run tests
```

### Docker
```bash
docker-compose up       # Start all services
docker-compose up --build  # Rebuild images
docker-compose down     # Stop services
```

---

## Environment Variables

### Key Backend Variables
```
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./data/fraudshield.db
UPLOAD_DIR=./app/storage/uploads
CHROMA_DB_PATH=./app/storage/chromadb
JWT_SECRET_KEY=your-secret-key
```

### Key Frontend Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

---

## Database Models

### Core Models
- **User**: User accounts and authentication
- **Analysis**: Analysis records with metadata
- **APKFile**: Uploaded APK file information
- **Report**: Generated fraud reports
- **RiskIndicator**: Risk scores and metrics

---

## Agents Overview

### 1. **APK Analyzer Agent**
- Uses Androguard to analyze Android packages
- Extracts permissions, manifest, dex files
- Detects suspicious patterns
- Returns structured analysis data

### 2. **RAG Agent**
- Indexes fraud detection knowledge base
- Uses ChromaDB for vector storage
- Generates embeddings with Sentence Transformers
- Retrieves contextual information
- Augments analysis with relevant knowledge

### 3. **Fraud Detector Agent**
- Uses OpenAI API for intelligent analysis
- Receives APK analysis + RAG context
- Calculates risk scores (0.0-1.0)
- Provides recommendations
- Explains fraud indicators

---

## Storage Structure

```
app/storage/
├── uploads/          # User-uploaded APK files
├── reports/          # Generated analysis reports (JSON/PDF)
├── chromadb/         # Vector database files (RAG)
└── temp/             # Temporary processing files
```

---

## Testing Strategy

### Unit Tests
- Test individual services
- Mock external dependencies
- Located in `backend/tests/unit/`

### Integration Tests
- Test full workflows
- Test API endpoints
- Test database operations
- Located in `backend/tests/integration/`

---

## Production Deployment Checklist

- [ ] Database migrated to PostgreSQL
- [ ] OpenAI API key configured
- [ ] Storage migrated to S3/Cloud
- [ ] Vector DB migrated to Pinecone/Milvus
- [ ] Environment variables set for production
- [ ] CORS configured properly
- [ ] JWT secrets updated
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] Docker images built and tested
- [ ] CI/CD pipeline configured

---

## Security Best Practices

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control
3. **Input Validation**: Pydantic schemas enforce types
4. **File Upload**: Validate file types and sizes
5. **Database**: SQL injection prevention via ORM
6. **Environment**: Sensitive keys in .env (not in git)
7. **CORS**: Configure allowed origins
8. **Rate Limiting**: Prevent abuse
9. **Error Handling**: Don't expose internal errors
10. **Logging**: Audit trail for security events

---

## Performance Optimization

- **Frontend**: Next.js code splitting & lazy loading
- **Backend**: Async/await for concurrent operations
- **Database**: Indexes on frequently queried fields
- **Caching**: Redis cache for expensive operations
- **Vector DB**: Optimize embeddings & similarity search
- **File Storage**: Stream large files instead of loading to memory

---

## Monitoring & Logging

- **Backend Logs**: FastAPI logging to files
- **Frontend Logs**: Browser console for debugging
- **Database Logs**: SQLAlchemy query logging (dev only)
- **Error Tracking**: Sentry or similar service
- **Performance Metrics**: APM tools

---

## Scaling Strategy

### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use shared database (PostgreSQL)
- Use cloud storage (S3) instead of local filesystem
- Use managed vector DB (Pinecone, Milvus)

### Vertical Scaling
- Increase CPU/RAM for backend services
- Optimize database queries & indexes
- Cache frequently accessed data
- Use connection pooling

---

## Additional Resources

- **API Docs**: http://localhost:8000/api/docs (Swagger)
- **Architecture Guide**: See `docs/ARCHITECTURE.md`
- **Setup Instructions**: See `docs/SETUP.md`
- **Database Schema**: See `docs/DATABASE_SCHEMA.md`

---

## Support & Contribution

See `docs/CONTRIBUTING.md` for:
- Code style guidelines
- Testing requirements
- PR process
- Issue reporting

