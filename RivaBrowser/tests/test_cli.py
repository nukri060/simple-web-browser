"""
Tests for the RivaBrowser command-line interface.

This module contains tests for:
- Argument parsing and validation
- Error handling
- Command-line option groups
- Logging configuration
- URL validation
"""

import pytest
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path

from riva.cli import (
    parse_args,
    main,
    CLIError,
    InvalidURLError,
    InvalidOptionError
)

class TestCLI:
    """Test suite for the command-line interface."""
    
    def test_parse_args_valid_url(self):
        """Test parsing arguments with a valid URL."""
        with patch('sys.argv', ['riva', 'https://example.com']):
            args = parse_args()
            assert args['url'] == 'https://example.com'
            assert args['timeout'] == 5.0
            assert args['verbose'] is False
    
    def test_parse_args_invalid_url(self):
        """Test parsing arguments with an invalid URL."""
        with patch('sys.argv', ['riva', 'invalid-url']):
            with pytest.raises(InvalidURLError):
                parse_args()
    
    def test_parse_args_invalid_timeout(self):
        """Test parsing arguments with an invalid timeout."""
        with patch('sys.argv', ['riva', '--timeout', '0']):
            with pytest.raises(InvalidOptionError):
                parse_args()
    
    def test_parse_args_invalid_max_redirects(self):
        """Test parsing arguments with an invalid max redirects value."""
        with patch('sys.argv', ['riva', '--max-redirects', '-1']):
            with pytest.raises(InvalidOptionError):
                parse_args()
    
    def test_parse_args_invalid_cache_size(self):
        """Test parsing arguments with an invalid cache size."""
        with patch('sys.argv', ['riva', '--cache-size', '-1']):
            with pytest.raises(InvalidOptionError):
                parse_args()
    
    def test_parse_args_verbose(self):
        """Test parsing arguments with verbose flag."""
        with patch('sys.argv', ['riva', '--verbose']):
            args = parse_args()
            assert args['verbose'] is True
            assert args['log_level'] == 'DEBUG'
    
    def test_parse_args_log_level(self):
        """Test parsing arguments with custom log level."""
        with patch('sys.argv', ['riva', '--log-level', 'ERROR']):
            args = parse_args()
            assert args['log_level'] == 'ERROR'
    
    def test_parse_args_history(self):
        """Test parsing arguments with history flag."""
        with patch('sys.argv', ['riva', '--history']):
            args = parse_args()
            assert args['history'] is True
    
    def test_parse_args_clear_history(self):
        """Test parsing arguments with clear history flag."""
        with patch('sys.argv', ['riva', '--clear-history']):
            args = parse_args()
            assert args['clear_history'] is True
    
    def test_parse_args_bookmarks(self):
        """Test parsing arguments with bookmarks flag."""
        with patch('sys.argv', ['riva', '--bookmarks']):
            args = parse_args()
            assert args['bookmarks'] is True
    
    def test_parse_args_disable_cache(self):
        """Test parsing arguments with disable cache flag."""
        with patch('sys.argv', ['riva', '--disable-cache']):
            args = parse_args()
            assert args['disable_cache'] is True
    
    def test_parse_args_disable_http2(self):
        """Test parsing arguments with disable HTTP/2 flag."""
        with patch('sys.argv', ['riva', '--disable-http2']):
            args = parse_args()
            assert args['disable_http2'] is True
    
    def test_parse_args_version(self):
        """Test parsing arguments with version flag."""
        with patch('sys.argv', ['riva', '--version']):
            with pytest.raises(SystemExit):
                parse_args()
    
    def test_parse_args_help(self):
        """Test parsing arguments with help flag."""
        with patch('sys.argv', ['riva', '--help']):
            with pytest.raises(SystemExit):
                parse_args()
    
    @patch('riva.cli.parse_args')
    def test_main_history(self, mock_parse_args):
        """Test main function with history flag."""
        mock_parse_args.return_value = {'history': True}
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("Browsing history:")
    
    @patch('riva.cli.parse_args')
    def test_main_clear_history(self, mock_parse_args):
        """Test main function with clear history flag."""
        mock_parse_args.return_value = {'clear_history': True}
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("Clearing browsing history...")
    
    @patch('riva.cli.parse_args')
    def test_main_bookmarks(self, mock_parse_args):
        """Test main function with bookmarks flag."""
        mock_parse_args.return_value = {'bookmarks': True}
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("Bookmarks:")
    
    @patch('riva.cli.parse_args')
    def test_main_url(self, mock_parse_args):
        """Test main function with URL."""
        mock_parse_args.return_value = {'url': 'https://example.com'}
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("Opening URL: https://example.com")
    
    @patch('riva.cli.parse_args')
    def test_main_no_action(self, mock_parse_args):
        """Test main function with no action specified."""
        mock_parse_args.return_value = {}
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("No action specified. Use --help for usage information.")
    
    @patch('riva.cli.parse_args')
    def test_main_invalid_url_error(self, mock_parse_args):
        """Test main function with invalid URL error."""
        mock_parse_args.side_effect = InvalidURLError("Invalid URL")
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("Error: Invalid URL")
    
    @patch('riva.cli.parse_args')
    def test_main_invalid_option_error(self, mock_parse_args):
        """Test main function with invalid option error."""
        mock_parse_args.side_effect = InvalidOptionError("Invalid option")
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("Error: Invalid option")
    
    @patch('riva.cli.parse_args')
    def test_main_unexpected_error(self, mock_parse_args):
        """Test main function with unexpected error."""
        mock_parse_args.side_effect = Exception("Unexpected error")
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("An unexpected error occurred: Unexpected error") 