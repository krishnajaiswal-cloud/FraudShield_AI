#!/usr/bin/env python
"""
Test script for APK Inspector functionality
Tests all modules and validates error handling
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    try:
        from app.analysis.androguard_parser import AndroguardParser, AndroguardParseError
        print("✓ AndroguardParser imported")
        
        from app.analysis.url_extractor import URLExtractor
        print("✓ URLExtractor imported")
        
        from app.analysis.permission_analyzer import PermissionAnalyzer
        print("✓ PermissionAnalyzer imported")
        
        from app.agents.apk_inspector import APKInspector, analyze_apk, APKAnalysisError
        print("✓ APKInspector imported")
        
        print("\n✓ All imports successful!\n")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}\n")
        return False


def test_url_extractor():
    """Test URLExtractor functionality"""
    print("=" * 60)
    print("TEST 2: URL Extractor")
    print("=" * 60)
    try:
        from app.analysis.url_extractor import URLExtractor
        
        extractor = URLExtractor(include_common=False)
        
        # Test URL extraction
        test_strings = [
            "https://secure.example.com/login",
            "http://malicious.xyz/payload",
            "ftp://files.domain.com/data",
            "example.com",  # Invalid format
            "192.168.1.1",  # IP address
        ]
        
        all_urls, suspicious_urls, classified = extractor.extract_urls_and_analyze(test_strings)
        
        print(f"Found {len(all_urls)} URLs")
        print(f"Found {len(suspicious_urls)} suspicious URLs")
        print(f"Classified {len(classified)} URLs with risk scores")
        
        if classified:
            for item in classified[:3]:  # Show first 3
                print(f"  - {item['url']}: risk={item['risk_score']:.2f}")
        
        print("\n✓ URL Extractor works!\n")
        return True
    except Exception as e:
        print(f"✗ URL Extractor failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_permission_analyzer():
    """Test PermissionAnalyzer functionality"""
    print("=" * 60)
    print("TEST 3: Permission Analyzer")
    print("=" * 60)
    try:
        from app.analysis.permission_analyzer import PermissionAnalyzer
        
        analyzer = PermissionAnalyzer()
        
        # Test permission classification
        test_permissions = [
            "android.permission.INTERNET",
            "android.permission.CAMERA",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.READ_SMS",
            "android.permission.RECORD_AUDIO",
        ]
        
        summary = analyzer.get_permission_summary(test_permissions)
        
        print(f"Risk Score: {summary['risk_score']:.2f}")
        print(f"Risk counts: {summary['risk_counts']}")
        
        # Test combination detection
        combination_perms = [
            "android.permission.CAMERA",
            "android.permission.RECORD_AUDIO",
            "android.permission.INTERNET",
        ]
        
        risky_combinations = analyzer.detect_suspicious_combinations(combination_perms)
        print(f"\nSuspicious combinations found: {len(risky_combinations)}")
        for combo in risky_combinations:
            print(f"  - {combo['name']}: {combo['permissions']}")
        
        print("\n✓ Permission Analyzer works!\n")
        return True
    except Exception as e:
        print(f"✗ Permission Analyzer failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_apk_validation():
    """Test APK validation and error handling"""
    print("=" * 60)
    print("TEST 4: APK Validation & Error Handling")
    print("=" * 60)
    try:
        from app.agents.apk_inspector import APKInspector, APKAnalysisError
        from app.core.exceptions import ValidationException
        
        inspector = APKInspector()
        
        # Test 1: Non-existent file
        try:
            inspector.analyze_apk("/nonexistent/path/app.apk")
            print("✗ Should have raised error for non-existent file")
            return False
        except (APKAnalysisError, ValidationException) as e:
            print(f"✓ Correctly caught non-existent file: {str(e)[:50]}...")
        
        # Test 2: Wrong file extension
        try:
            inspector.analyze_apk("/path/file.txt")
            print("✗ Should have raised error for wrong extension")
            return False
        except (APKAnalysisError, ValidationException) as e:
            print(f"✓ Correctly caught wrong extension: {str(e)[:50]}...")
        
        # Test 3: Empty path
        try:
            inspector.analyze_apk("")
            print("✗ Should have raised error for empty path")
            return False
        except (APKAnalysisError, ValidationException) as e:
            print(f"✓ Correctly caught empty path: {str(e)[:50]}...")
        
        print("\n✓ All validation tests passed!\n")
        return True
    except Exception as e:
        print(f"✗ Validation tests failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_androguard_integration():
    """Test Androguard integration"""
    print("=" * 60)
    print("TEST 5: Androguard Integration")
    print("=" * 60)
    try:
        from androguard.misc import AnalyzeAPK
        from androguard.core.apk import APK
        
        print("✓ androguard.misc.AnalyzeAPK available")
        print("✓ androguard.core.apk.APK available")
        
        # Verify Androguard version
        import androguard
        print(f"✓ Androguard version: {androguard.__version__}")
        
        print("\n✓ Androguard integration successful!\n")
        return True
    except Exception as e:
        print(f"✗ Androguard integration failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + " APK Inspector Test Suite ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("URL Extractor", test_url_extractor()))
    results.append(("Permission Analyzer", test_permission_analyzer()))
    results.append(("APK Validation", test_apk_validation()))
    results.append(("Androguard Integration", test_androguard_integration()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed\n")
    
    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
