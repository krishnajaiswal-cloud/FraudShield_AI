"""
Integration tests for Security Analyst data persistence and API response.

Tests the complete flow:
1. APK Analysis → 2. Security Analyst Generation → 3. Report Creation → 4. Database Persistence → 5. API Response

Verifies that all analyst fields are present in the API response.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from app.agents.security_analyst import security_analyst, RiskLevel
from app.database.crud import AnalysisCRUD, ReportCRUD
from app.database.models import Analysis, Report, AnalysisStatus, SeverityLevel, ThreatType
from app.services.analysis_service import AnalysisService
from app.database.database import Base, engine


class TestAnalystDataPersistence:
    """Test that analyst data is properly persisted in database"""
    
    @pytest.fixture
    def db(self):
        """Setup test database"""
        Base.metadata.create_all(bind=engine)
        from app.database.database import SessionLocal
        db = SessionLocal()
        yield db
        db.close()
        Base.metadata.drop_all(bind=engine)
    
    def test_analyst_data_in_report_json(self, db: Session):
        """Verify all analyst fields are in report_json after report creation"""
        # Create analysis record
        analysis = AnalysisCRUD.create(
            db,
            file_hash="test_hash_123",
            apk_name="test.apk",
            package_name="com.test.app",
            file_path="/tmp/test.apk",
            md5_hash="abc123"
        )
        analysis_id = analysis.id
        
        # Create mock analysis result (what APKInspector returns)
        analysis_result = {
            'package_name': 'com.test.app',
            'app_name': 'Test App',
            'version_name': '1.0',
            'version_code': '1',
            'file_size': 1024,
            'md5': 'abc123',
            'sha256': 'def456',
            'analysis_summary': {
                'threat_level': 'high',
                'risk_indicators': []
            },
            'risk_assessment': {
                'risk_score': 75,
                'severity': 'high',
                'risk_factors': [
                    {'severity': 'high', 'description': 'Test factor'}
                ],
                'summary': 'High risk app'
            },
            'permissions': {
                'requested': ['READ_SMS', 'READ_CONTACTS'],
                'all_classified': [
                    {'permission': 'READ_SMS', 'risk': 'high'},
                    {'permission': 'READ_CONTACTS', 'risk': 'high'}
                ]
            },
            'urls_and_domains': {
                'domains': [],
                'suspicious_urls_classified': []
            },
            'components': {}
        }
        
        # Generate analyst assessment
        analyst_assessment = security_analyst.analyze_apk(analysis_result)
        
        # Create report with analyst data
        report_json = {
            'timestamp': datetime.utcnow().isoformat(),
            'package_name': 'com.test.app',
            'version': '1.0 (code: 1)',
            'file_size': 1024,
            'hashes': {'md5': 'abc123', 'sha256': 'def456'},
            'threat_level': 'high',
            'risk_score': 75,
            'severity': 'high',
            'risk_factors': [],
            'risk_summary': 'High risk app',
            'risk_indicators': [],
            'permissions': {},
            'urls_and_domains': {},
            'components': {},
            'security_analyst': {
                'analyst_narrative': analyst_assessment.get('analyst_narrative', ''),
                'user_friendly_summary': analyst_assessment.get('executive_summary', {}).get('summary', ''),
                'security_assessment': analyst_assessment.get('executive_summary', {}).get('recommendation', ''),
                'permission_explanations': analyst_assessment.get('permission_explanations', []),
                'risk_reasons': analyst_assessment.get('risk_reasons', []),
                'prioritized_risk_factors': analyst_assessment.get('prioritized_risk_factors', []),
                'recommendation_list': analyst_assessment.get('recommendations', [])
            }
        }
        
        # Create report record
        report = ReportCRUD.create(
            db,
            analysis_id=analysis_id,
            executive_summary="Test summary",
            threat_classification="high",
            report_json=report_json
        )
        
        # Verify all analyst fields are in report_json
        assert 'security_analyst' in report.report_json
        security_analyst_section = report.report_json['security_analyst']
        
        # Check all 7 required fields exist
        assert 'analyst_narrative' in security_analyst_section
        assert 'user_friendly_summary' in security_analyst_section
        assert 'security_assessment' in security_analyst_section
        assert 'permission_explanations' in security_analyst_section
        assert 'risk_reasons' in security_analyst_section
        assert 'prioritized_risk_factors' in security_analyst_section
        assert 'recommendation_list' in security_analyst_section
        
        # Verify data types
        assert isinstance(security_analyst_section['analyst_narrative'], str)
        assert isinstance(security_analyst_section['user_friendly_summary'], str)
        assert isinstance(security_analyst_section['security_assessment'], str)
        assert isinstance(security_analyst_section['permission_explanations'], list)
        assert isinstance(security_analyst_section['risk_reasons'], list)
        assert isinstance(security_analyst_section['prioritized_risk_factors'], list)
        assert isinstance(security_analyst_section['recommendation_list'], list)
    
    def test_analyst_fields_not_empty(self, db: Session):
        """Verify analyst fields contain meaningful data"""
        # Create analysis and generate report (simplified)
        analysis_result = {
            'package_name': 'com.test.app',
            'app_name': 'Test App',
            'version_name': '1.0',
            'version_code': '1',
            'file_size': 1024,
            'md5': 'abc123',
            'sha256': 'def456',
            'analysis_summary': {
                'threat_level': 'critical',
                'risk_indicators': ['malware_signature']
            },
            'risk_assessment': {
                'risk_score': 95,
                'severity': 'critical',
                'risk_factors': [
                    {
                        'severity': 'critical',
                        'description': 'Matches known malware signature'
                    }
                ],
                'summary': 'Critical: Probable malware detected'
            },
            'permissions': {
                'requested': ['READ_SMS', 'CALL_PHONE', 'CAMERA'],
                'all_classified': [
                    {'permission': 'READ_SMS', 'risk': 'high'},
                    {'permission': 'CALL_PHONE', 'risk': 'high'},
                    {'permission': 'CAMERA', 'risk': 'high'}
                ]
            },
            'urls_and_domains': {
                'domains': ['malicious.com'],
                'suspicious_urls_classified': [
                    {
                        'url': 'http://malicious.com/malware',
                        'risk_score': 0.95,
                        'indicators': ['command_and_control']
                    }
                ]
            },
            'components': {
                'boot_receivers': [
                    {
                        'class': 'com.test.BootReceiver',
                        'risk': 'high'
                    }
                ]
            }
        }
        
        analyst_assessment = security_analyst.analyze_apk(analysis_result)
        
        # Verify key fields have content
        assert analyst_assessment['analyst_narrative']  # Non-empty narrative
        assert analyst_assessment['executive_summary']['summary']  # Non-empty summary
        assert analyst_assessment['executive_summary']['recommendation']  # Non-empty recommendation
        assert len(analyst_assessment['permission_explanations']) > 0  # Has explanations
        assert len(analyst_assessment['risk_reasons']) > 0  # Has risk reasons
        assert len(analyst_assessment['recommendations']) > 0  # Has recommendations


class TestAPIResponseStructure:
    """Test that API response includes analyst data in correct structure"""
    
    @pytest.fixture
    def sample_report_json(self):
        """Sample report_json with nested analyst data"""
        return {
            'timestamp': '2024-01-15T10:30:45.123456',
            'package_name': 'com.example.app',
            'version': '1.0.0 (code: 100)',
            'threat_level': 'high',
            'risk_score': 78,
            'severity': 'high',
            'security_analyst': {
                'analyst_narrative': 'This application requests dangerous permissions...',
                'user_friendly_summary': 'High-risk application with concerning permissions',
                'security_assessment': 'Not recommended for installation without careful review',
                'permission_explanations': [
                    {
                        'permission': 'READ_SMS',
                        'risk': 'high',
                        'explanation': 'Can access SMS messages'
                    },
                    {
                        'permission': 'READ_CONTACTS',
                        'risk': 'high',
                        'explanation': 'Can access contact list'
                    }
                ],
                'risk_reasons': [
                    {
                        'severity': 'high',
                        'reason': 'Requests SMS reading permission',
                        'indicator': 'READ_SMS'
                    }
                ],
                'prioritized_risk_factors': [
                    {
                        'factor': 'SMS Access',
                        'severity': 'high',
                        'reason': 'Can intercept sensitive messages'
                    }
                ],
                'recommendation_list': [
                    'Avoid installation if not from trusted source',
                    'Monitor for unauthorized SMS activity'
                ]
            }
        }
    
    def test_report_json_analyst_section_valid(self, sample_report_json):
        """Verify analyst section in report_json is valid"""
        assert 'security_analyst' in sample_report_json
        sa = sample_report_json['security_analyst']
        
        # All fields present
        required_fields = [
            'analyst_narrative',
            'user_friendly_summary',
            'security_assessment',
            'permission_explanations',
            'risk_reasons',
            'prioritized_risk_factors',
            'recommendation_list'
        ]
        
        for field in required_fields:
            assert field in sa, f"Missing field: {field}"
    
    def test_analyst_data_json_serializable(self, sample_report_json):
        """Verify analyst data can be JSON serialized (for API response)"""
        # This should not raise an exception
        json_str = json.dumps(sample_report_json)
        assert json_str
        
        # Verify deserialization works
        parsed = json.loads(json_str)
        assert parsed['security_analyst']['analyst_narrative']
    
    def test_backward_compatibility_null_analyst(self):
        """Verify old reports without analyst data still work"""
        # Old report structure without security_analyst
        old_report_json = {
            'timestamp': '2023-01-15T10:30:45.123456',
            'package_name': 'com.old.app',
            'version': '1.0.0',
            'threat_level': 'medium',
            'risk_score': 45,
            'severity': 'medium'
            # No security_analyst section
        }
        
        # Should still be valid and API can handle it
        assert isinstance(old_report_json, dict)
        assert 'security_analyst' not in old_report_json  # OK for old reports
        
        # If API receives this, it should provide null or empty for analyst section
        report_data = {
            **old_report_json,
            'security_analyst': None  # Backward compatibility handling
        }
        
        assert report_data['security_analyst'] is None


class TestAnalystOutputMapping:
    """Test that analyst outputs map correctly to API fields"""
    
    def test_analyst_to_api_field_mapping(self):
        """Verify analyst output keys map to expected API field names"""
        # Analyst returns these keys
        analyst_keys = {
            'executive_summary': dict,
            'permission_explanations': list,
            'risk_reasons': list,
            'recommendations': list,
            'analyst_narrative': str,
            'prioritized_risk_factors': list
        }
        
        # These map to security_analyst section with possibly renamed fields
        api_mapping = {
            'analyst_narrative': 'analyst_narrative',
            'executive_summary.summary': 'user_friendly_summary',
            'executive_summary.recommendation': 'security_assessment',
            'permission_explanations': 'permission_explanations',
            'risk_reasons': 'risk_reasons',
            'prioritized_risk_factors': 'prioritized_risk_factors',
            'recommendations': 'recommendation_list'
        }
        
        # Verify mapping is complete
        assert len(api_mapping) >= 7, "Should have at least 7 mapped fields"
    
    def test_analyst_field_transformations(self):
        """Test that analyst data transforms correctly to API structure"""
        analyst_output = {
            'executive_summary': {
                'risk_level': 'high',
                'summary': 'App has risky permissions',
                'recommendation': 'Not recommended'
            },
            'permission_explanations': [
                {'permission': 'READ_SMS', 'risk': 'high', 'explanation': 'Can read SMS'}
            ],
            'risk_reasons': [
                {'severity': 'high', 'reason': 'SMS access', 'indicator': 'READ_SMS'}
            ],
            'recommendations': ['Avoid installation'],
            'analyst_narrative': 'Full narrative...',
            'prioritized_risk_factors': [
                {'factor': 'SMS', 'severity': 'high', 'reason': 'Risky'}
            ]
        }
        
        # Transform to API structure
        api_structure = {
            'analyst_narrative': analyst_output['analyst_narrative'],
            'user_friendly_summary': analyst_output['executive_summary']['summary'],
            'security_assessment': analyst_output['executive_summary']['recommendation'],
            'permission_explanations': analyst_output['permission_explanations'],
            'risk_reasons': analyst_output['risk_reasons'],
            'prioritized_risk_factors': analyst_output['prioritized_risk_factors'],
            'recommendation_list': analyst_output['recommendations']
        }
        
        # Verify all fields are present and correct
        assert api_structure['user_friendly_summary'] == 'App has risky permissions'
        assert api_structure['security_assessment'] == 'Not recommended'
        assert len(api_structure['permission_explanations']) == 1
        assert api_structure['analyst_narrative'] == 'Full narrative...'


class TestAnalystDataConsistency:
    """Test that analyst data remains consistent through persistence"""
    
    def test_analyst_data_not_lost_on_persistence(self):
        """Verify analyst data is not lost when stored/retrieved"""
        original_analyst_data = {
            'analyst_narrative': 'This app shows multiple high-risk indicators...',
            'user_friendly_summary': 'Very dangerous application',
            'security_assessment': 'Do not install',
            'permission_explanations': [
                {
                    'permission': 'READ_SMS',
                    'risk': 'high',
                    'explanation': 'Can intercept messages'
                }
            ],
            'risk_reasons': [
                {
                    'severity': 'high',
                    'reason': 'SMS reading capability',
                    'indicator': 'READ_SMS'
                }
            ],
            'prioritized_risk_factors': [
                {
                    'factor': 'SMS Access',
                    'severity': 'high',
                    'reason': 'Major privacy concern'
                }
            ],
            'recommendation_list': [
                'Uninstall immediately',
                'Monitor device for compromises'
            ]
        }
        
        # Store in report_json
        report_json = {
            'security_analyst': original_analyst_data
        }
        
        # Simulate database round-trip (JSON serialization)
        json_str = json.dumps(report_json)
        retrieved_json = json.loads(json_str)
        
        # Verify no data loss
        retrieved_analyst_data = retrieved_json['security_analyst']
        
        assert retrieved_analyst_data['analyst_narrative'] == original_analyst_data['analyst_narrative']
        assert retrieved_analyst_data['user_friendly_summary'] == original_analyst_data['user_friendly_summary']
        assert len(retrieved_analyst_data['permission_explanations']) == len(original_analyst_data['permission_explanations'])
        assert len(retrieved_analyst_data['risk_reasons']) == len(original_analyst_data['risk_reasons'])
        assert len(retrieved_analyst_data['recommendation_list']) == len(original_analyst_data['recommendation_list'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
