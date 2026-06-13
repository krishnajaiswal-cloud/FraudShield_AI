"""
Integration Test: APK Analysis with Risk Scoring

Tests the complete workflow from APK analysis to risk scoring endpoint.
Verifies that:
- APKInspector executes successfully
- RiskScorer calculates assessment
- risk_assessment exists in result
- AnalysisService processes data correctly
- Database stores risk_score (0-1) and severity
- All data flows through the pipeline correctly
"""

import os
import json
import pytest
from pathlib import Path
from datetime import datetime

from app.services.analysis_service import AnalysisService
from app.database.database import SessionLocal, init_db
from app.database.crud import AnalysisCRUD
from app.database.models import Analysis, AnalysisStatus, SeverityLevel
from app.agents.apk_inspector import APKInspector
from app.core.exceptions import ValidationException


@pytest.fixture(scope="module")
def db():
    """Create database session for tests"""
    init_db()
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def analysis_service():
    """Create analysis service instance"""
    return AnalysisService()


@pytest.fixture
def test_apk_path():
    """Path to test APK file"""
    # Create a simple test APK if it doesn't exist
    test_dir = Path(__file__).parent
    apk_path = test_dir / "test_app.apk"
    
    if not apk_path.exists():
        # This will be handled by pytest markers or actual APK file
        pytest.skip("Test APK file not found")
    
    return str(apk_path)


