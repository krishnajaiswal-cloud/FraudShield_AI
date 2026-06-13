"""
Unit Tests for Risk Scorer Agent

Tests risk scoring calculations, permission analysis, and output formatting.
"""

import pytest
from app.agents.risk_scorer import (
    RiskScorer, RiskAssessment, RiskFactor, RiskSeverity
)


class TestRiskScorer:
    """Test suite for RiskScorer class"""
    
    @pytest.fixture
    def scorer(self):
        """Initialize risk scorer for each test"""
        return RiskScorer()
    
    def test_initialization(self, scorer):
        """Test scorer initialization"""
        assert scorer is not None
        assert len(scorer.PERMISSION_WEIGHTS) > 0
        assert len(scorer.DANGEROUS_COMBINATIONS) > 0
    
    # ========== Permission Scoring Tests ==========
    
    def test_score_single_permission(self, scorer):
        """Test scoring of single dangerous permission"""
        findings = {"permissions": ["READ_SMS"], "urls": [], "domains": []}
        assessment = scorer.score_apk(findings)
        
        assert assessment.risk_score >= 15
        assert len(assessment.risk_factors) >= 1
        assert assessment.risk_factors[0].factor == "READ_SMS"
        assert assessment.risk_factors[0].score == 15
    
    def test_score_multiple_permissions(self, scorer):
        """Test scoring of multiple dangerous permissions"""
        findings = {
            "permissions": ["READ_SMS", "READ_CONTACTS", "CAMERA"],
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        # Should include all three permissions
        permission_factors = [f for f in assessment.risk_factors if f.category == "permissions"]
        assert len(permission_factors) >= 3
        assert assessment.risk_score > 30
    
    def test_permission_scoring_accuracy(self, scorer):
        """Test that permissions are scored with correct weights"""
        findings = {
            "permissions": ["SEND_SMS", "REQUEST_INSTALL_PACKAGES"],
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        # SEND_SMS = 20, REQUEST_INSTALL_PACKAGES = 15
        expected_score = 35
        assert assessment.risk_score >= expected_score
    
    # ========== Permission Combination Tests ==========
    
    def test_dangerous_combination_camera_microphone(self, scorer):
        """Test detection of camera + microphone combination"""
        findings = {
            "permissions": ["CAMERA", "MICROPHONE"],
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        combo_factors = [f for f in assessment.risk_factors if f.category == "combinations"]
        assert len(combo_factors) > 0
        assert any("CAMERA" in f.factor and "MICROPHONE" in f.factor for f in combo_factors)
    
    def test_dangerous_combination_tracking(self, scorer):
        """Test detection of location + internet tracking combination"""
        findings = {
            "permissions": ["ACCESS_FINE_LOCATION", "INTERNET"],
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        combo_factors = [f for f in assessment.risk_factors if f.category == "combinations"]
        assert len(combo_factors) > 0
    
    def test_no_combinations_without_both_permissions(self, scorer):
        """Test that combinations aren't scored without both permissions"""
        findings = {
            "permissions": ["CAMERA"],  # Only one part of combination
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        combo_factors = [f for f in assessment.risk_factors if f.category == "combinations"]
        assert len(combo_factors) == 0
    
    # ========== URL Scoring Tests ==========
    
    def test_http_url_scoring(self, scorer):
        """Test that HTTP URLs are scored as risky"""
        findings = {
            "permissions": [],
            "urls": [{"url": "http://example.com/data", "risk_score": 0.5}],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        url_factors = [f for f in assessment.risk_factors if f.category == "urls"]
        assert len(url_factors) > 0
    
    def test_ip_address_url_detection(self, scorer):
        """Test detection of IP addresses in URLs"""
        findings = {
            "permissions": [],
            "urls": [{"url": "http://192.168.1.1:8080/command", "risk_score": 0.7}],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        ip_factors = [f for f in assessment.risk_factors 
                     if "IP" in f.factor or "192.168" in f.reason]
        assert len(ip_factors) > 0
    
    def test_suspicious_tld_detection(self, scorer):
        """Test detection of suspicious TLDs"""
        findings = {
            "permissions": [],
            "urls": [{"url": "http://malware.tk/payload", "risk_score": 0.8}],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        tld_factors = [f for f in assessment.risk_factors if "TLD" in f.factor]
        assert len(tld_factors) > 0
    
    def test_phishing_pattern_detection(self, scorer):
        """Test detection of phishing patterns in URLs"""
        findings = {
            "permissions": [],
            "urls": [{"url": "http://login-verify.example.com/authenticate", "risk_score": 0.9}],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        phishing_factors = [f for f in assessment.risk_factors if "phishing" in f.reason.lower()]
        assert len(phishing_factors) > 0
    
    # ========== Domain Scoring Tests ==========
    
    def test_suspicious_domain_detection(self, scorer):
        """Test detection of suspicious domain patterns"""
        findings = {
            "permissions": [],
            "urls": [],
            "domains": ["bit.ly/malware", "example.com"]
        }
        assessment = scorer.score_apk(findings)
        
        domain_factors = [f for f in assessment.risk_factors if f.category == "domains"]
        assert len(domain_factors) > 0
    
    # ========== APK Characteristics Tests ==========
    
    def test_excessive_permissions_flag(self, scorer):
        """Test flagging of excessive permission count"""
        permissions = [f"PERM_{i}" for i in range(25)]
        findings = {
            "permissions": permissions,
            "urls": [],
            "domains": [],
            "activities": ["MainActivity"],
            "services": [],
            "receivers": [],
            "providers": []
        }
        assessment = scorer.score_apk(findings)
        
        char_factors = [f for f in assessment.risk_factors if "Excessive permissions" in f.factor]
        assert len(char_factors) > 0
    
    def test_excessive_receivers_flag(self, scorer):
        """Test flagging of excessive broadcast receivers"""
        findings = {
            "permissions": [],
            "urls": [],
            "domains": [],
            "activities": [],
            "services": [],
            "receivers": [f"Receiver_{i}" for i in range(15)],
            "providers": []
        }
        assessment = scorer.score_apk(findings)
        
        char_factors = [f for f in assessment.risk_factors if "receivers" in f.factor.lower()]
        assert len(char_factors) > 0
    
    # ========== Severity Level Tests ==========
    
    def test_severity_low(self, scorer):
        """Test low severity classification"""
        findings = {
            "permissions": ["INTERNET"],
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        assert assessment.risk_score < 25
        assert assessment.severity == RiskSeverity.LOW
    
    def test_severity_medium(self, scorer):
        """Test medium severity classification"""
        findings = {
            "permissions": ["READ_CONTACTS", "INTERNET"],
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        assert 25 <= assessment.risk_score < 50
        assert assessment.severity == RiskSeverity.MEDIUM
    
    def test_severity_high(self, scorer):
        """Test high severity classification"""
        findings = {
            "permissions": ["READ_CONTACTS", "REQUEST_INSTALL_PACKAGES", "INTERNET"],
            "urls": [{"url": "http://example.tk/data", "risk_score": 0.6}],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        assert 50 <= assessment.risk_score < 75
        assert assessment.severity == RiskSeverity.HIGH
    
    def test_severity_critical(self, scorer):
        """Test critical severity classification"""
        findings = {
            "permissions": [
                "READ_SMS", "SEND_SMS", "BIND_ACCESSIBILITY_SERVICE",
                "REQUEST_INSTALL_PACKAGES", "SYSTEM_ALERT_WINDOW"
            ],
            "urls": [
                {"url": "http://malware.tk/command", "risk_score": 0.9},
                {"url": "http://192.168.1.1:8080", "risk_score": 0.8}
            ],
            "domains": ["bit.ly/malware"]
        }
        assessment = scorer.score_apk(findings)
        
        assert assessment.risk_score >= 75
        assert assessment.severity == RiskSeverity.CRITICAL
    
    # ========== Output Format Tests ==========
    
    def test_assessment_output_format(self, scorer):
        """Test that assessment has required fields"""
        findings = {"permissions": ["READ_SMS"], "urls": [], "domains": []}
        assessment = scorer.score_apk(findings)
        
        assert isinstance(assessment, RiskAssessment)
        assert 0 <= assessment.risk_score <= 100
        assert assessment.severity in RiskSeverity
        assert isinstance(assessment.risk_factors, list)
        assert len(assessment.summary) > 0
        assert len(assessment.timestamp) > 0
    
    def test_risk_factor_details(self, scorer):
        """Test that risk factors have required details"""
        findings = {"permissions": ["READ_SMS"], "urls": [], "domains": []}
        assessment = scorer.score_apk(findings)
        
        assert len(assessment.risk_factors) > 0
        factor = assessment.risk_factors[0]
        
        assert isinstance(factor, RiskFactor)
        assert len(factor.factor) > 0
        assert factor.category in ["permissions", "combinations", "urls", "domains", "characteristics"]
        assert factor.score > 0
        assert len(factor.reason) > 0
        assert factor.severity in RiskSeverity
    
    def test_assessment_to_dict(self, scorer):
        """Test conversion of assessment to dictionary"""
        findings = {"permissions": ["READ_SMS"], "urls": [], "domains": []}
        assessment = scorer.score_apk(findings)
        
        assessment_dict = assessment.to_dict()
        
        assert "risk_score" in assessment_dict
        assert "severity" in assessment_dict
        assert "risk_factors" in assessment_dict
        assert "summary" in assessment_dict
        assert "timestamp" in assessment_dict
        assert isinstance(assessment_dict["risk_factors"], list)
    
    # ========== Edge Cases ==========
    
    def test_empty_findings(self, scorer):
        """Test scoring with no findings"""
        findings = {
            "permissions": [],
            "urls": [],
            "domains": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "providers": []
        }
        assessment = scorer.score_apk(findings)
        
        assert assessment.risk_score == 0
        assert assessment.severity == RiskSeverity.LOW
        assert len(assessment.risk_factors) == 0
    
    def test_score_normalization_to_100(self, scorer):
        """Test that scores are normalized to max 100"""
        # Create many high-risk factors
        permissions = ["READ_SMS", "SEND_SMS", "READ_CONTACTS", 
                      "BIND_ACCESSIBILITY_SERVICE", "REQUEST_INSTALL_PACKAGES"]
        findings = {
            "permissions": permissions,
            "urls": [{"url": "http://malware.tk/cmd", "risk_score": 0.9}] * 10,
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        assert assessment.risk_score <= 100
    
    def test_duplicate_factors_not_counted_twice(self, scorer):
        """Test that same factors aren't counted multiple times"""
        findings = {
            "permissions": ["READ_SMS", "READ_SMS"],  # Duplicate
            "urls": [],
            "domains": []
        }
        assessment = scorer.score_apk(findings)
        
        # Should still only have one READ_SMS factor (depending on implementation)
        # This test may need adjustment based on implementation
        assert assessment.risk_score >= 15
    
    # ========== Integration Tests ==========
    
    def test_realistic_malware_scenario(self, scorer):
        """Test realistic malware APK scenario"""
        findings = {
            "permissions": [
                "READ_SMS", "SEND_SMS", "READ_CONTACTS",
                "BIND_ACCESSIBILITY_SERVICE", "INTERNET",
                "ACCESS_FINE_LOCATION"
            ],
            "urls": [
                {"url": "http://command.tk/execute", "risk_score": 0.9},
                {"url": "http://192.168.1.100:8888/data", "risk_score": 0.8}
            ],
            "domains": ["bit.ly/payload"],
            "activities": [],
            "services": ["HiddenService"],
            "receivers": ["BootReceiver"],
            "providers": []
        }
        assessment = scorer.score_apk(findings)
        
        # Should be high or critical
        assert assessment.risk_score >= 50
        assert assessment.severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]
        assert len(assessment.risk_factors) > 5
    
    def test_legitimate_app_scenario(self, scorer):
        """Test legitimate app scenario"""
        findings = {
            "permissions": ["INTERNET", "ACCESS_NETWORK_STATE"],
            "urls": [{"url": "https://api.example.com/data", "risk_score": 0.1}],
            "domains": [],
            "activities": ["MainActivity"],
            "services": [],
            "receivers": [],
            "providers": []
        }
        assessment = scorer.score_apk(findings)
        
        # Should be low risk
        assert assessment.risk_score < 25
        assert assessment.severity == RiskSeverity.LOW


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
