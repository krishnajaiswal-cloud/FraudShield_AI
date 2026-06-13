"""
Validation Script: APK Inspector + Risk Scorer Integration

Verifies the integration works without running full analysis.
"""

import sys
import traceback

print("=" * 70)
print("APK Inspector + Risk Scorer Integration Validation")
print("=" * 70)

try:
    # Test 1: Import modules
    print("\n[1] Checking imports...")
    from app.agents.apk_inspector import APKInspector
    print("  ✓ APKInspector imported")
    
    from app.agents.risk_scorer import risk_scorer
    print("  ✓ risk_scorer imported")
    
    from app.services.analysis_service import AnalysisService
    print("  ✓ AnalysisService imported")
    
    # Test 2: Verify APKInspector instantiation
    print("\n[2] Checking APKInspector integration...")
    inspector = APKInspector()
    
    if hasattr(inspector, 'permission_analyzer'):
        print("  ✓ APKInspector has permission_analyzer")
    
    if hasattr(inspector, 'url_extractor'):
        print("  ✓ APKInspector has url_extractor")
    
    print("  ✓ APKInspector instantiated successfully")
    
    # Test 3: Verify AnalysisService handles risk_assessment
    print("\n[3] Checking AnalysisService integration...")
    service = AnalysisService()
    print("  ✓ AnalysisService instantiated")
    
    if hasattr(service, '_map_severity_from_assessment'):
        print("  ✓ _map_severity_from_assessment method exists")
    else:
        print("  ✗ MISSING: _map_severity_from_assessment method")
        sys.exit(1)
    
    # Test 4: Verify RiskScorer
    print("\n[4] Checking RiskScorer...")
    from app.agents.risk_scorer import RiskScorer
    scorer = RiskScorer()
    print("  ✓ RiskScorer instantiated")
    
    # Test with sample data
    test_findings = {
        "permissions": ["READ_SMS", "SEND_SMS"],
        "urls": [],
        "domains": [],
        "activities": [],
        "services": [],
        "receivers": [],
        "providers": []
    }
    
    assessment = scorer.score_apk(test_findings)
    print(f"  ✓ RiskScorer.score_apk() works")
    print(f"    - Risk Score: {assessment.risk_score}/100")
    print(f"    - Severity: {assessment.severity}")
    print(f"    - Factors: {len(assessment.risk_factors)}")
    
    # Test 5: Verify data structure
    print("\n[5] Checking output structure...")
    result_dict = assessment.to_dict()
    
    required_fields = ['risk_score', 'severity', 'risk_factors', 'summary', 'timestamp']
    for field in required_fields:
        if field in result_dict:
            print(f"  ✓ {field} present")
        else:
            print(f"  ✗ MISSING: {field}")
            sys.exit(1)
    
    if 0 <= result_dict['risk_score'] <= 100:
        print(f"  ✓ risk_score in valid range: {result_dict['risk_score']}")
    else:
        print(f"  ✗ risk_score out of range: {result_dict['risk_score']}")
        sys.exit(1)
    
    if result_dict['severity'] in ['low', 'medium', 'high', 'critical']:
        print(f"  ✓ severity is valid: {result_dict['severity']}")
    else:
        print(f"  ✗ Invalid severity: {result_dict['severity']}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✓ ALL VALIDATION CHECKS PASSED")
    print("=" * 70)
    print("\nIntegration Status: READY FOR TESTING")
    print("\nNext Steps:")
    print("  1. Run backend server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("  2. Test API endpoint: POST /api/v1/analysis/{id}/run")
    print("  3. Verify database has risk_score and severity")
    
except Exception as e:
    print(f"\n✗ VALIDATION FAILED")
    print(f"Error: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
