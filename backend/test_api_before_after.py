"""
Before/After API Test

Demonstrates that the security analyst agent now correctly:
1. Reads permission data from APKInspector
2. Includes accurate permission counts in narrative
3. Explains dangerous permissions correctly
4. Includes critical permissions in risk reasons
"""

import json
from app.agents.apk_inspector import APKInspector
from app.agents.security_analyst import security_analyst


# Simulated APKInspector result (what analyze_apk() returns)
APKISPECTOR_RESULT = {
    "status": "success",
    "apk_name": "banking.apk",
    "package_name": "com.example.banking",
    "version_name": "1.0.0",
    "version_code": "1",
    "app_name": "Banking App",
    "file_size": 5242880,
    "md5": "abc123def456",
    "sha256": "sha256hash",
    "components": {
        "activities": ["MainActivity", "LoginActivity"],
        "services": ["SyncService", "NotificationService"],
        "broadcast_receivers": ["BootReceiver", "SMSReceiver"],
        "content_providers": []
    },
    "permissions": {
        "all_permissions": [
            "android.permission.RECEIVE_SMS",
            "android.permission.READ_SMS",
            "android.permission.SEND_SMS",
            "android.permission.RECEIVE_BOOT_COMPLETED",
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE",
            "android.permission.READ_CONTACTS",
            "android.permission.READ_CALL_LOG",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.CAMERA"
        ],
        "dangerous_list": [
            "android.permission.RECEIVE_SMS",
            "android.permission.READ_SMS",
            "android.permission.RECEIVE_BOOT_COMPLETED",
            "android.permission.INTERNET"
        ],
        "total_permissions": 12,
        "dangerous_permissions": 4,
        "risk_score": 0.75,
        "risk_counts": {"critical": 2, "high": 3, "medium": 4, "low": 3}
    },
    "urls_and_domains": {
        "url_count": 3,
        "domain_count": 2,
        "suspicious_count": 1,
        "urls": [
            "https://api.banking.com/v1",
            "https://cdn.banking.com/assets",
            "http://ads.suspicious.com"
        ],
        "domains": ["banking.com", "suspicious.com"],
        "suspicious_urls": ["http://ads.suspicious.com"],
        "classified_urls": []
    },
    "analysis_summary": {
        "threat_level": "high",
        "risk_indicators": [
            "✗ 2 critical permissions",
            "✗ 3 high-risk permissions",
            "⚠ 1 suspicious URLs/domains"
        ],
        "dangerous_permissions": 4,
        "suspicious_combinations": 1,
        "suspicious_urls": 1,
        "total_components": 5,
        "exported_components": 2
    },
    "risk_assessment": {
        "risk_score": 75,
        "severity": "high",
        "risk_factors": [
            {
                "factor": "SMS Access",
                "severity": "critical",
                "score": 25,
                "description": "Can intercept SMS messages"
            },
            {
                "factor": "Boot Persistence",
                "severity": "high",
                "score": 20,
                "description": "Runs on device boot"
            }
        ],
        "summary": "High-risk banking app with dangerous permissions"
    }
}


