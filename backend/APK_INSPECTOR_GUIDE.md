# APK Inspector Agent Implementation

## Overview

The APK Inspector is a comprehensive Android APK security analysis agent for FraudShield AI. It orchestrates multiple analysis modules to extract security-relevant intelligence from APK files and generate threat reports.

## Architecture

```
APKInspector (Orchestrator)
├── AndroguardParser (Low-level APK parsing)
├── PermissionAnalyzer (Permission risk analysis)
├── URLExtractor (URL/domain analysis)
└── Output: Comprehensive threat report
```

## Files Created

### 1. `app/analysis/androguard_parser.py`
**Purpose**: Low-level APK parsing using Androguard library

**Key Classes**:
- `AndroguardParser`: Main parser class
  - `__init__(apk_path)`: Load APK
  - `get_package_name()`: Extract package ID
  - `get_version_name/code()`: Extract version info
  - `get_app_name()`: Extract app label
  - `get_activities/services/receivers/providers()`: Extract components
  - `get_permissions()`: Extract requested permissions
  - `get_strings()`/`get_dex_strings()`: Extract embedded strings
  - `compute_file_hashes()`: Calculate MD5 and SHA256

**Error Handling**:
- `AndroguardParseError`: Raised for parsing failures
- Fallback to APK-only mode if DEX analysis fails
- Graceful handling of missing manifest fields

**Key Features**:
- Robust APK loading with fallback mechanisms
- Comprehensive metadata extraction
- String extraction from resources and bytecode
- File hash computation for integrity verification

---

### 2. `app/analysis/url_extractor.py`
**Purpose**: Extract and analyze URLs and domains from APK strings

**Key Classes**:
- `URLExtractor`: URL extraction and classification
  - `extract_urls(strings)`: Find URLs using regex
  - `extract_domains(urls)`: Parse domain names
  - `filter_urls(urls)`: Remove common legitimate URLs
  - `classify_url_risk(url)`: Security risk scoring
  - `extract_urls_and_analyze(strings)`: Complete pipeline

**Features**:
- **URL Detection**: Regex-based pattern matching for http://, https://, ftp://
- **Domain Extraction**: Parse URLs to extract unique domains
- **Filtering**: Remove common legitimate domains (google.com, facebook.com, etc.)
- **Risk Classification**:
  - HTTPS vs HTTP detection
  - Suspicious pattern detection (bank, login, verify, confirm, etc.)
  - IP address detection (suspicious)
  - Suspicious TLD detection (.xyz, .tk, .ml, .ga, .cf, .pw)
  - Risk scoring (0.0 - 1.0)

**Suspicious Indicators**:
- Non-HTTPS connections
- Phishing patterns (login, verify, confirm, authenticate)
- Financial/banking keywords
- IP addresses instead of domains
- Suspicious TLDs

**Example Risk Classification**:
```python
{
    'url': 'https://bank-login.xyz/verify',
    'domain': 'bank-login.xyz',
    'risk_score': 0.65,
    'is_suspicious': True,
    'indicators': [
        'Suspicious pattern: phishing',
        'Suspicious TLD: .xyz'
    ]
}
```

---

### 3. `app/analysis/permission_analyzer.py`
**Purpose**: Analyze Android permissions for security risks

**Key Classes**:
- `PermissionAnalyzer`: Permission security analysis
  - `classify_permission(perm)`: Classify single permission
  - `classify_permissions(perms)`: Classify all permissions
  - `get_dangerous_permissions(perms)`: Extract dangerous perms
  - `calculate_permission_risk_score(perms)`: Risk scoring
  - `detect_suspicious_combinations(perms)`: Find risky combinations
  - `get_permission_summary(perms)`: Complete analysis

**Permission Classification**:

| Category | Risk Level | Examples |
|----------|-----------|----------|
| **CRITICAL** | Highest risk | READ_SMS, RECEIVE_SMS, CAMERA, RECORD_AUDIO, BIND_ACCESSIBILITY_SERVICE |
| **HIGH** | Serious concern | ACCESS_FINE_LOCATION, READ_CONTACTS, SYSTEM_ALERT_WINDOW, CALL_PHONE |
| **MEDIUM** | Moderate risk | READ_CALENDAR, WRITE_CONTACTS, CHANGE_NETWORK_STATE, BODY_SENSORS |
| **LOW** | Minor concern | INTERNET, ACCESS_NETWORK_STATE |
| **INFO** | Informational | Standard permissions |

