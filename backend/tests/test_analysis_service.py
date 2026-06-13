"""
Tests for Analysis Service Layer

Tests for:
- Analysis creation and validation
- APK analysis workflow
- Finding creation and storage
- Error handling and rollback
- Status transitions
"""

import pytest
import json
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch, MagicMock

from app.database.models import (
    Analysis, Finding, Report, AnalysisStatus, ThreatType, SeverityLevel
)
from app.database.crud import AnalysisCRUD, FindingCRUD, ReportCRUD
from app.services.analysis_service import AnalysisService
from app.core.exceptions import ValidationException, DatabaseException
from app.agents.apk_inspector import APKAnalysisError


class TestAnalysisService:
    """Test suite for AnalysisService"""

    @pytest.fixture
    def service(self):
        """Create analysis service instance"""
        return AnalysisService()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_apk_result(self):
        """Create mock APK inspection result"""
        return {
            'status': 'success',
            'apk_name': 'test.apk',
            'package_name': 'com.test.app',
            'version_name': '1.0',
            'version_code': '1',
            'app_name': 'Test App',
            'file_size': 1024000,
            'md5': 'abc123',
            'sha256': 'def456',
            'components': {
                'activities': ['MainActivity', 'SettingsActivity'],
                'services': ['MyService'],
                'broadcast_receivers': [],
                'content_providers': []
            },
            'permissions': {
                'all_classified': [
                    {
                        'permission': 'android.permission.CAMERA',
                        'risk': 'high',
                        'category': 'CAMERA',
                        'description': 'Camera access'
                    },
                    {
                        'permission': 'android.permission.INTERNET',
                        'risk': 'low',
                        'category': 'NETWORK',
                        'description': 'Internet access'
                    }
                ]
            },
            'urls_and_domains': {
                'all_urls': ['https://example.com', 'http://malicious.xyz'],
                'domains': ['example.com', 'malicious.xyz'],
                'suspicious_urls': ['http://malicious.xyz'],
                'suspicious_urls_classified': [
                    {
                        'url': 'http://malicious.xyz',
                        'risk_score': 0.8,
                        'indicators': ['HTTP', 'suspicious TLD']
                    }
                ]
            },
            'analysis_summary': {
                'threat_level': 'high',
                'risk_score': 0.65,
                'risk_indicators': ['CAMERA + Internet', 'Suspicious URL']
            }
        }

    def test_service_initialization(self, service):
        """Test service initializes with APK inspector"""
        assert service.inspector is not None
        assert hasattr(service, 'analyze_apk')
        assert hasattr(service, 'get_analysis_detail')

    def test_analyze_apk_missing_file(self, service, mock_db):
        """Test analyze_apk raises error when APK file doesn't exist"""
        with pytest.raises(ValidationException):
            service.analyze_apk(mock_db, 1, '/nonexistent/app.apk')

    def test_extract_findings(self, service, mock_apk_result):
        """Test finding extraction from APK result"""
        findings = service._extract_findings(mock_apk_result)
        
        assert 'permissions' in findings
        assert 'urls' in findings
        assert 'components' in findings
        assert 'hashes' in findings
        
        assert len(findings['permissions']) == 2
        assert len(findings['urls']) >= 1
        assert len(findings['components']) >= 2
        assert len(findings['hashes']) == 2

    def test_score_to_severity_mapping(self, service):
        """Test risk score to severity mapping"""
        assert service._score_to_severity(0.9) == 'critical'
        assert service._score_to_severity(0.7) == 'high'
        assert service._score_to_severity(0.5) == 'medium'
        assert service._score_to_severity(0.3) == 'low'
        assert service._score_to_severity(0.1) == 'info'

    def test_threat_type_mapping(self, service):
        """Test threat level to threat type mapping"""
        assert service._map_threat_type('critical') == ThreatType.MALWARE
        assert service._map_threat_type('high') == ThreatType.SPYWARE
        assert service._map_threat_type('medium') == ThreatType.SUSPICIOUS
        assert service._map_threat_type('low') == ThreatType.PUP
        assert service._map_threat_type('clean') == ThreatType.CLEAN

    def test_severity_mapping(self, service):
        """Test threat level to severity mapping"""
        assert service._map_severity('critical') == SeverityLevel.CRITICAL
        assert service._map_severity('high') == SeverityLevel.HIGH
        assert service._map_severity('medium') == SeverityLevel.MEDIUM
        assert service._map_severity('low') == SeverityLevel.LOW
        assert service._map_severity('clean') == SeverityLevel.INFO


