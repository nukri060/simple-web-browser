"""URL handling module for RivaBrowser.

This module provides URL parsing, validation, and request handling functionality for various URL schemes:
- HTTP/HTTPS: Handles web requests with proper header handling and connection pooling
- File: Local file system access with proper error handling
- Data: In-line data URL handling
- View-source: Source code viewing capability for any supported URL type

The module implements connection pooling and reuse for HTTP(S) connections, proper SSL/TLS
handling for HTTPS, and comprehensive error handling for all operations.

Example:
    ```python
    url = URL("https://example.com")
    content = url.request()
    print(content)
    ```

Note:
    All network operations are handled synchronously. For async support, consider using
    the async version of this module (if available).
"""

import socket
import ssl
from urllib.parse import urlparse
from typing import Optional, Dict, Union, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import base64
import logging
from colorama import Fore
from datetime import datetime
from .cache import connection_cache

# Type aliases
SocketType = Union[socket.socket, ssl.SSLSocket]
HeadersType = Dict[str, str]

@dataclass
class HTTPResponse:
    """Container for HTTP response data."""
    status_code: int
    status_message: str
    headers: HeadersType
    body: str
    http_version: str

class URLError(Exception):
    """Base exception class for URL-related errors."""
    pass

class URLParseError(URLError):
    """Raised when URL parsing fails."""
    pass

class URLRequestError(URLError):
    """Raised when making a request fails."""
    pass

class URL:
    """Main URL handling class supporting multiple URL schemes.
    
    This class handles URL parsing, validation, and content retrieval for various
    URL schemes including HTTP(S), file, data, and view-source URLs.
    
    Attributes:
        SCHEME_PORTS (Dict[str, Optional[int]]): Mapping of schemes to their default ports
        original_url (str): The original URL string provided
        scheme (Optional[str]): The URL scheme (http, https, file, etc.)
        host (Optional[str]): The hostname for network URLs
        port (Optional[int]): The port number for network URLs
        path (Optional[str]): The path component of the URL
        inner_url (Optional[URL]): For view-source URLs, the wrapped URL object
        user_agent (str): The User-Agent string to use for HTTP(S) requests
    """

    SCHEME_PORTS: Dict[str, Optional[int]] = {
        'http': 80,
        'https': 443,
        'file': None,
        'data': None,
        'view-source': None
    }

    def __init__(self, url: str, user_agent: Optional[str] = None) -> None:
        """Initialize a URL object.
        
        Args:
            url: The URL string to parse and handle
            user_agent: Optional User-Agent string for HTTP(S) requests
        
        Raises:
            URLParseError: If the URL cannot be parsed
            ValueError: If the URL is invalid
        """
        self.original_url: str = url
        self.scheme: Optional[str] = None
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.path: Optional[str] = None
        self.inner_url: Optional['URL'] = None
        self.user_agent: str = user_agent or "RivaBrowser/1.0"
        self._parse_url(url)

    def _parse_url(self, url: str) -> None:
        """Parse and validate the URL, setting up internal state.
        
        This is the main URL parsing dispatcher that handles different URL schemes
        and formats, including special cases like view-source and Windows paths.
        
        Args:
            url: The URL string to parse
            
        Raises:
            URLParseError: If the URL format is invalid or unsupported
            ValueError: If the URL is too short or malformed
        """
        if not url or len(url) < 3:
            raise URLParseError("URL too short")
            
        try:
            if url.startswith("view-source:"):
                self._handle_view_source(url)
            elif url.startswith("data:text/html,"):
                self._handle_data(url)
            elif self._is_windows_path(url):
                self._handle_file(url)
            else:
                if "://" not in url and not self._is_windows_path(url):
                    raise URLParseError("Invalid URL format: missing scheme")
                self._handle_generic(url)
        except Exception as e:
            raise URLParseError(f"Failed to parse URL: {str(e)}") from e

    def _handle_view_source(self, url: str) -> None:
        """Process view-source URLs by creating an inner URL object.
        
        Args:
            url: The view-source URL to process
            
        Raises:
            URLParseError: If the inner URL is invalid
        """
        self.scheme = "view-source"
        inner_url = url[12:]  # Remove "view-source:" prefix
        try:
            self.inner_url = URL(inner_url)
        except Exception as e:
            raise URLParseError(f"Invalid view-source inner URL: {str(e)}") from e

    def _handle_data(self, url: str) -> None:
        """Process data URLs containing inline HTML content.
        
        Args:
            url: The data URL to process
            
        Raises:
            URLParseError: If the data URL format is invalid
        """
        self.scheme = "data"
        try:
            self.path = url.split(",", 1)[1]
        except IndexError as e:
            raise URLParseError("Invalid data URL format") from e

    def _handle_file(self, url: str) -> None:
        """Process file URLs and local file paths.
        
        Handles both file:// URLs and direct file paths, including Windows paths.
        
        Args:
            url: The file URL or path to process
        """
        self.scheme = "file"
        if url.startswith("file://"):
            self.path = url[7:]  # Remove "file://" prefix
            # Normalize path by removing leading slashes
            while self.path.startswith('/'):
                self.path = self.path[1:]
        else:
            self.path = url

    def _handle_http(self, url: str) -> None:
        """Process HTTP/HTTPS URLs.
        
        Handles authentication, host/port parsing, and path extraction.
        
        Args:
            url: The URL string after the scheme:// prefix
            
        Raises:
            URLParseError: If the URL format is invalid
            ValueError: If the port number is invalid
        """
        try:
            if '@' in url:
                auth_part, rest = url.split('@', 1)
                self.auth = auth_part
                url = rest
            
            if len(url) < 3:
                raise URLParseError("URL too short")
            
            if '/' not in url:
                url += "/"
            parts = url.split("/", 1)
            self.host = parts[0]
            self.path = "/" + parts[1] if len(parts) > 1 else "/"

            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                try:
                    self.port = int(port)
                    if not 0 <= self.port <= 65535:
                        raise ValueError("Port number out of range")
                except ValueError as e:
                    raise URLParseError(f"Invalid port number: {port}") from e
            else:
                self.port = self.SCHEME_PORTS[self.scheme]
        except Exception as e:
            if not isinstance(e, URLParseError):
                raise URLParseError(f"Failed to parse HTTP URL: {str(e)}") from e
            raise

    def _handle_generic(self, url: str) -> None:
        """Handle URLs with explicit schemes.
        
        Args:
            url: The full URL to process
            
        Raises:
            URLParseError: If the scheme is unsupported or the URL format is invalid
        """
        try:
            if "://" in url:
                self.scheme, rest = url.split("://", 1)
                if self.scheme not in self.SCHEME_PORTS:
                    raise URLParseError(f"Unsupported scheme: {self.scheme}")
                
                if self.scheme in ("http", "https"):
                    self._handle_http(rest)
                elif self.scheme == "file":
                    self._handle_file(rest)
            else:
                self._handle_file(url)
        except Exception as e:
            if not isinstance(e, URLParseError):
                raise URLParseError(f"Failed to parse URL: {str(e)}") from e
            raise

    @staticmethod
    def _is_windows_path(url: str) -> bool:
        """Check if a URL string appears to be a Windows file path.
        
        Args:
            url: The URL string to check
            
        Returns:
            bool: True if the string appears to be a Windows path
        """
        return '\\' in url or (len(url) > 1 and url[1] == ':')
    
    def request(self) -> str:
        """Make a request to retrieve the content of this URL.
        
        Returns:
            str: The content of the URL
            
        Raises:
            URLRequestError: If the request fails
        """
        try:
            if self.scheme == "view-source":
                return self._request_view_source()
            elif self.scheme in ["http", "https"]:
                return self._request_http()
            elif self.scheme == "file":
                return self._request_file()
            elif self.scheme == "data":
                return self._request_data()
            else:
                raise URLRequestError(f"Unsupported scheme: {self.scheme}")
        except Exception as e:
            if not isinstance(e, URLRequestError):
                raise URLRequestError(f"Request failed: {str(e)}") from e
            raise
    
    def _request_view_source(self) -> str:
        """Request the source view of a URL.
        
        Returns:
            str: The source view of the URL content
            
        Raises:
            URLRequestError: If the request fails
        """
        try:
            if self.inner_url.scheme in ["http", "https"]:
                return self.inner_url._request_http(source_mode=True)
            elif self.inner_url.scheme == "file":
                return self.inner_url._request_file()
            elif self.inner_url.scheme == "data":
                return self.inner_url._request_data()
            else:
                raise URLRequestError(f"Unsupported inner scheme: {self.inner_url.scheme}")
        except Exception as e:
            raise URLRequestError(f"View-source request failed: {str(e)}") from e
    
    @contextmanager
    def _get_connection(self) -> SocketType:
        """Get a connection from the cache or create a new one.
        
        Yields:
            socket.socket: The socket connection to use
            
        Raises:
            URLRequestError: If connection fails
        """
        sock = None
        try:
            sock = connection_cache.get(self.host, self.port, self.scheme)
            
            if sock is None:
                sock = socket.socket(
                    family=socket.AF_INET,
                    type=socket.SOCK_STREAM,
                    proto=socket.IPPROTO_TCP
                )
                sock.settimeout(30)  # 30 second timeout
                sock.connect((self.host, self.port))
                
                if self.scheme == "https":
                    ctx = ssl.create_default_context()
                    sock = ctx.wrap_socket(sock, server_hostname=self.host)
            
            yield sock
            
        except Exception as e:
            if sock:
                sock.close()
            raise URLRequestError(f"Connection failed: {str(e)}") from e
    
    def _request_http(self, source_mode: bool = False) -> str:
        """Make an HTTP(S) request.
        
        Args:
            source_mode: Whether to return the raw HTTP response
            
        Returns:
            str: The response content or raw HTTP response
            
        Raises:
            URLRequestError: If the request fails
        """
        with self._get_connection() as sock:
            try:
                # Prepare headers
                auth_header = ""
                if hasattr(self, 'auth'):
                    auth_header = f"Authorization: Basic {base64.b64encode(self.auth.encode()).decode()}\r\n"

                request = f"GET {self.path} HTTP/1.1\r\n"
                request += f"Host: {self.host}\r\n"
                request += "Connection: keep-alive\r\n"
                request += f"User-Agent: {self.user_agent}\r\n"
                request += auth_header
                request += "\r\n"
                
                # Send request
                sock.send(request.encode("utf8"))
                
                # Parse response
                response = sock.makefile("rb", newline="\r\n")
                statusline = response.readline().decode('utf-8')
                
                try:
                    version, status, explanation = statusline.split(" ", 2)
                    status_code = int(status)
                    if status_code >= 400:
                        msg = f"HTTP Error {status}: {explanation.strip()}"
                        logging.error(msg)
                        print(Fore.RED + msg)
                        if status_code >= 500:
                            raise URLRequestError(msg)
                except ValueError as e:
                    raise URLRequestError(f"Invalid HTTP status line: {statusline}") from e

                # Parse headers
                headers: HeadersType = {}
                content_length = None
                connection_close = False
                
                while True:
                    line = response.readline().decode('utf-8')
                    if line == "\r\n":
                        break
                    try:
                        header, value = line.split(":", 1)
                        header = header.casefold()
                        value = value.strip()
                        headers[header] = value
                        
                        if header == "content-length":
                            content_length = int(value)
                        elif header == "connection" and value.lower() == "close":
                            connection_close = True
                    except ValueError as e:
                        logging.warning(f"Invalid header line: {line}")
                        continue

                # Read body
                try:
                    if content_length is not None:
                        body = response.read(content_length).decode('utf-8', errors='replace')
                    else:
                        body = response.read().decode('utf-8', errors='replace')
                        connection_close = True
                except Exception as e:
                    raise URLRequestError(f"Failed to read response body: {str(e)}") from e

                # Create response object
                http_response = HTTPResponse(
                    status_code=status_code,
                    status_message=explanation.strip(),
                    headers=headers,
                    body=body,
                    http_version=version
                )

                # Handle connection
                if connection_close:
                    sock.close()
                else:
                    connection_cache.store(self.host, self.port, self.scheme, sock)

                # Return appropriate format
                if source_mode:
                    return f"{statusline}{''.join(f'{k}: {v}\r\n' for k, v in headers.items())}\r\n{body}"
                return body

            except Exception as e:
                sock.close()
                if not isinstance(e, URLRequestError):
                    raise URLRequestError(f"HTTP request failed: {str(e)}") from e
                raise
    
    def _request_file(self) -> str:
        """Read content from a local file.
        
        Returns:
            str: The file content
            
        Raises:
            URLRequestError: If file access fails
        """
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise URLRequestError(f"File not found: {self.path}") from e
        except IsADirectoryError as e:
            raise URLRequestError(f"Path is a directory: {self.path}") from e
        except PermissionError as e:
            raise URLRequestError(f"Permission denied: {self.path}") from e
        except UnicodeDecodeError:
            try:
                with open(self.path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise URLRequestError(f"Error reading file: {str(e)}") from e
        except Exception as e:
            raise URLRequestError(f"File access error: {str(e)}") from e

    def _request_data(self) -> str:
        """Process a data URL.
        
        Returns:
            str: The decoded content
            
        Raises:
            URLRequestError: If the data URL is invalid
        """
        try:
            if self.path.startswith("text/html,"):
                return self.path[len("text/html,"):]
            return self.path
        except Exception as e:
            raise URLRequestError(f"Failed to process data URL: {str(e)}") from e