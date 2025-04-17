import unittest
from riva.utils import show, load, print_links
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
        """Test show function"""
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

    def test_load(self):
        """Test load function"""
        test_content = "Test content"
        with patch('riva.url.URL') as mock_url:
            mock_url_instance = mock_url.return_value
            mock_url_instance.original_url = "test.txt"
            mock_url_instance.request.return_value = test_content
            load("test.txt")
            self.assertIn(Fore.GREEN + test_content, self.test_output.getvalue())

    def test_load_file_not_found(self):
        """Test load function with non-existent file"""
        with patch('riva.url.URL') as mock_url:
            mock_url_instance = mock_url.return_value
            mock_url_instance.original_url = "nonexistent.txt"
            mock_url_instance.request.side_effect = FileNotFoundError("File not found")
            load("nonexistent.txt")
            self.assertIn("Error loading", self.test_output.getvalue())

    def test_print_links(self):
        """Test print_links function"""
        html_content = """
        <html>
            <a href="https://example.com">Example</a>
            <a href="https://test.com">Test</a>
        </html>
        """
        print_links(html_content)
        output = self.test_output.getvalue()
        self.assertIn("Found links:", output)
        self.assertIn("https://example.com", output)
        self.assertIn("https://test.com", output)

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

    def test_print_links_with_attributes(self):
        """Test print_links with links having additional attributes"""
        html_content = """
        <html>
            <a href="https://example.com" target="_blank" rel="noopener">Example</a>
        </html>
        """
        print_links(html_content)
        self.assertIn("https://example.com", self.test_output.getvalue())

if __name__ == '__main__':
    unittest.main() 