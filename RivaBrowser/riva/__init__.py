"""
RivaBrowser - A simple Python web browser
"""

__version__ = "1.0"
__author__ = "Nukri Jijavadze"

from .url import URL
from .utils import load, show
from .cache import ConnectionCache

__all__ = ['URL', 'load', 'show', 'ConnectionCache']