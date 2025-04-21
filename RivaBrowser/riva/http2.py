"""HTTP/2 protocol implementation for RivaBrowser.

This module provides HTTP/2 protocol support with features including:
- Connection establishment and management
- Request/response handling
- Stream management
- Connection pooling
- ALPN negotiation for HTTP/2

The implementation uses the h2 library for HTTP/2 protocol handling and supports
both secure (HTTPS) and insecure (HTTP) connections.

Example:
    ```python
    conn = HTTP2Connection("example.com", 443)
    if conn.connect():
        stream_id = conn.send_request("GET", "/", {"user-agent": "RivaBrowser"})
        if stream_id:
            _, response = conn.receive_response()
            print(response)
        conn.close()
    ```

Note:
    This implementation requires the h2 package and supports HTTP/2 over TLS only.
"""

import socket
import ssl
import h2.connection
import h2.events
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass
from contextlib import contextmanager
import logging

class HTTP2Error(Exception):
    """Base exception class for HTTP/2 related errors."""
    pass

class HTTP2ConnectionError(HTTP2Error):
    """Raised when connection establishment fails."""
    pass

class HTTP2RequestError(HTTP2Error):
    """Raised when sending a request fails."""
    pass

class HTTP2ResponseError(HTTP2Error):
    """Raised when receiving a response fails."""
    pass

@dataclass
class HTTP2Response:
    """Container for HTTP/2 response data."""
    stream_id: int
    headers: Dict[str, str]
    data: bytes
    end_stream: bool

class HTTP2Connection:
    """HTTP/2 connection handler.
    
    This class manages HTTP/2 connections, including:
    - Connection establishment with ALPN negotiation
    - Request/response handling
    - Stream management
    - Connection cleanup
    
    Attributes:
        host (str): The target hostname
        port (int): The target port
        conn (Optional[ssl.SSLSocket]): The underlying socket connection
        h2_conn (Optional[h2.connection.H2Connection]): The HTTP/2 connection
        stream_id (Optional[int]): The current stream ID
        logger (logging.Logger): Logger instance for this connection
    """

    def __init__(self, host: str, port: int) -> None:
        """Initialize HTTP/2 connection handler.
        
        Args:
            host: The target hostname
            port: The target port
            
        Raises:
            ValueError: If host is empty or port is invalid
        """
        if not host:
            raise ValueError("Host cannot be empty")
        if not 0 <= port <= 65535:
            raise ValueError("Port must be between 0 and 65535")
            
        self.host: str = host
        self.port: int = port
        self.conn: Optional[ssl.SSLSocket] = None
        self.h2_conn: Optional[h2.connection.H2Connection] = None
        self.stream_id: Optional[int] = None
        self.logger: logging.Logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Establish HTTP/2 connection with ALPN negotiation.
        
        Returns:
            bool: True if connection was established successfully
            
        Raises:
            HTTP2ConnectionError: If connection establishment fails
        """
        try:
            # Create socket with timeout
            sock = socket.create_connection((self.host, self.port), timeout=30)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # Wrap with SSL and negotiate ALPN
            context = ssl.create_default_context()
            context.set_alpn_protocols(['h2'])
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            self.conn = context.wrap_socket(sock, server_hostname=self.host)
            
            # Verify ALPN negotiation
            if self.conn.selected_alpn_protocol() != 'h2':
                raise HTTP2ConnectionError("Server does not support HTTP/2")
            
            # Initialize HTTP/2 connection
            self.h2_conn = h2.connection.H2Connection()
            self.h2_conn.initiate_connection()
            self.conn.send(self.h2_conn.data_to_send())
            
            return True
        except ssl.SSLError as e:
            raise HTTP2ConnectionError(f"SSL error: {str(e)}") from e
        except socket.error as e:
            raise HTTP2ConnectionError(f"Socket error: {str(e)}") from e
        except Exception as e:
            raise HTTP2ConnectionError(f"Connection failed: {str(e)}") from e

    @contextmanager
    def _ensure_connection(self) -> None:
        """Context manager to ensure connection is established.
        
        Yields:
            None
            
        Raises:
            HTTP2ConnectionError: If connection cannot be established
        """
        if not self.h2_conn or not self.conn:
            if not self.connect():
                raise HTTP2ConnectionError("Failed to establish connection")
        try:
            yield
        except Exception as e:
            if not isinstance(e, HTTP2Error):
                raise HTTP2ConnectionError(f"Connection error: {str(e)}") from e
            raise

    def send_request(self, method: str, path: str, headers: Dict[str, str]) -> Optional[int]:
        """Send HTTP/2 request and return stream ID.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            headers: Additional headers to send
            
        Returns:
            Optional[int]: Stream ID if request was sent successfully, None otherwise
            
        Raises:
            HTTP2RequestError: If request sending fails
        """
        try:
            with self._ensure_connection():
                # Validate input
                if not method or not path:
                    raise HTTP2RequestError("Method and path are required")
                
                # Prepare headers
                request_headers = [
                    (':method', method.upper()),
                    (':path', path),
                    (':authority', self.host),
                    (':scheme', 'https'),
                ]
                
                # Add custom headers
                for key, value in headers.items():
                    if not key.startswith(':'):  # Don't allow pseudo-headers
                        request_headers.append((key.lower(), value))

                # Get stream ID and send request
                self.stream_id = self.h2_conn.get_next_available_stream_id()
                self.h2_conn.send_headers(self.stream_id, request_headers)
                self.conn.send(self.h2_conn.data_to_send())
                
                return self.stream_id
        except Exception as e:
            if not isinstance(e, HTTP2Error):
                raise HTTP2RequestError(f"Request failed: {str(e)}") from e
            raise

    def receive_response(self) -> Tuple[Optional[int], Optional[bytes]]:
        """Receive HTTP/2 response.
        
        Returns:
            Tuple[Optional[int], Optional[bytes]]: Stream ID and response data
            
        Raises:
            HTTP2ResponseError: If response receiving fails
        """
        try:
            with self._ensure_connection():
                if not self.stream_id:
                    raise HTTP2ResponseError("No active stream")

                data = self.conn.recv(65535)
                if not data:
                    return None, None
                    
                events = self.h2_conn.receive_data(data)
                
                for event in events:
                    if isinstance(event, h2.events.DataReceived):
                        self.h2_conn.acknowledge_received_data(
                            len(event.data),
                            event.stream_id
                        )
                        return event.stream_id, event.data
                    elif isinstance(event, h2.events.StreamEnded):
                        return event.stream_id, None
                    elif isinstance(event, h2.events.StreamReset):
                        raise HTTP2ResponseError(f"Stream {event.stream_id} was reset")

                return self.stream_id, None
        except Exception as e:
            if not isinstance(e, HTTP2Error):
                raise HTTP2ResponseError(f"Response error: {str(e)}") from e
            raise

    def close(self) -> None:
        """Close HTTP/2 connection gracefully.
        
        Raises:
            HTTP2Error: If connection closing fails
        """
        try:
            if self.h2_conn:
                self.h2_conn.close_connection()
            if self.conn:
                self.conn.send(self.h2_conn.data_to_send())
            self.conn.close()
        except Exception as e:
            raise HTTP2Error(f"Error closing connection: {str(e)}") from e
        finally:
            self.conn = None
            self.h2_conn = None
            self.stream_id = None 