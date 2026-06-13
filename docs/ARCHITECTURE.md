# FraudShield AI - Architecture & Folder Structure

## Complete Folder Tree

```
FraudShield-AI/
│
├── frontend/                          # Next.js React Frontend
│   ├── public/                        # Static assets
│   │   ├── assets/                    # Images, logos, media
│   │   └── icons/                     # SVG icons and favicon
│   │
│   ├── src/                           # Source code
│   │   ├── app/                       # Next.js App Router (Pages)
│   │   │   ├── layout.tsx             # Root layout
│   │   │   ├── page.tsx               # Home page
│   │   │   ├── api/                   # API route handlers
│   │   │   ├── dashboard/             # Dashboard page
│   │   │   ├── analysis/              # Analysis page
│   │   │   ├── reports/               # Reports page
│   │   │   └── settings/              # Settings page
│   │   │
│   │   ├── components/                # React Components (by feature)
│   │   │   ├── common/                # Shared components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Button.tsx
│   │   │   ├── dashboard/             # Dashboard components
│   │   │   │   ├── StatCard.tsx
│   │   │   │   ├── Chart.tsx
│   │   │   │   └── RecentActivity.tsx
│   │   │   ├── analysis/              # Analysis feature components
│   │   │   │   ├── FileUploader.tsx
│   │   │   │   ├── AnalysisResult.tsx
│   │   │   │   └── RiskIndicator.tsx
│   │   │   └── reports/               # Reports feature components
│   │   │       ├── ReportViewer.tsx
│   │   │       └── ExportOptions.tsx
│   │   │
│   │   ├── hooks/                     # Custom React Hooks
│   │   │   ├── useAnalysis.ts         # Analysis hook
│   │   │   ├── useAuth.ts             # Authentication hook
│   │   │   ├── useFetch.ts            # Data fetching hook
│   │   │   └── useLocalStorage.ts     # LocalStorage hook
│   │   │
│   │   ├── lib/                       # Utility functions
│   │   │   ├── api/                   # API client functions
│   │   │   │   ├── client.ts          # Axios/Fetch client
│   │   │   │   ├── analysis.ts        # Analysis endpoints
│   │   │   │   ├── reports.ts         # Reports endpoints
│   │   │   │   └── auth.ts            # Auth endpoints
│   │   │   └── utils/                 # Helper functions
│   │   │       ├── validators.ts      # Form validators
│   │   │       ├── formatters.ts      # Data formatters
│   │   │       ├── constants.ts       # App constants
│   │   │       └── helpers.ts         # General helpers
│   │   │
│   │   ├── contexts/                  # React Context Providers
│   │   │   ├── AuthContext.tsx        # Authentication state
│   │   │   ├── ThemeContext.tsx       # Theme state
│   │   │   └── NotificationContext.tsx
│   │   │
│   │   ├── types/                     # TypeScript type definitions
│   │   │   ├── api.ts                 # API response types
│   │   │   ├── analysis.ts            # Analysis types
│   │   │   ├── common.ts              # Common types
│   │   │   └── index.ts               # Type exports
│   │   │
│   │   └── styles/                    # Global styles
│   │       ├── globals.css            # Global Tailwind styles
│   │       └── variables.css          # CSS variables
│   │
│   ├── next.config.js                 # Next.js configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   ├── postcss.config.js              # PostCSS configuration
│   ├── package.json                   # Frontend dependencies
│   └── README.md                      # Frontend documentation
│
├── backend/                           # FastAPI Python Backend
│   ├── app/                           # Main application package
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── __init__.py                # Package initializer
│   │   │
│   │   ├── api/                       # API Routes
│   │   │   ├── __init__.py
│   │   │   └── v1/                    # API version 1
│   │   │       ├── __init__.py
│   │   │       └── endpoints/         # Endpoint modules
│   │   │           ├── __init__.py
│   │   │           ├── analysis.py    # /api/v1/analysis endpoints
│   │   │           ├── reports.py     # /api/v1/reports endpoints
│   │   │           ├── apk.py         # /api/v1/apk endpoints
│   │   │           ├── auth.py        # /api/v1/auth endpoints
│   │   │           └── health.py      # /api/v1/health endpoint
│   │   │
│   │   ├── core/                      # Core configurations
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Environment & settings config
│   │   │   ├── security.py            # JWT, authentication logic
│   │   │   ├── dependencies.py        # FastAPI dependency injection
│   │   │   └── exceptions.py          # Custom exceptions
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM Models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base model class
│   │   │   ├── analysis.py            # Analysis model
│   │   │   ├── apk_file.py            # APK file model
│   │   │   ├── report.py              # Report model
│   │   │   ├── user.py                # User model
│   │   │   └── risk_indicator.py      # Risk indicator model
│   │   │
│   │   ├── schemas/                   # Pydantic Request/Response Schemas
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py            # Analysis request/response schemas
│   │   │   ├── apk.py                 # APK schemas
│   │   │   ├── report.py              # Report schemas
│   │   │   ├── user.py                # User schemas
│   │   │   └── common.py              # Common response schemas
│   │   │
│   │   ├── services/                  # Business Logic Layer
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py    # Analysis orchestration
│   │   │   ├── apk_service.py         # APK handling service
│   │   │   ├── report_service.py      # Report generation service
│   │   │   ├── auth_service.py        # Authentication service
│   │   │   ├── storage_service.py     # File storage service
│   │   │   └── notification_service.py
│   │   │
│   │   ├── agents/                    # AI Agents
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py          # Base agent class
│   │   │   │
│   │   │   ├── apk_analyzer/          # APK Analysis Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── apk_agent.py       # Main APK analyzer
│   │   │   │   ├── permissions.py     # Permission analyzer
│   │   │   │   ├── manifest.py        # AndroidManifest analyzer
│   │   │   │   └── behavior.py        # Behavior analyzer
│   │   │   │
│   │   │   ├── rag/                   # RAG Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rag_agent.py       # RAG orchestrator
│   │   │   │   ├── retriever.py       # Document retriever
│   │   │   │   ├── indexer.py         # Document indexer
│   │   │   │   └── embeddings.py      # Embedding generator
│   │   │   │
│   │   │   └── fraud_detector/        # Fraud Detection Agent
│   │   │       ├── __init__.py
│   │   │       ├── detector.py        # Main detector
│   │   │       ├── patterns.py        # Pattern detection
│   │   │       └── scoring.py         # Risk scoring
│   │   │
│   │   ├── database/                  # Database Layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Database session factory
│   │   │   ├── session.py             # Session management
│   │   │   ├── migrations/            # Alembic migrations
│   │   │   │   ├── versions/          # Migration versions
│   │   │   │   ├── alembic.ini        # Alembic configuration
│   │   │   │   ├── env.py
│   │   │   │   └── script.py.mako
│   │   │   └── repositories.py        # Repository pattern (optional)
│   │   │
│   │   ├── utils/                     # Utilities & Helpers
│   │   │   ├── __init__.py
│   │   │   ├── logger.py              # Logging setup
│   │   │   ├── validators.py          # Input validators
│   │   │   ├── analyzers/             # Analysis utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── risk_analyzer.py   # Risk analysis
│   │   │   │   ├── pattern_detector.py
│   │   │   │   └── stat_calculator.py
│   │   │   ├── file_handler.py        # File handling utilities
│   │   │   ├── formatters.py          # Data formatters
│   │   │   └── constants.py           # Constants
│   │   │
│   │   └── storage/                   # Storage Management
│   │       ├── uploads/               # Uploaded APK files
│   │       ├── reports/               # Generated reports
│   │       ├── chromadb/              # ChromaDB vector store
│   │       └── temp/                  # Temporary files
│   │
│   ├── tests/                         # Test Suite
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest configuration
│   │   ├── unit/                      # Unit tests
│   │   │   ├── test_services.py
│   │   │   ├── test_agents.py
│   │   │   └── test_utils.py
│   │   └── integration/               # Integration tests
│   │       ├── test_api.py
│   │       ├── test_analysis_flow.py
│   │       └── test_database.py
│   │
│   ├── main.py                        # Entry point (alias for app/main.py)
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Docker configuration
│   ├── .dockerignore                  # Docker ignore file
│   └── README.md                      # Backend documentation
│
├── docs/                              # Project Documentation
│   ├── ARCHITECTURE.md                # This file
│   ├── API.md                         # API documentation
│   ├── SETUP.md                       # Setup instructions
│   ├── DEPLOYMENT.md                  # Deployment guide
│   ├── DATABASE_SCHEMA.md             # Database schema
│   └── CONTRIBUTING.md                # Contributing guidelines
│
├── .gitignore                         # Git ignore rules
├── .env.example                       # Environment template
├── docker-compose.yml                 # Docker compose file
└── README.md                          # Root README
```