**Dangerous Permission Database**:
Each permission includes:
- Risk level classification
- Functional category (SMS, Location, Camera, etc.)
- Description of capability
- Threat description

**Dangerous Combinations Detected**:
1. **Camera + Microphone**: Surveillance capability
2. **Location + Internet**: Tracking and data exfiltration
3. **SMS + Internet**: Credential theft (OTP, verification codes)
4. **Accessibility + Internet**: Keystroke logging and credential theft

**Risk Score Calculation**:
```
score = (critical_perms × 1.0 + high_perms × 0.7 + medium_perms × 0.4 + low_perms × 0.1) / total_perms
Result: 0.0 (safe) to 1.0 (dangerous)
```

---

### 4. `app/agents/apk_inspector.py`
**Purpose**: Orchestrator for complete APK security analysis

**Key Classes**:
- `APKInspector`: Main analysis agent
  - `analyze_apk(apk_path)`: Complete analysis pipeline
  - `_extract_metadata()`: Basic APK metadata
  - `_extract_components()`: Activities, Services, Receivers, Providers
  - `_analyze_permissions()`: Permission risk analysis
  - `_extract_urls_and_domains()`: URL/domain analysis
  - `_compute_hashes()`: File integrity hashes
  - `_calculate_threat_level()`: Overall threat classification
  - `_generate_risk_indicators()`: Human-readable risk list

**Analysis Pipeline**:

```
1. Validate APK path
   ↓
2. Parse APK with Androguard
   ↓
3. Extract metadata (package, version, app name)
   ↓
4. Extract Android components (Activities, Services, etc.)
   ↓
5. Analyze permissions for risks
   ↓
6. Extract and classify URLs/domains
   ↓
7. Compute file hashes (MD5, SHA256)
   ↓
8. Calculate threat level
   ↓
9. Generate comprehensive report
```

**Output Structure**:
```json
{
    "status": "success",
    "apk_name": "app.apk",
    "package_name": "com.example.app",
    "version_name": "1.0.0",
    "version_code": "1",
    "app_name": "Example App",
    "file_size": 5242880,
    "md5": "abc123...",
    "sha256": "def456...",
    "components": {
        "activities": [...],
        "services": [...],
        "broadcast_receivers": [...],
        "content_providers": [...]
    },
    "permissions": {
        "total_permissions": 15,
        "dangerous_permissions": 3,
        "risk_score": 0.45,
        "risk_counts": {
            "critical": 1,
            "high": 2,
            "medium": 4,
            "low": 8,
            "info": 0
        },
        "dangerous_list": [...],
        "suspicious_combinations": [...]
    },
    "urls_and_domains": {
        "url_count": 5,
        "domain_count": 3,
        "suspicious_count": 2,
        "urls": [...],
        "domains": [...],
        "suspicious_urls": [...],
        "classified_urls": [...]
    },
    "analysis_summary": {
        "threat_level": "medium",
        "risk_indicators": [...],
        "permission_risk_score": 0.45,
        "dangerous_permissions": 3,
        "suspicious_combinations": 1,
        "suspicious_urls": 2
    }
}
```

**Threat Level Classification**:
- **critical** (score ≥ 0.8): Severe security threats, likely malware
- **high** (score ≥ 0.6): Significant security concerns
- **medium** (score ≥ 0.4): Moderate concerns, proceed with caution
- **low** (score ≥ 0.2): Minor concerns
- **clean** (score < 0.2): No major threats detected

**Error Handling**:
- Input validation (file existence, format, size)
- APK parsing error recovery
- Graceful degradation (DEX analysis optional)
- Comprehensive logging at all stages
- Custom exceptions for specific error types

---

## Design Patterns

### 1. **Orchestrator Pattern**
The APKInspector coordinates multiple analysis modules without implementing core logic itself. Each module has a single responsibility:
- AndroguardParser: APK parsing
- PermissionAnalyzer: Permission analysis
- URLExtractor: URL extraction

### 2. **Strategy Pattern**
Different analysis strategies (permission, URL, component extraction) are encapsulated in separate classes and can be swapped or extended.

### 3. **Factory Pattern**
```python
inspector = create_apk_inspector()
result = inspector.analyze_apk(apk_path)
```

### 4. **Pipeline Pattern**
Analysis follows a structured pipeline with clear stages:
1. Validation
2. Parsing
3. Extraction
4. Analysis
5. Classification
6. Reporting

