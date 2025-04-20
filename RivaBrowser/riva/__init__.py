"""
RivaBrowser - A lightweight web browser engine with HTTP/2 support.

This package provides a simple yet powerful web browser engine that supports
both HTTP/1.1 and HTTP/2 protocols. It features connection pooling, caching,
and automatic protocol detection.

Key features:
- HTTP/1.1 and HTTP/2 protocol support
- Automatic protocol detection
- Connection pooling and caching
- SSL/TLS support
- Interactive command interface
- Smart content preview
- History management
"""

__version__ = "1.3.0"
__author__ = "RivaBrowser Team"
__license__ = "MIT"

from .url import URL
from .cache import ConnectionCache, connection_cache
from .http2 import HTTP2Connection
from .utils import show, load, print_links

__all__ = [
    'URL',
    'ConnectionCache',
    'connection_cache',
    'HTTP2Connection',
    'show',
    'load',
    'print_links'
]