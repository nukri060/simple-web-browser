"""
Tests for the utils module.

This module contains tests for:
- HTML processing utilities
- Content display functions
- URL loading and error handling
- Link extraction and printing
"""

import unittest
from riva.utils import show, load, print_links, HTMLUtils, LinkInfo
import io
import sys
from unittest.mock import patch
from colorama import Fore, Style

class TestUtils(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.test_output = io.StringIO()
        sys.stdout = self.test_output

    def tearDown(self):
        """Clean up after tests"""
        sys.stdout = sys.__stdout__

    def test_show(self):
        """Test show function with basic text"""
        test_text = "Hello, World!"
        show(test_text)
        expected = Fore.GREEN + test_text + Style.RESET_ALL
        self.assertEqual(self.test_output.getvalue().strip(), expected.strip())

    def test_show_with_error(self):
        """Test show function with error message"""
        test_text = "HTTP/1.1 404 Not Found"
        show(test_text)
        expected = Fore.RED + test_text + Style.RESET_ALL
        self.assertEqual(self.test_output.getvalue().strip(), expected.strip())

    def test_show_with_binary(self):
        """Test show function with binary content"""
        test_binary = b"Binary content"
        show(test_binary)
        expected = Fore.GREEN + "Binary content" + Style.RESET_ALL
        self.assertEqual(self.test_output.getvalue().strip(), expected.strip())

    def test_show_with_max_length(self):
        """Test show function with maximum length"""
        test_text = "This is a long text that should be shortened"
        show(test_text, max_length=10)
        output = self.test_output.getvalue().strip()
        self.assertTrue(output.startswith(Fore.GREEN))
        self.assertTrue(output.endswith(Style.RESET_ALL))
        self.assertTrue(len(output) <= len(Fore.GREEN) + 10 + len(Style.RESET_ALL) + 3)  # +3 for "..."

    def test_load(self):
        """Test load function with successful request"""
        test_content = "Test content"
        with patch('riva.url.URL') as mock_url:
            mock_url_instance = mock_url.return_value
            mock_url_instance.original_url = "test.txt"
            mock_url_instance.request.return_value = test_content
            load("test.txt")
            output = self.test_output.getvalue()
            self.assertIn(Fore.GREEN + test_content, output)
            self.assertIn("Loaded in", output)

    def test_load_file_not_found(self):
        """Test load function with non-existent file"""
        with patch('riva.url.URL') as mock_url:
            mock_url_instance = mock_url.return_value
            mock_url_instance.original_url = "nonexistent.txt"
            mock_url_instance.request.side_effect = FileNotFoundError("File not found")
            load("nonexistent.txt")
            self.assertIn("Error loading", self.test_output.getvalue())

    def test_print_links(self):
        """Test print_links function with valid HTML"""
        html_content = """
        <html>
            <a href="https://example.com" target="_blank">Example</a>
            <a href="https://test.com">Test</a>
        </html>
        """
        print_links(html_content)
        output = self.test_output.getvalue()
        self.assertIn("Found links:", output)
        self.assertIn("https://example.com", output)
        self.assertIn("https://test.com", output)
        self.assertIn("target", output)

    def test_print_links_with_base_url(self):
        """Test print_links function with base URL"""
        html_content = '<a href="/about">About</a>'
        print_links(html_content, base_url="https://example.com")
        output = self.test_output.getvalue()
        self.assertIn("https://example.com/about", output)

    def test_print_links_no_links(self):
        """Test print_links with no links"""
        html_content = "<html><body>No links here</body></html>"
        print_links(html_content)
        self.assertIn("No valid links found in content", self.test_output.getvalue())

    def test_print_links_invalid_html(self):
        """Test print_links with invalid HTML"""
        invalid_html = "Not HTML content"
        print_links(invalid_html)
        self.assertIn("No valid links found in content", self.test_output.getvalue())

    def test_html_utils_strip_scripts(self):
        """Test HTMLUtils.strip_scripts"""
        html = '<script>alert("test")</script><p>Hello</p>'
        result = HTMLUtils.strip_scripts(html)
        self.assertEqual(result, '<p>Hello</p>')

    def test_html_utils_sanitize_html(self):
        """Test HTMLUtils.sanitize_html"""
        html = '<p onclick="alert(\'xss\')" style="color:red">Hello</p>'
        result = HTMLUtils.sanitize_html(html)
        self.assertEqual(result, '<p>Hello</p>')

    def test_link_info(self):
        """Test LinkInfo dataclass"""
        link = LinkInfo(url="https://example.com", text="Example")
        self.assertEqual(link.url, "https://example.com")
        self.assertEqual(link.text, "Example")
        self.assertEqual(link.attributes, {})

if __name__ == '__main__':
    unittest.main() 