### 5. **Error Handling Strategy**
- Specific exceptions for different failure modes
- Graceful degradation (fallbacks)
- Comprehensive logging
- User-friendly error messages

---

## Security Analysis Details

### Permission Analysis
**Process**:
1. Extract permissions from manifest
2. Look up each permission in dangerous database
3. Classify by risk level and category
4. Detect suspicious combinations
5. Calculate composite risk score

**Combination Detection Examples**:
- Camera + Microphone = Surveillance
- Location + Internet = Tracking
- SMS + Internet = Credential theft
- Accessibility + Internet = Keystroke logging

### URL Analysis
**Process**:
1. Extract strings from resources and bytecode
2. Apply regex pattern for URL detection
3. Remove known legitimate domains
4. Classify each URL for risk
5. Extract unique domains

**Risk Factors**:
- Protocol (HTTP vs HTTPS)
- Domain reputation
- Suspicious keywords
- IP address usage
- TLD reputation

### Component Analysis
**Extracted Components**:
- Activities: UI screens
- Services: Background processes
- Broadcast Receivers: Event listeners
- Content Providers: Data sharing

---

## Error Handling

### Exception Hierarchy
```
Exception
├── APKAnalysisError (Analysis failure)
├── AndroguardParseError (Parsing failure)
└── ValidationException (Input validation)
```

### Handled Scenarios
1. File not found
2. Invalid file format
3. Corrupted APK
4. Missing manifest
5. Permission denied
6. Insufficient disk space
7. DEX analysis optional failure

---

## Usage Examples

### Basic Usage
```python
from app.agents import APKInspector

inspector = APKInspector()
result = inspector.analyze_apk("/path/to/app.apk")
print(json.dumps(result, indent=2))
```

### Convenience Function
```python
from app.agents import analyze_apk

result = analyze_apk("/path/to/app.apk")
if result['analysis_summary']['threat_level'] == 'critical':
    print("Malware detected!")
```

### Integration with FastAPI
```python
@router.post("/api/v1/analysis")
async def create_analysis(file: UploadFile, db: Session = Depends(get_db)):
    # Save uploaded file
    apk_path = save_upload(file)
    
    # Analyze APK
    inspector = APKInspector()
    analysis = inspector.analyze_apk(apk_path)
    
    # Store results in database
    db_analysis = Analysis.create(db, analysis)
    return AnalysisResponseSchema.from_orm(db_analysis)
```

---

## Performance Considerations

### Time Complexity
- Parsing: O(n) where n = APK file size
- String analysis: O(m) where m = total strings
- URL extraction: O(m) with regex matching
- Permission analysis: O(p) where p = permissions

### Space Complexity
- APK in memory: O(n)
- Extracted strings: O(m)
- Analysis results: O(output_size)

### Optimization Opportunities
1. Stream APK parsing for large files
2. Cache permission database
3. Parallel URL classification
4. Incremental DEX analysis

---

## Testing

### Unit Test Examples
```python
def test_permission_classification():
    analyzer = PermissionAnalyzer()
    result = analyzer.classify_permission("android.permission.READ_SMS")
    assert result['risk'] == "critical"

def test_url_extraction():
    extractor = URLExtractor()
    strings = ["Visit https://example.com for more"]
    urls = extractor.extract_urls(strings)
    assert "https://example.com" in urls

def test_apk_analysis():
    inspector = APKInspector()
    result = inspector.analyze_apk("test_app.apk")
    assert result['status'] == 'success'
    assert 'package_name' in result
```

---

## Future Enhancements

1. **Machine Learning Integration**
   - Malware classification models
   - Permission risk prediction
   - URL reputation scoring

2. **Dynamic Analysis**
   - Sandbox execution
   - Runtime behavior monitoring
   - Network traffic analysis

3. **Threat Intelligence**
   - VirusTotal integration
   - Known malware database
   - Zero-day detection

4. **Advanced Analysis**
   - Smali code analysis
   - Dataflow tracking
   - Cryptography detection

5. **Performance**
   - Parallel processing
   - Incremental analysis
   - Caching layer

---

## Dependencies

```
androguard==4.1.0
sqlalchemy==2.0.23
pydantic==2.5.0
```

---

## Conclusion

The APK Inspector provides a production-ready framework for Android security analysis. Its modular design allows easy extension and maintenance, while comprehensive error handling ensures reliability in production environments.
