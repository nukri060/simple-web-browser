"""
Utility functions and helpers for RivaBrowser.

This module provides various utility functions for HTML processing, content display,
and URL handling. It includes functionality for:
- HTML content sanitization and link extraction
- Content display with color formatting
- URL loading and error handling
- Text processing and formatting

Example usage:
    >>> from riva.utils import show, load, print_links
    >>> show("<html>Hello World</html>")
    Hello World
    >>> load("https://example.com")
    Loading: https://example.com
    [Content displayed here]
"""

import re
from html import unescape
from typing import Union, Optional, List, Dict, Any
from textwrap import shorten
from datetime import datetime
import colorama
from colorama import Fore, Style
import logging
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class LinkInfo:
    """Information about an extracted link."""
    url: str
    text: Optional[str] = None
    attributes: Dict[str, str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.attributes is None:
            self.attributes = {}

class HTMLUtils:
    """Utility class for HTML processing operations."""
    
    @staticmethod
    def strip_scripts(html: str) -> str:
        """
        Remove script and style tags from HTML content.
        
        Args:
            html: The HTML content to process
            
        Returns:
            Cleaned HTML content without script and style tags
            
        Example:
            >>> HTMLUtils.strip_scripts('<script>alert("test")</script><p>Hello</p>')
            '<p>Hello</p>'
        """
        try:
            html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
            html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
            html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
            return html
        except Exception as e:
            logger.error(f"Error stripping scripts: {e}")
            return html

    @staticmethod
    def extract_links(html: str, base_url: Optional[str] = None) -> List[LinkInfo]:
        """
        Extract all href links from HTML with validation and additional information.
        
        Args:
            html: The HTML content to process
            base_url: Optional base URL for resolving relative links
            
        Returns:
            List of LinkInfo objects containing link details
            
        Example:
            >>> HTMLUtils.extract_links('<a href="/about">About</a>', 'https://example.com')
            [LinkInfo(url='https://example.com/about', text='About')]
        """
        try:
            links = []
            # Find all anchor tags with their content
            for match in re.finditer(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1(.*?)>(.*?)</a>', 
                                   html, flags=re.IGNORECASE|re.DOTALL):
                url = match.group(2)
                attributes = match.group(3)
                text = match.group(4).strip()
                
                # Skip invalid links
                if not url or url.startswith(('#', 'javascript:', 'mailto:')):
                    continue
                    
                # Resolve relative URLs if base_url is provided
                if base_url and not urlparse(url).netloc:
                    url = urljoin(base_url, url)
                    
                # Extract additional attributes
                attr_dict = {}
                for attr_match in re.finditer(r'(\w+)=["\'](.*?)["\']', attributes):
                    attr_dict[attr_match.group(1)] = attr_match.group(2)
                    
                links.append(LinkInfo(url=url, text=text, attributes=attr_dict))
                
            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []

    @staticmethod
    def sanitize_html(html: str) -> str:
        """
        Sanitize HTML content by removing potentially dangerous elements.
        
        Args:
            html: The HTML content to sanitize
            
        Returns:
            Sanitized HTML content
            
        Example:
            >>> HTMLUtils.sanitize_html('<script>alert("xss")</script><p>Safe</p>')
            '<p>Safe</p>'
        """
        try:
            # Remove script tags
            html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
            
            # Remove event handlers
            html = re.sub(r'on\w+="[^"]*"', '', html)
            html = re.sub(r"on\w+='[^']*'", '', html)
            
            # Remove style attributes that could contain malicious content
            html = re.sub(r'style="[^"]*"', '', html)
            html = re.sub(r"style='[^']*'", '', html)
            
            return html
        except Exception as e:
            logger.error(f"Error sanitizing HTML: {e}")
            return html

def show(body: Union[str, bytes], max_length: Optional[int] = None) -> None:
    """
    Enhanced content display with error handling and formatting.
    
    Args:
        body: The content to display, either as string or bytes
        max_length: Optional maximum length for the displayed content
        
    Returns:
        None
        
    Example:
        >>> show("<html>Hello World</html>")
        Hello World
        >>> show(b"Binary content", max_length=10)
        Binary co...
    """
    if isinstance(body, bytes):
        try:
            body = body.decode('utf-8')
        except UnicodeDecodeError:
            try:
                body = body.decode('latin-1')
            except Exception as e:
                logger.error(f"Decoding failed: {e}")
                body = "[Binary data]"

    error_prefixes = (
        "HTTP/", "File not found", "Path is a directory",
        "Permission denied", "Error reading file", "HTTP Error"
    )
    
    if any(body.startswith(prefix) for prefix in error_prefixes):
        color = Fore.RED if "Error" in body or "HTTP/" in body else Fore.YELLOW
        print(color + body + Style.RESET_ALL)
        return
    
    try:
        decoded = unescape(body)
        cleaned = HTMLUtils.strip_scripts(decoded)
        text_only = re.sub(r'<[^>]*>', ' ', cleaned)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        
        if max_length and len(text_only) > max_length:
            text_only = shorten(text_only, width=max_length, placeholder="...")
            
        print(Fore.GREEN + text_only + Style.RESET_ALL)
        
    except Exception as e:
        logger.error(f"Content rendering failed: {e}")
        print(Fore.RED + f"Error rendering content: {str(e)}" + Style.RESET_ALL)
        print(Fore.CYAN + "Raw content preview:" + Style.RESET_ALL)
        print(body[:1000] + ("..." if len(body) > 1000 else ""))

def load(url: Union[str, 'URL'], max_length: Optional[int] = None) -> None:
    """
    Enhanced URL loader with error handling and performance tracking.
    
    Args:
        url: The URL to load, either as string or URL object
        max_length: Optional maximum length for the displayed content
        
    Returns:
        None
        
    Example:
        >>> load("https://example.com")
        Loading: https://example.com
        [Content displayed here]
        Loaded in 0.45 seconds
    """
    from .url import URL
    
    try:
        start_time = datetime.now()
        url_obj = URL(url) if isinstance(url, str) else url
        
        print(Fore.BLUE + f"\nLoading: {url_obj.original_url}" + Style.RESET_ALL)
        body = url_obj.request()
        
        show(body, max_length=max_length)
        
        load_time = (datetime.now() - start_time).total_seconds()
        print(Fore.MAGENTA + f"\nLoaded in {load_time:.2f} seconds" + Style.RESET_ALL)
        
    except Exception as e:
        logger.error(f"Failed to load {url}: {e}")
        print(Fore.RED + f"\nError loading {url}: {str(e)}" + Style.RESET_ALL)

def print_links(html: str, base_url: Optional[str] = None) -> None:
    """
    Extract and print all valid links from HTML with additional information.
    
    Args:
        html: The HTML content to process
        base_url: Optional base URL for resolving relative links
        
    Returns:
        None
        
    Example:
        >>> print_links('<a href="/about">About</a>', 'https://example.com')
        Found links:
        1. https://example.com/about (About)
    """
    try:
        links = HTMLUtils.extract_links(html, base_url)
        if links:
            print(Fore.CYAN + "\nFound links:" + Style.RESET_ALL)
            for i, link in enumerate(links[:15], 1):
                link_text = f" ({link.text})" if link.text else ""
                print(f"{i}. {link.url}{link_text}")
                if link.attributes:
                    print(f"   Attributes: {link.attributes}")
        else:
            print(Fore.YELLOW + "No valid links found in content" + Style.RESET_ALL)
    except Exception as e:
        logger.error(f"Error printing links: {e}")
        print(Fore.RED + f"Error processing links: {str(e)}" + Style.RESET_ALL)

if __name__ == '__main__':
    import doctest
    doctest.testmod()