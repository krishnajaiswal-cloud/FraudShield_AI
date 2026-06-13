"""
Health check endpoint
"""
from fastapi import APIRouter
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns service health status
    
    Response:
        - status: "healthy" or "unhealthy"
        - service: Service name
        - version: API version
        - environment: Current environment
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint
    
    Checks if service is ready to handle requests
    
    Response:
        - ready: true/false
        - checks: Dict of component checks
    """
    checks = {
        "database": "ok",  # TODO: Actually check database connection
        "storage": "ok",   # TODO: Actually check storage
        "api": "ok"
    }
    
    return {
        "ready": all(v == "ok" for v in checks.values()),
        "checks": checks
    }


@router.get("/info", tags=["Health"])
async def info():
    """
    Get API information
    
    Returns basic API information and configuration
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.API_DESCRIPTION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "docs_url": "/api/docs",
        "openapi_url": "/api/openapi.json"
    }
