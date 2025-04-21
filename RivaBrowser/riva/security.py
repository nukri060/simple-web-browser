"""
Security policies and configurations for RivaBrowser.
"""

from typing import Dict, List, Optional
import re

class SecurityPolicy:
    """Security policy configuration for the browser."""
    
    def __init__(self):
        self.csp_rules: Dict[str, List[str]] = {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", "data:", "https:"],
            'connect-src': ["'self'", "https:"],
            'font-src': ["'self'", "https:"],
            'object-src': ["'none'"],
            'media-src': ["'self'"],
            'frame-src': ["'none'"]
        }
        
        self.xss_protection = True
        self.csrf_protection = True
        self.content_type_options = True
        self.frame_options = "DENY"
        self.referrer_policy = "strict-origin-when-cross-origin"
        
    def get_csp_header(self) -> str:
        """Generate Content Security Policy header."""
        return "; ".join(
            f"{directive} {' '.join(sources)}"
            for directive, sources in self.csp_rules.items()
        )
    
    def sanitize_html(self, html: str) -> str:
        """Basic HTML sanitization to prevent XSS."""
        # Remove script tags
        html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html)
        
        # Remove event handlers
        html = re.sub(r'on\w+="[^"]*"', '', html)
        html = re.sub(r"on\w+='[^']*'", '', html)
        
        # Remove javascript: URLs
        html = re.sub(r'javascript:[^\'"]*', '', html)
        
        return html
    
    def validate_url(self, url: str) -> bool:
        """Validate URL for security purposes."""
        try:
            # Basic URL validation
            if not url.startswith(('http://', 'https://', 'file://')):
                return False
                
            # Check for potentially dangerous protocols
            if url.startswith(('javascript:', 'data:', 'vbscript:')):
                return False
                
            return True
        except:
            return False 