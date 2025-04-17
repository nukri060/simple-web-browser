import unittest
from unittest.mock import patch, MagicMock
from riva.__main__ import HistoryManager, parse_args, print_header, print_help
import os
import tempfile
from datetime import datetime

class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.temp_dir = tempfile.mkdtemp()
        self.history_file = os.path.join(self.temp_dir, 'test_history.log')
        self.history = HistoryManager(self.history_file)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        os.rmdir(self.temp_dir)

    def test_history_initialization(self):
        """Test history manager initialization"""
        self.assertTrue(os.path.exists(self.history_file))
        with open(self.history_file, 'r') as f:
            content = f.read()
            self.assertIn("Timestamp | Status | URL", content)

    def test_add_entry(self):
        """Test adding entry to history"""
        url = "https://example.com"
        status = "SUCCESS"
        self.history.add(url, status)
        
        with open(self.history_file, 'r') as f:
            content = f.read()
            self.assertIn(url, content)
            self.assertIn(status, content)

    def test_show_history(self):
        """Test showing history"""
        url = "https://example.com"
        status = "SUCCESS"
        self.history.add(url, status)
        
        with patch('builtins.print') as mock_print:
            self.history.show_history()
            mock_print.assert_called()

    def test_history_file_permissions(self):
        """Test history file permissions"""
        self.assertTrue(os.access(self.history_file, os.W_OK))

class TestMainFunctions(unittest.TestCase):
    def test_parse_args(self):
        """Test argument parsing"""
        test_args = ["https://example.com", "--timeout", "10", "--verbose"]
        with patch('sys.argv', ['test'] + test_args):
            args = parse_args()
            self.assertEqual(args.url, "https://example.com")
            self.assertEqual(args.timeout, 10.0)
            self.assertTrue(args.verbose)

    def test_print_header(self):
        """Test header printing"""
        with patch('builtins.print') as mock_print:
            print_header("1.2.2")
            mock_print.assert_called()

    def test_print_help(self):
        """Test help menu printing"""
        with patch('builtins.print') as mock_print:
            print_help()
            mock_print.assert_called()

    @patch('riva.__main__.URL')
    def test_process_url(self, mock_url):
        """Test URL processing"""
        from riva.__main__ import process_url
        mock_url.return_value.request.return_value = "Test content"
        
        content, load_time = process_url("https://example.com", "TestAgent")
        self.assertEqual(content, "Test content")
        self.assertIsInstance(load_time, float)

    def test_display_content(self):
        """Test content display"""
        from riva.__main__ import display_content
        test_content = "<html><title>Test</title><p>Test paragraph</p></html>"
        
        with patch('builtins.print') as mock_print:
            display_content(test_content, 0.5)
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main() 