---

## Folder Purposes

### Frontend Structure

#### `public/`
**Purpose**: Static assets served directly by Next.js
- `assets/`: Images, logos, brand materials
- `icons/`: SVG icons, favicon

#### `src/app/`
**Purpose**: Next.js App Router pages (routing structure mirrors file system)
- `dashboard/`: Main dashboard page
- `analysis/`: APK analysis upload and results page
- `reports/`: Generated reports viewing page
- `settings/`: User preferences and configuration

#### `src/components/`
**Purpose**: Reusable React components organized by feature
- `common/`: Shared components (Header, Footer, Buttons, etc.)
- `dashboard/`: Dashboard-specific components
- `analysis/`: Analysis feature components
- `reports/`: Report viewing components

#### `src/hooks/`
**Purpose**: Custom React hooks for logic reuse
- `useAnalysis`: Manage analysis state and operations
- `useAuth`: Authentication logic
- `useFetch`: Generic data fetching

#### `src/lib/`
**Purpose**: Utility functions and business logic
- `api/`: API client and endpoint functions
- `utils/`: Helper functions, validators, formatters

#### `src/contexts/`
**Purpose**: React Context API for global state
- Authentication state, theme, notifications

#### `src/types/`
**Purpose**: TypeScript type definitions
- API response types, domain models, enums

