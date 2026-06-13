"""
Android Permission Analyzer Module

Analyzes Android permissions for security risks.
Classifies permissions by risk level and category.

Responsibilities:
- Classify permissions by risk level
- Identify dangerous permission combinations
- Categorize permissions by functionality
- Generate permission-based risk assessment
"""

import logging
from typing import List, Dict, Set, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PermissionRisk(Enum):
    """Permission risk classification."""
    CRITICAL = "critical"     # Can cause severe harm
    HIGH = "high"             # Can compromise privacy/security
    MEDIUM = "medium"         # Moderately sensitive
    LOW = "low"               # Minor functionality
    INFO = "info"             # Informational only


class PermissionCategory(Enum):
    """Permission functionality category."""
    CONTACTS = "contacts"
    CALENDAR = "calendar"
    CAMERA = "camera"
    LOCATION = "location"
    MICROPHONE = "microphone"
    SMS = "sms"
    PHONE_CALLS = "phone_calls"
    STORAGE = "storage"
    SENSORS = "sensors"
    SYSTEM = "system"
    NETWORK = "network"
    ACCESSIBILITY = "accessibility"
    PAYMENT = "payment"
    OTHER = "other"


# Dangerous Permission Database
DANGEROUS_PERMISSIONS = {
    # SMS & Messaging
    "android.permission.READ_SMS": {
        "risk": PermissionRisk.CRITICAL,
        "category": PermissionCategory.SMS,
        "description": "Can read all SMS messages",
        "threat": "Access private messages, banking codes, verification codes"
    },
    "android.permission.RECEIVE_SMS": {
        "risk": PermissionRisk.CRITICAL,
        "category": PermissionCategory.SMS,
        "description": "Can intercept incoming SMS",
        "threat": "Intercept messages, block notifications"
    },
    "android.permission.SEND_SMS": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.SMS,
        "description": "Can send SMS messages",
        "threat": "Send malicious messages, incur charges"
    },
    "android.permission.WRITE_SMS": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.SMS,
        "description": "Can modify SMS messages",
        "threat": "Tamper with message records"
    },
    
    # Location
    "android.permission.ACCESS_FINE_LOCATION": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.LOCATION,
        "description": "Can access precise GPS location",
        "threat": "Track user's precise location in real-time"
    },
    "android.permission.ACCESS_COARSE_LOCATION": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.LOCATION,
        "description": "Can access approximate location",
        "threat": "Track user's general location"
    },
    
    # Contacts
    "android.permission.READ_CONTACTS": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.CONTACTS,
        "description": "Can read all contacts",
        "threat": "Access to phone numbers, email addresses, names"
    },
    "android.permission.WRITE_CONTACTS": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.CONTACTS,
        "description": "Can modify contacts",
        "threat": "Add malicious contacts, modify existing entries"
    },
    
    # Calendar
    "android.permission.READ_CALENDAR": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.CALENDAR,
        "description": "Can read calendar events",
        "threat": "Access to personal schedule, meetings, locations"
    },
    "android.permission.WRITE_CALENDAR": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.CALENDAR,
        "description": "Can modify calendar events",
        "threat": "Add/remove calendar entries"
    },
    
    # Camera & Media
    "android.permission.CAMERA": {
        "risk": PermissionRisk.CRITICAL,
        "category": PermissionCategory.CAMERA,
        "description": "Can access camera without notification",
        "threat": "Capture photos/video of user"
    },
    "android.permission.RECORD_AUDIO": {
        "risk": PermissionRisk.CRITICAL,
        "category": PermissionCategory.MICROPHONE,
        "description": "Can record audio without notification",
        "threat": "Record conversations, ambient sounds"
    },
    "android.permission.READ_EXTERNAL_STORAGE": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.STORAGE,
        "description": "Can read all files on device",
        "threat": "Access photos, documents, sensitive files"
    },
    "android.permission.WRITE_EXTERNAL_STORAGE": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.STORAGE,
        "description": "Can write/delete files on device",
        "threat": "Modify or delete user files"
    },
    
    # Phone Calls
    "android.permission.CALL_PHONE": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.PHONE_CALLS,
        "description": "Can make phone calls",
        "threat": "Make unauthorized calls, incur charges"
    },
    "android.permission.READ_CALL_LOG": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.PHONE_CALLS,
        "description": "Can read call history",
        "threat": "Access to call records, numbers, duration"
    },
    "android.permission.WRITE_CALL_LOG": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.PHONE_CALLS,
        "description": "Can modify call history",
        "threat": "Tamper with call logs"
    },
    "android.permission.READ_PHONE_STATE": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.PHONE_CALLS,
        "description": "Can access phone state and identity",
        "threat": "Get phone number, IMSI, IMEI"
    },
    
    # System Access
    "android.permission.SYSTEM_ALERT_WINDOW": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.SYSTEM,
        "description": "Can display system-level alerts/overlays",
        "threat": "Phishing overlays, fake login screens"
    },
    "android.permission.BIND_ACCESSIBILITY_SERVICE": {
        "risk": PermissionRisk.CRITICAL,
        "category": PermissionCategory.ACCESSIBILITY,
        "description": "Can intercept all user interactions",
        "threat": "Monitor all user input, capture credentials"
    },
    "android.permission.RECEIVE_BOOT_COMPLETED": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.SYSTEM,
        "description": "Can run on device startup",
        "threat": "Auto-start malicious code"
    },
    "android.permission.DISABLE_KEYGUARD": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.SYSTEM,
        "description": "Can disable lock screen",
        "threat": "Bypass device protection"
    },
    
    # Network
    "android.permission.INTERNET": {
        "risk": PermissionRisk.LOW,
        "category": PermissionCategory.NETWORK,
        "description": "Can access network/internet",
        "threat": "Send data over internet (normal for apps)"
    },
    "android.permission.CHANGE_NETWORK_STATE": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.NETWORK,
        "description": "Can modify network settings",
        "threat": "Change WiFi, enable airplane mode"
    },
    "android.permission.ACCESS_NETWORK_STATE": {
        "risk": PermissionRisk.LOW,
        "category": PermissionCategory.NETWORK,
        "description": "Can query network state",
        "threat": "Determine network type/connectivity"
    },
    
    # Sensors
    "android.permission.BODY_SENSORS": {
        "risk": PermissionRisk.MEDIUM,
        "category": PermissionCategory.SENSORS,
        "description": "Can access motion/fitness sensors",
        "threat": "Monitor physical activity, health data"
    },
    
    # Payment & Billing
    "com.android.vending.BILLING": {
        "risk": PermissionRisk.HIGH,
        "category": PermissionCategory.PAYMENT,
        "description": "Can make in-app purchases",
        "threat": "Make unauthorized purchases"
    },
}


