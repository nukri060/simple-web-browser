import argparse

def parse_args():
    """Parse command line arguments with version support"""
    parser = argparse.ArgumentParser(
        description='RivaBrowser - Lightweight Web Browser',
        epilog='Example: python -m Riva https://example.com --timeout 10'
    )
    
    parser.add_argument(
        'url', 
        nargs='?', 
        help='URL to open (http://, file://, view-source:)'
    )
    
    parser.add_argument(
        '--timeout', 
        type=float, 
        default=5.0,
        help='Connection timeout in seconds (default: 5)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable debug output'
    )

    parser.add_argument(
        '--user-agent',
        type=str,
        default="RivaBrowser/1.0",
        help='Custom User-Agent header'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='riva_debug.log',
        help='Path to debug log file'
    )

    parser.add_argument(
        '--history',
        action='store_true',
        help='Show browsing history'
    )

    parser.add_argument(
        '--version', 
        action='version',
        version='%(prog)s 1.2',
        help='Show version and exit'
    )
    
    return parser.parse_args()