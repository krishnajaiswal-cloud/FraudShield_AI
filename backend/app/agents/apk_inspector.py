"""
APK Inspector Agent for FraudShield AI

Main orchestrator for APK security analysis.
Coordinates all analysis modules and generates comprehensive threat reports.

This agent:
- Loads and parses APK files
- Extracts security-relevant data
- Analyzes components, permissions, and embedded resources
- Generates structured threat intelligence
- Handles errors gracefully

Clean Architecture:
- Agent = orchestration layer
- Analysis modules = domain logic
- Models/Schemas = data layer
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import asdict

from app.analysis.androguard_parser import AndroguardParser, AndroguardParseError
from app.analysis.url_extractor import URLExtractor
from app.analysis.permission_analyzer import PermissionAnalyzer
from app.agents.risk_scorer import risk_scorer
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class APKAnalysisError(Exception):
    """Exception raised for APK analysis failures."""
    pass


class APKInspector:
    """
    Android APK Inspector Agent.
    
    Orchestrates complete security analysis of APK files:
    1. Parses APK structure using Androguard
    2. Extracts manifest metadata
    3. Analyzes permissions for risks
    4. Scans for suspicious URLs/domains
    5. Extracts components (Activities, Services, etc.)
    6. Computes file hashes
    7. Generates threat intelligence report
    
    Usage:
        inspector = APKInspector()
        result = inspector.analyze_apk("/path/to/app.apk")
        print(json.dumps(result, indent=2))
    """
    
    def __init__(self):
        """Initialize APK Inspector with analysis modules."""
        self.permission_analyzer = PermissionAnalyzer()
        self.url_extractor = URLExtractor(include_common=False)
        logger.info("APKInspector initialized")
    
    def analyze_apk(self, apk_path: str) -> Dict[str, Any]:
        """
        Analyze Android APK file for security threats.
        
        Complete analysis pipeline:
        - Validate APK file
        - Parse APK structure
        - Extract metadata
        - Analyze permissions
        - Extract components
        - Scan for URLs/domains
        - Compute hashes
        - Generate report
        
        Args:
            apk_path: Path to APK file
            
        Returns:
            Dictionary with comprehensive analysis results
            
        Raises:
            APKAnalysisError: On analysis failure
            ValidationException: On invalid input
        
        Example return value:
        {
            "status": "success",
            "apk_name": "app.apk",
            "package_name": "com.example.app",
            "version_name": "1.0.0",
            "version_code": "1",
            "app_name": "Example App",
            "file_size": 5242880,
            "md5": "abc123...",
            "sha256": "def456...",
            "components": {...},
            "permissions": {...},
            "urls_and_domains": {...},
            "analysis_summary": {...}
        }
        """
        try:
            logger.info(f"Starting APK analysis: {apk_path}")
            
            # Validate input
            self._validate_apk_path(apk_path)
            
            # Parse APK
            parser = AndroguardParser(apk_path)
            logger.info(f"✓ APK parsed successfully")
            
            # Extract basic metadata
            metadata = self._extract_metadata(parser)
            logger.info(f"✓ Metadata extracted: {metadata['package_name']}")
            
            # Extract components
            components = self._extract_components(parser)
            logger.info(f"✓ Components extracted: {sum(len(c) for c in components.values())} total")
            
            # Analyze permissions
            permissions_data = self._analyze_permissions(parser)
            logger.info(f"✓ Permissions analyzed: {permissions_data['total_permissions']} total")
            
            # Extract and analyze URLs
            urls_data = self._extract_urls_and_domains(parser)
            logger.info(f"✓ URLs extracted: {urls_data['url_count']} total, {urls_data['suspicious_count']} suspicious")
            
            # Compute hashes
            hashes = self._compute_hashes(parser)
            logger.info(f"✓ Hashes computed")
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(
                metadata, permissions_data, urls_data, components
            )
            
            # Calculate risk score using RiskScorer
            logger.info(f"Calculating comprehensive risk assessment")
            risk_assessment = risk_scorer.score_apk({
                "permissions": permissions_data.get("all_permissions", []),
                "urls": urls_data.get("classified_urls", []),
                "domains": urls_data.get("domains", []),
                "activities": components.get("activities", []),
                "services": components.get("services", []),
                "receivers": components.get("broadcast_receivers", []),
                "providers": components.get("content_providers", [])
            })
            logger.info(f"✓ Risk assessment calculated: score={risk_assessment.risk_score}, severity={risk_assessment.severity}")
            
            # Build complete response
            result = {
                "status": "success",
                "apk_name": Path(apk_path).name,
                "package_name": metadata['package_name'],
                "version_name": metadata['version_name'],
                "version_code": metadata['version_code'],
                "app_name": metadata['app_name'],
                "file_size": metadata['file_size'],
                "md5": hashes['md5'],
                "sha256": hashes['sha256'],
                "components": components,
                "permissions": permissions_data,
                "urls_and_domains": urls_data,
                "analysis_summary": analysis_summary,
                "risk_assessment": risk_assessment.to_dict()
            }
            
            logger.info(f"✓ APK analysis completed successfully")
            return result
        
        except ValidationException as e:
            logger.error(f"Validation error: {e}")
            raise
        except AndroguardParseError as e:
            logger.error(f"APK parsing error: {e}")
            raise APKAnalysisError(f"Failed to parse APK: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            raise APKAnalysisError(f"APK analysis failed: {str(e)}") from e
    
    def _validate_apk_path(self, apk_path: str) -> None:
        """
        Validate APK file path.
        
        Args:
            apk_path: Path to validate
            
        Raises:
            ValidationException: If invalid
        """
        if not apk_path:
            raise ValidationException("APK path is required")
        
        path = Path(apk_path)
        
        if not path.exists():
            raise ValidationException(f"APK file not found: {apk_path}")
        
        if not path.is_file():
            raise ValidationException(f"APK path is not a file: {apk_path}")
        
        if not str(path).lower().endswith('.apk'):
            raise ValidationException(f"File must have .apk extension: {apk_path}")
        
        if path.stat().st_size == 0:
            raise ValidationException(f"APK file is empty: {apk_path}")
        
        logger.debug(f"APK path validation passed: {apk_path}")
    
    def _extract_metadata(self, parser: AndroguardParser) -> Dict[str, Any]:
        """
        Extract APK metadata.
        
        Args:
            parser: Androguard parser instance
            
        Returns:
            Dictionary with metadata
        """
        return {
            'package_name': parser.get_package_name(),
            'version_name': parser.get_version_name(),
            'version_code': parser.get_version_code(),
            'app_name': parser.get_app_name(),
            'file_size': parser.get_apk_size()
        }
    
    def _extract_components(self, parser: AndroguardParser) -> Dict[str, list]:
        """
        Extract Android components.
        
        Args:
            parser: Androguard parser instance
            
        Returns:
            Dictionary with component lists
        """
        return {
            'activities': parser.get_activities(),
            'services': parser.get_services(),
            'broadcast_receivers': parser.get_receivers(),
            'content_providers': parser.get_providers()
        }
    
    def _analyze_permissions(self, parser: AndroguardParser) -> Dict[str, Any]:
        """
        Analyze permissions for security risks.
        
        Args:
            parser: Androguard parser instance
            
        Returns:
            Dictionary with permission analysis
        """
        permissions = parser.get_permissions()
        summary = self.permission_analyzer.get_permission_summary(permissions)
        
        return {
            'total_permissions': summary['total_permissions'],
            'dangerous_permissions': summary['dangerous_permissions'],
            'risk_score': summary['risk_score'],
            'risk_counts': summary['risk_counts'],
            'dangerous_list': summary['dangerous_permissions_list'],
            'suspicious_combinations': summary['suspicious_combinations'],
            'all_permissions': permissions
        }
    
    def _extract_urls_and_domains(self, parser: AndroguardParser) -> Dict[str, Any]:
        """
        Extract and analyze URLs and domains.
        
        Args:
            parser: Androguard parser instance
            
        Returns:
            Dictionary with URLs and domains
        """
        # Combine strings from resources and DEX
        all_strings = parser.get_strings() + parser.get_dex_strings()
        logger.debug(f"Analyzing {len(all_strings)} strings for URLs")
        
        # Extract URLs
        urls, suspicious_urls, classified = self.url_extractor.extract_urls_and_analyze(all_strings)
        
        # Extract domains
        domains = self.url_extractor.extract_domains(urls)
        
        return {
            'url_count': len(urls),
            'domain_count': len(domains),
            'suspicious_count': len(suspicious_urls),
            'urls': urls,
            'domains': domains,
            'suspicious_urls': suspicious_urls,
            'classified_urls': classified
        }
    
    def _compute_hashes(self, parser: AndroguardParser) -> Dict[str, str]:
        """
        Compute file hashes.
        
        Args:
            parser: Androguard parser instance
            
        Returns:
            Dictionary with MD5 and SHA256 hashes
        """
        md5, sha256 = parser.compute_file_hashes()
        return {'md5': md5, 'sha256': sha256}
    
    def _generate_analysis_summary(
        self,
        metadata: Dict[str, Any],
        permissions: Dict[str, Any],
        urls: Dict[str, Any],
        components: Dict[str, list]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis summary.
        
        Args:
            metadata: Extracted metadata
            permissions: Permission analysis
            urls: URL/domain analysis
            components: Android components
            
        Returns:
            Analysis summary dictionary
        """
        # Calculate overall threat level
        threat_level = self._calculate_threat_level(permissions, urls, components)
        
        # Generate risk indicators
        indicators = self._generate_risk_indicators(permissions, urls, components)
        
        return {
            'threat_level': threat_level,
            'risk_indicators': indicators,
            'permission_risk_score': permissions['risk_score'],
            'dangerous_permissions': permissions['dangerous_permissions'],
            'suspicious_combinations': len(permissions['suspicious_combinations']),
            'suspicious_urls': urls['suspicious_count'],
            'total_components': sum(len(c) for c in components.values()),
            'exported_components': self._count_exported_components(components)
        }
    
    def _calculate_threat_level(
        self,
        permissions: Dict[str, Any],
        urls: Dict[str, Any],
        components: Dict[str, list]
    ) -> str:
        """
        Calculate overall threat level.
        
        Args:
            permissions: Permission analysis
            urls: URL analysis
            components: Component analysis
            
        Returns:
            Threat level: "critical", "high", "medium", "low", or "clean"
        """
        score = 0.0
        
        # Permission risk
        perm_score = permissions['risk_score']
        score += perm_score * 0.4
        
        # Suspicious combinations
        if permissions['suspicious_combinations']:
            score += 0.3
        
        # Suspicious URLs
        if urls['suspicious_count'] > 0:
            score += min(urls['suspicious_count'] / 5, 0.2)
        
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "clean"
    
    def _generate_risk_indicators(
        self,
        permissions: Dict[str, Any],
        urls: Dict[str, Any],
        components: Dict[str, list]
    ) -> list:
        """
        Generate list of risk indicators.
        
        Args:
            permissions: Permission analysis
            urls: URL analysis
            components: Component analysis
            
        Returns:
            List of risk indicator strings
        """
        indicators = []
        
        # Permission indicators
        if permissions['risk_counts']['critical'] > 0:
            indicators.append(f"✗ {permissions['risk_counts']['critical']} critical permissions")
        
        if permissions['risk_counts']['high'] > 0:
            indicators.append(f"✗ {permissions['risk_counts']['high']} high-risk permissions")
        
        if permissions['suspicious_combinations']:
            indicators.append(f"⚠ {len(permissions['suspicious_combinations'])} suspicious permission combinations")
        
        # URL indicators
        if urls['suspicious_count'] > 0:
            indicators.append(f"⚠ {urls['suspicious_count']} suspicious URLs/domains")
        
        # Component indicators
        if components['services']:
            indicators.append(f"ℹ {len(components['services'])} background services")
        
        if components['broadcast_receivers']:
            indicators.append(f"ℹ {len(components['broadcast_receivers'])} broadcast receivers")
        
        # If no indicators, app appears clean
        if not indicators:
            indicators.append("✓ No major security concerns detected")
        
        return indicators
    
    def _count_exported_components(self, components: Dict[str, list]) -> int:
        """Count potentially exported components (simplified)."""
        # In a full implementation, would check android:exported attribute
        return len(components['services']) + len(components['broadcast_receivers'])


def create_apk_inspector() -> APKInspector:
    """Factory function to create APK Inspector."""
    return APKInspector()


# Convenience function for one-shot analysis
def analyze_apk(apk_path: str) -> Dict[str, Any]:
    """
    Quick analysis function.
    
    Args:
        apk_path: Path to APK file
        
    Returns:
        Analysis results
    """
    inspector = APKInspector()
    return inspector.analyze_apk(apk_path)
