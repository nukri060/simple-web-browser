import unittest
from unittest.mock import patch, MagicMock
from riva.url import URL
import socket
import ssl

class TestURL(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.test_url = "https://example.com"
        self.url_obj = URL(self.test_url)

    def test_url_initialization(self):
        """Test URL object initialization"""
        self.assertEqual(self.url_obj.original_url, self.test_url)
        self.assertEqual(self.url_obj.user_agent, "RivaBrowser/1.0")
        self.assertEqual(self.url_obj.scheme, "https")
        self.assertEqual(self.url_obj.host, "example.com")
        self.assertEqual(self.url_obj.port, 443)
        self.assertEqual(self.url_obj.path, "/")

    def test_custom_user_agent(self):
        """Test URL initialization with custom user agent"""
        custom_agent = "CustomAgent/1.0"
        url = URL(self.test_url, user_agent=custom_agent)
        self.assertEqual(url.user_agent, custom_agent)

    @patch('socket.socket')
    @patch('ssl.create_default_context')
    def test_request_success(self, mock_ssl_context, mock_socket):
        """Test successful request"""
        # Configuring a regular socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Configuring SSL context and socket
        mock_ssl_context_instance = MagicMock()
        mock_ssl_context.return_value = mock_ssl_context_instance
        mock_ssl_socket = MagicMock()
        mock_ssl_context_instance.wrap_socket.return_value = mock_ssl_socket
        
        # Creating a moc for a file object
        mock_file = MagicMock()
        mock_file.readline.side_effect = [
            b"HTTP/1.1 200 OK\r\n",
            b"Content-Type: text/html\r\n",
            b"Content-Length: 24\r\n",
            b"\r\n"
        ]
        mock_file.read.return_value = b"<html>Test content</html>"
        
        # Customize the makefile to return our moc file
        mock_ssl_socket.makefile.return_value = mock_file

        content = self.url_obj.request()
        self.assertEqual(content, "<html>Test content</html>")

    @patch('socket.socket')
    def test_request_failure(self, mock_socket):
        """Test request failure"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = socket.error("Connection error")

        with self.assertRaises(socket.error):
            self.url_obj.request()

    def test_invalid_url(self):
        """Test invalid URL handling"""
        invalid_urls = [
            "not-a-url",
            "://invalid.com",
            "http://",
            "ftp://example.com"  # Unsupported scheme
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    URL(url)

    def test_http_scheme(self):
        """Test HTTP scheme handling"""
        http_url = URL("http://example.com")
        self.assertEqual(http_url.scheme, "http")
        self.assertEqual(http_url.port, 80)

    def test_https_scheme(self):
        """Test HTTPS scheme handling"""
        https_url = URL("https://example.com")
        self.assertEqual(https_url.scheme, "https")
        self.assertEqual(https_url.port, 443)

    def test_file_scheme(self):
        """Test file scheme handling"""
        file_url = URL("file:///path/to/file")
        self.assertEqual(file_url.scheme, "file")
        self.assertEqual(file_url.path, "/path/to/file")

    def test_view_source_scheme(self):
        """Test view-source scheme handling"""
        view_source_url = URL("view-source:https://example.com")
        self.assertEqual(view_source_url.scheme, "view-source")
        self.assertIsNotNone(view_source_url.inner_url)
        self.assertEqual(view_source_url.inner_url.scheme, "https")

if __name__ == '__main__':
    unittest.main() 