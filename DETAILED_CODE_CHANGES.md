# Detailed Code Changes Reference

## File 1: backend/app/agents/security_analyst.py

### Change 1: analyze_apk() method (Line ~688)
**Location**: Around line 688 in analyze_apk()

**Old Code**:
```python
permissions_list = permissions_dict.get('requested', [])
```

**New Code**:
```python
permissions_list = permissions_dict.get('all_permissions', [])
logger.info(f"[Permission Data Flow] Extracted {len(permissions_list)} permissions from APK")
```

**Purpose**: Read from correct APKInspector key that contains all permissions

---

### Change 2: generate_analysis_narrative() method (Line ~545)

**Old Code**:
```python
dangerous_count = len(permissions_dict.get('requested', []))
narrative = f"The application requests {dangerous_count} permissions and contains {len(urls)} external URLs."
```

**New Code**:
```python
total_count = permissions_dict.get('total_permissions', 0)
dangerous_count = permissions_dict.get('dangerous_permissions', 0)
narrative = f"The application requests {total_count} permissions, including {dangerous_count} sensitive permissions and contains {len(urls)} external URLs."
```

**Purpose**: Use actual permission counts from APKInspector instead of calculating from empty list

---

### Change 3: generate_analysis_narrative() second paragraph (Line ~549)

**Old Code**:
```python
# No check for specific dangerous permissions - empty list results in no findings
```

**New Code**:
```python
# Check for specific dangerous permissions
dangerous_perms_str = ', '.join([p.split('.')[-1] for p in permissions_dict.get('dangerous_list', [])])
if 'RECEIVE_SMS' in dangerous_perms_str or 'READ_SMS' in dangerous_perms_str:
    narrative += " Notably, the app has SMS permissions which could enable interception of authentication codes."
if 'RECEIVE_BOOT_COMPLETED' in dangerous_perms_str:
    narrative += " The app can run automatically on device boot, potentially enabling persistent background access."
```

**Purpose**: Specifically mention dangerous permissions (SMS, boot) in the narrative

---

### Change 4: generate_risk_reasons() method (Line ~244)

**Old Code**:
```python
dangerous_perms = permissions_dict.get('requested', [])
```

**New Code**:
```python
dangerous_perms = permissions_dict.get('dangerous_list', []) or permissions_dict.get('all_permissions', [])
```

**Purpose**: Use dangerous_list which contains the filtered dangerous permissions

---

### Change 5: explain_permissions() method (Line ~190)

**Old Code**:
```python
explanation = self.PERMISSION_EXPLANATIONS.get(permission)
```

**New Code**:
```python
# Extract short name from full permission name (e.g., android.permission.READ_SMS -> READ_SMS)
short_name = permission.split('.')[-1] if '.' in permission else permission
explanation = self.PERMISSION_EXPLANATIONS.get(short_name)
```

**Purpose**: Handle both full names (android.permission.X) and short names (X)

---

### Change 6: Enhanced PERMISSION_EXPLANATIONS dictionary (Lines ~50-120)

**Updated Entries**:
```python
PERMISSION_EXPLANATIONS = {
    # ... existing entries ...
    
    "RECEIVE_SMS": {
        "risk": "critical",
        "explanation": "Allows the app to receive and intercept incoming SMS messages without notification. Could be used to steal OTP codes or block emergency messages. This is especially dangerous for banking apps."
    },
    "READ_SMS": {
        "risk": "critical",
        "explanation": "Allows reading all SMS messages including 2FA codes and banking information. This is a CRITICAL risk as it enables interception of sensitive authentication codes."
    },
    "RECEIVE_BOOT_COMPLETED": {
        "risk": "high",
        "explanation": "Allows the app to start automatically when device boots. Once installed, the malicious app will run even if the device restarts without user interaction."
    },
    "ACCESS_NETWORK_STATE": {
        "risk": "medium",
        "explanation": "Allows the app to check WiFi/mobile network state. Could be used to detect connection type before exfiltrating data."
    },
    "WRITE_EXTERNAL_STORAGE": {
        "risk": "medium",
        "explanation": "Allows writing to shared storage. Could be used to drop malware or exfiltrate data."
    },
}
```

**Purpose**: Provide detailed threat-specific explanations for dangerous permissions

---

## File 2: backend/app/services/analysis_service.py

### Change 1: _extract_findings() method (Line ~250)

**Old Code**:
```python
all_perms = perms_analysis.get('all_classified', [])  # ← WRONG KEY
```

**New Code**:
```python
all_perms = perms_analysis.get('all_permissions', [])  # ← CORRECT KEY
```

**Purpose**: Read from correct key in APKInspector output

---

### Change 2: Added helper method _get_permission_risk_level() (New, ~25 lines)

**Location**: New method after _extract_findings()

