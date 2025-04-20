"""Tests for HTTP/2 protocol implementation.

This module contains unit tests for the HTTP/2 protocol implementation,
including connection handling, request/response processing, and error cases.
"""

import unittest
import socket
import ssl
from unittest.mock import patch, MagicMock
from riva.http2 import HTTP2Connection, HTTP2Error, HTTP2ConnectionError, HTTP2RequestError, HTTP2ResponseError
from riva.cache import ConnectionCache

class TestHTTP2Connection(unittest.TestCase):
    """Test suite for HTTP2Connection class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.host = "example.com"
        self.port = 443
        self.conn = HTTP2Connection(self.host, self.port)

    def test_init_invalid_host(self) -> None:
        """Test initialization with invalid host."""
        with self.assertRaises(ValueError):
            HTTP2Connection("", 443)

    def test_init_invalid_port(self) -> None:
        """Test initialization with invalid port."""
        with self.assertRaises(ValueError):
            HTTP2Connection("example.com", -1)
        with self.assertRaises(ValueError):
            HTTP2Connection("example.com", 65536)

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_connect_success(self, mock_ssl_context: MagicMock, mock_create_connection: MagicMock) -> None:
        """Test successful connection establishment."""
        # Mock SSL context and socket
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.selected_alpn_protocol.return_value = 'h2'
        mock_ssl_context.return_value.wrap_socket.return_value = mock_ssl_socket
        
        # Test connection
        result = self.conn.connect()
        
        self.assertTrue(result)
        self.assertEqual(self.conn.conn, mock_ssl_socket)
        self.assertIsNotNone(self.conn.h2_conn)
        
        # Verify SSL context configuration
        mock_ssl_context.return_value.set_alpn_protocols.assert_called_with(['h2'])
        mock_ssl_context.return_value.check_hostname = True
        mock_ssl_context.return_value.verify_mode = ssl.CERT_REQUIRED
        
        # Verify socket configuration
        mock_create_connection.assert_called_with((self.host, self.port), timeout=30)
        mock_socket.setsockopt.assert_called_with(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    @patch('socket.create_connection')
    def test_connect_failure(self, mock_create_connection: MagicMock) -> None:
        """Test connection failure."""
        mock_create_connection.side_effect = socket.error("Connection failed")
        
        with self.assertRaises(HTTP2ConnectionError):
            self.conn.connect()

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_connect_no_http2(self, mock_ssl_context: MagicMock, mock_create_connection: MagicMock) -> None:
        """Test connection to non-HTTP/2 server."""
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.selected_alpn_protocol.return_value = 'http/1.1'
        mock_ssl_context.return_value.wrap_socket.return_value = mock_ssl_socket
        
        with self.assertRaises(HTTP2ConnectionError):
            self.conn.connect()

    @patch('riva.http2.HTTP2Connection.connect')
    def test_send_request(self, mock_connect: MagicMock) -> None:
        """Test sending HTTP/2 request."""
        # Setup mock connection
        self.conn.h2_conn = MagicMock()
        self.conn.conn = MagicMock()
        self.conn.h2_conn.get_next_available_stream_id.return_value = 1
        
        # Test request
        stream_id = self.conn.send_request(
            "GET",
            "/test",
            {"user-agent": "test-agent"}
        )
        
        self.assertEqual(stream_id, 1)
        self.conn.h2_conn.send_headers.assert_called_once()
        self.conn.conn.send.assert_called_once()

    def test_send_request_invalid_input(self) -> None:
        """Test sending request with invalid input."""
        with self.assertRaises(HTTP2RequestError):
            self.conn.send_request("", "/test", {})
        with self.assertRaises(HTTP2RequestError):
            self.conn.send_request("GET", "", {})

    @patch('riva.http2.HTTP2Connection.connect')
    def test_send_request_pseudo_headers(self, mock_connect: MagicMock) -> None:
        """Test sending request with pseudo-headers."""
        self.conn.h2_conn = MagicMock()
        self.conn.conn = MagicMock()
        self.conn.h2_conn.get_next_available_stream_id.return_value = 1
        
        stream_id = self.conn.send_request(
            "GET",
            "/test",
            {":custom": "value"}  # Should be ignored
        )
        
        self.assertEqual(stream_id, 1)
        # Verify pseudo-header was not added
        for header in self.conn.h2_conn.send_headers.call_args[0][1]:
            self.assertFalse(header[0].startswith(':'))

    @patch('riva.http2.HTTP2Connection.connect')
    def test_receive_response(self, mock_connect: MagicMock) -> None:
        """Test receiving HTTP/2 response."""
        # Setup mock connection
        self.conn.h2_conn = MagicMock()
        self.conn.stream_id = 1
        self.conn.conn = MagicMock()
        
        # Mock response data
        mock_data = b"test data"
        self.conn.conn.recv.return_value = mock_data
        
        # Mock H2 events
        mock_event = MagicMock()
        mock_event.stream_id = 1
        mock_event.data = mock_data
        self.conn.h2_conn.receive_data.return_value = [mock_event]
        
        # Test response
        stream_id, data = self.conn.receive_response()
        
        self.assertEqual(stream_id, 1)
        self.assertEqual(data, mock_data)
        self.conn.h2_conn.acknowledge_received_data.assert_called_once()

    @patch('riva.http2.HTTP2Connection.connect')
    def test_receive_response_stream_reset(self, mock_connect: MagicMock) -> None:
        """Test receiving stream reset."""
        self.conn.h2_conn = MagicMock()
        self.conn.stream_id = 1
        self.conn.conn = MagicMock()
        
        # Mock stream reset event
        mock_event = MagicMock()
        mock_event.stream_id = 1
        self.conn.h2_conn.receive_data.return_value = [mock_event]
        
        with self.assertRaises(HTTP2ResponseError):
            self.conn.receive_response()

    def test_receive_response_no_stream(self) -> None:
        """Test receiving response without active stream."""
        with self.assertRaises(HTTP2ResponseError):
            self.conn.receive_response()

    @patch('riva.http2.HTTP2Connection.connect')
    def test_close(self, mock_connect: MagicMock) -> None:
        """Test closing connection."""
        # Setup mock connection
        self.conn.h2_conn = MagicMock()
        self.conn.conn = MagicMock()
        
        # Test close
        self.conn.close()
        
        self.conn.h2_conn.close_connection.assert_called_once()
        self.conn.conn.close.assert_called_once()
        self.assertIsNone(self.conn.conn)
        self.assertIsNone(self.conn.h2_conn)
        self.assertIsNone(self.conn.stream_id)

class TestHTTP2Cache(unittest.TestCase):
    """Test suite for HTTP/2 connection caching."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cache = ConnectionCache(enable_http2=True)

    def test_store_http2_connection(self) -> None:
        """Test storing HTTP/2 connection in cache."""
        conn = HTTP2Connection("example.com", 443)
        conn.h2_conn = MagicMock()
        
        result = self.cache.store("example.com", 443, "https", conn)
        
        self.assertTrue(result)
        self.assertEqual(len(self.cache.cache), 1)

    def test_get_http2_connection(self) -> None:
        """Test retrieving HTTP/2 connection from cache."""
        # Store connection
        conn = HTTP2Connection("example.com", 443)
        conn.h2_conn = MagicMock()
        self.cache.store("example.com", 443, "https", conn)
        
        # Get connection
        cached_conn = self.cache.get("example.com", 443, "https")
        
        self.assertEqual(cached_conn, conn)

    def test_remove_http2_connection(self) -> None:
        """Test removing HTTP/2 connection from cache."""
        # Store connection
        conn = HTTP2Connection("example.com", 443)
        conn.h2_conn = MagicMock()
        conn.close = MagicMock()
        self.cache.store("example.com", 443, "https", conn)
        
        # Remove connection
        self.cache._remove_connection(("example.com", 443, "https"))
        
        self.assertEqual(len(self.cache.cache), 0)
        conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main() 