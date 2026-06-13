"""
API v1 router configuration - includes all endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, upload, analysis, report, chat

# Create main router
router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(health.router)
router.include_router(upload.router)
router.include_router(analysis.router)
router.include_router(report.router)
router.include_router(chat.router)
