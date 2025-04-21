"""
Tests for the RivaBrowser main module.

This module contains tests for:
- History management
- Dependency checking
- Protocol detection
- Content display
- Error handling
"""

import pytest
import os
import sys
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path

from riva.__main__ import (
    HistoryManager,
    check_dependencies,
    make_request,
    display_content,
    main,
    BrowserError,
    ProtocolError,
    ContentError
)

class TestHistoryManager:
    """Test suite for history management."""
    
    def setup_method(self):
        """Setup test environment."""
        self.history_file = 'test_history.log'
        self.history = HistoryManager(self.history_file)
        
    def teardown_method(self):
        """Cleanup test environment."""
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
    
    def test_init_creates_file(self):
        """Test that initialization creates history file."""
        assert os.path.exists(self.history_file)
        with open(self.history_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Timestamp | Status | URL" in content
    
    def test_add_entry(self):
        """Test adding entry to history."""
        self.history.add("https://example.com", "success")
        assert len(self.history.entries) == 1
        assert self.history.entries[0]['url'] == "https://example.com"
        assert self.history.entries[0]['status'] == "success"
    
    def test_add_entry_invalid_file(self):
        """Test adding entry with invalid file."""
        with patch('os.access', return_value=False):
            with pytest.raises(PermissionError):
                self.history.add("https://example.com", "success")
    
    def test_show_history(self):
        """Test showing history."""
        self.history.add("https://example.com", "success")
        with patch('builtins.print') as mock_print:
            self.history.show_history()
            mock_print.assert_called()
    
    def test_show_history_no_file(self):
        """Test showing history with no file."""
        os.remove(self.history_file)
        with pytest.raises(FileNotFoundError):
            self.history.show_history()

class TestDependencies:
    """Test suite for dependency checking."""
    
    @patch('importlib.metadata.version')
    def test_check_dependencies_all_installed(self, mock_version):
        """Test dependency check with all packages installed."""
        mock_version.return_value = "2.0.0"
        check_dependencies()  # Should not raise any exceptions
    
    @patch('importlib.metadata.version')
    def test_check_dependencies_missing(self, mock_version):
        """Test dependency check with missing packages."""
        mock_version.side_effect = importlib.metadata.PackageNotFoundError
        with patch('builtins.input', return_value='y'):
            with patch('subprocess.check_call'):
                check_dependencies()  # Should not raise any exceptions
    
    @patch('importlib.metadata.version')
    def test_check_dependencies_outdated(self, mock_version):
        """Test dependency check with outdated packages."""
        mock_version.return_value = "1.0.0"
        with patch('builtins.input', return_value='y'):
            with patch('subprocess.check_call'):
                check_dependencies()  # Should not raise any exceptions
    
    @patch('importlib.metadata.version')
    def test_check_dependencies_install_failed(self, mock_version):
        """Test dependency check with installation failure."""
        mock_version.side_effect = importlib.metadata.PackageNotFoundError
        with patch('builtins.input', return_value='y'):
            with patch('subprocess.check_call', side_effect=subprocess.CalledProcessError(1, 'cmd')):
                with pytest.raises(subprocess.CalledProcessError):
                    check_dependencies()

class TestProtocol:
    """Test suite for protocol handling."""
    
    @patch('riva.__main__.URL')
    @patch('riva.__main__.HTTP2Connection')
    def test_make_request_http2(self, mock_conn, mock_url):
        """Test making HTTP/2 request."""
        mock_url.return_value.scheme = 'https'
        mock_conn.return_value.connect.return_value = True
        mock_conn.return_value.send_request.return_value = 1
        mock_conn.return_value.receive_response.return_value = (200, b'content')
        
        response = make_request("https://example.com", "http/2")
        assert response['protocol'] == 'http/2'
        assert response['content'] == 'content'
    
    @patch('riva.__main__.URL')
    def test_make_request_http1(self, mock_url):
        """Test making HTTP/1.1 request."""
        mock_url.return_value.request.return_value = {
            'status': 200,
            'content': 'content'
        }
        
        response = make_request("http://example.com", "http/1.1")
        assert response['status'] == 200
        assert response['content'] == 'content'
    
    @patch('riva.__main__.URL')
    def test_make_request_invalid_url(self, mock_url):
        """Test making request with invalid URL."""
        mock_url.side_effect = ValueError("Invalid URL")
        with pytest.raises(ProtocolError):
            make_request("invalid-url")

class TestContent:
    """Test suite for content display."""
    
    def test_display_content_html(self):
        """Test displaying HTML content."""
        content = "<html><title>Test</title><p>Content</p></html>"
        with patch('builtins.print') as mock_print:
            display_content(content, 1.0)
            mock_print.assert_called()
    
    def test_display_content_text(self):
        """Test displaying text content."""
        content = "Plain text content"
        with patch('builtins.print') as mock_print:
            display_content(content, 1.0)
            mock_print.assert_called()
    
    def test_display_content_error(self):
        """Test displaying content with error."""
        with pytest.raises(ContentError):
            display_content(None, 1.0)

class TestMain:
    """Test suite for main function."""
    
    @patch('riva.__main__.check_dependencies')
    @patch('riva.__main__.process_url')
    def test_main_success(self, mock_process, mock_check):
        """Test main function with successful execution."""
        mock_process.return_value = ("content", 1.0)
        with patch('sys.argv', ['riva', 'https://example.com']):
            main()  # Should not raise any exceptions
    
    @patch('riva.__main__.check_dependencies')
    def test_main_no_url(self, mock_check):
        """Test main function with no URL."""
        with patch('sys.argv', ['riva']):
            with pytest.raises(SystemExit):
                main()
    
    @patch('riva.__main__.check_dependencies')
    @patch('riva.__main__.process_url')
    def test_main_error(self, mock_process, mock_check):
        """Test main function with error."""
        mock_process.side_effect = Exception("Test error")
        with patch('sys.argv', ['riva', 'https://example.com']):
            with pytest.raises(SystemExit):
                main() 