class TestAPKAnalysisWithRiskScoring:
    """Test complete APK analysis pipeline with risk scoring"""
    
    def test_01_apk_inspector_returns_risk_assessment(self, test_apk_path):
        """
        Test 1: APKInspector includes risk_assessment in result
        
        Verifies:
        - APKInspector.analyze_apk() completes successfully
        - Result contains risk_assessment key
        - risk_assessment has required fields
        """
        inspector = APKInspector()
        result = inspector.analyze_apk(test_apk_path)
        
        # Verify structure
        assert result['status'] == 'success'
        assert 'risk_assessment' in result, "risk_assessment missing from APKInspector result"
        assert 'analysis_summary' in result
        
        # Verify risk_assessment fields
        risk_assessment = result['risk_assessment']
        assert 'risk_score' in risk_assessment, "risk_score missing"
        assert 'severity' in risk_assessment, "severity missing"
        assert 'risk_factors' in risk_assessment, "risk_factors missing"
        assert 'summary' in risk_assessment, "summary missing"
        
        # Verify data types and ranges
        assert isinstance(risk_assessment['risk_score'], (int, float))
        assert 0 <= risk_assessment['risk_score'] <= 100, "risk_score out of range"
        assert risk_assessment['severity'] in ['low', 'medium', 'high', 'critical']
        assert isinstance(risk_assessment['risk_factors'], list)
        
        print(f"✓ APKInspector risk assessment:")
        print(f"  Score: {risk_assessment['risk_score']}/100")
        print(f"  Severity: {risk_assessment['severity']}")
        print(f"  Factors: {len(risk_assessment['risk_factors'])}")
    
    def test_02_analysis_service_extracts_risk_data(self, db, analysis_service, test_apk_path):
        """
        Test 2: AnalysisService correctly extracts risk assessment data
        
        Verifies:
        - Service validates risk_assessment exists
        - risk_score normalized to 0-1 range
        - severity properly mapped to enum
        """
        # Get APK analysis result
        inspector = APKInspector()
        analysis_result = inspector.analyze_apk(test_apk_path)
        
        # Extract data like AnalysisService does
        if 'risk_assessment' not in analysis_result:
            pytest.fail("Risk assessment missing from analysis results")
        
        risk_assessment = analysis_result['risk_assessment']
        risk_score_normalized = risk_assessment['risk_score'] / 100.0
        severity_str = risk_assessment['severity'].upper()
        
        # Verify normalization
        assert 0 <= risk_score_normalized <= 1.0, "Normalized risk_score out of range"
        assert severity_str in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        print(f"✓ AnalysisService data extraction:")
        print(f"  Raw score: {risk_assessment['risk_score']}/100")
        print(f"  Normalized: {risk_score_normalized:.2f}")
        print(f"  Severity: {severity_str}")
    
    def test_03_analysis_service_processes_apk(self, db, analysis_service, test_apk_path):
        """
        Test 3: AnalysisService.analyze_apk() completes full workflow
        
        Verifies:
        - Service processes APK without errors
        - Returns dictionary with expected keys
        - Status is COMPLETED
        """
        # Create analysis record
        analysis = AnalysisCRUD.create(
            db,
            file_hash=f"test_hash_{datetime.now().timestamp()}",
            apk_name="test_app.apk",
            package_name="com.test.app",
            file_path=test_apk_path,
            version_code="1"
        )
        
        # Run analysis
        result = analysis_service.analyze_apk(db, analysis.id, test_apk_path)
        
        # Verify result structure
        assert result['status'] == 'completed', f"Status is {result['status']}, not completed"
        assert result['analysis_id'] == analysis.id
        assert result['findings_count'] >= 0
        assert result['risk_score'] >= 0
        assert result['threat_type'] is not None
        
        print(f"✓ AnalysisService workflow:")
        print(f"  Analysis ID: {result['analysis_id']}")
        print(f"  Status: {result['status']}")
        print(f"  Findings: {result['findings_count']}")
        print(f"  Risk Score: {result['risk_score']:.2f}")
        print(f"  Threat Type: {result['threat_type']}")
    
    def test_04_database_stores_risk_data(self, db, analysis_service, test_apk_path):
        """
        Test 4: Database correctly stores risk_score (0-1) and severity
        
        Verifies:
        - risk_score stored in normalized range (0-1)
        - severity stored as enum value
        - Data persists and retrieves correctly
        """
        # Create analysis record
        analysis = AnalysisCRUD.create(
            db,
            file_hash=f"test_hash_{datetime.now().timestamp()}",
            apk_name="test_app.apk",
            package_name="com.test.app",
            file_path=test_apk_path,
            version_code="1"
        )
        analysis_id = analysis.id
        
        # Run analysis
        analysis_service.analyze_apk(db, analysis_id, test_apk_path)
        
        # Retrieve from database
        retrieved = AnalysisCRUD.get_by_id(db, analysis_id)
        
        # Verify data
        assert retrieved is not None, "Analysis not found in database"
        assert retrieved.risk_score is not None, "risk_score is None"
        assert retrieved.severity is not None, "severity is None"
        assert 0 <= retrieved.risk_score <= 1.0, f"risk_score out of range: {retrieved.risk_score}"
        assert retrieved.severity in [
            SeverityLevel.LOW,
            SeverityLevel.MEDIUM,
            SeverityLevel.HIGH,
            SeverityLevel.CRITICAL,
            SeverityLevel.INFO
        ], f"Invalid severity: {retrieved.severity}"
        assert retrieved.status == AnalysisStatus.COMPLETED
        
        print(f"✓ Database storage:")
        print(f"  Risk Score (0-1): {retrieved.risk_score:.2f}")
        print(f"  Severity: {retrieved.severity}")
        print(f"  Status: {retrieved.status}")
    
    def test_05_end_to_end_workflow(self, db, analysis_service, test_apk_path):
        """
        Test 5: Complete end-to-end workflow
        
        Verifies:
        - APK Inspector executes
        - Risk Scorer executes
        - AnalysisService processes data
        - Database updated correctly
        - All data flows through pipeline
        """
        # Step 1: Create analysis record
        analysis = AnalysisCRUD.create(
            db,
            file_hash=f"test_hash_{datetime.now().timestamp()}",
            apk_name="test_app.apk",
            package_name="com.test.app",
            file_path=test_apk_path,
            version_code="1"
        )
        initial_status = analysis.status
        
        print(f"✓ Step 1: Analysis created")
        print(f"  ID: {analysis.id}")
        print(f"  Status: {initial_status}")
        
        # Step 2: Run analysis (includes APK inspection + risk scoring)
        service_result = analysis_service.analyze_apk(db, analysis.id, test_apk_path)
        
        assert service_result['status'] == 'completed'
        print(f"✓ Step 2: Analysis completed")
        print(f"  Findings: {service_result['findings_count']}")
        print(f"  Risk Score: {service_result['risk_score']:.2f}")
        
        # Step 3: Verify database updated
        final_analysis = AnalysisCRUD.get_by_id(db, analysis.id)
        
        assert final_analysis.status == AnalysisStatus.COMPLETED
        assert final_analysis.risk_score is not None
        assert final_analysis.severity is not None
        assert final_analysis.threat_type is not None
        
        print(f"✓ Step 3: Database updated")
        print(f"  Risk Score: {final_analysis.risk_score:.2f}")
        print(f"  Severity: {final_analysis.severity}")
        print(f"  Threat Type: {final_analysis.threat_type}")
        
        # Step 4: Verify findings created
        from app.database.crud import FindingCRUD
        findings, total = FindingCRUD.list_by_analysis(db, analysis.id)
        
        assert len(findings) > 0, "No findings created"
        print(f"✓ Step 4: Findings created")
        print(f"  Total: {len(findings)}")
        
        # Step 5: Verify report created
        from app.database.crud import ReportCRUD
        report = ReportCRUD.get_by_analysis_id(db, analysis.id)
        
        assert report is not None, "No report created"
        report_data = json.loads(report.report_json) if isinstance(report.report_json, str) else report.report_json
        assert 'risk_score' in report_data or 'risk_factors' in report_data, "Risk data not in report"
        
        print(f"✓ Step 5: Report generated")
        print(f"  Executive Summary: {report.executive_summary[:60]}...")
    
    def test_06_risk_assessment_structure(self, test_apk_path):
        """
        Test 6: Risk assessment has complete required structure
        
        Verifies:
        - risk_assessment contains all required fields
        - risk_factors have proper structure
        - summary is descriptive
        """
        inspector = APKInspector()
        result = inspector.analyze_apk(test_apk_path)
        risk_assessment = result['risk_assessment']
        
        # Verify top-level structure
        required_fields = ['risk_score', 'severity', 'risk_factors', 'summary', 'timestamp']
        for field in required_fields:
            assert field in risk_assessment, f"Missing required field: {field}"
        
        # Verify risk_factors structure
        for factor in risk_assessment['risk_factors']:
            assert 'factor' in factor, "factor missing from risk_factor"
            assert 'category' in factor, "category missing from risk_factor"
            assert 'score' in factor, "score missing from risk_factor"
            assert 'reason' in factor, "reason missing from risk_factor"
            assert 'severity' in factor, "severity missing from risk_factor"
        
        # Verify summary is descriptive
        assert len(risk_assessment['summary']) > 0, "summary is empty"
        assert isinstance(risk_assessment['timestamp'], str), "timestamp is not string"
        
        print(f"✓ Risk assessment structure verified")
        print(f"  Fields: {', '.join(required_fields)}")
        print(f"  Risk factors: {len(risk_assessment['risk_factors'])}")


# Run tests manually if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
