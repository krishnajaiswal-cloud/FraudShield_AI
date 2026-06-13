"""
Enhanced configuration with Pydantic Settings
"""
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    Priority:
    1. Environment variables
    2. .env file
    3. Default values
    """
    
    # ==================== Application ====================
    APP_NAME: str = "FraudShield AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    
    # ==================== API ====================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_TITLE: str = "FraudShield AI API"
    API_DESCRIPTION: str = "AI-powered Android APK fraud detection system"
    API_VERSION: str = "1.0.0"
    
    # ==================== Logging ====================
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    # ==================== Database ====================
    DATABASE_URL: str = "sqlite:///./data/fraudshield.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True
    
    # ==================== Storage ====================
    UPLOAD_DIR: str = "./app/storage/uploads"
    REPORT_DIR: str = "./app/storage/reports"
    CHROMA_DB_PATH: str = "./app/storage/chromadb"
    APK_TEMP_DIR: str = "./app/storage/uploads/temp"
    APK_MAX_FILE_SIZE: int = 104857600  # 100MB
    
    # ==================== Security ====================
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # ==================== CORS ====================
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # ==================== OpenAI ====================
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # ==================== RAG Configuration ====================
    RAG_MODEL_NAME: str = "all-MiniLM-L6-v2"
    RAG_EMBEDDING_DIMENSION: int = 384
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_TOP_K_RESULTS: int = 5
    
    # ==================== APK Analysis ====================
    APK_ANALYSIS_TIMEOUT: int = 300  # 5 minutes
    APK_TEMP_RETENTION_HOURS: int = 24
    
    # ==================== Rate Limiting ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # ==================== Email (Optional) ====================
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # ==================== Monitoring ====================
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = False
    METRICS_PORT: int = 8001

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_flag(cls, value):
        """Accept common environment DEBUG strings used by other tooling."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
        return value
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra attributes from environment
        extra = "allow"
    
    def get_database_url(self) -> str:
        """
        Get database URL with environment-specific adjustments
        
        For SQLite: Resolves relative paths to absolute paths based on backend directory
        This ensures database works regardless of working directory when app starts.
        """
        url = self.DATABASE_URL
        
        # Ensure SQLite path exists and is absolute
        if "sqlite" in url:
            db_path = url.replace("sqlite:///", "")
            
            # Skip in-memory databases
            if db_path == ":memory:":
                return url
            
            # Convert to Path object
            db_path_obj = Path(db_path)
            
            # If relative path, resolve relative to backend directory
            if not db_path_obj.is_absolute():
                # Get the backend directory (parent of app directory)
                app_dir = Path(__file__).parent.parent
                backend_dir = app_dir.parent
                db_path_obj = backend_dir / db_path
            
            # Ensure directory exists
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Return URL with absolute path
            abs_db_path = str(db_path_obj.resolve())
            # Convert Windows paths to forward slashes for SQLite
            abs_db_path = abs_db_path.replace("\\", "/")
            return f"sqlite:///{abs_db_path}"
        
        return url
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT == "testing"


# Create global settings instance
settings = Settings()

# Override debug setting based on environment
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
elif settings.ENVIRONMENT == "development":
    settings.DEBUG = True
elif settings.ENVIRONMENT == "testing":
    settings.DEBUG = True
    settings.DATABASE_URL = "sqlite:///:memory:"
