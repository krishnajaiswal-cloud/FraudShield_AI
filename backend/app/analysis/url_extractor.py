"""
URL and Domain Extractor Module

Extracts URLs and domains from APK strings and resources.
Performs security analysis on extracted URLs.

Responsibilities:
- Extract URLs from strings
- Parse domains from URLs
- Deduplicate URLs
- Classify URL security risk
- Filter common/legitimate URLs
"""

import logging
import re
from typing import List, Set, Dict, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class URLInfo:
    """Structured URL information."""
    url: str
    domain: str
    scheme: str
    is_https: bool
    is_suspicious: bool


class URLExtractor:
    """
    Extract and analyze URLs from APK strings.
    
    Features:
    - URL pattern matching
    - Domain extraction
    - Duplicate elimination
    - Security classification
    - Common URL filtering
    """
    
    # Regex pattern for URL detection
    # Matches http://, https://, ftp://, and scheme-relative URLs
    URL_PATTERN = re.compile(
        r'(?:(?:https?|ftp)://)'  # Protocol
        r'(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*'  # Subdomains
        r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)'  # Domain
        r'(?::\d+)?'  # Optional port
        r'(?:/[^\s\'"]*)?',  # Optional path
        re.IGNORECASE
    )
    
    # Common legitimate domains to filter out
    COMMON_DOMAINS = {
        'google.com', 'googleapis.com', 'gstatic.com',
        'android.com', 'googleapis.com', 'google-analytics.com',
        'facebook.com', 'fbcdn.net', 'cdn.jsdelivr.net',
        'cloudflare.com', 'amazonaws.com', 'microsoft.com',
        'github.com', 'twitter.com', 'github.io'
    }
    
    # Suspicious domain patterns
    SUSPICIOUS_PATTERNS = {
        'bank': 'banking',
        'paypal': 'payment',
        'amazon': 'shopping',
        'login': 'phishing',
        'verify': 'phishing',
        'confirm': 'phishing',
        'authenticate': 'authentication',
        'credit': 'financial',
        'account': 'authentication'
    }
    
    def __init__(self, include_common: bool = False):
        """
        Initialize URL extractor.
        
        Args:
            include_common: Whether to include common legitimate domains
        """
        self.include_common = include_common
        logger.debug(f"URLExtractor initialized (include_common={include_common})")
    
    def extract_urls(self, strings: List[str]) -> List[str]:
        """
        Extract URLs from a list of strings.
        
        Args:
            strings: List of strings to search
            
        Returns:
            List of unique URLs found
        """
        urls: Set[str] = set()
        
        for string in strings:
            if not isinstance(string, str):
                continue
            
            # Find all URLs in string
            matches = self.URL_PATTERN.findall(string)
            urls.update(matches)
        
        logger.debug(f"Extracted {len(urls)} unique URLs from {len(strings)} strings")
        return sorted(list(urls))
    
    def extract_domains(self, urls: List[str]) -> List[str]:
        """
        Extract domain names from URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            List of unique domain names
        """
        domains: Set[str] = set()
        
        for url in urls:
            try:
                # Ensure URL has scheme for proper parsing
                if not url.startswith(('http://', 'https://', 'ftp://')):
                    url = 'https://' + url
                
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Remove port if present
                if ':' in domain:
                    domain = domain.split(':')[0]
                
                if domain:
                    domains.add(domain)
            except Exception as e:
                logger.warning(f"Failed to parse domain from URL {url}: {e}")
                continue
        
        logger.debug(f"Extracted {len(domains)} unique domains")
        return sorted(list(domains))
    
    def filter_urls(self, urls: List[str]) -> List[str]:
        """
        Filter out common/legitimate URLs.
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            Filtered list of potentially suspicious URLs
        """
        if self.include_common:
            return urls
        
        filtered = []
        
        for url in urls:
            try:
                parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'https://' + url)
                domain = parsed.netloc.split(':')[0].lower()
                
                # Check if domain is in common list
                is_common = any(domain.endswith(common) for common in self.COMMON_DOMAINS)
                
                if not is_common:
                    filtered.append(url)
            except Exception as e:
                logger.warning(f"Error filtering URL {url}: {e}")
                filtered.append(url)  # Include on error
        
        logger.debug(f"Filtered {len(urls)} URLs down to {len(filtered)} suspicious URLs")
        return filtered
    
    def classify_url_risk(self, url: str) -> Dict[str, any]:
        """
        Classify URL for security risk.
        
        Args:
            url: URL to classify
            
        Returns:
            Dictionary with risk classification
        """
        risk_score = 0.0
        indicators = []
        
        try:
            parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'https://' + url)
            domain = parsed.netloc.split(':')[0].lower()
            
            # Check for HTTPS
            if parsed.scheme != 'https':
                risk_score += 0.1
                indicators.append("Not HTTPS")
            
            # Check for suspicious patterns in domain
            for pattern, category in self.SUSPICIOUS_PATTERNS.items():
                if pattern.lower() in domain.lower():
                    risk_score += 0.2
                    indicators.append(f"Suspicious pattern: {category}")
                    break
            
            # Check for IP address instead of domain
            if self._is_ip_address(domain):
                risk_score += 0.15
                indicators.append("IP address used instead of domain")
            
            # Check for suspicious TLDs
            suspicious_tlds = {'.xyz', '.tk', '.ml', '.ga', '.cf', '.pw'}
            tld = '.' + domain.split('.')[-1].lower()
            if tld in suspicious_tlds:
                risk_score += 0.15
                indicators.append(f"Suspicious TLD: {tld}")
            
            # Clamp risk score to 0-1
            risk_score = min(risk_score, 1.0)
            
            return {
                'url': url,
                'domain': domain,
                'risk_score': risk_score,
                'is_suspicious': risk_score > 0.3,
                'indicators': indicators
            }
        except Exception as e:
            logger.warning(f"Failed to classify URL {url}: {e}")
            return {
                'url': url,
                'risk_score': 0.0,
                'is_suspicious': False,
                'indicators': []
            }
    
    @staticmethod
    def _is_ip_address(domain: str) -> bool:
        """
        Check if domain is an IP address.
        
        Args:
            domain: Domain or IP to check
            
        Returns:
            True if IP address
        """
        # Remove port
        ip = domain.split(':')[0]
        
        # Check for IPv4
        ipv4_pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
        if ipv4_pattern.match(ip):
            return True
        
        # Check for IPv6
        if ':' in ip:  # Basic IPv6 check
            return True
        
        return False
    
    def extract_urls_and_analyze(self, strings: List[str]) -> Tuple[List[str], List[str], List[Dict]]:
        """
        Complete URL extraction and analysis pipeline.
        
        Args:
            strings: List of strings from APK
            
        Returns:
            Tuple of (all_urls, suspicious_urls, classified_urls)
        """
        # Extract all URLs
        all_urls = self.extract_urls(strings)
        
        # Filter suspicious URLs
        suspicious_urls = self.filter_urls(all_urls)
        
        # Classify each suspicious URL
        classified = []
        for url in suspicious_urls:
            classification = self.classify_url_risk(url)
            classified.append(classification)
        
        logger.info(f"URL Analysis: {len(all_urls)} total, {len(suspicious_urls)} suspicious")
        
        return all_urls, suspicious_urls, classified


def extract_urls_from_strings(strings: List[str], filter_common: bool = True) -> Dict[str, any]:
    """
    Convenience function for URL extraction.
    
    Args:
        strings: List of strings from APK
        filter_common: Whether to filter common URLs
        
    Returns:
        Dictionary with extracted URLs and domains
    """
    extractor = URLExtractor(include_common=not filter_common)
    
    urls = extractor.extract_urls(strings)
    domains = extractor.extract_domains(urls)
    suspicious_urls = extractor.filter_urls(urls)
    
    return {
        'urls': urls,
        'domains': domains,
        'suspicious_urls': suspicious_urls,
        'url_count': len(urls),
        'domain_count': len(domains),
        'suspicious_count': len(suspicious_urls)
    }
