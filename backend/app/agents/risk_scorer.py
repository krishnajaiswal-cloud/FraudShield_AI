"""
Risk Scoring Agent for FraudShield AI

Converts APK findings into an explainable cybersecurity risk score.
Analyzes permissions, URLs, domains, and APK characteristics to produce
a comprehensive risk assessment with detailed explanations.

Architecture:
- RiskScorer: Main orchestrator
- Individual scoring methods for each risk category
- Logging for audit trail
- Detailed output with reasoning
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RiskSeverity(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskFactor:
    """Individual risk factor with explanation"""
    factor: str
    category: str  # permissions, urls, domains, characteristics
    score: int
    reason: str
    severity: RiskSeverity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "factor": self.factor,
            "category": self.category,
            "score": self.score,
            "reason": self.reason,
            "severity": self.severity.value
        }


@dataclass
class RiskAssessment:
    """Complete risk assessment output"""
    risk_score: int  # 0-100
    severity: RiskSeverity
    risk_factors: List[RiskFactor]
    summary: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "risk_score": self.risk_score,
            "severity": self.severity.value,
            "risk_factors": [factor.to_dict() for factor in self.risk_factors],
            "summary": self.summary,
            "timestamp": self.timestamp
        }


class RiskScorer:
    """
    Cybersecurity Risk Scoring Engine
    
    Analyzes APK findings and generates explainable risk scores.
    Factors considered:
    - Dangerous permissions (SMS, contacts, accessibility, etc.)
    - Permission combinations (camera + microphone, location + internet)
    - Suspicious URLs and IP addresses
    - Phishing indicators
    - APK structure characteristics
    
    Output: Risk score 0-100, severity level, and detailed explanations
    """
    
    # Permission scoring weights
    PERMISSION_WEIGHTS = {
        # SMS access - credential theft vector
        "READ_SMS": 15,
        "RECEIVE_SMS": 15,
        "SEND_SMS": 20,
        
        # Contact access
        "READ_CONTACTS": 10,
        "WRITE_CONTACTS": 10,
        
        # Call log access
        "READ_CALL_LOG": 15,
        "WRITE_CALL_LOG": 15,
        
        # Accessibility service - keystroke logging vector
        "BIND_ACCESSIBILITY_SERVICE": 25,
        
        # Device installation
        "REQUEST_INSTALL_PACKAGES": 15,
        "SYSTEM_ALERT_WINDOW": 20,
        
        # Location tracking
        "ACCESS_FINE_LOCATION": 12,
        "ACCESS_COARSE_LOCATION": 8,
        
        # Camera and microphone
        "CAMERA": 10,
        "MICROPHONE": 10,
        "RECORD_AUDIO": 10,
        
        # Internet access
        "INTERNET": 5,
        
        # Storage access
        "READ_EXTERNAL_STORAGE": 5,
        "WRITE_EXTERNAL_STORAGE": 5,
    }
    
    # Dangerous permission combinations (synergistic threats)
    DANGEROUS_COMBINATIONS = {
        ("CAMERA", "MICROPHONE"): (15, "Surveillance capability - can record audio/video"),
        ("CAMERA", "RECORD_AUDIO"): (15, "Surveillance capability - can record audio/video"),
        ("ACCESS_FINE_LOCATION", "INTERNET"): (12, "Tracking capability - location + exfiltration"),
        ("READ_CONTACTS", "INTERNET"): (10, "Contact harvesting - can exfiltrate contacts"),
        ("READ_SMS", "INTERNET"): (15, "OTP interception - credential theft vector"),
        ("SEND_SMS", "INTERNET"): (12, "Premium SMS fraud capability"),
        ("BIND_ACCESSIBILITY_SERVICE", "INTERNET"): (20, "Keystroke logging + exfiltration"),
    }
    
    # Suspicious URL indicators
    SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".gq", ".cf", ".pw"}
    
    # Known phishing patterns
    PHISHING_PATTERNS = [
        "login", "signin", "authenticate", "verify", "confirm", "update",
        "account", "paypal", "amazon", "apple", "google", "microsoft",
        "bank", "credential", "password"
    ]
    
    # Known suspicious domains
    SUSPICIOUS_DOMAIN_PATTERNS = [
        "bit.ly", "tinyurl", "short.link",  # URL shorteners
        "pastebin", "github.raw",  # Code repositories (payload hosting)
    ]
    
    def __init__(self):
        """Initialize risk scorer"""
        logger.info("Risk Scorer initialized")
    
    def score_apk(self, apk_findings: Dict[str, Any]) -> RiskAssessment:
        """
        Calculate comprehensive risk score for APK
        
        Args:
            apk_findings: Dictionary containing APK analysis findings
                - permissions: List[str]
                - urls: List[Dict] with 'url' and 'risk_score'
                - domains: List[str]
                - activities: List[str]
                - services: List[str]
                - receivers: List[str]
                - providers: List[str]
        
        Returns:
            RiskAssessment with score, severity, factors, and explanation
        """
        logger.info("Starting APK risk assessment")
        
        risk_factors: List[RiskFactor] = []
        total_score = 0
        
        # Extract findings
        permissions = apk_findings.get("permissions", [])
        urls = apk_findings.get("urls", [])
        domains = apk_findings.get("domains", [])
        activities = apk_findings.get("activities", [])
        services = apk_findings.get("services", [])
        receivers = apk_findings.get("receivers", [])
        providers = apk_findings.get("providers", [])
        
        # Score permissions
        permission_factors, permission_score = self._score_permissions(permissions)
        risk_factors.extend(permission_factors)
        total_score += permission_score
        
        # Score permission combinations
        combo_factors, combo_score = self._score_permission_combinations(permissions)
        risk_factors.extend(combo_factors)
        total_score += combo_score
        
        # Score URLs
        url_factors, url_score = self._score_urls(urls)
        risk_factors.extend(url_factors)
        total_score += url_score
        
        # Score domains
        domain_factors, domain_score = self._score_domains(domains)
        risk_factors.extend(domain_factors)
        total_score += domain_score
        
        # Score APK characteristics
        char_factors, char_score = self._score_characteristics(
            permissions, activities, services, receivers, providers
        )
        risk_factors.extend(char_factors)
        total_score += char_score
        
        # Normalize score to 0-100
        risk_score = min(100, total_score)
        
        # Determine severity
        severity = self._score_to_severity(risk_score)
        
        # Generate summary
        summary = self._generate_summary(risk_score, severity, risk_factors)
        
        # Create assessment
        assessment = RiskAssessment(
            risk_score=risk_score,
            severity=severity,
            risk_factors=risk_factors,
            summary=summary,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        logger.info(
            f"Risk assessment complete: score={risk_score}, severity={severity.value}, "
            f"factors={len(risk_factors)}"
        )
        
        return assessment
    
    def _score_permissions(
        self, permissions: List[str]
    ) -> Tuple[List[RiskFactor], int]:
        """Score individual dangerous permissions"""
        factors: List[RiskFactor] = []
        score = 0
        
        for permission in permissions:
            if permission in self.PERMISSION_WEIGHTS:
                weight = self.PERMISSION_WEIGHTS[permission]
                severity = self._score_to_severity(weight)
                
                factor = RiskFactor(
                    factor=permission,
                    category="permissions",
                    score=weight,
                    reason=self._get_permission_reason(permission),
                    severity=severity
                )
                factors.append(factor)
                score += weight
                logger.debug(f"Permission {permission}: +{weight}")
        
        logger.info(f"Permission scoring: {score} points from {len(factors)} factors")
        return factors, score
    
    def _score_permission_combinations(
        self, permissions: List[str]
    ) -> Tuple[List[RiskFactor], int]:
        """Score dangerous permission combinations"""
        factors: List[RiskFactor] = []
        score = 0
        detected_combos = set()
        
        permissions_set = set(permissions)
        
        for (perm1, perm2), (combo_score, reason) in self.DANGEROUS_COMBINATIONS.items():
            if perm1 in permissions_set and perm2 in permissions_set:
                combo_name = f"{perm1} + {perm2}"
                
                # Avoid duplicate scoring
                if combo_name not in detected_combos:
                    severity = self._score_to_severity(combo_score)
                    
                    factor = RiskFactor(
                        factor=combo_name,
                        category="combinations",
                        score=combo_score,
                        reason=reason,
                        severity=severity
                    )
                    factors.append(factor)
                    score += combo_score
                    detected_combos.add(combo_name)
                    logger.debug(f"Combination {combo_name}: +{combo_score}")
        
        logger.info(f"Combination scoring: {score} points from {len(factors)} factors")
        return factors, score
    
    def _score_urls(self, urls: List[Dict[str, Any]]) -> Tuple[List[RiskFactor], int]:
        """Score suspicious URLs"""
        factors: List[RiskFactor] = []
        score = 0
        
        for url_data in urls:
            url = url_data.get("url", "")
            risk_score = url_data.get("risk_score", 0.0)
            
            url_factors, url_score = self._analyze_url(url, risk_score)
            factors.extend(url_factors)
            score += url_score
        
        logger.info(f"URL scoring: {score} points from {len(factors)} factors")
        return factors, score
    
    def _analyze_url(self, url: str, risk_score: float) -> Tuple[List[RiskFactor], int]:
        """Analyze individual URL for risk indicators"""
        factors: List[RiskFactor] = []
        total_score = 0
        
        url_lower = url.lower()
        
        # Check for IP addresses
        if self._is_ip_address(url):
            factor = RiskFactor(
                factor=f"IP URL: {url}",
                category="urls",
                score=15,
                reason="Direct IP address usage - bypasses domain reputation",
                severity=RiskSeverity.HIGH
            )
            factors.append(factor)
            total_score += 15
            logger.debug(f"IP address detected: {url}")
        
        # Check for suspicious TLDs
        tld = self._extract_tld(url)
        if tld in self.SUSPICIOUS_TLDS:
            factor = RiskFactor(
                factor=f"Suspicious TLD: {tld}",
                category="urls",
                score=15,
                reason=f"Suspicious top-level domain - {tld} is commonly used for phishing",
                severity=RiskSeverity.HIGH
            )
            factors.append(factor)
            total_score += 15
            logger.debug(f"Suspicious TLD detected: {tld}")
        
        # Check for phishing patterns
        phishing_matches = [p for p in self.PHISHING_PATTERNS if p in url_lower]
        if phishing_matches:
            factor = RiskFactor(
                factor=f"Phishing patterns: {', '.join(phishing_matches)}",
                category="urls",
                score=20,
                reason="URL contains phishing keywords - likely credential harvesting",
                severity=RiskSeverity.CRITICAL
            )
            factors.append(factor)
            total_score += 20
            logger.debug(f"Phishing patterns detected: {phishing_matches}")
        
        # HTTP vs HTTPS
        if url.startswith("http://"):
            factor = RiskFactor(
                factor=f"HTTP URL: {url}",
                category="urls",
                score=10,
                reason="Unencrypted HTTP connection - vulnerable to interception",
                severity=RiskSeverity.MEDIUM
            )
            factors.append(factor)
            total_score += 10
            logger.debug(f"HTTP URL detected: {url}")
        
        return factors, total_score
    
    def _score_domains(self, domains: List[str]) -> Tuple[List[RiskFactor], int]:
        """Score suspicious domains"""
        factors: List[RiskFactor] = []
        score = 0
        
        for domain in domains:
            for pattern in self.SUSPICIOUS_DOMAIN_PATTERNS:
                if pattern in domain:
                    factor = RiskFactor(
                        factor=f"Suspicious domain: {domain}",
                        category="domains",
                        score=15,
                        reason=f"Domain contains suspicious pattern - {pattern}",
                        severity=RiskSeverity.HIGH
                    )
                    factors.append(factor)
                    score += 15
                    logger.debug(f"Suspicious domain detected: {domain}")
                    break
        
        logger.info(f"Domain scoring: {score} points from {len(factors)} factors")
        return factors, score
    
    def _score_characteristics(
        self,
        permissions: List[str],
        activities: List[str],
        services: List[str],
        receivers: List[str],
        providers: List[str]
    ) -> Tuple[List[RiskFactor], int]:
        """Score APK structural characteristics"""
        factors: List[RiskFactor] = []
        score = 0
        
        # Large permission count
        if len(permissions) > 20:
            factor = RiskFactor(
                factor="Excessive permissions",
                category="characteristics",
                score=10,
                reason=f"APK requests {len(permissions)} permissions - unusual for most apps",
                severity=RiskSeverity.MEDIUM
            )
            factors.append(factor)
            score += 10
            logger.debug(f"Excessive permissions: {len(permissions)}")
        
        # Excessive receivers
        if len(receivers) > 10:
            factor = RiskFactor(
                factor="Excessive broadcast receivers",
                category="characteristics",
                score=10,
                reason=f"APK has {len(receivers)} receivers - can monitor system events",
                severity=RiskSeverity.MEDIUM
            )
            factors.append(factor)
            score += 10
            logger.debug(f"Excessive receivers: {len(receivers)}")
        
        # Excessive services
        if len(services) > 10:
            factor = RiskFactor(
                factor="Excessive background services",
                category="characteristics",
                score=10,
                reason=f"APK has {len(services)} services - potential for persistent malware",
                severity=RiskSeverity.MEDIUM
            )
            factors.append(factor)
            score += 10
            logger.debug(f"Excessive services: {len(services)}")
        
        # Hidden activities
        if len(activities) == 0 and len(permissions) > 5:
            factor = RiskFactor(
                factor="No launcher activities",
                category="characteristics",
                score=5,
                reason="APK has many permissions but no launcher activity - may be hidden",
                severity=RiskSeverity.LOW
            )
            factors.append(factor)
            score += 5
            logger.debug("No launcher activities detected")
        
        logger.info(f"Characteristic scoring: {score} points from {len(factors)} factors")
        return factors, score
    
    def _score_to_severity(self, score: int) -> RiskSeverity:
        """Convert risk score to severity level"""
        if score >= 75:
            return RiskSeverity.CRITICAL
        elif score >= 50:
            return RiskSeverity.HIGH
        elif score >= 25:
            return RiskSeverity.MEDIUM
        else:
            return RiskSeverity.LOW
    
    def _get_permission_reason(self, permission: str) -> str:
        """Get explanation for permission risk"""
        reasons = {
            "READ_SMS": "Can access incoming SMS messages (OTP interception)",
            "RECEIVE_SMS": "Can receive SMS messages for credential theft",
            "SEND_SMS": "Can send SMS messages (premium fraud, spam)",
            "READ_CONTACTS": "Can access device contacts list",
            "WRITE_CONTACTS": "Can modify device contacts",
            "READ_CALL_LOG": "Can access call history and metadata",
            "WRITE_CALL_LOG": "Can modify call logs",
            "BIND_ACCESSIBILITY_SERVICE": "Keystroke logging, screen observation capability",
            "REQUEST_INSTALL_PACKAGES": "Can silently install packages",
            "SYSTEM_ALERT_WINDOW": "Can display system overlays for phishing",
            "ACCESS_FINE_LOCATION": "Can track precise location",
            "ACCESS_COARSE_LOCATION": "Can track approximate location",
            "CAMERA": "Can record video without user awareness",
            "MICROPHONE": "Can record audio without user awareness",
            "RECORD_AUDIO": "Can record audio streams",
            "INTERNET": "Required for data exfiltration",
        }
        return reasons.get(permission, f"Permission with potential security impact")
    
    def _is_ip_address(self, url: str) -> bool:
        """Check if URL contains IP address"""
        import re
        # Basic IP address pattern
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return bool(re.search(ip_pattern, url))
    
    def _extract_tld(self, url: str) -> str:
        """Extract top-level domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            parts = domain.split('.')
            if len(parts) > 1:
                return '.' + parts[-1]
        except Exception:
            pass
        return ""
    
    def _generate_summary(
        self,
        risk_score: int,
        severity: RiskSeverity,
        risk_factors: List[RiskFactor]
    ) -> str:
        """Generate human-readable risk summary"""
        if not risk_factors:
            return "No significant security risks detected."
        
        # Find top risk factors
        top_factors = sorted(risk_factors, key=lambda f: f.score, reverse=True)[:3]
        factor_summary = ", ".join([f.factor for f in top_factors])
        
        severity_descriptions = {
            RiskSeverity.LOW: "minimal security concerns",
            RiskSeverity.MEDIUM: "notable security concerns that require attention",
            RiskSeverity.HIGH: "significant security risks and suspicious behavior",
            RiskSeverity.CRITICAL: "critical security threats indicating likely malicious intent"
        }
        
        description = severity_descriptions.get(
            severity,
            "security concerns"
        )
        
        return (
            f"APK exhibits {description}. "
            f"Primary risk factors include: {factor_summary}. "
            f"Recommend further investigation before installation."
        )


# Singleton instance
risk_scorer = RiskScorer()
