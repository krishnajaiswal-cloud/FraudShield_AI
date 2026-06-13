# FraudShield AI

A comprehensive fraud detection system for mobile applications using AI agents, APK analysis, and RAG (Retrieval-Augmented Generation).

## Project Overview

FraudShield AI is a full-stack application designed to detect and analyze fraudulent activities in mobile applications through intelligent analysis, machine learning, and RAG-powered insights.

## Tech Stack

### Frontend
- **Framework**: Next.js 14+
- **UI Library**: React 18+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API / Zustand

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Database**: SQLite with SQLAlchemy ORM
- **APK Analysis**: Androguard
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
- **LLM**: OpenAI API

## Project Structure

### Root Directory
```
FraudShield-AI/
├── frontend/          # Next.js React application
├── backend/           # FastAPI Python application
├── docs/              # Project documentation
├── docker-compose.yml # Container orchestration
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Quick Start

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Backend
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./data/fraudshield.db
UPLOAD_DIR=./app/storage/uploads
REPORT_DIR=./app/storage/reports
CHROMA_DB_PATH=./app/storage/chromadb

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features

- **APK Analysis**: Automated Android package analysis with Androguard
- **Fraud Detection**: AI-powered fraud detection using OpenAI
- **RAG System**: Intelligent retrieval-augmented generation for insights
- **Report Generation**: Comprehensive fraud analysis reports
- **Dashboard**: Real-time analytics and monitoring
- **Responsive UI**: Mobile-friendly interface

## Architecture Principles

- **Clean Architecture**: Separation of concerns across layers
- **Microservices Ready**: Modular design for scaling
- **API-First**: RESTful API design
- **Type Safety**: Full TypeScript and Python type hints
- **Testing**: Comprehensive unit and integration tests
- **Documentation**: Self-documenting code with docstrings

## Documentation

See the [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed folder structure explanation.

## License

MIT License - See LICENSE file for details