def test_security_analyst_output():
    """Test that SecurityAnalystAgent now outputs correct permission data"""
    
    print("=" * 80)
    print("SECURITY ANALYST AGENT - PERMISSION FIX VERIFICATION")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("INPUT: APKInspector Result")
    print("=" * 80)
    print(f"Total Permissions: {APKISPECTOR_RESULT['permissions']['total_permissions']}")
    print(f"Dangerous Permissions: {APKISPECTOR_RESULT['permissions']['dangerous_permissions']}")
    print(f"Dangerous List: {APKISPECTOR_RESULT['permissions']['dangerous_list']}")
    
    print("\n" + "=" * 80)
    print("PROCESSING: Generating Security Analysis")
    print("=" * 80)
    
    result = security_analyst.analyze_apk(APKISPECTOR_RESULT)
    
    print("\n" + "=" * 80)
    print("OUTPUT: Security Analyst Assessment")
    print("=" * 80)
    
    # 1. Analyst Narrative
    print("\n--- ANALYST NARRATIVE ---")
    narrative = result.get("analyst_narrative", "")
    print(narrative[:500] + "...\n")
    
    # Verify narrative includes permission counts
    if "12" in narrative and "4" not in narrative.split("permissions")[0]:
        print("✓ FIXED: Narrative now includes actual permission counts (not 0)")
    else:
        print(f"✗ ISSUE: Narrative doesn't have correct counts. First 300 chars:\n{narrative[:300]}")
    
    # 2. Permission Explanations
    print("\n--- PERMISSION EXPLANATIONS (Dangerous Permissions) ---")
    explanations = result.get("permission_explanations", [])
    print(f"Total explanations generated: {len(explanations)}")
    
    # Show dangerous permission explanations
    dangerous_explanations = [e for e in explanations if e["risk"] in ["critical", "high"]]
    print(f"Dangerous/Critical permissions explained: {len(dangerous_explanations)}\n")
    
    for exp in dangerous_explanations[:5]:  # Show first 5
        perm_short = exp["permission"].split('.')[-1] if '.' in exp["permission"] else exp["permission"]
        print(f"{perm_short} (Risk: {exp['risk']})")
        print(f"  {exp['explanation']}\n")
    
    # Verify dangerous permissions are explained
    explained_perms = {e["permission"] for e in explanations}
    if "android.permission.RECEIVE_SMS" in explained_perms:
        print("✓ FIXED: RECEIVE_SMS is properly explained")
    if "android.permission.RECEIVE_BOOT_COMPLETED" in explained_perms:
        print("✓ FIXED: RECEIVE_BOOT_COMPLETED is properly explained")
    
    # 3. Risk Reasons
    print("\n--- RISK REASONS (Top Critical Findings) ---")
    risk_reasons = result.get("risk_reasons", [])
    print(f"Total risk reasons: {len(risk_reasons)}\n")
    
    critical_reasons = [r for r in risk_reasons if r["severity"] in ["critical", "high"]]
    for reason in critical_reasons[:3]:
        print(f"[{reason['severity'].upper()}] {reason['reason']}")
        print(f"  Indicator: {reason['indicator']}\n")
    
    # Verify critical permissions are in risk reasons
    sms_reasons = [r for r in risk_reasons if "sms" in r["reason"].lower()]
    boot_reasons = [r for r in risk_reasons if "boot" in r["reason"].lower()]
    
    if sms_reasons:
        print("✓ FIXED: SMS risks are identified in risk reasons")
    if boot_reasons:
        print("✓ FIXED: Boot persistence risks are identified in risk reasons")
    
    # 4. Executive Summary
    print("\n--- EXECUTIVE SUMMARY ---")
    summary = result.get("executive_summary", {})
    print(f"Risk Level: {summary.get('risk_level')}")
    print(f"Summary: {summary.get('summary')}")
    print(f"Recommendation: {summary.get('recommendation')}")
    
    # 5. Recommendations
    print("\n--- RECOMMENDATIONS ---")
    recommendations = result.get("recommendations", [])
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    checks = {
        "Permission count in narrative matches actual (12)": "12" in narrative,
        "Dangerous permission count in narrative (4)": "4" in narrative or "4" in ' '.join([e.get("permission", "") for e in explanations]),
        "RECEIVE_SMS explained (CRITICAL)": any("RECEIVE_SMS" in e.get("permission", "") for e in explanations),
        "RECEIVE_BOOT_COMPLETED explained (HIGH)": any("RECEIVE_BOOT_COMPLETED" in e.get("permission", "") for e in explanations),
        "INTERNET explained (LOW)": any("INTERNET" in e.get("permission", "") and e.get("risk") == "low" for e in explanations),
        "SMS risks in risk reasons": len(sms_reasons) > 0,
        "Boot persistence risks in risk reasons": len(boot_reasons) > 0,
        "Total permissions explained equals actual": len(explanations) == 12,
        "Not claiming '0 permissions'": "0 permissions" not in narrative.lower()
    }
    
    print("\nTest Results:")
    passed = 0
    failed = 0
    for check, result_val in checks.items():
        status = "✓ PASS" if result_val else "✗ FAIL"
        print(f"  {status}: {check}")
        if result_val:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed out of {len(checks)} checks")
    
    if failed == 0:
        print("\n🎉 ALL CHECKS PASSED - PERMISSION DATA FLOW IS FIXED!")
    else:
        print(f"\n⚠️  {failed} checks failed - Review output above")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_security_analyst_output()
