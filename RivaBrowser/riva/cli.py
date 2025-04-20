"""
Command-line interface for RivaBrowser.

This module provides a command-line interface for RivaBrowser, allowing users to:
- Open URLs in the browser
- Configure connection settings
- Manage browsing history
- Enable debugging and logging
- Customize browser behavior

Example usage:
    python -m riva https://example.com --timeout 10 --verbose
    python -m riva --history
    python -m riva --version
"""

import argparse
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .url import URL
from .utils import setup_logging

class CLIError(Exception):
    """Base exception for CLI-related errors."""
    pass

class InvalidURLError(CLIError):
    """Raised when an invalid URL is provided."""
    pass

class InvalidOptionError(CLIError):
    """Raised when invalid command-line options are provided."""
    pass

def parse_args() -> Dict[str, Any]:
    """
    Parse command line arguments with enhanced validation and type safety.
    
    Returns:
        Dict[str, Any]: Parsed command-line arguments
        
    Raises:
        InvalidURLError: If the provided URL is invalid
        InvalidOptionError: If invalid options are provided
    """
    parser = argparse.ArgumentParser(
        description='RivaBrowser - Lightweight Web Browser',
        epilog='Example: python -m riva https://example.com --timeout 10'
    )
    
    # URL argument
    parser.add_argument(
        'url', 
        nargs='?', 
        help='URL to open (http://, https://, file://, view-source:)'
    )
    
    # Connection settings
    connection_group = parser.add_argument_group('Connection Settings')
    connection_group.add_argument(
        '--timeout', 
        type=float, 
        default=5.0,
        help='Connection timeout in seconds (default: 5)'
    )
    connection_group.add_argument(
        '--max-redirects',
        type=int,
        default=5,
        help='Maximum number of redirects to follow (default: 5)'
    )
    connection_group.add_argument(
        '--user-agent',
        type=str,
        default="RivaBrowser/1.0",
        help='Custom User-Agent header'
    )
    
    # Browser settings
    browser_group = parser.add_argument_group('Browser Settings')
    browser_group.add_argument(
        '--cache-size',
        type=int,
        default=100,
        help='Maximum number of cached connections (default: 100)'
    )
    browser_group.add_argument(
        '--disable-cache',
        action='store_true',
        help='Disable connection caching'
    )
    browser_group.add_argument(
        '--disable-http2',
        action='store_true',
        help='Disable HTTP/2 support'
    )
    
    # History and bookmarks
    history_group = parser.add_argument_group('History and Bookmarks')
    history_group.add_argument(
        '--history',
        action='store_true',
        help='Show browsing history'
    )
    history_group.add_argument(
        '--clear-history',
        action='store_true',
        help='Clear browsing history'
    )
    history_group.add_argument(
        '--bookmarks',
        action='store_true',
        help='Show bookmarks'
    )
    
    # Debug and logging
    debug_group = parser.add_argument_group('Debug and Logging')
    debug_group.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable debug output'
    )
    debug_group.add_argument(
        '--log-file',
        type=str,
        default='riva_debug.log',
        help='Path to debug log file'
    )
    debug_group.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    # Version and help
    parser.add_argument(
        '--version', 
        action='version',
        version='%(prog)s 1.2',
        help='Show version and exit'
    )
    
    args = parser.parse_args()
    
    # Validate URL if provided
    if args.url:
        try:
            URL(args.url)
        except ValueError as e:
            raise InvalidURLError(f"Invalid URL: {e}")
    
    # Validate timeout
    if args.timeout <= 0:
        raise InvalidOptionError("Timeout must be greater than 0")
    
    # Validate max redirects
    if args.max_redirects < 0:
        raise InvalidOptionError("Max redirects must be non-negative")
    
    # Validate cache size
    if args.cache_size < 0:
        raise InvalidOptionError("Cache size must be non-negative")
    
    # Setup logging
    if args.verbose:
        args.log_level = 'DEBUG'
    setup_logging(args.log_file, args.log_level)
    
    return vars(args)

def main() -> None:
    """
    Main entry point for the CLI.
    
    This function:
    1. Parses command-line arguments
    2. Sets up logging
    3. Handles the requested action
    4. Provides appropriate error messages
    """
    try:
        args = parse_args()
        logging.info("Starting RivaBrowser with arguments: %s", args)
        
        # Handle different actions based on arguments
        if args.get('history'):
            # TODO: Implement history viewing
            print("Browsing history:")
            # Add history implementation
        elif args.get('clear_history'):
            # TODO: Implement history clearing
            print("Clearing browsing history...")
            # Add history clearing implementation
        elif args.get('bookmarks'):
            # TODO: Implement bookmarks viewing
            print("Bookmarks:")
            # Add bookmarks implementation
        elif args.get('url'):
            # TODO: Implement URL opening
            print(f"Opening URL: {args['url']}")
            # Add URL opening implementation
        else:
            print("No action specified. Use --help for usage information.")
            
    except (InvalidURLError, InvalidOptionError) as e:
        logging.error(str(e))
        print(f"Error: {e}")
    except Exception as e:
        logging.exception("Unexpected error occurred")
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()