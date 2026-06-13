"""
Analysis Service Layer for FraudShield AI

Orchestrates APK analysis workflow:
- File handling and validation
- APK Inspector execution
- Database transaction management
- Status tracking
- Error handling with rollback

Clean Architecture: Service → CRUD → Database
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.agents.apk_inspector import APKInspector, APKAnalysisError
from app.agents.security_analyst import security_analyst
from app.analysis.androguard_parser import AndroguardParseError
from app.database.crud import AnalysisCRUD, FindingCRUD, ReportCRUD, AnalyticsCRUD
from app.database.models import Analysis, AnalysisStatus, SeverityLevel, ThreatType
from app.core.exceptions import ValidationException, DatabaseException

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service layer for APK analysis workflow.
    
    Responsibilities:
    1. Coordinate APK analysis
    2. Manage database transactions
    3. Handle errors and rollback
    4. Track analysis status
    5. Generate findings from analysis results
    """

    def __init__(self):
        """Initialize service with APK Inspector"""
        self.inspector = APKInspector()
        logger.info("AnalysisService initialized")

    def analyze_apk(self, db: Session, analysis_id: int, apk_file_path: str) -> Dict[str, Any]:
        """
        Execute APK analysis workflow.
        
        Status Flow:
            PENDING → PROCESSING → COMPLETED (success)
            PENDING → PROCESSING → FAILED (error)
        
        Args:
            db: Database session
            analysis_id: Analysis record ID to update
            apk_file_path: Path to APK file
            
        Returns:
            Dictionary with:
                - analysis_id: ID of the analysis
                - status: Final status (completed/failed)
                - findings_count: Number of findings created
                - risk_score: Calculated risk score
                - threat_type: Determined threat type
                - message: Status message
                
        Raises:
            ValidationException: If APK file invalid
            DatabaseException: If database error occurs
            APKAnalysisError: If analysis fails
        """
        logger.info(f"Starting analysis workflow for analysis_id={analysis_id}")
        
        # Validate inputs
        if not apk_file_path or not os.path.exists(apk_file_path):
            error_msg = f"APK file not found: {apk_file_path}"
            logger.error(error_msg)
            self._update_analysis_failed(db, analysis_id, error_msg)
            raise ValidationException(error_msg)
        
        try:
            # Step 1: Update status to PROCESSING
            logger.info(f"Updating analysis {analysis_id} to PROCESSING")
            AnalysisCRUD.update(db, analysis_id, status=AnalysisStatus.PROCESSING)
            
            # Step 2: Execute APK inspection
            logger.info(f"Executing APK Inspector for {apk_file_path}")
            analysis_result = self.inspector.analyze_apk(apk_file_path)
            logger.info(f"APK inspection completed: {json.dumps(analysis_result, indent=2)[:500]}...")
            
            # Step 3: Extract analysis data
            findings_data = self._extract_findings(analysis_result)
            
            # Validate risk assessment exists
            if 'risk_assessment' not in analysis_result:
                error_msg = "Risk assessment missing from analysis results"
                logger.error(error_msg)
                self._update_analysis_failed(db, analysis_id, error_msg)
                raise ValueError(error_msg)
            
            # Extract risk assessment data
            risk_assessment = analysis_result['risk_assessment']
            threat_level = analysis_result['analysis_summary']['threat_level']
            risk_score = risk_assessment['risk_score'] / 100.0  # Normalize 0-100 to 0-1
            severity_str = risk_assessment['severity'].upper()
            threat_type = self._map_threat_type(threat_level)
            severity = self._map_severity_from_assessment(severity_str)
            
            logger.info(
                f"Risk Assessment: "
                f"score={risk_assessment['risk_score']}/100 (normalized: {risk_score:.2f}), "
                f"severity={severity_str}, "
                f"factors={len(risk_assessment.get('risk_factors', []))}"
            )
            
            # Step 4: Update analysis record
            logger.info(f"Updating analysis record with results")
            AnalysisCRUD.update(
                db,
                analysis_id,
                status=AnalysisStatus.COMPLETED,
                threat_type=threat_type,
                risk_score=risk_score,
                severity=severity,
                version_name=analysis_result.get('version_name'),
                version_code=analysis_result.get('version_code'),
                app_name=analysis_result.get('app_name'),
                file_size=analysis_result.get('file_size'),
                md5_hash=analysis_result.get('md5')
            )
            
            # Step 5: Create finding records
            logger.info(f"Creating {len(findings_data)} finding records")
            findings_count = self._create_findings(db, analysis_id, findings_data)
            
            # Step 6: Create report
            logger.info(f"Creating report for analysis {analysis_id}")
            self._create_report(db, analysis_id, analysis_result)
            
            logger.info(
                f"Analysis completed successfully: "
                f"analysis_id={analysis_id}, "
                f"findings={findings_count}, "
                f"risk_score={risk_score:.2f}"
            )
            
            return {
                'analysis_id': analysis_id,
                'status': AnalysisStatus.COMPLETED.value,
                'findings_count': findings_count,
                'risk_score': risk_score,
                'threat_type': threat_type.value,
                'message': f'Analysis completed. Found {findings_count} findings.',
            }
            
        except (APKAnalysisError, AndroguardParseError) as e:
            error_msg = f"APK analysis failed: {str(e)}"
            logger.error(error_msg)
            self._update_analysis_failed(db, analysis_id, error_msg)
            raise APKAnalysisError(error_msg)
            
        except (ValidationException, DatabaseException):
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error during analysis: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._update_analysis_failed(db, analysis_id, error_msg)
            raise DatabaseException(error_msg)

    def _update_analysis_failed(self, db: Session, analysis_id: int, error_message: str) -> None:
        """Update analysis status to FAILED with error message"""
        try:
            AnalysisCRUD.update(
                db,
                analysis_id,
                status=AnalysisStatus.FAILED,
                severity=SeverityLevel.INFO,
                error_message=error_message[:1024]  # Truncate to column limit
            )
            logger.info(f"Analysis {analysis_id} marked as FAILED")
        except Exception as e:
            logger.error(f"Failed to update analysis status to FAILED: {e}")

    def _extract_findings(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract findings data from APK inspection results.
        
        Args:
            analysis_result: Complete analysis result from APKInspector
            
        Returns:
            Dictionary organized by finding type:
                - permissions: List of permission findings
                - urls: List of URL findings
                - components: List of component findings
                - hashes: Hash findings
        """
        findings = {
            'permissions': [],
            'urls': [],
            'components': [],
            'hashes': []
        }
        
        # Extract permissions
        if 'permissions' in analysis_result:
            perms_analysis = analysis_result['permissions']
            # Get all permissions from the correct source
            permission_list = perms_analysis.get('all_permissions', [])
            for perm in permission_list:
                # Extract short name for display
                perm_short = perm.split('.')[-1] if '.' in perm else perm
                findings['permissions'].append({
                    'finding_type': 'permission',
                    'category': 'PERMISSION',
                    'value': perm,
                    'short_name': perm_short,
                    'risk_level': self._get_permission_risk_level(perm_short),
                    'description': f'Permission: {perm_short}'
                })
        
        # Extract URLs and domains
        if 'urls_and_domains' in analysis_result:
            urls_data = analysis_result['urls_and_domains']
            
            # Suspicious URLs with risk scores
            for url_item in urls_data.get('suspicious_urls_classified', []):
                findings['urls'].append({
                    'finding_type': 'url',
                    'category': 'SUSPICIOUS_URL',
                    'value': url_item.get('url', ''),
                    'risk_level': self._score_to_severity(url_item.get('risk_score', 0.0)),
                    'risk_score': url_item.get('risk_score', 0.0),
                    'description': f"URL risk indicators: {', '.join(url_item.get('indicators', []))}"
                })
            
            # Domains
            for domain in urls_data.get('domains', []):
                findings['urls'].append({
                    'finding_type': 'domain',
                    'category': 'DOMAIN',
                    'value': domain,
                    'risk_level': 'info',
                    'description': 'Domain extracted from APK'
                })
        
        # Extract components
        if 'components' in analysis_result:
            components = analysis_result['components']
            
            # Activities
            for activity in components.get('activities', []):
                findings['components'].append({
                    'finding_type': 'component',
                    'category': 'ACTIVITY',
                    'value': activity,
                    'risk_level': 'info',
                    'description': 'Android Activity component'
                })
            
            # Services
            for service in components.get('services', []):
                findings['components'].append({
                    'finding_type': 'component',
                    'category': 'SERVICE',
                    'value': service,
                    'risk_level': 'info',
                    'description': 'Android Service component'
                })
            
            # Receivers
            for receiver in components.get('broadcast_receivers', []):
                findings['components'].append({
                    'finding_type': 'component',
                    'category': 'RECEIVER',
                    'value': receiver,
                    'risk_level': 'info',
                    'description': 'Android BroadcastReceiver component'
                })
            
            # Providers
            for provider in components.get('content_providers', []):
                findings['components'].append({
                    'finding_type': 'component',
                    'category': 'PROVIDER',
                    'value': provider,
                    'risk_level': 'info',
                    'description': 'Android ContentProvider component'
                })
        
        # Extract hashes
        hashes = {
            'md5': analysis_result.get('md5', ''),
            'sha256': analysis_result.get('sha256', '')
        }
        findings['hashes'] = [
            {
                'finding_type': 'hash',
                'category': 'MD5',
                'value': hashes['md5'],
                'risk_level': 'info',
                'description': 'MD5 hash of APK file'
            },
            {
                'finding_type': 'hash',
                'category': 'SHA256',
                'value': hashes['sha256'],
                'risk_level': 'info',
                'description': 'SHA256 hash of APK file'
            }
        ]
        
        logger.debug(
            f"Extracted findings: "
            f"permissions={len(findings['permissions'])}, "
            f"urls={len(findings['urls'])}, "
            f"components={len(findings['components'])}, "
            f"hashes={len(findings['hashes'])}"
        )
        
        return findings

    def _create_findings(self, db: Session, analysis_id: int, findings_data: Dict[str, Any]) -> int:
        """
        Create Finding records in database from extracted findings.
        
        Args:
            db: Database session
            analysis_id: Analysis ID to associate findings with
            findings_data: Extracted findings data
            
        Returns:
            Total number of findings created
        """
        total_created = 0
        
        # Create findings for each type
        for finding_type, findings_list in findings_data.items():
            for finding in findings_list:
                try:
                    FindingCRUD.create(
                        db,
                        analysis_id=analysis_id,
                        finding_type=finding.get('finding_type', finding_type),
                        category=finding.get('category', finding_type.upper()),
                        value=finding.get('value', ''),
                        risk_level=finding.get('risk_level', 'info'),
                        risk_score=finding.get('risk_score', None),
                        description=finding.get('description', '')
                    )
                    total_created += 1
                except Exception as e:
                    logger.error(f"Failed to create finding: {e}")
                    # Continue creating other findings
                    continue
        
        logger.info(f"Created {total_created} finding records for analysis {analysis_id}")
        return total_created

    def _create_report(self, db: Session, analysis_id: int, analysis_result: Dict[str, Any]) -> None:
        """
        Create Report record with analysis summary.
        
        Includes comprehensive security analyst assessment nested under 'security_analyst' key.
        Provides backward compatibility for missing analyst data.
        
        Args:
            db: Database session
            analysis_id: Analysis ID
            analysis_result: Complete analysis result
        """
        try:
            summary = analysis_result.get('analysis_summary', {})
            risk_assessment = analysis_result.get('risk_assessment', {})
            
            # Generate security analyst assessment
            logger.info(f"[Analyst-Start] Generating security analyst assessment for analysis {analysis_id}")
            analyst_assessment = security_analyst.analyze_apk(analysis_result)
            logger.info(
                f"[Analyst-Completed] Assessment generated with keys: {list(analyst_assessment.keys())}"
            )
            
            # Build analyst section with comprehensive output
            security_analyst_section = {
                'analyst_narrative': analyst_assessment.get('analyst_narrative', ''),
                'user_friendly_summary': analyst_assessment.get('executive_summary', {}).get('summary', ''),
                'security_assessment': analyst_assessment.get('executive_summary', {}).get('recommendation', ''),
                'permission_explanations': analyst_assessment.get('permission_explanations', []),
                'risk_reasons': analyst_assessment.get('risk_reasons', []),
                'prioritized_risk_factors': analyst_assessment.get('prioritized_risk_factors', []),
                'recommendation_list': analyst_assessment.get('recommendations', [])
            }
            
            logger.info(
                f"[Analyst-Fields] Added 7 analyst fields: "
                f"analyst_narrative={bool(security_analyst_section['analyst_narrative'])}, "
                f"user_friendly_summary={bool(security_analyst_section['user_friendly_summary'])}, "
                f"security_assessment={bool(security_analyst_section['security_assessment'])}, "
                f"permission_explanations={len(security_analyst_section['permission_explanations'])} items, "
                f"risk_reasons={len(security_analyst_section['risk_reasons'])} items, "
                f"prioritized_risk_factors={len(security_analyst_section['prioritized_risk_factors'])} items, "
                f"recommendation_list={len(security_analyst_section['recommendation_list'])} items"
            )
            
            # Build main report JSON
            report_json = {
                'timestamp': datetime.utcnow().isoformat(),
                'package_name': analysis_result.get('package_name'),
                'version': f"{analysis_result.get('version_name', 'N/A')} (code: {analysis_result.get('version_code', 'N/A')})",
                'file_size': analysis_result.get('file_size'),
                'hashes': {
                    'md5': analysis_result.get('md5'),
                    'sha256': analysis_result.get('sha256')
                },
                'threat_level': summary.get('threat_level'),
                'risk_score': risk_assessment.get('risk_score', 0),
                'severity': risk_assessment.get('severity', 'unknown'),
                'risk_factors': risk_assessment.get('risk_factors', []),
                'risk_summary': risk_assessment.get('summary', ''),
                'risk_indicators': summary.get('risk_indicators', []),
                'permissions': analysis_result.get('permissions', {}),
                'urls_and_domains': analysis_result.get('urls_and_domains', {}),
                'components': analysis_result.get('components', {}),
                # Security Analyst Section (Nested)
                'security_analyst': security_analyst_section
            }
            
            logger.info(f"[Report-Creation] Creating report record for analysis {analysis_id}")
            ReportCRUD.create(
                db,
                analysis_id=analysis_id,
                executive_summary=f"Threat Level: {summary.get('threat_level', 'unknown').upper()} | Risk Score: {risk_assessment.get('risk_score', 0)}/100 | Severity: {risk_assessment.get('severity', 'unknown').upper()}",
                threat_classification=summary.get('threat_level', 'unknown'),
                report_json=report_json
            )
            
            logger.info(f"[Report-Saved] Report created successfully with {len(security_analyst_section)} analyst fields")
            
        except Exception as e:
            logger.error(f"[Report-Error] Failed to create report: {e}", exc_info=True)
            # Don't fail the analysis if report creation fails

    def _map_threat_type(self, threat_level: str) -> ThreatType:
        """Map threat level to ThreatType enum"""
        threat_mapping = {
            'critical': ThreatType.MALWARE,
            'high': ThreatType.SPYWARE,
            'medium': ThreatType.SUSPICIOUS,
            'low': ThreatType.PUP,
            'clean': ThreatType.CLEAN
        }
        return threat_mapping.get(threat_level.lower(), ThreatType.SUSPICIOUS)

    def _map_severity(self, threat_level: str) -> SeverityLevel:
        """Map threat level to SeverityLevel enum"""
        severity_mapping = {
            'critical': SeverityLevel.CRITICAL,
            'high': SeverityLevel.HIGH,
            'medium': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
            'clean': SeverityLevel.INFO
        }
        return severity_mapping.get(threat_level.lower(), SeverityLevel.MEDIUM)

    def _map_severity_from_assessment(self, severity_str: str) -> SeverityLevel:
        """Map severity string from risk assessment to SeverityLevel enum"""
        severity_mapping = {
            'CRITICAL': SeverityLevel.CRITICAL,
            'HIGH': SeverityLevel.HIGH,
            'MEDIUM': SeverityLevel.MEDIUM,
            'LOW': SeverityLevel.LOW,
            'INFO': SeverityLevel.INFO
        }
        return severity_mapping.get(severity_str.upper(), SeverityLevel.MEDIUM)

    def _score_to_severity(self, risk_score: float) -> str:
        """Convert risk score to severity level"""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        elif risk_score >= 0.2:
            return 'low'
        else:
            return 'info'

    def get_analysis_detail(self, db: Session, analysis_id: int) -> Dict[str, Any]:
        """Get complete analysis details with findings and report"""
        try:
            analysis = AnalysisCRUD.get_by_id(db, analysis_id)
            
            # Get findings with pagination
            findings, findings_total = FindingCRUD.list_by_analysis(db, analysis_id, limit=1000)
            
            # Get report
            report = ReportCRUD.get_by_analysis_id(db, analysis_id)
            
            return {
                'analysis': analysis,
                'findings': findings,
                'findings_count': findings_total,
                'report': report
            }
        except Exception as e:
            logger.error(f"Error fetching analysis detail: {e}")
            raise

    def get_analysis_statistics(self, db: Session) -> Dict[str, Any]:
        """Get analysis statistics for dashboard"""
        try:
            return AnalyticsCRUD.get_analysis_stats(db)
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            raise
    
    def _get_permission_risk_level(self, permission_short_name: str) -> str:
        """
        Determine risk level for a permission.
        
        Args:
            permission_short_name: Short permission name (e.g., 'READ_SMS')
            
        Returns:
            Risk level string: 'critical', 'high', 'medium', 'low', 'info'
        """
        # Critical permissions
        critical_perms = {
            'READ_SMS', 'RECEIVE_SMS', 'CALL_PHONE', 'CAMERA', 'RECORD_AUDIO',
            'REQUEST_INSTALL_PACKAGES', 'BIND_ACCESSIBILITY_SERVICE',
            'ACCESS_FINE_LOCATION', 'READ_CONTACTS', 'RECEIVE_BOOT_COMPLETED'
        }
        
        # High risk permissions
        high_perms = {
            'SEND_SMS', 'WRITE_SMS', 'READ_CALENDAR', 'WRITE_CALENDAR',
            'ACCESS_COARSE_LOCATION', 'READ_EXTERNAL_STORAGE',
            'WRITE_EXTERNAL_STORAGE', 'DISABLE_KEYGUARD', 'GET_ACCOUNTS',
            'READ_CALL_LOG', 'PROCESS_OUTGOING_CALLS', 'READ_PHONE_STATE',
            'WRITE_CONTACTS', 'SYSTEM_ALERT_WINDOW'
        }
        
        # Medium risk permissions
        medium_perms = {
            'ACCESS_NETWORK_STATE', 'CHANGE_NETWORK_STATE', 'CHANGE_WIFI_STATE'
        }
        
        if permission_short_name in critical_perms:
            return 'critical'
        elif permission_short_name in high_perms:
            return 'high'
        elif permission_short_name in medium_perms:
            return 'medium'
        elif permission_short_name in {'INTERNET', 'ACCESS_WIFI_STATE'}:
            return 'low'
        else:
            return 'info'
    
    def _score_to_severity(self, score: float) -> str:
        """
        Convert risk score (0.0-1.0) to severity level.
        
        Args:
            score: Risk score 0.0-1.0
            
        Returns:
            Severity level string
        """
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        elif score >= 0.2:
            return 'low'
        else:
            return 'info'


# Create singleton instance
analysis_service = AnalysisService()
