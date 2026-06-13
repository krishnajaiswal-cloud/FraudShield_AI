"""
Database session management
"""
from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages database sessions"""
    
    def __init__(self):
        self.session_local = SessionLocal
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.session_local()
    
    @contextmanager
    def session_scope(self):
        """
        Context manager for database sessions
        
        Automatically commits on success or rolls back on exception
        
        Usage:
            with session_manager.session_scope() as session:
                user = session.query(User).first()
        """
        session = self.session_local()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {str(e)}")
            raise
        finally:
            session.close()


# Global session manager instance
session_manager = SessionManager()


def get_session() -> Session:
    """
    Get a database session
    
    Returns:
        Database session
    """
    return session_manager.get_session()
