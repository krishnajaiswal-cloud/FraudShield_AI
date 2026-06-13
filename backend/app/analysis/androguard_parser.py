"""
Androguard APK Parser Module

Provides low-level APK parsing utilities using Androguard library.
Handles extraction of AndroidManifest.xml data and APK structure.

This module is responsible for:
- Loading APK files via Androguard
- Extracting manifest information
- Parsing application metadata
- Error handling for corrupted/invalid APKs
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from androguard.misc import AnalyzeAPK
from androguard.core.apk import APK
import hashlib
import os

logger = logging.getLogger(__name__)


class AndroguardParseError(Exception):
    """Exception raised for Androguard parsing failures."""
    pass


class AndroguardParser:
    """
    Low-level APK parser using Androguard library.
    
    Responsibilities:
    - Load and parse APK files
    - Extract manifest data
    - Handle parsing errors gracefully
    - Compute file hashes
    """
    
    def __init__(self, apk_path: str):
        """
        Initialize parser with APK file path.
        
        Args:
            apk_path: Path to APK file
            
        Raises:
            AndroguardParseError: If APK is invalid/corrupted
        """
        self.apk_path = apk_path
        self.apk: Optional[APK] = None
        self.dex: Optional[Any] = None
        self.analysis: Optional[Any] = None
        
        logger.debug(f"Initializing AndroguardParser for: {apk_path}")
        self._load_apk()
    
    def _load_apk(self) -> None:
        """
        Load APK file using Androguard.
        
        Raises:
            AndroguardParseError: If APK fails to load
        """
        try:
            if not os.path.exists(self.apk_path):
                raise FileNotFoundError(f"APK file not found: {self.apk_path}")
            
            if not self.apk_path.lower().endswith('.apk'):
                raise ValueError(f"Invalid file extension (must be .apk): {self.apk_path}")
            
            # Try to load with full analysis
            try:
                self.apk, self.dex, self.analysis = AnalyzeAPK(self.apk_path)
                logger.info(f"✓ APK loaded with DEX analysis: {self.apk_path}")
            except Exception as dex_error:
                # Fallback: Load APK only (no DEX analysis)
                logger.warning(f"DEX analysis failed, loading APK only: {dex_error}")
                self.apk = APK(self.apk_path)
                
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise AndroguardParseError(f"APK file not found: {self.apk_path}") from e
        except ValueError as e:
            logger.error(f"Invalid APK file: {e}")
            raise AndroguardParseError(f"Invalid APK file: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load APK: {e}")
            raise AndroguardParseError(f"Failed to load APK: {self.apk_path}: {str(e)}") from e
    
    def get_package_name(self) -> str:
        """
        Extract package name from manifest.
        
        Returns:
            Package name (e.g., "com.example.app")
        """
        try:
            package = self.apk.get_package()
            if not package:
                raise AndroguardParseError("Package name not found in manifest")
            logger.debug(f"Package name: {package}")
            return package
        except Exception as e:
            logger.error(f"Failed to extract package name: {e}")
            raise AndroguardParseError(f"Package name extraction failed: {e}") from e
    
    def get_version_name(self) -> str:
        """
        Extract version name (e.g., "1.0.0").
        
        Returns:
            Version name string
        """
        try:
            version = self.apk.get_android_version_name() or "unknown"
            logger.debug(f"Version name: {version}")
            return version
        except Exception as e:
            logger.warning(f"Failed to extract version name: {e}")
            return "unknown"
    
    def get_version_code(self) -> str:
        """
        Extract version code (e.g., "1").
        
        Returns:
            Version code string
        """
        try:
            code = self.apk.get_android_version_code() or "unknown"
            logger.debug(f"Version code: {code}")
            return str(code)
        except Exception as e:
            logger.warning(f"Failed to extract version code: {e}")
            return "unknown"
    
    def get_app_name(self) -> str:
        """
        Extract application label/name from manifest.
        
        Returns:
            App name or package name if label not found
        """
        try:
            app_name = self.apk.get_app_name()
            if not app_name:
                app_name = self.get_package_name()
            logger.debug(f"App name: {app_name}")
            return app_name
        except Exception as e:
            logger.warning(f"Failed to extract app name: {e}")
            return self.get_package_name()
    
    def get_activities(self) -> List[str]:
        """
        Extract all Activity components.
        
        Activities are Android components representing UI screens.
        
        Returns:
            List of activity class names
        """
        try:
            activities = self.apk.get_activities() or []
            logger.debug(f"Found {len(activities)} activities")
            return list(activities)
        except Exception as e:
            logger.warning(f"Failed to extract activities: {e}")
            return []
    
    def get_services(self) -> List[str]:
        """
        Extract all Service components.
        
        Services are Android components that run in background without UI.
        
        Returns:
            List of service class names
        """
        try:
            services = self.apk.get_services() or []
            logger.debug(f"Found {len(services)} services")
            return list(services)
        except Exception as e:
            logger.warning(f"Failed to extract services: {e}")
            return []
    
    def get_receivers(self) -> List[str]:
        """
        Extract all BroadcastReceiver components.
        
        Broadcast receivers respond to system or app broadcasts.
        
        Returns:
            List of receiver class names
        """
        try:
            receivers = self.apk.get_receivers() or []
            logger.debug(f"Found {len(receivers)} broadcast receivers")
            return list(receivers)
        except Exception as e:
            logger.warning(f"Failed to extract receivers: {e}")
            return []
    
    def get_providers(self) -> List[str]:
        """
        Extract all ContentProvider components.
        
        Content providers manage access to structured data.
        
        Returns:
            List of provider class names
        """
        try:
            providers = self.apk.get_providers() or []
            logger.debug(f"Found {len(providers)} content providers")
            return list(providers)
        except Exception as e:
            logger.warning(f"Failed to extract providers: {e}")
            return []
    
    def get_permissions(self) -> List[str]:
        """
        Extract all requested permissions from manifest.
        
        Returns:
            List of permission names (e.g., "android.permission.READ_SMS")
        """
        try:
            perms = self.apk.get_permissions() or []
            logger.debug(f"Found {len(perms)} permissions")
            return list(perms)
        except Exception as e:
            logger.warning(f"Failed to extract permissions: {e}")
            return []
    
    def get_strings(self) -> List[str]:
        """
        Extract all strings from APK resources.
        
        Useful for URL extraction and static analysis.
        
        Returns:
            List of string resources
        """
        try:
            strings = []
            # Get strings from resources
            if hasattr(self.apk, 'get_android_resources'):
                resources = self.apk.get_android_resources()
                if resources and hasattr(resources, 'get_strings'):
                    all_strings = resources.get_strings()
                    if all_strings:
                        for locale_strings in all_strings.values():
                            strings.extend(locale_strings.values())
            
            logger.debug(f"Extracted {len(strings)} strings from resources")
            return strings
        except Exception as e:
            logger.warning(f"Failed to extract strings: {e}")
            return []
    
    def get_dex_strings(self) -> List[str]:
        """
        Extract strings from DEX files (bytecode).
        
        DEX strings include embedded URLs, API endpoints, etc.
        
        Returns:
            List of strings from DEX code
        """
        try:
            if not self.analysis:
                logger.warning("DEX analysis not available")
                return []
            
            strings = []
            # Extract strings from DEX analysis
            if hasattr(self.analysis, 'get_strings'):
                strings = list(self.analysis.get_strings())
            
            logger.debug(f"Extracted {len(strings)} strings from DEX")
            return strings
        except Exception as e:
            logger.warning(f"Failed to extract DEX strings: {e}")
            return []
    
    def compute_file_hashes(self) -> Tuple[str, str]:
        """
        Compute MD5 and SHA-256 hashes of APK file.
        
        Used for:
        - Duplicate detection
        - Integrity verification
        - Malware database matching
        
        Returns:
            Tuple of (md5_hash, sha256_hash)
        """
        try:
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            
            with open(self.apk_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
            
            md5_str = md5_hash.hexdigest()
            sha256_str = sha256_hash.hexdigest()
            
            logger.debug(f"MD5: {md5_str}, SHA256: {sha256_str}")
            return md5_str, sha256_str
        except Exception as e:
            logger.error(f"Failed to compute hashes: {e}")
            raise AndroguardParseError(f"Hash computation failed: {e}") from e
    
    def get_apk_size(self) -> int:
        """
        Get APK file size in bytes.
        
        Returns:
            File size
        """
        try:
            size = os.path.getsize(self.apk_path)
            logger.debug(f"APK size: {size} bytes")
            return size
        except Exception as e:
            logger.warning(f"Failed to get APK size: {e}")
            return 0
