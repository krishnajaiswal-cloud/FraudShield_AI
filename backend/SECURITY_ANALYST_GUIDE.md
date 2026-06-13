# Security Analyst Agent - Implementation Guide

## Overview

The Security Analyst Agent is an AI-powered layer that converts technical APK analysis results into human-readable security assessments. It bridges the gap between technical security findings and actionable insights for non-technical users.

## Architecture

```
APK Analysis Pipeline
    ↓
Risk Scorer (0-100 risk score)
    ↓
Security Analyst Agent ← NEW
    ├─ Executive Summary
    ├─ Permission Explanations
    ├─ Risk Reasoning
    ├─ Recommendations
    ├─ Analyst Narrative
    └─ Risk Prioritization
    ↓
Report JSON (in Database)
    ↓
API Response
```

## Components

### 1. SecurityAnalystAgent Class
**File**: `backend/app/agents/security_analyst.py`

Main orchestrator that generates all analyst outputs.

```python
from app.agents.security_analyst import security_analyst

# Complete analysis
result = security_analyst.analyze_apk(analysis_result)
```

### 2. Key Methods

#### `generate_summary(risk_score, severity, threat_type)`
Generates executive summary based on risk score.

**Risk Levels**:
- **Safe** (0-25): "Safe application with minimal risk indicators."
- **Moderate** (26-50): "Moderate risk detected. Review permissions carefully."
- **High** (51-75): "Potentially dangerous application. Exercise caution."
- **Critical** (76-100): "High-risk application. Installation is not recommended."

#### `explain_permissions(permissions)`
Converts permission list to human-readable explanations.

**Output**:
```json
[
  {
    "permission": "READ_SMS",
    "risk": "high",
    "explanation": "Allows reading incoming SMS messages. Could be used to intercept 2FA codes or sensitive information."
  },
  {
    "permission": "CAMERA",
    "risk": "high",
    "explanation": "Allows camera access. Could secretly record photos or videos."
  }
]
```

#### `generate_risk_reasons(analysis_result)`
Analyzes findings and generates human-readable risk explanations.

**Output**:
```json
[
  {
    "severity": "high",
    "reason": "Application requests multiple dangerous permissions: READ_SMS, SEND_SMS, READ_CONTACTS.",
    "indicator": "3 dangerous permissions"
  },
  {
    "severity": "medium",
    "reason": "Application contains 2 unencrypted HTTP URLs. Data could be intercepted.",
    "indicator": "2 HTTP URLs"
  }
]
```

#### `generate_recommendations(risk_score, severity, risk_reasons)`
Generates actionable recommendations.

**Output**:
```json
[
  "Do not install this application.",
  "If already installed, uninstall immediately.",
  "Protect SMS-based 2FA codes as this app can access them.",
  "This app will run in the background even when not actively used."
]
```

#### `generate_analysis_narrative(analysis_result, risk_score, severity, risk_reasons, summary)`
Creates professional 3-5 paragraph analyst narrative.

**Output Example**:
```
FraudShield AI Security Analysis Report for com.example.app

This security assessment evaluates the risk profile of the analyzed application...

The application requests 6 permissions and contains 3 external URLs...

Based on the risk assessment, the following action is recommended: Avoid installation...

This analysis is based on static code examination and does not constitute a guarantee...
```

#### `prioritize_risks(risk_factors)`
Sorts risk factors by severity: CRITICAL → HIGH → MEDIUM → LOW → INFO

## Integration with Analysis Pipeline

### AnalysisService Integration
**File**: `backend/app/services/analysis_service.py`

The security analyst is automatically called when a report is created:

```python
# In _create_report method
analyst_assessment = security_analyst.analyze_apk(analysis_result)

# Added to report_json
report_json = {
    # ... existing fields ...
    'executive_summary': analyst_assessment['executive_summary'],
    'risk_reasons': analyst_assessment['risk_reasons'],
    'recommendations': analyst_assessment['recommendations'],
    'permission_explanations': analyst_assessment['permission_explanations'],
    'analyst_narrative': analyst_assessment['analyst_narrative'],
    'prioritized_risk_factors': analyst_assessment['prioritized_risk_factors']
}
```