**Code**:
```python
def _get_permission_risk_level(self, permission_short_name: str) -> str:
    """
    Map permission name to risk level.
    
    Returns: "critical", "high", "medium", "low", or "info"
    """
    CRITICAL_PERMS = {
        "READ_SMS", "RECEIVE_SMS", "CALL_PHONE", "CAMERA", 
        "RECORD_AUDIO", "ACCESS_FINE_LOCATION"
    }
    HIGH_PERMS = {
        "SEND_SMS", "WRITE_SMS", "READ_CONTACTS", "RECEIVE_BOOT_COMPLETED",
        "READ_CALL_LOG", "CHANGE_NETWORK_STATE"
    }
    MEDIUM_PERMS = {
        "ACCESS_NETWORK_STATE", "CHANGE_NETWORK_STATE", 
        "WRITE_EXTERNAL_STORAGE", "READ_EXTERNAL_STORAGE"
    }
    LOW_PERMS = {"INTERNET"}
    
    if permission_short_name in CRITICAL_PERMS:
        return "critical"
    elif permission_short_name in HIGH_PERMS:
        return "high"
    elif permission_short_name in MEDIUM_PERMS:
        return "medium"
    elif permission_short_name in LOW_PERMS:
        return "low"
    return "info"
```

**Purpose**: Standardize permission risk classification

---

### Change 3: Added helper method _score_to_severity() (New, ~15 lines)

**Location**: New method after _get_permission_risk_level()

**Code**:
```python
def _score_to_severity(self, score: float) -> str:
    """
    Convert numeric risk score (0.0-1.0) to severity string.
    
    Mapping:
    - >= 0.8: critical
    - >= 0.6: high
    - >= 0.4: medium
    - >= 0.2: low
    - < 0.2: info
    """
    if score >= 0.8:
        return "critical"
    elif score >= 0.6:
        return "high"
    elif score >= 0.4:
        return "medium"
    elif score >= 0.2:
        return "low"
    return "info"
```

**Purpose**: Standardize score-to-severity conversion

---

## File 3: backend/tests/test_security_analyst.py

### Change 1: Updated test_generate_risk_reasons_sms_permissions() (Line ~176)

**Old Code**:
```python
analysis = {
    "permissions": {
        "requested": ["android.permission.READ_SMS", "android.permission.SEND_SMS"]
    },
    "urls_and_domains": {"urls": [], "domains": []},
    "components": {"receivers": [], "services": []}
}
```

**New Code**:
```python
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
```

**Purpose**: Update test to use new data structure with all_permissions key

---

### Change 2: Added TestPermissionDataFlow class (New, ~200 lines)

**Location**: New test class starting around line 200

**Tests Include**:

1. **test_analyze_apk_with_all_permissions_key**
   - Verifies permission explanations are generated from all_permissions

2. **test_permission_narrative_includes_actual_counts** ⭐ MAIN TEST
   - Verifies narrative contains "12" not "0"
   - Verifies narrative mentions "4 sensitive permissions"
   - Verifies narrative does NOT say "0 permissions"

3. **test_dangerous_permissions_in_explanations**
   - Verifies RECEIVE_SMS, READ_SMS, RECEIVE_BOOT_COMPLETED in explanations

4. **test_sms_permission_explanation_content**
   - Verifies RECEIVE_SMS is CRITICAL risk
   - Verifies explanation mentions OTP/authentication/interception

5. **test_boot_completed_permission_explanation**
   - Verifies RECEIVE_BOOT_COMPLETED is HIGH/CRITICAL
   - Verifies explanation mentions boot/automatic/background

6. **test_risk_reasons_include_critical_permissions**
   - Verifies risk reasons include SMS threats
   - Verifies SMS reasons marked as high/critical

7. **test_narrative_mentions_sms_threat**
   - Verifies narrative mentions SMS, intercept, otp, or authentication

8. **test_narrative_mentions_boot_completed**
   - Verifies narrative mentions boot, automatic, or background

9. **test_internet_permission_low_risk**
   - Verifies INTERNET is marked as LOW risk

10. **test_access_network_state_medium_risk**
    - Verifies ACCESS_NETWORK_STATE is marked as MEDIUM

11. **test_permission_count_accuracy**
    - Verifies permission counts match actual data
    - Verifies narrative mentions correct count

12. **test_full_permission_names_handled**
    - Verifies full permission names (android.permission.X) are handled

**Purpose**: Comprehensive test coverage proving permission data flow works correctly

---

## Summary of Changes

| File | Type | Lines | Changes |
|------|------|-------|---------|
| security_analyst.py | Bug Fix | 688, 545, 549, 244, 190 | 5 methods updated |
| security_analyst.py | Enhancement | 50-120 | 5 permissions explained |
| analysis_service.py | Bug Fix | 250 | 1 key updated |
| analysis_service.py | Enhancement | New | 2 helper methods |
| test_security_analyst.py | Bug Fix | 176 | 1 test updated |
| test_security_analyst.py | New Tests | 200-350 | 12 comprehensive tests |

---

## How to Review Changes

1. **For Bug Understanding**: Read Changes 1-4 in security_analyst.py
2. **For Enhancement Understanding**: Read Changes 5-6 in security_analyst.py
3. **For Permission Mapping**: Read Changes 2-3 in analysis_service.py
4. **For Test Coverage**: Review all 12 tests in TestPermissionDataFlow

## Files to Read for Complete Understanding

1. [security_analyst.py](../backend/app/agents/security_analyst.py)
2. [analysis_service.py](../backend/app/services/analysis_service.py)
3. [test_security_analyst.py](../backend/tests/test_security_analyst.py)
