import re
from html import unescape
from typing import Union, Optional
from textwrap import shorten
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

class HTMLUtils:
    @staticmethod
    def strip_scripts(html: str) -> str:
        """Remove script and style tags from HTML"""
        html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        return html

    @staticmethod
    def extract_links(html: str) -> list:
        """Extract all href links from HTML"""
        return re.findall(r'href=[\'"]?([^\'" >]+)', html)

def show(body: str, max_length: Optional[int] = None) -> None:
    """
    Render response body with enhanced formatting:
    - Preserves technical messages
    - Cleans HTML content
    - Adds color output
    - Optional length limiting
    
    Args:
        body: Content to display
        max_length: Optional max characters to display
    """
    # Check for non-HTML responses
    if any(body.startswith(prefix) for prefix in (
        "HTTP/", "File not found", "Path is a directory",
        "Permission denied", "Error reading file"
    )):
        print(Fore.YELLOW + body + Style.RESET_ALL)
        return
    
    try:
        # Enhanced HTML cleaning
        decoded = unescape(body)
        cleaned = HTMLUtils.strip_scripts(decoded)
        text_only = re.sub(r'<[^>]*>', '', cleaned)
        normalized = ' '.join(text_only.split())
        
        # Apply length limit if specified
        if max_length and len(normalized) > max_length:
            normalized = shorten(normalized, width=max_length, placeholder="...")
            
        print(Fore.GREEN + normalized + Style.RESET_ALL)
        
    except Exception as e:
        print(Fore.RED + f"Error rendering content: {str(e)}" + Style.RESET_ALL)
        print(Fore.CYAN + "Raw content:" + Style.RESET_ALL)
        print(body[:1000] + ("..." if len(body) > 1000 else ""))

def load(url: Union[str, 'URL'], max_length: Optional[int] = None) -> None:
    """
    Enhanced URL loader with error handling and logging
    
    Args:
        url: URL string or URL object
        max_length: Optional max content length to display
    """
    from .url import URL  # Local import to avoid circular imports
    
    try:
        start_time = datetime.now()
        url_obj = URL(url) if isinstance(url, str) else url
        
        print(Fore.BLUE + f"\nLoading: {url_obj.original_url}" + Style.RESET_ALL)
        body = url_obj.request()
        
        show(body, max_length=max_length)
        
        load_time = (datetime.now() - start_time).total_seconds()
        print(Fore.MAGENTA + f"\nLoaded in {load_time:.2f} seconds" + Style.RESET_ALL)
        
    except Exception as e:
        print(Fore.RED + f"\nError loading {url}: {str(e)}" + Style.RESET_ALL)

def print_links(html: str) -> None:
    """Extract and print all links from HTML"""
    links = HTMLUtils.extract_links(html)
    if links:
        print(Fore.CYAN + "\nFound links:" + Style.RESET_ALL)
        for i, link in enumerate(links[:10], 1):  # Show first 10 links
            print(f"{i}. {link}")
    else:
        print(Fore.YELLOW + "No links found in content" + Style.RESET_ALL)