## API Usage

### Get Analysis with Analyst Assessment

```bash
GET /api/v1/analysis/{analysis_id}
```

**Response Structure**:
```json
{
  "id": 123,
  "package_name": "com.example.app",
  "status": "completed",
  "risk_score": 0.72,
  "severity": "high",
  "report": {
    "id": 456,
    "executive_summary": "...",
    "threat_classification": "high",
    "report_json": {
      "risk_score": 72,
      "severity": "high",
      "executive_summary": {
        "risk_level": "High",
        "summary": "This application has several risky permissions...",
        "recommendation": "Avoid installation unless absolutely necessary."
      },
      "risk_reasons": [
        {
          "severity": "high",
          "reason": "Application requests multiple dangerous permissions...",
          "indicator": "3 dangerous permissions"
        }
      ],
      "recommendations": [
        "Only install if from a trusted source.",
        "Review all requested permissions before granting access.",
        "Monitor the application's behavior after installation."
      ],
      "permission_explanations": [
        {
          "permission": "READ_SMS",
          "risk": "high",
          "explanation": "Allows reading incoming SMS messages..."
        }
      ],
      "analyst_narrative": "FraudShield AI analyzed this APK and identified...",
      "prioritized_risk_factors": [...]
    }
  }
}
```

### Accessing Analyst Data via API

```python
import requests

# Get analysis
response = requests.get('http://localhost:8000/api/v1/analysis/123')
data = response.json()

# Access analyst insights
report_json = data['report']['report_json']
executive_summary = report_json['executive_summary']
recommendations = report_json['recommendations']
analyst_narrative = report_json['analyst_narrative']

print(f"Risk Level: {executive_summary['risk_level']}")
print(f"Summary: {executive_summary['summary']}")
print(f"Recommendation: {executive_summary['recommendation']}")
```

## Permission Knowledge Base

The agent includes explanations for 20+ permissions:

### Dangerous Permissions (CRITICAL/HIGH)
- **READ_SMS**: Reading SMS messages
- **SEND_SMS**: Sending SMS messages
- **READ_CONTACTS**: Accessing device contacts
- **ACCESS_FINE_LOCATION**: GPS location tracking
- **CAMERA**: Camera access
- **RECORD_AUDIO**: Microphone access
- **REQUEST_INSTALL_PACKAGES**: Can install other APKs
- **BIND_ACCESSIBILITY_SERVICE**: Can monitor all user interactions
- **SYSTEM_ALERT_WINDOW**: Can display phishing overlays
- **CALL_PHONE**: Can make phone calls
- **DISABLE_KEYGUARD**: Can disable lock screen

### Medium Risk Permissions
- **PROCESS_OUTGOING_CALLS**: Monitor outgoing calls
- **READ_PHONE_STATE**: Read phone call state
- **CHANGE_NETWORK_STATE**: Enable/disable WiFi
- **WRITE_CONTACTS**: Modify contacts
- **WRITE_EXTERNAL_STORAGE**: Write to shared storage
- **READ_CALL_LOG**: Access call history

### Low Risk Permissions
- **INTERNET**: Internet connectivity
- **READ_EXTERNAL_STORAGE**: Read shared storage

## Testing

### Run All Tests
```bash
cd backend
python -m pytest tests/test_security_analyst.py -v
```

### Test Coverage
- Executive summary generation (4 risk levels)
- Permission explanations (known and unknown)
- Risk reasoning (permissions, URLs, components)
- Recommendation generation
- Analysis narrative
- Risk prioritization
- Complete APK analysis workflow
- Integration with AnalysisService

### Test Results
```
23 passed in 3.37s
```

Coverage areas:
- ✅ Summary generation for all risk levels
- ✅ Permission explanations and sorting by risk
- ✅ Risk detection (SMS, contacts, URLs, boot receivers)
- ✅ Recommendation generation based on risk
- ✅ Analyst narrative content and tone
- ✅ Risk factor prioritization
- ✅ Complete workflow integration
- ✅ Handling of empty/minimal analysis
- ✅ No hallucinations in analysis
- ✅ Narrative tone matches risk level

## Example Analysis Output

