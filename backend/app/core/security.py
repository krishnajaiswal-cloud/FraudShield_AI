"""
Security utilities: JWT, password hashing, authentication
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT security scheme
security = HTTPBearer()

class SecurityConfig:
    """Security configuration constants"""
    ALGORITHM = "HS256"
    TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @classmethod
    def from_settings(cls, settings):
        """Create config from settings"""
        cls.SECRET_KEY = settings.JWT_SECRET_KEY
        cls.ALGORITHM = settings.JWT_ALGORITHM
        cls.TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRATION_HOURS * 60
        return cls


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    secret_key: str,
    expires_delta: Optional[timedelta] = None,
    algorithm: str = "HS256"
) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode
        secret_key: Secret key for signing
        expires_delta: Token expiration time delta
        algorithm: JWT algorithm
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(
    data: dict,
    secret_key: str,
    algorithm: str = "HS256"
) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Payload data to encode
        secret_key: Secret key for signing
        algorithm: JWT algorithm
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256"
) -> Optional[dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token to verify
        secret_key: Secret key for verification
        algorithm: JWT algorithm
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    secret_key: str = None,
    algorithm: str = "HS256"
) -> dict:
    """
    Dependency to get current authenticated user from JWT
    
    Args:
        credentials: HTTP bearer credentials
        secret_key: JWT secret key
        algorithm: JWT algorithm
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    if secret_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Secret key not configured"
        )
    
    payload = verify_token(token, secret_key, algorithm)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "payload": payload}
