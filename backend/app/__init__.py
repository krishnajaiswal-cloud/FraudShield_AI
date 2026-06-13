"""
FraudShield AI Backend Application Package

This package contains the FastAPI application and all business logic
for the FraudShield AI fraud detection system.
"""
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Version
__version__ = "1.0.0"
__author__ = "FraudShield AI"
__description__ = "AI-powered Android APK fraud detection system"

logger.debug(f"Initializing {__name__} v{__version__}")

