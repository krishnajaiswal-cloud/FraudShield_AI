"""
Unit Tests for Security Analyst Agent

Tests cover:
- Executive summary generation
- Permission explanations
- Risk reasoning
- Recommendations
- Analysis narrative
- Risk factor prioritization
- Complete APK analysis workflow
"""

import unittest
import json
from datetime import datetime, timezone
from app.agents.security_analyst import (
    SecurityAnalystAgent, ExecutiveSummary, PermissionExplanation,
    RiskReason, RiskLevel, security_analyst
)


class TestSecurityAnalystAgent(unittest.TestCase):
    """Test suite for SecurityAnalystAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyst = SecurityAnalystAgent()
        
        # Sample analysis result
        self.sample_analysis = {
            "package_name": "com.example.app",
            "app_name": "Example App",
            "version_name": "1.0.0",
            "version_code": "100",
            "file_size": 5242880,
            "md5": "abc123def456",
            "sha256": "sha256hash",
            "permissions": {
                "requested": [
                    "android.permission.READ_SMS",
                    "android.permission.SEND_SMS",
                    "android.permission.READ_CONTACTS",
                    "android.permission.ACCESS_FINE_LOCATION",
                    "android.permission.CAMERA",
                    "android.permission.INTERNET"
                ]
            },
            "urls_and_domains": {
                "urls": [
                    "http://example.com",
                    "https://secure.example.com",
                    "http://suspicious-site.com"
                ],
                "domains": ["example.com", "suspicious-site.com"]
            },
            "components": {
                "activities": ["Activity1", "Activity2"],
                "services": ["Service1", "Service2", "Service3"],
                "receivers": [
                    {"name": "BootReceiver", "intent_filters": ["BOOT_COMPLETED"]},
                    {"name": "SMSReceiver", "intent_filters": ["SMS_RECEIVED"]}
                ],
                "providers": ["Provider1"]
            },
            "analysis_summary": {
                "threat_level": "high",
                "risk_indicators": ["sms_access", "location_access", "suspicious_urls"]
            },
            "risk_assessment": {
                "risk_score": 72,
                "severity": "high",
                "risk_factors": [
                    {
                        "factor": "SMS Access",
                        "category": "permissions",
                        "score": 20,
                        "reason": "Can read SMS messages",
                        "severity": "high"
                    }
                ],
                "summary": "High-risk application with dangerous permissions"
            }
        }
    
    def test_summary_generation_safe(self):
        """Test executive summary for safe app (score 0-25)"""
        summary = self.analyst.generate_summary(15, "low", "clean")
        
        self.assertEqual(summary.risk_level, "Safe")
        self.assertIn("minimal risk", summary.summary.lower())
        self.assertIn("safe", summary.recommendation.lower())
    
    def test_summary_generation_moderate(self):
        """Test executive summary for moderate app (score 26-50)"""
        summary = self.analyst.generate_summary(40, "medium", "suspicious")
        
        self.assertEqual(summary.risk_level, "Moderate")
        self.assertIn("concerning", summary.summary.lower())
        self.assertIn("trusted source", summary.recommendation.lower())
    
    def test_summary_generation_high(self):
        """Test executive summary for high-risk app (score 51-75)"""
        summary = self.analyst.generate_summary(65, "high", "spyware")
        
        self.assertEqual(summary.risk_level, "High")
        self.assertIn("risky", summary.summary.lower())
        self.assertTrue(
            "caution" in summary.recommendation.lower() or 
            "necessary" in summary.recommendation.lower()
        )
    
    def test_summary_generation_critical(self):
        """Test executive summary for critical app (score 76-100)"""
        summary = self.analyst.generate_summary(90, "critical", "malware")
        
        self.assertEqual(summary.risk_level, "Critical")
        self.assertIn("dangerous", summary.summary.lower())
        self.assertIn("not install", summary.recommendation.lower())
    
    def test_explain_permissions_known(self):
        """Test explaining known permissions"""
        permissions = ["READ_SMS", "SEND_SMS", "CAMERA"]
        explanations = self.analyst.explain_permissions(permissions)
        
        self.assertEqual(len(explanations), 3)
        
        # Verify all permissions are explained
        perm_names = {e["permission"] for e in explanations}
        self.assertEqual(perm_names, {"READ_SMS", "SEND_SMS", "CAMERA"})
        
        # Verify explanations have required fields
        for exp in explanations:
            self.assertIn("permission", exp)
            self.assertIn("risk", exp)
            self.assertIn("explanation", exp)
            self.assertIn(exp["risk"], ["critical", "high", "medium", "low", "info"])
    
    def test_explain_permissions_unknown(self):
        """Test explaining unknown permissions"""
        permissions = ["UNKNOWN_PERMISSION"]
        explanations = self.analyst.explain_permissions(permissions)
        
        self.assertEqual(len(explanations), 1)
        self.assertEqual(explanations[0]["permission"], "UNKNOWN_PERMISSION")
        self.assertEqual(explanations[0]["risk"], "low")
    
    def test_explain_permissions_sorting(self):
        """Test that permissions are sorted by risk"""
        permissions = ["INTERNET", "REQUEST_INSTALL_PACKAGES", "RECORD_AUDIO"]
        explanations = self.analyst.explain_permissions(permissions)
        
        # Should be sorted with CRITICAL/HIGH first
        risk_order = [e["risk"] for e in explanations]
        # REQUEST_INSTALL_PACKAGES is CRITICAL, so it should be first
        self.assertEqual(risk_order[0], "critical")
    
    def test_generate_risk_reasons(self):
        """Test generating risk reasons from analysis"""
        reasons = self.analyst.generate_risk_reasons(self.sample_analysis)
        
        self.assertIsInstance(reasons, list)
        
        # Should have at least one reason
        self.assertGreater(len(reasons), 0)
        
        # Each reason should have required fields
        for reason in reasons:
            self.assertIn("severity", reason)
            self.assertIn("reason", reason)
            self.assertIn("indicator", reason)
            self.assertIn(reason["severity"], ["critical", "high", "medium", "low", "info"])
    
    def test_generate_risk_reasons_sms_permissions(self):
        """Test detection of SMS-related risks"""
        analysis = {
            "permissions": {
                "all_permissions": ["android.permission.READ_SMS", "android.permission.SEND_SMS"],
                "dangerous_list": ["android.permission.READ_SMS", "android.permission.SEND_SMS"],
                "total_permissions": 2,
                "dangerous_permissions": 2
            },
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []}
        }
        
        reasons = self.analyst.generate_risk_reasons(analysis)
        
        # Should detect SMS permissions risk
        sms_reasons = [r for r in reasons if "sms" in r["reason"].lower()]
        self.assertGreater(len(sms_reasons), 0)
    
    def test_generate_risk_reasons_boot_receiver(self):
        """Test detection of boot receiver risks"""
        analysis = {
            "permissions": {"requested": []},
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {
                "receivers": [
                    {"name": "BootReceiver", "intent_filters": ["BOOT_COMPLETED"]}
                ],
                "services": []
            }
        }
        
        reasons = self.analyst.generate_risk_reasons(analysis)
        
        # Should detect boot receiver
        boot_reasons = [r for r in reasons if "boot" in r["reason"].lower()]
        self.assertGreater(len(boot_reasons), 0)
    
    def test_generate_recommendations_safe(self):
        """Test recommendations for safe app"""
        recommendations = self.analyst.generate_recommendations(20, "low", [])
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("safe" in r.lower() for r in recommendations))
    
    def test_generate_recommendations_high_risk(self):
        """Test recommendations for high-risk app"""
        reasons = [
            {"severity": "high", "reason": "App can read SMS"},
            {"severity": "critical", "reason": "App can install packages"}
        ]
        recommendations = self.analyst.generate_recommendations(80, "critical", reasons)
        
        self.assertIsInstance(recommendations, list)
        self.assertTrue(any("not install" in r.lower() for r in recommendations))
    
    def test_generate_analysis_narrative(self):
        """Test generating analyst narrative"""
        risk_assessment = self.sample_analysis.get('risk_assessment', {})
        summary = self.analyst.generate_summary(
            risk_assessment.get('risk_score', 0),
            risk_assessment.get('severity', 'unknown'),
            'high'
        )
        
        reasons = self.analyst.generate_risk_reasons(self.sample_analysis)
        
        narrative = self.analyst.generate_analysis_narrative(
            self.sample_analysis,
            72,
            "high",
            reasons,
            summary
        )
        
        self.assertIsInstance(narrative, str)
        self.assertGreater(len(narrative), 100)  # Should be substantial
        
        # Check for professional elements
        self.assertIn("FraudShield AI", narrative)
        self.assertIn("\n\n", narrative)  # Multiple paragraphs
    
    def test_analyze_narrative_content(self):
        """Test that narrative contains expected information"""
        risk_assessment = self.sample_analysis.get('risk_assessment', {})
        summary = self.analyst.generate_summary(
            risk_assessment.get('risk_score', 0),
            risk_assessment.get('severity', 'unknown'),
            'high'
        )
        
        reasons = self.analyst.generate_risk_reasons(self.sample_analysis)
        
        narrative = self.analyst.generate_analysis_narrative(
            self.sample_analysis,
            72,
            "high",
            reasons,
            summary
        )
        
        # Check for key components
        self.assertIn("analysis", narrative.lower())
        self.assertIn("risk", narrative.lower())
        self.assertTrue(
            "recommendation" in narrative.lower() or "recommended" in narrative.lower()
        )
    
    def test_prioritize_risks(self):
        """Test risk prioritization"""
        risk_factors = [
            {"severity": "low", "reason": "Low risk factor"},
            {"severity": "critical", "reason": "Critical factor"},
            {"severity": "medium", "reason": "Medium factor"},
            {"severity": "high", "reason": "High factor"}
        ]
        
        prioritized = self.analyst.prioritize_risks(risk_factors)
        
        # Should be sorted CRITICAL → HIGH → MEDIUM → LOW
        severities = [f["severity"] for f in prioritized]
        self.assertEqual(severities[0], "critical")
        self.assertEqual(severities[1], "high")
        self.assertEqual(severities[2], "medium")
        self.assertEqual(severities[3], "low")
    
    def test_complete_apk_analysis(self):
        """Test complete APK analysis workflow"""
        result = self.analyst.analyze_apk(self.sample_analysis)
        
        # Verify all outputs are present
        self.assertIn("executive_summary", result)
        self.assertIn("permission_explanations", result)
        self.assertIn("risk_reasons", result)
        self.assertIn("recommendations", result)
        self.assertIn("analyst_narrative", result)
        self.assertIn("prioritized_risk_factors", result)
        
        # Verify executive summary structure
        exec_summary = result["executive_summary"]
        self.assertIn("risk_level", exec_summary)
        self.assertIn("summary", exec_summary)
        self.assertIn("recommendation", exec_summary)
        
        # Verify arrays
        self.assertIsInstance(result["permission_explanations"], list)
        self.assertIsInstance(result["risk_reasons"], list)
        self.assertIsInstance(result["recommendations"], list)
        
        # Verify narrative is substantial
        self.assertGreater(len(result["analyst_narrative"]), 100)
    
    def test_permission_explanation_to_dict(self):
        """Test permission explanation dictionary conversion"""
        perm = PermissionExplanation(
            permission="READ_SMS",
            risk=RiskLevel.HIGH,
            explanation="Allows reading SMS messages"
        )
        
        perm_dict = perm.to_dict()
        
        self.assertEqual(perm_dict["permission"], "READ_SMS")
        self.assertEqual(perm_dict["risk"], "high")
        self.assertIn("SMS", perm_dict["explanation"])
    
    def test_executive_summary_to_dict(self):
        """Test executive summary dictionary conversion"""
        summary = ExecutiveSummary(
            risk_level="High",
            summary="This app is risky",
            recommendation="Do not install"
        )
        
        summary_dict = summary.to_dict()
        
        self.assertEqual(summary_dict["risk_level"], "High")
        self.assertEqual(summary_dict["summary"], "This app is risky")
        self.assertEqual(summary_dict["recommendation"], "Do not install")


class TestPermissionDataFlow(unittest.TestCase):
    """
    Test suite for permission data flow through the system.
    
    Verifies that:
    1. Permission data correctly flows from APKInspector to SecurityAnalystAgent
    2. Dangerous permissions are correctly identified and explained
    3. Narratives include actual permission counts
    4. Permission explanations include dangerous permissions
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyst = SecurityAnalystAgent()
        
        # APKInspector-compatible data structure with all_permissions key
        self.analysis_with_permissions = {
            "package_name": "com.example.banking",
            "app_name": "Banking App",
            "version_name": "1.0.0",
            "version_code": "1",
            "file_size": 5242880,
            "md5": "abc123",
            "sha256": "def456",
            "permissions": {
                "all_permissions": [
                    "android.permission.RECEIVE_SMS",
                    "android.permission.READ_SMS",
                    "android.permission.RECEIVE_BOOT_COMPLETED",
                    "android.permission.INTERNET",
                    "android.permission.ACCESS_NETWORK_STATE",
                    "android.permission.READ_CONTACTS",
                    "android.permission.ACCESS_FINE_LOCATION",
                    "android.permission.CAMERA",
                    "android.permission.WRITE_EXTERNAL_STORAGE",
                    "android.permission.READ_CALENDAR",
                    "android.permission.WRITE_CALENDAR",
                    "android.permission.CALL_PHONE"
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
                "risk_counts": {"critical": 2, "high": 2, "medium": 3, "low": 5}
            },
            "urls_and_domains": {
                "urls": ["https://api.example.com"],
                "domains": ["api.example.com"],
                "suspicious_urls": []
            },
            "components": {
                "activities": ["MainActivity"],
                "services": ["SyncService"],
                "broadcast_receivers": ["BootReceiver"],
                "content_providers": []
            },
            "analysis_summary": {
                "threat_level": "high",
                "risk_indicators": ["sms_access", "boot_persistence"]
            },
            "risk_assessment": {
                "risk_score": 75,
                "severity": "high",
                "risk_factors": []
            }
        }
    
    def test_analyze_apk_with_all_permissions_key(self):
        """Test that analyze_apk correctly reads from all_permissions key"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        
        # Verify permission explanations were generated
        explanations = result.get("permission_explanations", [])
        self.assertGreater(len(explanations), 0, "No permission explanations generated")
        
        # Verify dangerous permissions are explained
        explained_perms = {e["permission"] for e in explanations}
        self.assertIn("android.permission.RECEIVE_SMS", explained_perms)
        self.assertIn("android.permission.READ_SMS", explained_perms)
    
    def test_permission_narrative_includes_actual_counts(self):
        """Test that analyst narrative includes actual permission counts, not 0"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        narrative = result.get("analyst_narrative", "")
        
        # Should mention 12 permissions, not 0
        self.assertIn("12", narrative, 
                     f"Narrative should mention 12 permissions but got: {narrative[:200]}")
        
        # Should mention dangerous/sensitive permissions
        self.assertNotIn("requests 0 permissions", narrative,
                        "Narrative should not say 0 permissions")
        
        # Should mention 4 sensitive permissions
        self.assertIn("4", narrative,
                     "Narrative should mention 4 sensitive permissions")
    
    def test_dangerous_permissions_in_explanations(self):
        """Test that dangerous permissions appear in explanations"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        explanations = result.get("permission_explanations", [])
        
        # Extract short names
        explained_short = {e["permission"].split('.')[-1] for e in explanations}
        
        # Verify RECEIVE_SMS is explained
        self.assertIn("RECEIVE_SMS", explained_short,
                     "RECEIVE_SMS should be in explanations")
        
        # Verify READ_SMS is explained
        self.assertIn("READ_SMS", explained_short,
                     "READ_SMS should be in explanations")
        
        # Verify RECEIVE_BOOT_COMPLETED is explained
        self.assertIn("RECEIVE_BOOT_COMPLETED", explained_short,
                     "RECEIVE_BOOT_COMPLETED should be in explanations")
    
    def test_sms_permission_explanation_content(self):
        """Test that SMS permissions have appropriate risk explanations"""
        permissions = ["android.permission.RECEIVE_SMS", "android.permission.READ_SMS"]
        explanations = self.analyst.explain_permissions(permissions)
        
        # Find RECEIVE_SMS explanation
        receive_sms = next((e for e in explanations if "RECEIVE_SMS" in e["permission"]), None)
        self.assertIsNotNone(receive_sms, "RECEIVE_SMS should be explained")
        
        # Verify it's marked as CRITICAL
        self.assertEqual(receive_sms["risk"], "critical",
                        f"RECEIVE_SMS should be CRITICAL, got {receive_sms['risk']}")
        
        # Verify explanation mentions OTP/authentication
        explanation = receive_sms["explanation"].lower()
        self.assertTrue(
            "otp" in explanation or "authentication" in explanation or "intercept" in explanation,
            f"SMS explanation should mention interception risk: {receive_sms['explanation']}"
        )
    
    def test_boot_completed_permission_explanation(self):
        """Test that RECEIVE_BOOT_COMPLETED is properly explained"""
        permissions = ["android.permission.RECEIVE_BOOT_COMPLETED"]
        explanations = self.analyst.explain_permissions(permissions)
        
        self.assertEqual(len(explanations), 1)
        boot_perm = explanations[0]
        
        # Should be HIGH risk
        self.assertIn(boot_perm["risk"], ["high", "critical"])
        
        # Should explain persistence
        explanation = boot_perm["explanation"].lower()
        self.assertTrue(
            "boot" in explanation or "automatic" in explanation or "background" in explanation,
            f"Boot permission should explain automatic startup: {boot_perm['explanation']}"
        )
    
    def test_risk_reasons_include_critical_permissions(self):
        """Test that risk reasons include critical permissions"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        risk_reasons = result.get("risk_reasons", [])
        
        # Should have SMS-related reasons
        sms_reasons = [r for r in risk_reasons if "sms" in r["reason"].lower()]
        self.assertGreater(len(sms_reasons), 0,
                          "Risk reasons should include SMS permission risks")
        
        # At least one SMS reason should be high/critical
        sms_high_risk = [r for r in sms_reasons if r["severity"] in ["high", "critical"]]
        self.assertGreater(len(sms_high_risk), 0,
                          "SMS risks should be marked as high/critical")
    
    def test_narrative_mentions_sms_threat(self):
        """Test that narrative specifically mentions SMS threat"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        narrative = result.get("analyst_narrative", "")
        
        # Should mention SMS-specific threat
        sms_mentioned = any(keyword in narrative.lower() for keyword in 
                          ["sms", "intercept", "otp", "authentication"])
        self.assertTrue(sms_mentioned,
                       f"Narrative should mention SMS threat: {narrative[:300]}")
    
    def test_narrative_mentions_boot_completed(self):
        """Test that narrative mentions RECEIVE_BOOT_COMPLETED threat"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        narrative = result.get("analyst_narrative", "")
        
        # Should mention boot/background persistence
        boot_mentioned = any(keyword in narrative.lower() for keyword in 
                           ["boot", "automatic", "background"])
        self.assertTrue(boot_mentioned,
                       f"Narrative should mention boot/background persistence: {narrative[:300]}")
    
    def test_internet_permission_low_risk(self):
        """Test that INTERNET permission is marked as LOW risk"""
        permissions = ["android.permission.INTERNET"]
        explanations = self.analyst.explain_permissions(permissions)
        
        self.assertEqual(len(explanations), 1)
        internet_perm = explanations[0]
        
        # Should be LOW risk
        self.assertEqual(internet_perm["risk"], "low",
                        f"INTERNET should be LOW risk, got {internet_perm['risk']}")
    
    def test_access_network_state_medium_risk(self):
        """Test that ACCESS_NETWORK_STATE is marked as MEDIUM risk"""
        permissions = ["android.permission.ACCESS_NETWORK_STATE"]
        explanations = self.analyst.explain_permissions(permissions)
        
        self.assertEqual(len(explanations), 1)
        net_state = explanations[0]
        
        # Should be MEDIUM risk
        self.assertEqual(net_state["risk"], "medium",
                        f"ACCESS_NETWORK_STATE should be MEDIUM risk, got {net_state['risk']}")
    
    def test_permission_count_accuracy(self):
        """Test that permission counts in narrative match actual data"""
        result = self.analyst.analyze_apk(self.analysis_with_permissions)
        narrative = result.get("analyst_narrative", "")
        explanations = result.get("permission_explanations", [])
        
        # Count should match all_permissions length
        actual_count = len(self.analysis_with_permissions["permissions"]["all_permissions"])
        self.assertEqual(len(explanations), actual_count,
                        f"Should explain all {actual_count} permissions, got {len(explanations)}")
        
        # Narrative should mention correct count
        self.assertIn(str(actual_count), narrative,
                     f"Narrative should mention {actual_count} permissions")
    
    def test_full_permission_names_handled(self):
        """Test that full permission names (android.permission.X) are handled"""
        permissions = [
            "android.permission.READ_SMS",
            "android.permission.WRITE_SMS",
            "android.permission.CAMERA"
        ]
        explanations = self.analyst.explain_permissions(permissions)
        
        self.assertEqual(len(explanations), 3)
        
        # All should be explained
        for exp in explanations:
            self.assertTrue(exp["explanation"], 
                          f"Permission {exp['permission']} has no explanation")
            self.assertIn(exp["risk"], ["critical", "high", "medium", "low", "info"])


if __name__ == '__main__':
    unittest.main()
    
    def test_singleton_instance(self):
        """Test that security_analyst is a singleton"""
        # The singleton should be accessible
        self.assertIsNotNone(security_analyst)
        self.assertIsInstance(security_analyst, SecurityAnalystAgent)
    
    def test_no_hallucinations_in_analysis(self):
        """Test that analysis only uses actual findings"""
        analysis = {
            "package_name": "com.test.app",
            "permissions": {"requested": []},
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []},
            "analysis_summary": {"threat_level": "clean"},
            "risk_assessment": {
                "risk_score": 10,
                "severity": "low",
                "risk_factors": [],
                "summary": "No threats detected"
            }
        }
        
        result = self.analyst.analyze_apk(analysis)
        narrative = result["analyst_narrative"]
        
        # Should not mention things that don't exist in the analysis
        # (This is a basic check - actual hallucinations would be detected during review)
        self.assertNotIn("trojan", narrative.lower())
        self.assertNotIn("backdoor", narrative.lower())
    
    def test_handling_empty_analysis(self):
        """Test handling of empty/minimal analysis"""
        minimal_analysis = {
            "permissions": {"requested": []},
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {},
            "analysis_summary": {"threat_level": "clean"},
            "risk_assessment": {
                "risk_score": 0,
                "severity": "low",
                "risk_factors": [],
                "summary": "No issues"
            }
        }
        
        # Should not crash
        result = self.analyst.analyze_apk(minimal_analysis)
        
        self.assertIsNotNone(result)
        self.assertIn("executive_summary", result)
        self.assertEqual(result["executive_summary"]["risk_level"], "Safe")


class TestSecurityAnalystIntegration(unittest.TestCase):
    """Integration tests for SecurityAnalystAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyst = SecurityAnalystAgent()
    
    def test_recommend_based_on_permissions(self):
        """Test that recommendations reflect permissions"""
        analysis = {
            "permissions": {
                "requested": [
                    "android.permission.REQUEST_INSTALL_PACKAGES",
                    "android.permission.BIND_ACCESSIBILITY_SERVICE"
                ]
            },
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []}
        }
        
        reasons = self.analyst.generate_risk_reasons(analysis)
        recommendations = self.analyst.generate_recommendations(85, "critical", reasons)
        
        # Should strongly recommend against installation
        strong_warns = [r for r in recommendations if "not install" in r.lower() or "do not" in r.lower()]
        self.assertGreater(len(strong_warns), 0)
    
    def test_narrative_matches_risk_score(self):
        """Test that narrative tone matches risk score"""
        # Low risk narrative
        low_analysis = {
            "package_name": "safe_app",
            "permissions": {"requested": []},
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []},
            "analysis_summary": {"threat_level": "clean"},
            "risk_assessment": {
                "risk_score": 10,
                "severity": "low",
                "risk_factors": [],
                "summary": "Safe"
            }
        }
        
        low_result = self.analyst.analyze_apk(low_analysis)
        low_narrative = low_result["analyst_narrative"].lower()
        
        # Should be positive/neutral
        self.assertNotIn("dangerous", low_narrative)
        self.assertNotIn("critical", low_narrative)
        
        # High risk narrative should be more cautious
        high_analysis = {
            "package_name": "risky_app",
            "permissions": {
                "requested": [
                    "android.permission.REQUEST_INSTALL_PACKAGES",
                    "android.permission.BIND_ACCESSIBILITY_SERVICE"
                ]
            },
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []},
            "analysis_summary": {"threat_level": "critical"},
            "risk_assessment": {
                "risk_score": 95,
                "severity": "critical",
                "risk_factors": [],
                "summary": "Critical risk"
            }
        }
        
        high_result = self.analyst.analyze_apk(high_analysis)
        high_narrative = high_result["analyst_narrative"].lower()
        
        # Should include cautionary language
        self.assertTrue(
            any(word in high_narrative for word in ["critical", "dangerous", "caution", "risk"])
        )


if __name__ == '__main__':
    unittest.main()
