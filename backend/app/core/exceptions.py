"""
Custom exception classes for FraudShield AI
"""
from fastapi import HTTPException, status
from typing import Optional, Any


class FraudShieldException(Exception):
    """Base exception for FraudShield AI"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationException(FraudShieldException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class AuthenticationException(FraudShieldException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(FraudShieldException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundException(FraudShieldException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            f"{resource} with id {identifier} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ConflictException(FraudShieldException):
    """Raised when there's a conflict (e.g., duplicate resource)"""
    
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message,
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class APKProcessingException(FraudShieldException):
    """Raised when APK processing fails"""
    
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class AnalysisException(FraudShieldException):
    """Raised when analysis fails"""
    
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class StorageException(FraudShieldException):
    """Raised when storage operations fail"""
    
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class DatabaseException(FraudShieldException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ExternalServiceException(FraudShieldException):
    """Raised when external service call fails (OpenAI, etc.)"""
    
    def __init__(self, service: str, message: str, detail: Optional[dict] = None):
        super().__init__(
            f"{service} error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        )