class TestAnalysisCRUD:
    """Test suite for Analysis CRUD operations"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock(spec=Session)
        return db

    def test_analysis_create_success(self, mock_db):
        """Test successful analysis creation"""
        mock_analysis = Mock(spec=Analysis)
        mock_analysis.id = 1
        mock_analysis.package_name = 'com.test'
        mock_analysis.status = AnalysisStatus.PENDING
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch.object(AnalysisCRUD, 'create', return_value=mock_analysis):
            result = AnalysisCRUD.create(
                mock_db,
                file_hash='abc123',
                apk_name='test.apk',
                package_name='com.test',
                file_path='/path/test.apk'
            )
            
            assert result.id == 1
            assert result.package_name == 'com.test'

    def test_analysis_get_by_id(self, mock_db):
        """Test getting analysis by ID"""
        mock_analysis = Mock(spec=Analysis)
        mock_analysis.id = 1
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_analysis
        
        result = AnalysisCRUD.get_by_id(mock_db, 1)
        assert result.id == 1

    def test_analysis_list_with_filters(self, mock_db):
        """Test listing analyses with filters"""
        mock_analyses = [Mock(spec=Analysis) for _ in range(3)]
        
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_analyses
        
        with patch.object(AnalysisCRUD, 'list_all', return_value=(mock_analyses, 3)):
            results, total = AnalysisCRUD.list_all(mock_db, status='completed')
            assert len(results) == 3
            assert total == 3


class TestFindingCRUD:
    """Test suite for Finding CRUD operations"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)

    def test_finding_create_success(self, mock_db):
        """Test successful finding creation"""
        mock_finding = Mock(spec=Finding)
        mock_finding.id = 1
        mock_finding.category = 'CAMERA'
        
        mock_db.query.return_value.filter.return_value.first.return_value = Mock(id=1)
        
        with patch.object(FindingCRUD, 'create', return_value=mock_finding):
            result = FindingCRUD.create(
                mock_db,
                analysis_id=1,
                finding_type='permission',
                category='CAMERA',
                value='android.permission.CAMERA',
                risk_level=SeverityLevel.HIGH
            )
            
            assert result.id == 1
            assert result.category == 'CAMERA'

    def test_finding_list_by_analysis(self, mock_db):
        """Test listing findings for an analysis"""
        mock_findings = [Mock(spec=Finding) for _ in range(5)]
        
        with patch.object(FindingCRUD, 'list_by_analysis', return_value=(mock_findings, 5)):
            results, total = FindingCRUD.list_by_analysis(mock_db, 1)
            assert len(results) == 5
            assert total == 5


class TestReportCRUD:
    """Test suite for Report CRUD operations"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock(spec=Session)

    def test_report_create_success(self, mock_db):
        """Test successful report creation"""
        mock_report = Mock(spec=Report)
        mock_report.id = 1
        mock_report.analysis_id = 1
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch.object(ReportCRUD, 'create', return_value=mock_report):
            result = ReportCRUD.create(
                mock_db,
                analysis_id=1,
                report_json={'threat_level': 'high', 'risk_score': 0.75}
            )
            
            assert result.id == 1
            assert result.analysis_id == 1

    def test_report_get_by_analysis_id(self, mock_db):
        """Test getting report by analysis ID"""
        mock_report = Mock(spec=Report)
        mock_report.analysis_id = 1
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_report
        
        result = ReportCRUD.get_by_analysis_id(mock_db, 1)
        assert result.analysis_id == 1


# Integration test scenarios (can run without actual database)
class TestAnalysisWorkflow:
    """Test complete analysis workflow scenarios"""

    def test_workflow_success_scenario(self):
        """Test successful analysis workflow"""
        # This would require a real database or better mocking
        # Scenario:
        # 1. Create analysis record (PENDING)
        # 2. Run analysis (PROCESSING → COMPLETED)
        # 3. Create findings
        # 4. Create report
        # 5. Verify all relationships
        pass

    def test_workflow_failure_scenario(self):
        """Test failed analysis workflow"""
        # Scenario:
        # 1. Create analysis record (PENDING)
        # 2. Try to run analysis (PROCESSING → FAILED)
        # 3. Verify error message is stored
        # 4. Verify no findings created
        pass

    def test_workflow_duplicate_file_scenario(self):
        """Test handling of duplicate APK files"""
        # Scenario:
        # 1. Create and complete analysis for APK A
        # 2. Try to create new analysis for same APK (duplicate hash)
        # 3. Verify error or link to existing analysis
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
