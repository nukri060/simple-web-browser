import unittest
from unittest.mock import patch, MagicMock
from riva.cache import ConnectionCache
import time
import socket

class TestConnectionCache(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.cache = ConnectionCache(
            timeout=1.0,
            max_pool_size=2,
            enable_metrics=True
        )
        self.test_socket = MagicMock(spec=socket.socket)

    def test_cache_initialization(self):
        """Test cache initialization"""
        self.assertEqual(self.cache.timeout, 1.0)
        self.assertEqual(self.cache.max_pool_size, 2)
        self.assertTrue(self.cache.enable_metrics)

    def test_get_new_connection(self):
        """Test getting new connection"""
        host = "example.com"
        port = 80
        scheme = "http"
        connection = self.cache.get(host, port, scheme)
        self.assertIsNone(connection)  # Should return None for new connection

    def test_store_and_get_connection(self):
        """Test storing and getting connection"""
        host = "example.com"
        port = 80
        scheme = "http"
        
        # Store connection
        self.cache.store(host, port, scheme, self.test_socket)
        
        # Get connection
        connection = self.cache.get(host, port, scheme)
        self.assertEqual(connection, self.test_socket)

    def test_connection_timeout(self):
        """Test connection timeout"""
        host = "example.com"
        port = 80
        scheme = "http"
        
        self.cache.store(host, port, scheme, self.test_socket)
        time.sleep(1.1)  # Wait for timeout
        connection = self.cache.get(host, port, scheme)
        self.assertIsNone(connection)

    def test_max_pool_size(self):
        """Test maximum pool size"""
        # Store connections up to max_pool_size
        for i in range(3):
            host = f"example{i}.com"
            self.cache.store(host, 80, "http", self.test_socket)
        
        # Check if oldest connection was evicted
        self.assertEqual(len(self.cache.cache), 2)

    def test_get_stats(self):
        """Test getting statistics"""
        host = "example.com"
        port = 80
        scheme = "http"
        
        # Make some requests
        self.cache.get(host, port, scheme)  # miss
        self.cache.store(host, port, scheme, self.test_socket)
        self.cache.get(host, port, scheme)  # hit
        self.cache.get(host, port, scheme)  # hit

        stats = self.cache.get_metrics()
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)

    def test_close_all(self):
        """Test closing all connections"""
        host1 = "example1.com"
        host2 = "example2.com"
        port = 80
        scheme = "http"

        self.cache.store(host1, port, scheme, self.test_socket)
        self.cache.store(host2, port, scheme, self.test_socket)

        self.cache.close_all()
        self.assertEqual(len(self.cache.cache), 0)

    def test_metrics_disabled(self):
        """Test behavior when metrics are disabled"""
        cache = ConnectionCache(enable_metrics=False)
        host = "example.com"
        port = 80
        scheme = "http"

        cache.get(host, port, scheme)
        cache.store(host, port, scheme, self.test_socket)
        cache.get(host, port, scheme)

        stats = cache.get_metrics()
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)

if __name__ == '__main__':
    unittest.main() 