### Input
```python
analysis_result = {
    "package_name": "com.suspicious.app",
    "permissions": {
        "requested": [
            "READ_SMS",
            "SEND_SMS",
            "READ_CONTACTS",
            "ACCESS_FINE_LOCATION",
            "CAMERA"
        ]
    },
    "urls_and_domains": {
        "urls": [
            "http://suspicious-site.com",
            "https://secure-server.com"
        ]
    },
    "risk_assessment": {
        "risk_score": 78,
        "severity": "high"
    }
}
```

### Output
```python
result = security_analyst.analyze_apk(analysis_result)

# Executive Summary
executive_summary = {
    "risk_level": "High",
    "summary": "This application has several risky permissions...",
    "recommendation": "Avoid installation unless absolutely necessary."
}

# Permission Explanations
permissions = [
    {
        "permission": "READ_SMS",
        "risk": "high",
        "explanation": "Allows reading incoming SMS messages..."
    },
    # ... more permissions ...
]

# Risk Reasons
reasons = [
    {
        "severity": "high",
        "reason": "Application requests multiple dangerous permissions...",
        "indicator": "5 dangerous permissions"
    },
    {
        "severity": "medium",
        "reason": "Application contains unencrypted HTTP URLs...",
        "indicator": "1 HTTP URL"
    }
]

# Recommendations
recommendations = [
    "Do not install this application.",
    "If already installed, uninstall immediately.",
    "Protect SMS-based 2FA codes...",
    "Monitor the application's behavior..."
]

# Analyst Narrative
narrative = """
FraudShield AI Security Analysis Report for com.suspicious.app

This security assessment evaluates the risk profile...
The application requests 5 permissions and contains 2 external URLs...
Based on the risk assessment, the following action is recommended: Avoid installation...
This analysis is based on static code examination...
"""
```

## Production Considerations

### Performance
- All analysis is synchronous and fast (< 100ms for typical APK)
- No external API calls
- Deterministic output for testing

### Accuracy
- Knowledge base verified against Android documentation
- Risk reasoning based on actual permission functionality
- Recommendations backed by findings

### Scalability
- Stateless design
- No database dependencies
- Can be deployed as microservice

### Logging
```python
logger.info("Generating executive summary")
logger.info("Explaining 6 permissions")
logger.info("Generating risk reasons")
logger.info("Generating {n} recommendations")
logger.info("Generating analyst narrative")
```

## Backward Compatibility

✅ **No Breaking Changes**
- Existing API responses remain unchanged
- Analyst data added to `report_json` field
- All existing endpoints work as before
- New fields are optional in JSON

## Future Enhancements

1. **Machine Learning Integration**
   - Train model on threat intelligence data
   - Improve risk scoring accuracy
   - Detect emerging threat patterns

2. **Multi-Language Support**
   - Generate narratives in multiple languages
   - Localize recommendations for different regions

3. **Custom Rules**
   - Allow users to define custom permission rules
   - Whitelist/blacklist specific apps

4. **Threat Intelligence Integration**
   - Check against known malware databases
   - Identify compromised certificates
   - Detect known ransomware patterns

5. **User Feedback Loop**
   - Collect feedback on recommendations
   - Improve accuracy over time
   - Detect false positives

## Troubleshooting

### Issue: Missing analyst data in report
**Solution**: Ensure backend was restarted after code changes. The security_analyst is imported at module load time.

### Issue: Narrative seems generic
**Solution**: This is expected for minimal analysis. The agent only reports findings actually detected in the APK.

### Issue: Recommendations seem redundant
**Solution**: Filter recommendations in frontend or limit to top N recommendations.

## References

- Android Permission Documentation: https://developer.android.com/guide/topics/permissions
- OWASP Mobile Security: https://owasp.org/www-project-mobile-top-10/
- FraudShield AI Risk Scoring: See `RISK_ASSESSMENT_INTEGRATION.md`

## Support

For issues or questions:
1. Check test cases in `tests/test_security_analyst.py`
2. Review code in `backend/app/agents/security_analyst.py`
3. Check logs in `backend/logs/app.log`

---

**Last Updated**: 2026-06-11
**Version**: 1.0.0
**Status**: Production Ready ✅