class PermissionAnalyzer:
    """
    Analyzes Android permissions for security risks.
    
    Features:
    - Risk classification
    - Permission categorization
    - Dangerous combination detection
    - Risk score calculation
    """
    
    def __init__(self):
        """Initialize permission analyzer."""
        logger.debug("PermissionAnalyzer initialized")
    
    def classify_permission(self, permission: str) -> Dict:
        """
        Classify a single permission.
        
        Args:
            permission: Permission name (e.g., "android.permission.READ_SMS")
            
        Returns:
            Dictionary with permission classification
        """
        if permission in DANGEROUS_PERMISSIONS:
            info = DANGEROUS_PERMISSIONS[permission]
            return {
                'permission': permission,
                'risk': info['risk'].value,
                'category': info['category'].value,
                'description': info['description'],
                'threat': info['threat'],
                'is_dangerous': True
            }
        else:
            return {
                'permission': permission,
                'risk': PermissionRisk.LOW.value,
                'category': PermissionCategory.OTHER.value,
                'description': 'Standard permission',
                'threat': 'Minimal threat',
                'is_dangerous': False
            }
    
    def classify_permissions(self, permissions: List[str]) -> Tuple[List[Dict], Dict[str, int]]:
        """
        Classify all permissions.
        
        Args:
            permissions: List of permission names
            
        Returns:
            Tuple of (classified_perms, risk_counts)
        """
        classified = []
        risk_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for perm in permissions:
            classification = self.classify_permission(perm)
            classified.append(classification)
            risk_counts[classification['risk']] += 1
        
        logger.debug(f"Classified {len(classified)} permissions")
        return classified, risk_counts
    
    def get_dangerous_permissions(self, permissions: List[str]) -> List[Dict]:
        """
        Extract only dangerous permissions.
        
        Args:
            permissions: List of all permissions
            
        Returns:
            List of dangerous permission classifications
        """
        dangerous = []
        for perm in permissions:
            if perm in DANGEROUS_PERMISSIONS:
                dangerous.append(self.classify_permission(perm))
        
        logger.debug(f"Found {len(dangerous)} dangerous permissions")
        return dangerous
    
    def calculate_permission_risk_score(self, permissions: List[str]) -> float:
        """
        Calculate overall risk score based on permissions.
        
        Args:
            permissions: List of permissions
            
        Returns:
            Risk score (0.0 - 1.0)
        """
        if not permissions:
            return 0.0
        
        risk_weights = {
            PermissionRisk.CRITICAL.value: 1.0,
            PermissionRisk.HIGH.value: 0.7,
            PermissionRisk.MEDIUM.value: 0.4,
            PermissionRisk.LOW.value: 0.1,
            PermissionRisk.INFO.value: 0.0
        }
        
        total_score = 0.0
        for perm in permissions:
            classified = self.classify_permission(perm)
            risk = classified['risk']
            total_score += risk_weights.get(risk, 0.0)
        
        # Normalize to 0-1 range
        avg_score = total_score / len(permissions)
        logger.debug(f"Permission risk score: {avg_score:.2f}")
        
        return min(avg_score, 1.0)
    
    def detect_suspicious_combinations(self, permissions: List[str]) -> List[Dict]:
        """
        Detect suspicious permission combinations.
        
        Args:
            permissions: List of permissions
            
        Returns:
            List of suspicious combinations
        """
        suspicious = []
        perm_set = set(permissions)
        
        # Check for combination: Camera + Audio
        if ("android.permission.CAMERA" in perm_set and
            "android.permission.RECORD_AUDIO" in perm_set):
            suspicious.append({
                'name': 'Camera + Microphone',
                'permissions': ['android.permission.CAMERA', 'android.permission.RECORD_AUDIO'],
                'risk': 'critical',
                'description': 'Can record video and audio - surveillance capability'
            })
        
        # Check for combination: Fine Location + Internet
        if ("android.permission.ACCESS_FINE_LOCATION" in perm_set and
            "android.permission.INTERNET" in perm_set):
            suspicious.append({
                'name': 'Location + Internet',
                'permissions': ['android.permission.ACCESS_FINE_LOCATION', 'android.permission.INTERNET'],
                'risk': 'high',
                'description': 'Can track and transmit location data'
            })
        
        # Check for combination: SMS + Internet
        if ("android.permission.READ_SMS" in perm_set and
            "android.permission.INTERNET" in perm_set):
            suspicious.append({
                'name': 'SMS + Internet',
                'permissions': ['android.permission.READ_SMS', 'android.permission.INTERNET'],
                'risk': 'critical',
                'description': 'Can read SMS and send to remote server - credential theft'
            })
        
        # Check for combination: Accessibility + Internet
        if ("android.permission.BIND_ACCESSIBILITY_SERVICE" in perm_set and
            "android.permission.INTERNET" in perm_set):
            suspicious.append({
                'name': 'Accessibility + Internet',
                'permissions': ['android.permission.BIND_ACCESSIBILITY_SERVICE', 'android.permission.INTERNET'],
                'risk': 'critical',
                'description': 'Can monitor input and exfiltrate to remote server'
            })
        
        logger.debug(f"Detected {len(suspicious)} suspicious permission combinations")
        return suspicious
    
    def get_permission_summary(self, permissions: List[str]) -> Dict:
        """
        Get comprehensive permission analysis summary.
        
        Args:
            permissions: List of permissions
            
        Returns:
            Dictionary with complete permission analysis
        """
        classified, risk_counts = self.classify_permissions(permissions)
        dangerous = self.get_dangerous_permissions(permissions)
        risk_score = self.calculate_permission_risk_score(permissions)
        combinations = self.detect_suspicious_combinations(permissions)
        
        return {
            'total_permissions': len(permissions),
            'dangerous_permissions': len(dangerous),
            'risk_score': risk_score,
            'risk_counts': risk_counts,
            'dangerous_permissions_list': dangerous,
            'suspicious_combinations': combinations,
            'all_classified': classified
        }
