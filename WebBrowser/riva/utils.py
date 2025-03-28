import re
from html import unescape
from typing import Union

def show(body: str) -> None:
    """
    Render response body with HTML entity decoding and basic tag stripping.
    Preserves special cases like HTTP responses and file operation messages.
    
    Args:
        body: Response content to display (HTTP response, HTML or plain text)
    """
    # Check for non-HTML responses that should be printed as-is
    if any(body.startswith(prefix) for prefix in (
        "HTTP/", "File not found", "Path is a directory",
        "Permission denied", "Error reading file"
    )):
        print(body)
        return
    
    # Decode HTML entities (faster and more complete than manual handling)
    decoded_body = unescape(body)
    
    # Basic HTML tag stripping while preserving content
    clean_body = re.sub(r'<[^>]*>', '', decoded_body)
    
    # Normalize whitespace and print
    normalized_body = ' '.join(clean_body.split())
    print(normalized_body)

def load(url: Union[str, 'URL']) -> None:
    """
    Load and display content from a URL object or URL string.
    Maintains compatibility with the existing URL class.
    
    Args:
        url: Either a URL object or string representation of URL
    """
    from .url import URL  # Local import to avoid circular dependencies
    
    try:
        # Handle both string URLs and URL objects
        url_obj = URL(url) if isinstance(url, str) else url
        body = url_obj.request()
        show(body)
    except Exception as e:
        print(f"Error loading URL: {str(e)}")