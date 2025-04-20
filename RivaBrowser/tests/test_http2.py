import unittest
import socket
import ssl
from unittest.mock import patch, MagicMock
from riva.http2 import HTTP2Connection
from riva.cache import ConnectionCache

class TestHTTP2Connection(unittest.TestCase):
    def setUp(self):
        self.host = "example.com"
        self.port = 443
        self.conn = HTTP2Connection(self.host, self.port)

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_connect_success(self, mock_ssl_context, mock_create_connection):
        # Mock SSL context and socket
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        mock_ssl_socket = MagicMock()
        mock_ssl_context.return_value.wrap_socket.return_value = mock_ssl_socket
        
        # Test connection
        result = self.conn.connect()
        
        self.assertTrue(result)
        self.assertEqual(self.conn.conn, mock_ssl_socket)
        self.assertIsNotNone(self.conn.h2_conn)
        
        # Verify SSL context configuration
        mock_ssl_context.return_value.set_alpn_protocols.assert_called_with(['h2'])
        
        # Verify socket configuration
        mock_create_connection.assert_called_with((self.host, self.port))
        mock_ssl_context.return_value.wrap_socket.assert_called_with(
            mock_socket, server_hostname=self.host
        )

    @patch('socket.create_connection')
    def test_connect_failure(self, mock_create_connection):
        mock_create_connection.side_effect = socket.error("Connection failed")
        
        result = self.conn.connect()
        
        self.assertFalse(result)
        self.assertIsNone(self.conn.conn)
        self.assertIsNone(self.conn.h2_conn)

    @patch('riva.http2.HTTP2Connection.connect')
    def test_send_request(self, mock_connect):
        # Setup mock connection
        self.conn.h2_conn = MagicMock()
        self.conn.conn = MagicMock()  # Add mock for the socket connection
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

    @patch('riva.http2.HTTP2Connection.connect')
    def test_send_request_no_connection(self, mock_connect):
        mock_connect.return_value = False  # Имитируем неудачное подключение
        stream_id = self.conn.send_request("GET", "/test", {})
        self.assertIsNone(stream_id)
        mock_connect.assert_called_once()

    @patch('riva.http2.HTTP2Connection.connect')
    def test_receive_response(self, mock_connect):
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

    def test_receive_response_no_connection(self):
        stream_id, data = self.conn.receive_response()
        self.assertIsNone(stream_id)
        self.assertIsNone(data)

    @patch('riva.http2.HTTP2Connection.connect')
    def test_close(self, mock_connect):
        # Setup mock connection
        self.conn.h2_conn = MagicMock()
        self.conn.conn = MagicMock()
        
        # Test close
        self.conn.close()
        
        self.conn.h2_conn.close_connection.assert_called_once()
        self.conn.conn.close.assert_called_once()

class TestHTTP2Cache(unittest.TestCase):
    def setUp(self):
        self.cache = ConnectionCache(enable_http2=True)

    def test_store_http2_connection(self):
        conn = HTTP2Connection("example.com", 443)
        conn.h2_conn = MagicMock()
        
        result = self.cache.store("example.com", 443, "https", conn)
        
        self.assertTrue(result)
        self.assertEqual(len(self.cache.cache), 1)

    def test_get_http2_connection(self):
        # Store connection
        conn = HTTP2Connection("example.com", 443)
        conn.h2_conn = MagicMock()
        self.cache.store("example.com", 443, "https", conn)
        
        # Get connection
        cached_conn = self.cache.get("example.com", 443, "https")
        
        self.assertEqual(cached_conn, conn)

    def test_remove_http2_connection(self):
        # Store connection
        conn = HTTP2Connection("example.com", 443)
        conn.h2_conn = MagicMock()
        conn.close = MagicMock()  # Создаем mock для метода close
        self.cache.store("example.com", 443, "https", conn)
        
        # Remove connection
        self.cache._remove_connection(("example.com", 443, "https"))
        
        self.assertEqual(len(self.cache.cache), 0)
        conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main() 