---

### Backend Structure

#### `app/api/v1/endpoints/`
**Purpose**: RESTful API route handlers
- `analysis.py`: POST/GET analysis operations
- `apk.py`: APK file upload and analysis endpoints
- `reports.py`: Report generation and retrieval
- `auth.py`: Authentication and user management
- Organized by resource type (RESTful design)

#### `app/core/`
**Purpose**: Core application configurations and utilities
- `config.py`: Environment variables, settings management
- `security.py`: JWT token generation, password hashing
- `dependencies.py`: FastAPI dependency injection (DB session, auth, etc.)
- `exceptions.py`: Custom exception classes

#### `app/models/`
**Purpose**: SQLAlchemy ORM models (database tables)
- `analysis.py`: Analysis records
- `apk_file.py`: APK file metadata
- `report.py`: Generated reports
- `user.py`: User accounts
- `risk_indicator.py`: Risk scores and indicators

#### `app/schemas/`
**Purpose**: Pydantic models for request/response validation
- Validates input from API requests
- Defines response shapes returned to frontend
- Provides API documentation via Swagger

#### `app/services/`
**Purpose**: Business logic layer (service layer pattern)
- `analysis_service.py`: Orchestrates analysis workflow
- `apk_service.py`: APK file handling and parsing
- `report_service.py`: Report generation logic
- Decouples API endpoints from business logic
- Enables code reuse across endpoints

#### `app/agents/`
**Purpose**: AI Agent implementations

##### `agents/apk_analyzer/`
- Analyzes Android APK files using Androguard
- Extracts permissions, manifest data
- Detects suspicious behavior patterns
- Returns structured analysis results

##### `agents/rag/`
- RAG (Retrieval-Augmented Generation) system
- Indexes fraud detection knowledge base
- Retrieves relevant context for analysis
- Uses ChromaDB for vector storage
- Sentence Transformers for embeddings

##### `agents/fraud_detector/`
- OpenAI-powered fraud detection
- Uses RAG context for intelligent analysis
- Scores risk levels
- Generates recommendations

#### `app/database/`
**Purpose**: Data access layer
- `base.py`: Database connection and session factory
- `session.py`: Session lifecycle management
- `migrations/`: Alembic schema version control
- Ensures data consistency and transactions

#### `app/utils/`
**Purpose**: Helper functions and utilities
- `analyzers/`: Risk analysis, pattern detection
- `logger.py`: Structured logging
- `validators.py`: Input validation
- `formatters.py`: Data formatting
- `file_handler.py`: File operations

#### `app/storage/`
**Purpose**: File storage management
- `uploads/`: Stores uploaded APK files
- `reports/`: Generated PDF/JSON reports
- `chromadb/`: Vector database files
- `temp/`: Temporary processing files

#### `tests/`
**Purpose**: Test suite
- `unit/`: Unit tests for isolated components
- `integration/`: End-to-end workflow tests

---

## Clean Architecture Benefits

### Separation of Concerns
- **API Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Model Layer**: Database entities
- **Agent Layer**: AI/ML operations

### Scalability
- Easy to add new endpoints without modifying existing code
- Agents can be independently scaled
- Database can be migrated without changing services

### Testability
- Mock services in unit tests
- Test business logic independently
- Integration tests verify full workflows

### Maintainability
- Clear responsibility boundaries
- Easy to locate and fix bugs
- Self-documenting folder structure

### Reusability
- Hooks and utilities can be shared across components
- Services can be called from multiple endpoints
- Agents can be used independently

---

## Data Flow

```
User (Frontend) 
    ↓
API Request (Next.js API Routes)
    ↓
FastAPI Endpoints (app/api/v1/endpoints/)
    ↓
Services (app/services/)
    ↓
Agents (app/agents/) + Models (app/models/)
    ↓
Database (app/database/) + Storage (app/storage/)
    ↓
Response Data
    ↓
React Components (src/components/)
```

---

## Development Guidelines

1. **Add new features**: Create new folders following the pattern
2. **Database changes**: Use Alembic migrations
3. **API changes**: Update schemas first, then endpoints
4. **Testing**: Write tests for services and agents
5. **Documentation**: Update docstrings and README files

---

## Deployment Notes

- Frontend: Deploy to Vercel, Netlify, or Docker
- Backend: Deploy to AWS, GCP, or Docker
- Database: SQLite (dev) → PostgreSQL (prod)
- Storage: Local filesystem (dev) → S3 (prod)
- Vectors: ChromaDB (dev) → Pinecone/Milvus (prod)
