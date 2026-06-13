"""
Security Analyst Agent for FraudShield AI

Converts technical APK analysis results into human-readable security assessments.

Responsibilities:
- Generate executive summaries
- Explain permissions in plain English
- Provide risk reasoning
- Generate actionable recommendations
- Create professional analyst narratives
- Prioritize security concerns

Architecture:
- SecurityAnalystAgent: Main orchestrator
- Knowledge base: Permission explanations, risk mapping
- Output generation: Structured analysis reports
- Logging: Audit trail for analyst decisions
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk levels for sorting and prioritization"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PermissionExplanation:
    """Explanation for a single permission"""
    permission: str
    risk: RiskLevel
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "permission": self.permission,
            "risk": self.risk.value,
            "explanation": self.explanation
        }


@dataclass
class RiskReason:
    """Reason why the APK has detected risk"""
    severity: RiskLevel
    reason: str
    indicator: str  # The specific finding that triggered this reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "severity": self.severity.value,
            "reason": self.reason,
            "indicator": self.indicator
        }


@dataclass
class ExecutiveSummary:
    """Executive summary of security assessment"""
    risk_level: str
    summary: str
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "risk_level": self.risk_level,
            "summary": self.summary,
            "recommendation": self.recommendation
        }


class SecurityAnalystAgent:
    """
    AI Security Analyst Agent
    
    Analyzes technical APK findings and generates human-readable security assessments
    with explanations, recommendations, and professional analyst narratives.
    """
    
    # Permission knowledge base
    PERMISSION_EXPLANATIONS = {
        # SMS/Messaging (Full permission names with android.permission prefix)
        "READ_SMS": {
            "explanation": "Allows reading all SMS messages including 2FA codes and banking information. This is a CRITICAL risk as it enables interception of sensitive authentication codes.",
            "risk": RiskLevel.CRITICAL
        },
        "RECEIVE_SMS": {
            "explanation": "Allows the app to receive and intercept incoming SMS messages without notification. Could be used to steal OTP codes or block emergency messages. This is especially dangerous for banking apps.",
            "risk": RiskLevel.CRITICAL
        },
        "SEND_SMS": {
            "explanation": "Allows sending SMS messages without user confirmation. Could incur charges or send fraudulent messages.",
            "risk": RiskLevel.HIGH
        },
        "WRITE_SMS": {
            "explanation": "Allows modifying or deleting SMS messages. Could cover up evidence of fraud.",
            "risk": RiskLevel.HIGH
        },
        
        # Contacts
        "READ_CONTACTS": {
            "explanation": "Allows accessing the device's contact list. Could be used to harvest personal information.",
            "risk": RiskLevel.HIGH
        },
        "WRITE_CONTACTS": {
            "explanation": "Allows modifying the device's contacts. Could be used for phishing or social engineering.",
            "risk": RiskLevel.MEDIUM
        },
        
        # Phone
        "READ_PHONE_STATE": {
            "explanation": "Allows reading phone call state and number. Could be used to track call activity.",
            "risk": RiskLevel.MEDIUM
        },
        "PROCESS_OUTGOING_CALLS": {
            "explanation": "Allows detecting outgoing calls. Could be used to intercept or monitor communications.",
            "risk": RiskLevel.MEDIUM
        },
        "CALL_PHONE": {
            "explanation": "Allows making phone calls. Could incur charges without user knowledge.",
            "risk": RiskLevel.HIGH
        },
        
        # Location
        "ACCESS_FINE_LOCATION": {
            "explanation": "Allows precise GPS location tracking. Could track user's movements in real-time.",
            "risk": RiskLevel.HIGH
        },
        "ACCESS_COARSE_LOCATION": {
            "explanation": "Allows approximate location via network. Could be used for location-based fraud.",
            "risk": RiskLevel.MEDIUM
        },
        
        # Media/Microphone
        "CAMERA": {
            "explanation": "Allows camera access. Could secretly record photos or videos.",
            "risk": RiskLevel.HIGH
        },
        "RECORD_AUDIO": {
            "explanation": "Allows microphone access. Could secretly record conversations.",
            "risk": RiskLevel.HIGH
        },
        
        # System
        "SYSTEM_ALERT_WINDOW": {
            "explanation": "Allows displaying system-level alerts and overlays. Could be used for phishing overlays.",
            "risk": RiskLevel.HIGH
        },
        "REQUEST_INSTALL_PACKAGES": {
            "explanation": "Allows installing other APK files. Could be used to install malware.",
            "risk": RiskLevel.CRITICAL
        },
        "WRITE_EXTERNAL_STORAGE": {
            "explanation": "Allows writing to shared storage. Could be used to store malicious files.",
            "risk": RiskLevel.MEDIUM
        },
        "READ_EXTERNAL_STORAGE": {
            "explanation": "Allows reading shared storage. Could access sensitive user files.",
            "risk": RiskLevel.MEDIUM
        },
        
        # Accessibility
        "BIND_ACCESSIBILITY_SERVICE": {
            "explanation": "Allows accessibility service binding. Could monitor all user interactions including passwords.",
            "risk": RiskLevel.CRITICAL
        },
        
        # Account
        "GET_ACCOUNTS": {
            "explanation": "Allows accessing device accounts. Could access banking or email credentials.",
            "risk": RiskLevel.HIGH
        },
        "READ_CALENDAR": {
            "explanation": "Allows reading calendar events. Could access sensitive appointment information.",
            "risk": RiskLevel.MEDIUM
        },
        "READ_CALL_LOG": {
            "explanation": "Allows reading call history. Could expose communication patterns.",
            "risk": RiskLevel.MEDIUM
        },
        
        # Network
        "INTERNET": {
            "explanation": "Allows internet access. While commonly required, this permission combined with data-sensitive permissions could enable data exfiltration to remote servers.",
            "risk": RiskLevel.LOW
        },
        "ACCESS_NETWORK_STATE": {
            "explanation": "Allows the app to check WiFi/mobile network state. Could be used to detect connection type before exfiltrating data.",
            "risk": RiskLevel.MEDIUM
        },
        "CHANGE_NETWORK_STATE": {
            "explanation": "Allows enabling/disabling WiFi and mobile networks. Could force data over specific connections or block internet access.",
            "risk": RiskLevel.MEDIUM
        },
        "RECEIVE_BOOT_COMPLETED": {
            "explanation": "Allows the app to start automatically when device boots. Once installed, the malicious app will run even if the device restarts without user interaction.",
            "risk": RiskLevel.HIGH
        },
        
        # Device Admin
        "DISABLE_KEYGUARD": {
            "explanation": "Allows disabling lock screen. Could prevent user from accessing their device or clearing cache.",
            "risk": RiskLevel.HIGH
        },
        # Storage (Additional entries for completeness)
        "WRITE_EXTERNAL_STORAGE": {
            "explanation": "Allows writing to shared storage where it can install malware, store stolen data, or drop malicious files.",
            "risk": RiskLevel.MEDIUM
        },
    }
    
    # Risk score thresholds for summary generation
    RISK_THRESHOLDS = {
        25: {"level": "Safe", "color": "green"},
        50: {"level": "Moderate", "color": "yellow"},
        75: {"level": "High", "color": "orange"},
        100: {"level": "Critical", "color": "red"}
    }
    
    def __init__(self):
        """Initialize the Security Analyst Agent"""
        logger.info("SecurityAnalystAgent initialized")
    
    def generate_summary(self, risk_score: int, severity: str, threat_type: str) -> ExecutiveSummary:
        """
        Generate executive summary based on risk score.
        
        Args:
            risk_score: Risk score from 0-100
            severity: Severity level (low, medium, high, critical)
            threat_type: Type of threat detected
            
        Returns:
            ExecutiveSummary with risk assessment
        """
        logger.info(f"Generating summary: score={risk_score}, severity={severity}")
        
        # Determine risk level string
        if risk_score <= 25:
            risk_level = "Safe"
            summary = "This application has minimal risk indicators. It appears to be safe for use."
            recommendation = "Safe to install."
        elif risk_score <= 50:
            risk_level = "Moderate"
            summary = "This application shows some concerning permissions. Review them carefully before installation."
            recommendation = "Install only if obtained from a trusted source."
        elif risk_score <= 75:
            risk_level = "High"
            summary = "This application has several risky permissions and behaviors. It could pose a security or privacy threat."
            recommendation = "Avoid installation unless absolutely necessary."
        else:
            risk_level = "Critical"
            summary = "This application has multiple critical risk indicators. It may be malicious or highly dangerous."
            recommendation = "Do not install this application."
        
        return ExecutiveSummary(
            risk_level=risk_level,
            summary=summary,
            recommendation=recommendation
        )
    
    def explain_permissions(self, permissions: List[str]) -> List[Dict[str, Any]]:
        """
        Explain requested permissions in human-readable terms.
        
        Handles both short names (READ_SMS) and full names (android.permission.READ_SMS).
        
        Args:
            permissions: List of permission names (short or full form)
            
        Returns:
            List of permission explanations sorted by risk
        """
        logger.info(f"Explaining {len(permissions)} permissions")
        
        explanations = []
        
        for perm in permissions:
            # Extract short permission name (e.g., 'READ_SMS' from 'android.permission.READ_SMS')
            short_name = perm.split('.')[-1] if '.' in perm else perm
            
            if short_name in self.PERMISSION_EXPLANATIONS:
                info = self.PERMISSION_EXPLANATIONS[short_name]
                explanations.append({
                    "permission": perm,
                    "short_name": short_name,
                    "risk": info["risk"].value,
                    "explanation": info["explanation"]
                })
            else:
                # For unknown permissions, provide a generic explanation
                explanations.append({
                    "permission": perm,
                    "short_name": short_name,
                    "risk": RiskLevel.LOW.value,
                    "explanation": f"Permission {short_name}: Check Android documentation for security implications."
                })
        
        # Sort by risk level
        risk_order = {
            RiskLevel.CRITICAL.value: 0,
            RiskLevel.HIGH.value: 1,
            RiskLevel.MEDIUM.value: 2,
            RiskLevel.LOW.value: 3,
            RiskLevel.INFO.value: 4
        }
        
        explanations.sort(
            key=lambda x: risk_order.get(x["risk"], 999)
        )
        
        logger.info(f"Generated explanations for {len(explanations)} permissions")
        return explanations
    
    def generate_risk_reasons(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate detailed reasons for detected risks.
        
        Analyzes findings and creates human-readable explanations of what's risky.
        Handles both apk_inspector data structure and direct permission lists.
        
        Args:
            analysis_result: Complete analysis result from APKInspector
            
        Returns:
            List of risk reasons sorted by severity
        """
        logger.info("Generating risk reasons")
        
        reasons = []
        
        # Analyze permissions - try both data sources
        permissions_dict = analysis_result.get('permissions', {})
        # Use dangerous_list if available (from APKInspector), otherwise all_permissions
        permission_list = (permissions_dict.get('dangerous_list', []) or 
                          permissions_dict.get('all_permissions', []))
        
        if permission_list:
            dangerous_perms = []
            for perm in permission_list:
                perm_name = perm.split('.')[-1] if '.' in perm else perm  # Get last part of permission
                if perm_name in self.PERMISSION_EXPLANATIONS:
                    info = self.PERMISSION_EXPLANATIONS[perm_name]
                    if info["risk"] in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                        dangerous_perms.append(perm_name)
            
            if dangerous_perms:
                severity = RiskLevel.CRITICAL if any(
                    p in ["REQUEST_INSTALL_PACKAGES", "BIND_ACCESSIBILITY_SERVICE"]
                    for p in dangerous_perms
                ) else RiskLevel.HIGH
                
                if len(dangerous_perms) == 1:
                    reason = f"Application requests {dangerous_perms[0]} permission."
                else:
                    reason = f"Application requests multiple dangerous permissions: {', '.join(dangerous_perms[:3])}."
                
                reasons.append({
                    "severity": severity.value,
                    "reason": reason,
                    "indicator": f"{len(dangerous_perms)} dangerous permissions"
                })
        
        # Analyze URLs
        urls_and_domains = analysis_result.get('urls_and_domains', {})
        urls = urls_and_domains.get('urls', [])
        
        if urls:
            http_urls = [u for u in urls if u.startswith('http://')]
            if http_urls:
                reasons.append({
                    "severity": RiskLevel.MEDIUM.value,
                    "reason": f"Application contains {len(http_urls)} unencrypted HTTP URLs. Data could be intercepted.",
                    "indicator": f"{len(http_urls)} HTTP URLs"
                })
            
            # Check for suspicious patterns
            suspicious_patterns = ['bit.ly', 'tinyurl', 'goo.gl', 'short.link', 'exe', '.zip']
            suspicious_urls = [u for u in urls if any(p in u.lower() for p in suspicious_patterns)]
            if suspicious_urls:
                reasons.append({
                    "severity": RiskLevel.HIGH.value,
                    "reason": "Application contains suspicious shortened or executable URLs.",
                    "indicator": f"{len(suspicious_urls)} suspicious URLs"
                })
        
        # Analyze components
        components = analysis_result.get('components', {})
        
        if components.get('receivers'):
            boot_receivers = [
                r for r in components['receivers']
                if 'BOOT_COMPLETED' in r.get('intent_filters', [])
            ]
            if boot_receivers:
                reasons.append({
                    "severity": RiskLevel.HIGH.value,
                    "reason": "Application starts automatically after device reboot.",
                    "indicator": f"{len(boot_receivers)} boot receivers"
                })
        
        if components.get('services') and len(components['services']) > 10:
            reasons.append({
                "severity": RiskLevel.MEDIUM.value,
                "reason": f"Application has excessive background services ({len(components['services'])}).",
                "indicator": f"{len(components['services'])} services"
            })
        
        if components.get('receivers') and len(components['receivers']) > 10:
            reasons.append({
                "severity": RiskLevel.MEDIUM.value,
                "reason": f"Application has excessive broadcast receivers ({len(components['receivers'])}).",
                "indicator": f"{len(components['receivers'])} receivers"
            })
        
        # Sort by severity
        severity_order = {
            RiskLevel.CRITICAL.value: 0,
            RiskLevel.HIGH.value: 1,
            RiskLevel.MEDIUM.value: 2,
            RiskLevel.LOW.value: 3,
            RiskLevel.INFO.value: 4
        }
        
        reasons.sort(key=lambda x: severity_order.get(x["severity"], 999))
        
        logger.info(f"Generated {len(reasons)} risk reasons")
        return reasons
    
    def generate_recommendations(self, risk_score: int, severity: str, risk_reasons: List[Dict[str, Any]]) -> List[str]:
        """
        Generate actionable recommendations based on risk assessment.
        
        Args:
            risk_score: Risk score from 0-100
            severity: Severity level
            risk_reasons: List of identified risk reasons
            
        Returns:
            List of recommendations
        """
        logger.info(f"Generating recommendations for score={risk_score}")
        
        recommendations = []
        
        # Base recommendations from risk score
        if risk_score <= 25:
            recommendations.append("This application appears safe. Safe to install.")
        elif risk_score <= 50:
            recommendations.append("Verify the application source before installation.")
            recommendations.append("Review the requested permissions carefully.")
        elif risk_score <= 75:
            recommendations.append("Only install if the application is from a trusted source.")
            recommendations.append("Review all requested permissions before granting access.")
            recommendations.append("Monitor the application's behavior after installation.")
        else:
            recommendations.append("Do not install this application.")
            recommendations.append("If already installed, uninstall immediately.")
            recommendations.append("Consider running a full device security scan.")
        
        # Specific recommendations based on risks
        for reason in risk_reasons:
            indicator = reason.get('indicator', '').lower()
            severity_val = reason.get('severity', '').lower()
            
            if 'sms' in indicator.lower():
                recommendations.append("Protect SMS-based 2FA codes as this app can access them.")
            
            if 'contacts' in indicator.lower():
                recommendations.append("Be aware this app can access your contact list.")
            
            if 'location' in indicator.lower():
                recommendations.append("Disable location services when not needed.")
            
            if 'camera' in indicator.lower() or 'record' in indicator.lower():
                recommendations.append("Cover your camera and check microphone permissions.")
            
            if 'HTTP' in indicator or 'unencrypted' in indicator.lower():
                recommendations.append("Avoid entering sensitive data while using this app.")
            
            if 'boot' in indicator.lower():
                recommendations.append("This app will run in the background even when not actively used.")
            
            if severity_val == 'critical':
                recommendations.append("This app poses critical security risk. Avoid installation.")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        logger.info(f"Generated {len(unique_recommendations)} recommendations")
        return unique_recommendations
    
    def generate_analysis_narrative(
        self,
        analysis_result: Dict[str, Any],
        risk_score: int,
        severity: str,
        risk_reasons: List[Dict[str, Any]],
        executive_summary: ExecutiveSummary
    ) -> str:
        """
        Generate a professional analyst narrative.
        
        Creates a 3-5 paragraph human-readable security assessment that explains
        findings in non-technical language.
        
        Args:
            analysis_result: Complete analysis result
            risk_score: Risk score 0-100
            severity: Severity level
            risk_reasons: List of risk reasons
            executive_summary: Executive summary
            
        Returns:
            Professional analyst narrative (3-5 paragraphs)
        """
        logger.info("Generating analyst narrative")
        
        package_name = analysis_result.get('package_name', 'Unknown')
        
        narrative_parts = []
        
        # Paragraph 1: Introduction
        narrative_parts.append(
            f"FraudShield AI Security Analysis Report for {package_name}\n\n"
            f"This security assessment evaluates the risk profile of the analyzed application. "
            f"The analysis examines permissions, network connectivity, system integration, "
            f"and behavioral characteristics to determine overall security risk."
        )
        
        # Paragraph 2: Risk Assessment
        # Try to get permissions from multiple sources
        permissions_dict = analysis_result.get('permissions', {})
        permissions = permissions_dict.get('all_permissions', [])
        dangerous_perms = permissions_dict.get('dangerous_list', [])
        dangerous_count = permissions_dict.get('dangerous_permissions', len(dangerous_perms))
        total_count = permissions_dict.get('total_permissions', len(permissions))
        
        urls = analysis_result.get('urls_and_domains', {}).get('urls', [])
        components = analysis_result.get('components', {})
        
        # Build assessment text with actual counts
        if total_count > 0:
            assessment_text = f"The application requests {total_count} permissions"
            if dangerous_count > 0:
                assessment_text += f", including {dangerous_count} sensitive permissions"
            assessment_text += f" and contains {len(urls)} external URLs. "
        else:
            assessment_text = f"The application contains {len(urls)} external URLs. "
        
        if risk_reasons:
            top_risks = risk_reasons[:2]
            risk_descriptions = []
            for reason in top_risks:
                risk_descriptions.append(reason['reason'].lower().strip('.'))
            
            assessment_text += "Key findings include: " + "; ".join(risk_descriptions) + ". "
        
        assessment_text += f"The overall risk level is determined to be {severity.upper()}."
        
        narrative_parts.append(assessment_text)
        
        # Paragraph 3: Detailed Analysis
        detailed_findings = []
        
        if total_count > 0:
            # Check for specific dangerous permissions
            all_perms_str = ' '.join(permissions)
            
            if 'SMS' in all_perms_str or 'RECEIVE_SMS' in all_perms_str or 'READ_SMS' in all_perms_str:
                detailed_findings.append(
                    f"The application requests access to SMS messages, which is a critical risk "
                    f"as it could intercept authentication codes and sensitive messages."
                )
            
            if 'BOOT_COMPLETED' in all_perms_str or 'RECEIVE_BOOT_COMPLETED' in all_perms_str:
                detailed_findings.append(
                    f"The application will start automatically when the device boots, persisting in the background."
                )
            
            if 'CONTACTS' in all_perms_str or 'READ_CONTACTS' in all_perms_str:
                detailed_findings.append(
                    f"The application can access your contacts, potentially harvesting personal information."
                )
            
            if 'LOCATION' in all_perms_str:
                detailed_findings.append(
                    f"The application can track your precise location in real-time, compromising your privacy."
                )
            
            if 'CAMERA' in all_perms_str or 'RECORD_AUDIO' in all_perms_str:
                detailed_findings.append(
                    f"The application can access your camera and microphone without notification."
                )
        
        if len(urls) > 0:
            http_count = len([u for u in urls if u.startswith('http://')])
            if http_count > 0:
                detailed_findings.append(
                    f"The application contains {http_count} unencrypted HTTP URLs, which could allow "
                    f"interception of data transmitted to these servers."
                )
        
        if components.get('services') and len(components['services']) > 5:
            detailed_findings.append(
                f"The application includes {len(components['services'])} background services, "
                f"indicating it will continue running even after the user closes it."
            )
        
        if detailed_findings:
            narrative_parts.append(" ".join(detailed_findings))
        else:
            narrative_parts.append(
                f"The analysis did not reveal obvious malicious patterns. "
                f"The application appears to follow standard Android development practices."
            )
        
        # Paragraph 4: Recommendation
        recommendation_text = (
            f"Based on the risk assessment, the following action is recommended: "
            f"{executive_summary.recommendation.lower()} "
        )
        
        if risk_reasons:
            recommendation_text += (
                f"Users should be particularly cautious about the identified risk factors before installation. "
            )
        
        narrative_parts.append(recommendation_text)
        
        # Paragraph 5: Conclusion
        narrative_parts.append(
            f"This analysis is based on static code examination and does not constitute a guarantee "
            f"of application safety. Users should exercise caution and only install applications from "
            f"trusted sources. FraudShield AI recommends running periodic security scans on all installed applications."
        )
        
        narrative = "\n\n".join(narrative_parts)
        
        logger.info("Analyst narrative generated successfully")
        return narrative
    
    def prioritize_risks(
        self,
        risk_factors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Sort risk factors by severity level.
        
        Args:
            risk_factors: List of risk factors from risk assessment
            
        Returns:
            Risk factors sorted by severity (CRITICAL → HIGH → MEDIUM → LOW → INFO)
        """
        logger.info(f"Prioritizing {len(risk_factors)} risk factors")
        
        severity_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "info": 4
        }
        
        # Make a copy to avoid modifying original
        sorted_factors = list(risk_factors)
        
        sorted_factors.sort(
            key=lambda x: severity_order.get(x.get("severity", "info").lower(), 999)
        )
        
        logger.info("Risk factors prioritized")
        return sorted_factors
    
    def analyze_apk(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete security analysis orchestration.
        
        Generates all analyst outputs in one call.
        Handles permission data from APKInspector with all_permissions key.
        
        Args:
            analysis_result: Complete analysis result from APKInspector
            
        Returns:
            Complete analyst assessment with all outputs
        """
        logger.info("Starting comprehensive APK analysis")
        logger.debug(f"Analysis result keys: {list(analysis_result.keys())}")
        logger.debug(f"Permissions keys: {list(analysis_result.get('permissions', {}).keys())}")
        
        # Extract risk data
        risk_assessment = analysis_result.get('risk_assessment', {})
        risk_score = risk_assessment.get('risk_score', 0)
        severity = risk_assessment.get('severity', 'unknown')
        threat_type = analysis_result.get('analysis_summary', {}).get('threat_level', 'unknown')
        
        # Generate all components
        executive_summary = self.generate_summary(risk_score, severity, threat_type)
        
        # Get permissions from correct source - use all_permissions from APKInspector
        permissions_dict = analysis_result.get('permissions', {})
        permissions = permissions_dict.get('all_permissions', [])
        logger.info(f"Processing {len(permissions)} permissions for explanation")
        permission_explanations = self.explain_permissions(permissions)
        
        risk_reasons = self.generate_risk_reasons(analysis_result)
        
        recommendations = self.generate_recommendations(
            risk_score,
            severity,
            risk_reasons
        )
        
        analyst_narrative = self.generate_analysis_narrative(
            analysis_result,
            risk_score,
            severity,
            risk_reasons,
            executive_summary
        )
        
        # Prioritize risk factors from risk assessment
        risk_factors = risk_assessment.get('risk_factors', [])
        if risk_factors:
            # Convert RiskFactor objects to dicts if needed
            risk_factors_list = [
                f.to_dict() if hasattr(f, 'to_dict') else f
                for f in risk_factors
            ]
            prioritized_risks = self.prioritize_risks(risk_factors_list)
        else:
            prioritized_risks = []
        
        logger.info("Comprehensive APK analysis completed")
        
        return {
            "executive_summary": executive_summary.to_dict(),
            "permission_explanations": permission_explanations,
            "risk_reasons": risk_reasons,
            "recommendations": recommendations,
            "analyst_narrative": analyst_narrative,
            "prioritized_risk_factors": prioritized_risks
        }


# Singleton instance
security_analyst = SecurityAnalystAgent()
