"""Analysis module for FraudShield AI.

Provides security analysis utilities for APK files:
- androguard_parser: Low-level APK parsing
- url_extractor: URL and domain extraction
- permission_analyzer: Android permission risk analysis
"""

from app.analysis.androguard_parser import AndroguardParser, AndroguardParseError
from app.analysis.url_extractor import URLExtractor, extract_urls_from_strings
from app.analysis.permission_analyzer import PermissionAnalyzer, PermissionRisk, PermissionCategory

__all__ = [
    'AndroguardParser',
    'AndroguardParseError',
    'URLExtractor',
    'extract_urls_from_strings',
    'PermissionAnalyzer',
    'PermissionRisk',
    'PermissionCategory',
]
