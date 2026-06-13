"""
FraudShield AI - FastAPI Application Entry Point

Production-grade FastAPI backend with:
- Structured logging
- Exception handling middleware
- CORS configuration
- Database initialization
- Startup/shutdown events
- Health checks
- API versioning
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from contextlib import asynccontextmanager
import os

# Import configuration and utilities
from app.core.config import settings
from app.core.logger import setup_logging, get_logger
from app.core.exceptions import FraudShieldException
from app.database.database import init_db
from app.api.v1 import router as api_v1_router

# Initialize logging
setup_logging(log_level=settings.LOG_LEVEL, log_dir=settings.LOG_DIR)
logger = get_logger(__name__)


# ==================== Database Validation ====================

def validate_database_configuration():
    """
    Validate database configuration and connectivity on startup
    
    Checks:
    - Database path resolution (absolute vs relative)
    - File exists (for SQLite)
    - Connection can be established
    - All required tables exist
    
    Raises:
    - Exception if critical issues found
    """
    from sqlalchemy import inspect, text
    from app.database.database import engine, SessionLocal
    from pathlib import Path
    
    logger.info("Validating database configuration...")
    
    # Get resolved database URL
    resolved_url = settings.get_database_url()
    logger.info(f"  Resolved database URL: {resolved_url}")
    
    # For SQLite, check file exists
    if "sqlite" in resolved_url and ":memory:" not in resolved_url:
        db_path = resolved_url.replace("sqlite:///", "").replace("/", "\\")
        if db_path.startswith("C:"):  # Windows absolute path
            db_file = Path(db_path)
        else:
            db_file = Path(db_path)
        
        if db_file.exists():
            size_kb = db_file.stat().st_size / 1024
            logger.info(f"  Database file exists: {db_file} ({size_kb:.1f} KB)")
        else:
            logger.warning(f"  Database file not found: {db_file}")
            logger.warning(f"  Will be created on first write")
    
    # Test connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        logger.info("  Database connection: OK")
    except Exception as e:
        logger.error(f"  Database connection: FAILED - {str(e)}")
        raise
    
    # Check tables exist
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = {'analyses', 'findings', 'reports', 'chat_histories'}
        found_tables = set(tables)
        
        if required_tables.issubset(found_tables):
            logger.info(f"  Database schema: OK ({len(tables)} tables)")
        else:
            missing = required_tables - found_tables
            logger.warning(f"  Database schema: INCOMPLETE (missing: {', '.join(missing)})")
            logger.warning(f"  Tables will be created by init_db()")
    except Exception as e:
        logger.error(f"  Schema check failed: {str(e)}")
        # Don't fail here - let init_db() handle it


# ==================== Startup & Shutdown Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events
    
    Runs on startup:
    - Validate database configuration
    - Initialize database
    - Log startup information
    - Create storage directories
    
    Runs on shutdown:
    - Log shutdown information
    - Cleanup resources
    """
    # Startup
    logger.info("=" * 60)
    logger.info("FraudShield AI - Starting Application")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Database (configured): {settings.DATABASE_URL}")
    logger.info(f"API: {settings.API_HOST}:{settings.API_PORT}")
    
    try:
        # Validate database configuration
        validate_database_configuration()
        
        # Initialize database tables
        init_db()
        logger.info("Database initialization: OK")
    except Exception as e:
        logger.error(f"Database initialization: FAILED - {str(e)}")
        raise
    
    # Create storage directories
    for directory in [settings.UPLOAD_DIR, settings.REPORT_DIR, 
                      settings.CHROMA_DB_PATH, settings.APK_TEMP_DIR]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Storage directory ready: {directory}")
    
    logger.info("=" * 60)
    logger.info("Application started successfully")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("FraudShield AI - Shutting Down")
    logger.info("=" * 60)


# ==================== Application Creation ====================

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ==================== Middleware ====================

# Custom CORS Middleware Decorator
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """Simple CORS middleware that adds headers to all responses"""
    # Handle OPTIONS requests (preflight)
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "600",
            }
        )
    
    # For regular requests, get the response and add CORS headers
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response

# Trusted Host Middleware - Security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)


# ==================== Exception Handlers ====================

@app.exception_handler(FraudShieldException)
async def fraudshield_exception_handler(request: Request, exc: FraudShieldException):
    """Handle FraudShield custom exceptions"""
    logger.error(
        f"FraudShield Exception: {exc.message}",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "status_code": exc.status_code,
            "type": "FraudShieldException",
            **({"extra": exc.detail} if exc.detail else {})
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    error_count = len(exc.errors())
    logger.warning(
        f"Validation Error: {error_count} errors",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "type": "validation_error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    # Return generic error in production
    if settings.is_production():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "type": "internal_server_error",
            },
        )
    
    # Return detailed error in development
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
        },
    )


# ==================== Root Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    
    Returns basic information about the API
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/api/docs",
        "api_v1": "/api/v1",
        "health": "/health",
        "status": "operational"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Simple health status check for load balancers and monitoring
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


# ==================== API Routes ====================

# Include all API v1 routes
app.include_router(api_v1_router)


# ==================== Application Entry ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        f"Starting Uvicorn server: {settings.API_HOST}:{settings.API_PORT}"
    )
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )
