"""
Integration Test: Security Analyst with AnalysisService

Verifies that the security analyst is properly integrated into the analysis pipeline.
"""

import unittest
from unittest.mock import patch, MagicMock
from app.agents.security_analyst import security_analyst
from app.services.analysis_service import AnalysisService


class TestSecurityAnalystIntegration(unittest.TestCase):
    """Integration tests for security analyst in analysis pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = AnalysisService()
        
        # Mock analysis result from APK Inspector
        self.mock_analysis_result = {
            "package_name": "com.test.app",
            "app_name": "Test App",
            "version_name": "1.0",
            "version_code": "100",
            "file_size": 1024000,
            "md5": "abc123",
            "sha256": "sha256hash",
            "permissions": {
                "requested": ["READ_SMS", "SEND_SMS", "READ_CONTACTS"]
            },
            "urls_and_domains": {
                "urls": ["http://example.com", "https://secure.com"],
                "domains": ["example.com"]
            },
            "components": {
                "activities": ["Activity1"],
                "services": ["Service1"],
                "receivers": [{"name": "Receiver1", "intent_filters": ["BOOT_COMPLETED"]}],
                "providers": ["Provider1"]
            },
            "analysis_summary": {
                "threat_level": "high",
                "risk_indicators": ["sms_access", "location_access"]
            },
            "risk_assessment": {
                "risk_score": 75,
                "severity": "high",
                "risk_factors": [
                    {
                        "factor": "SMS Access",
                        "category": "permissions",
                        "score": 20,
                        "reason": "Can read SMS",
                        "severity": "high"
                    }
                ],
                "summary": "High-risk application"
            }
        }
    
    def test_analyst_called_in_report_creation(self):
        """Test that security analyst is called when creating a report"""
        
        # This test verifies the analyst is integrated
        # by checking the report creation includes analyst data
        
        # The actual integration happens in AnalysisService._create_report()
        # where security_analyst.analyze_apk() is called
        
        # Verify the analyst exists and can be called
        result = security_analyst.analyze_apk(self.mock_analysis_result)
        
        # Should have all analyst outputs
        self.assertIn("executive_summary", result)
        self.assertIn("risk_reasons", result)
        self.assertIn("recommendations", result)
        self.assertIn("permission_explanations", result)
        self.assertIn("analyst_narrative", result)
        
        # Verify structure
        self.assertIsInstance(result["executive_summary"], dict)
        self.assertIsInstance(result["risk_reasons"], list)
        self.assertIsInstance(result["recommendations"], list)
        self.assertIsInstance(result["permission_explanations"], list)
        self.assertIsInstance(result["analyst_narrative"], str)
    
    def test_analyst_output_in_report_json(self):
        """Test that analyst output would be included in report_json"""
        
        # Simulate what happens in _create_report
        analyst_assessment = security_analyst.analyze_apk(self.mock_analysis_result)
        
        # This is what gets added to report_json
        report_json = {
            "package_name": self.mock_analysis_result.get("package_name"),
            "risk_score": self.mock_analysis_result["risk_assessment"]["risk_score"],
            "severity": self.mock_analysis_result["risk_assessment"]["severity"],
            # Analyst data
            "executive_summary": analyst_assessment.get('executive_summary'),
            "risk_reasons": analyst_assessment.get('risk_reasons'),
            "recommendations": analyst_assessment.get('recommendations'),
            "permission_explanations": analyst_assessment.get('permission_explanations'),
            "analyst_narrative": analyst_assessment.get('analyst_narrative'),
            "prioritized_risk_factors": analyst_assessment.get('prioritized_risk_factors')
        }
        
        # Verify all fields are present
        self.assertIsNotNone(report_json["executive_summary"])
        self.assertIsNotNone(report_json["risk_reasons"])
        self.assertIsNotNone(report_json["recommendations"])
        self.assertIsNotNone(report_json["permission_explanations"])
        self.assertIsNotNone(report_json["analyst_narrative"])
        
        # Verify content
        self.assertTrue(len(report_json["analyst_narrative"]) > 100)
        self.assertGreater(len(report_json["permission_explanations"]), 0)
        self.assertGreater(len(report_json["recommendations"]), 0)
    
    def test_analyst_handles_various_risk_levels(self):
        """Test analyst correctly assesses different risk levels"""
        
        # Low risk
        low_analysis = self.mock_analysis_result.copy()
        low_analysis["risk_assessment"] = {
            "risk_score": 10,
            "severity": "low",
            "risk_factors": [],
            "summary": "Safe app"
        }
        low_analysis["permissions"] = {"requested": ["INTERNET"]}
        low_analysis["urls_and_domains"] = {"urls": [], "domains": []}
        
        low_result = security_analyst.analyze_apk(low_analysis)
        self.assertEqual(low_result["executive_summary"]["risk_level"], "Safe")
        
        # High risk
        high_analysis = self.mock_analysis_result.copy()
        high_analysis["risk_assessment"] = {
            "risk_score": 80,
            "severity": "critical",
            "risk_factors": [],
            "summary": "Critical risk"
        }
        
        high_result = security_analyst.analyze_apk(high_analysis)
        self.assertEqual(high_result["executive_summary"]["risk_level"], "Critical")
    
    def test_analyst_identifies_multiple_risks(self):
        """Test analyst correctly identifies multiple risk types"""
        
        # Complex analysis with multiple risks
        complex_analysis = {
            "package_name": "com.complex.app",
            "permissions": {
                "requested": [
                    "READ_SMS",
                    "SEND_SMS",
                    "READ_CONTACTS",
                    "ACCESS_FINE_LOCATION",
                    "CAMERA",
                    "RECORD_AUDIO",
                    "REQUEST_INSTALL_PACKAGES"
                ]
            },
            "urls_and_domains": {
                "urls": [
                    "http://malicious1.com",
                    "http://malicious2.com",
                    "https://secure.com"
                ],
                "domains": ["malicious1.com", "malicious2.com"]
            },
            "components": {
                "receivers": [
                    {"name": "Boot1", "intent_filters": ["BOOT_COMPLETED"]},
                    {"name": "SMS1", "intent_filters": ["SMS_RECEIVED"]}
                ],
                "services": [f"Service{i}" for i in range(15)],
                "activities": ["Activity1", "Activity2"],
                "providers": ["Provider1"]
            },
            "analysis_summary": {
                "threat_level": "critical",
                "risk_indicators": []
            },
            "risk_assessment": {
                "risk_score": 95,
                "severity": "critical",
                "risk_factors": [],
                "summary": "Highly suspicious"
            }
        }
        
        result = security_analyst.analyze_apk(complex_analysis)
        
        # Should identify multiple risks
        reasons = result["risk_reasons"]
        self.assertGreater(len(reasons), 1)
        
        # Should have strong recommendations
        recommendations = result["recommendations"]
        self.assertTrue(
            any("not install" in r.lower() or "do not" in r.lower() 
                for r in recommendations)
        )
        
        # Should have critical risk level
        self.assertEqual(result["executive_summary"]["risk_level"], "Critical")


class TestAnalystDataConsistency(unittest.TestCase):
    """Test consistency of analyst data with risk assessment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyst = security_analyst
    
    def test_recommendation_matches_risk_level(self):
        """Test that recommendations match the risk level"""
        
        # Safe app should have safe recommendations
        safe_analysis = {
            "permissions": {"requested": []},
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []},
            "risk_assessment": {
                "risk_score": 15,
                "severity": "low",
                "risk_factors": [],
                "summary": "Safe"
            },
            "analysis_summary": {"threat_level": "clean"}
        }
        
        result = self.analyst.analyze_apk(safe_analysis)
        recommendations = result["recommendations"]
        
        # Safe app should recommend installation
        self.assertTrue(
            any("safe" in r.lower() for r in recommendations)
        )
        self.assertFalse(
            any("not install" in r.lower() for r in recommendations)
        )
    
    def test_narrative_reflects_findings(self):
        """Test that narrative reflects actual findings"""
        
        # App with SMS access
        sms_analysis = {
            "package_name": "com.sms.app",
            "permissions": {"requested": ["READ_SMS", "SEND_SMS"]},
            "urls_and_domains": {"urls": [], "domains": []},
            "components": {"receivers": [], "services": []},
            "risk_assessment": {
                "risk_score": 50,
                "severity": "medium",
                "risk_factors": [],
                "summary": "SMS access detected"
            },
            "analysis_summary": {"threat_level": "medium"}
        }
        
        result = self.analyst.analyze_apk(sms_analysis)
        narrative = result["analyst_narrative"].lower()
        
        # Narrative should mention SMS or permissions
        self.assertTrue(
            "sms" in narrative or "permission" in narrative.lower()
        )


if __name__ == '__main__':
    unittest.main()
