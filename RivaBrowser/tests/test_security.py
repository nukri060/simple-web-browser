"""
Tests for security module.
"""

import unittest
from riva.security import SecurityPolicy

class TestSecurityPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = SecurityPolicy()
    
    def test_csp_header_generation(self):
        """Test CSP header generation."""
        csp_header = self.policy.get_csp_header()
        self.assertIn("default-src 'self'", csp_header)
        self.assertIn("script-src 'self' 'unsafe-inline'", csp_header)
        self.assertIn("frame-src 'none'", csp_header)
    
    def test_html_sanitization(self):
        """Test HTML sanitization."""
        malicious_html = """
        <script>alert('xss')</script>
        <img src="x" onerror="alert('xss')">
        <a href="javascript:alert('xss')">Click me</a>
        """
        
        sanitized = self.policy.sanitize_html(malicious_html)
        self.assertNotIn("<script>", sanitized)
        self.assertNotIn("onerror", sanitized)
        self.assertNotIn("javascript:", sanitized)
    
    def test_url_validation(self):
        """Test URL validation."""
        self.assertTrue(self.policy.validate_url("https://example.com"))
        self.assertTrue(self.policy.validate_url("http://example.com"))
        self.assertTrue(self.policy.validate_url("file:///path/to/file"))
        
        self.assertFalse(self.policy.validate_url("javascript:alert('xss')"))
        self.assertFalse(self.policy.validate_url("data:text/html,<script>alert('xss')</script>"))
        self.assertFalse(self.policy.validate_url("vbscript:msgbox('xss')"))
        self.assertFalse(self.policy.validate_url("invalid-url"))

if __name__ == '__main__':
    unittest.main() 