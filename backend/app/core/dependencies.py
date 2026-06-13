"""
FastAPI dependency injection utilities
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def get_db() -> Generator:
    """
    Dependency to get database session
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Database session
    """
    from app.database.session import SessionLocal
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_query_params(
    skip: int = 0,
    limit: int = 10
) -> dict:
    """
    Dependency for pagination parameters
    
    Args:
        skip: Number of items to skip
        limit: Maximum items to return
        
    Returns:
        Pagination dict
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="skip must be >= 0"
        )
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 100"
        )
    
    return {"skip": skip, "limit": limit}
