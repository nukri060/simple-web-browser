"""
RivaBrowser - A simple Python web browser with advanced features

Features:
- HTTP/HTTPS support with connection caching
- Local file browsing
- View-source mode
- Interactive command interface
- History tracking
"""

__version__ = "1.2.0"  
__author__ = "Nukri Jijavadze"
__license__ = "MIT"

from .url import URL
from .utils import load, show, print_links
from .cache import ConnectionCache
from .cli import parse_args

__all__ = [
    'URL',
    'load',
    'show',
    'print_links',
    'ConnectionCache',
    'parse_args'
]