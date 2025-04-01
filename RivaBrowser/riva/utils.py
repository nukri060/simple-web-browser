import re
from html import unescape
from typing import Union, Optional, List
from textwrap import shorten
from datetime import datetime
import colorama
from colorama import Fore, Style
import logging

# Initialize colorama
colorama.init()

class HTMLUtils:
    @staticmethod
    def strip_scripts(html: str) -> str:
        """Remove script and style tags from HTML"""
        html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        return html

    @staticmethod
    def extract_links(html: str) -> List[str]:
        """Extract all href links from HTML with validation"""
        raw_links = re.findall(r'href=[\'"]?([^\'" >]+)', html, flags=re.IGNORECASE)
        return [
            link for link in raw_links 
            if link and not link.startswith(('#', 'javascript:', 'mailto:'))
        ]

def show(body: Union[str, bytes], max_length: Optional[int] = None) -> None:
    """Enhanced content display with error handling and formatting"""
    if isinstance(body, bytes):
        try:
            body = body.decode('utf-8')
        except UnicodeDecodeError:
            try:
                body = body.decode('latin-1')
            except Exception as e:
                logging.error(f"Decoding failed: {e}")
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
        logging.error(f"Content rendering failed: {e}")
        print(Fore.RED + f"Error rendering content: {str(e)}" + Style.RESET_ALL)
        print(Fore.CYAN + "Raw content preview:" + Style.RESET_ALL)
        print(body[:1000] + ("..." if len(body) > 1000 else ""))

def load(url: Union[str, 'URL'], max_length: Optional[int] = None) -> None:
    """Enhanced URL loader with error handling"""
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
        logging.error(f"Failed to load {url}: {e}")
        print(Fore.RED + f"\nError loading {url}: {str(e)}" + Style.RESET_ALL)

def print_links(html: str) -> None:
    """Extract and print all valid links from HTML"""
    links = HTMLUtils.extract_links(html)
    if links:
        print(Fore.CYAN + "\nFound links:" + Style.RESET_ALL)
        for i, link in enumerate(links[:15], 1):
            print(f"{i}. {link}")
    else:
        print(Fore.YELLOW + "No valid links found in content" + Style.RESET_ALL)