"""
Database configuration and session management
"""
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()


def get_engine(database_url: str, debug: bool = False, is_sqlite: bool = True):
    """
    Create database engine with optimal settings
    
    Args:
        database_url: Database connection URL
        debug: Enable SQL echo
        is_sqlite: SQLite-specific optimizations
        
    Returns:
        SQLAlchemy Engine
    """
    if "sqlite" in database_url:
        # SQLite specific configuration
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=debug,
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    else:
        # PostgreSQL or other database
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=debug,
        )
    
    return engine


def create_db_engine(
    database_url: str,
    debug: bool = False,
    echo_pool: bool = False
) -> Engine:
    """
    Create database engine
    
    Args:
        database_url: Database connection URL
        debug: Enable SQL debugging
        echo_pool: Enable connection pool logging
        
    Returns:
        SQLAlchemy Engine
    """
    engine = get_engine(database_url, debug=debug)
    
    if echo_pool:
        logging.basicConfig()
        logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
    
    return engine


# Import settings here to avoid circular imports
from app.core.config import settings

# Create engine
engine = create_db_engine(
    settings.get_database_url(),
    debug=settings.DATABASE_ECHO
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def init_db():
    """
    Initialize database tables
    
    Creates all tables defined in Base.metadata
    """
    try:
        # Import models to register them with Base before creating tables
        from app.database.models import Analysis, Finding, Report, ChatHistory
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def drop_db():
    """
    Drop all database tables
    
    WARNING: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    
    Usage:
        from fastapi import Depends
        
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
