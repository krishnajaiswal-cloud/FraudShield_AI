"""
Integration Test for Risk Scoring Endpoint

Tests the complete risk scoring workflow through the API.
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api/v1"


def create_test_analysis():
    """Create a test analysis record"""
    print("Creating test analysis...")
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    payload = {
        "apk_name": f"test_malware_{unique_id}.apk",
        "package_name": f"com.test.malware.{unique_id}",
        "file_path": f"./app/storage/uploads/test_malware_{unique_id}.apk",
        "file_hash": f"abc123def456_{unique_id}",
        "file_size": 5000000,
        "version_name": "1.0.0",
        "version_code": "1",
        "app_name": "Test Malware",
        "md5_hash": f"abc123def456_{unique_id}"
    }
    
    response = requests.post(f"{API_BASE}/analysis", json=payload)
    assert response.status_code == 201, f"Failed to create analysis: {response.text}"
    
    analysis = response.json()
    analysis_id = analysis["id"]
    print(f"[OK] Analysis created: ID {analysis_id}")
    
    return analysis_id


def manually_add_findings(analysis_id):
    """Manually add findings to analysis via database"""
    print(f"Adding findings to analysis {analysis_id}...")
    
    from app.database.database import SessionLocal
    from app.database.crud import FindingCRUD
    from app.database.models import SeverityLevel
    
    db = SessionLocal()
    
    try:
        # Add dangerous permissions
        permissions = [
            "READ_SMS", "SEND_SMS", "READ_CONTACTS",
            "BIND_ACCESSIBILITY_SERVICE", "REQUEST_INSTALL_PACKAGES"
        ]
        
        for perm in permissions:
            FindingCRUD.create(
                db,
                analysis_id=analysis_id,
                finding_type="permission",
                category="PERMISSIONS",
                value=perm,
                risk_level=SeverityLevel.HIGH
            )
        
        # Add suspicious URLs
        urls = [
            "http://malware.tk/command",
            "http://192.168.1.1:8080/data"
        ]
        
        for url in urls:
            FindingCRUD.create(
                db,
                analysis_id=analysis_id,
                finding_type="url",
                category="URLS",
                value=url,
                risk_level=SeverityLevel.HIGH,
                risk_score=0.8
            )
        
        # Add suspicious domains
        domains = ["bit.ly/malware"]
        
        for domain in domains:
            FindingCRUD.create(
                db,
                analysis_id=analysis_id,
                finding_type="domain",
                category="DOMAINS",
                value=domain,
                risk_level=SeverityLevel.HIGH
            )
        
        db.commit()
        print(f"[OK] Added {len(permissions)} permissions, {len(urls)} URLs, {len(domains)} domains")
        
    finally:
        db.close()


def test_risk_scoring(analysis_id):
    """Test risk scoring endpoint"""
    print(f"\nTesting risk scoring for analysis {analysis_id}...")
    
    response = requests.post(f"{API_BASE}/analysis/{analysis_id}/score")
    
    if response.status_code != 200:
        print(f"[FAIL] Risk scoring failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    assessment = response.json()
    
    print(f"[OK] Risk assessment calculated:")
    print(f"  Risk Score: {assessment['risk_score']}/100")
    print(f"  Severity: {assessment['severity']}")
    print(f"  Risk Factors: {len(assessment['risk_factors'])}")
    
    # Print top risk factors
    print(f"\n  Top Risk Factors:")
    for factor in sorted(assessment['risk_factors'], key=lambda x: x['score'], reverse=True)[:5]:
        print(f"    - {factor['factor']}: +{factor['score']} ({factor['category']})")
        print(f"      Reason: {factor['reason']}")
    
    print(f"\n  Summary: {assessment['summary']}")
    
    # Verify assessment structure
    assert "risk_score" in assessment
    assert "severity" in assessment
    assert "risk_factors" in assessment
    assert "summary" in assessment
    assert "timestamp" in assessment
    
    # Verify risk score is in valid range
    assert 0 <= assessment['risk_score'] <= 100, "Risk score out of range"
    
    # Verify severity is valid
    assert assessment['severity'] in ["low", "medium", "high", "critical"]
    
    # Verify risk factors have details
    assert len(assessment['risk_factors']) > 0
    for factor in assessment['risk_factors']:
        assert "factor" in factor
        assert "category" in factor
        assert "score" in factor
        assert "reason" in factor
        assert "severity" in factor
    
    print("\n[OK] All assertions passed!")
    return True


def test_risk_scoring_empty_findings(analysis_id):
    """Test risk scoring with no findings"""
    print(f"\nTesting risk scoring with no findings...")
    
    from app.database.database import SessionLocal
    from app.database.crud import AnalysisCRUD
    from app.database.models import Analysis
    import uuid
    
    db = SessionLocal()
    unique_id = str(uuid.uuid4())[:8]
    
    # Create another analysis with no findings
    analysis = Analysis(
        apk_name=f"clean_app_{unique_id}.apk",
        package_name=f"com.test.clean.{unique_id}",
        file_path=f"./test_{unique_id}.apk",
        file_hash=f"clean{unique_id}",
        md5_hash=f"clean{unique_id}"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    analysis_id = analysis.id
    db.close()
    
    # Try to score it (should fail because no findings)
    response = requests.post(f"{API_BASE}/analysis/{analysis_id}/score")
    
    if response.status_code == 400:
        error = response.json()
        print(f"[OK] Correctly rejected: {error['detail']}")
        return True
    else:
        print(f"[FAIL] Expected 400, got {response.status_code}")
        return False


def test_nonexistent_analysis():
    """Test risk scoring for non-existent analysis"""
    print(f"\nTesting risk scoring for non-existent analysis...")
    
    response = requests.post(f"{API_BASE}/analysis/99999/score")
    
    if response.status_code == 404:
        print(f"[OK] Correctly returned 404")
        return True
    else:
        print(f"[FAIL] Expected 404, got {response.status_code}")
        return False


def verify_database_update(analysis_id):
    """Verify risk score was stored in database"""
    print(f"\nVerifying database update for analysis {analysis_id}...")
    
    from app.database.database import SessionLocal
    from app.database.crud import AnalysisCRUD
    
    db = SessionLocal()
    
    try:
        analysis = AnalysisCRUD.get_by_id(db, analysis_id)
        
        assert analysis is not None, "Analysis not found in database"
        assert analysis.risk_score is not None, "Risk score not stored"
        assert analysis.severity is not None, "Severity not stored"
        assert 0 <= analysis.risk_score <= 1, "Risk score out of range (should be 0-1 in DB)"
        
        print(f"[OK] Database updated:")
        print(f"  Risk Score: {analysis.risk_score:.2f}")
        print(f"  Severity: {analysis.severity}")
        
        return True
        
    finally:
        db.close()


def main():
    """Run integration tests"""
    print("\n" + "="*70)
    print("Risk Scoring Endpoint Integration Test")
    print("="*70 + "\n")
    
    results = []
    
    try:
        # Create test analysis
        analysis_id = create_test_analysis()
        
        # Add findings
        manually_add_findings(analysis_id)
        
        # Test risk scoring
        results.append(("Risk Scoring", test_risk_scoring(analysis_id)))
        
        # Verify database update
        results.append(("Database Update", verify_database_update(analysis_id)))
        
        # Test empty findings
        results.append(("Empty Findings", test_risk_scoring_empty_findings(analysis_id)))
        
        # Test non-existent analysis
        results.append(("Non-existent Analysis", test_nonexistent_analysis()))
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
