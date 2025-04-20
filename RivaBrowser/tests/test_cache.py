"""
Tests for the cache module.

This module contains tests for:
- Connection caching and reuse
- Connection lifecycle management
- Performance metrics collection
- Error handling and validation
- Thread safety
"""

import unittest
from unittest.mock import patch, MagicMock
from riva.cache import ConnectionCache, CacheMetrics, CacheError
import time
import socket
from riva.http2 import HTTP2Connection

class TestConnectionCache(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.cache = ConnectionCache(
            timeout=1.0,
            max_pool_size=2,
            enable_metrics=True
        )
        self.test_socket = MagicMock(spec=socket.socket)
        self.test_http2 = MagicMock(spec=HTTP2Connection)
        self.test_http2.h2_conn = MagicMock()
        self.test_http2.h2_conn.get_next_available_stream_id.return_value = 1

    def tearDown(self):
        """Clean up after tests"""
        self.cache.close_all()

    def test_cache_initialization(self):
        """Test cache initialization with valid parameters"""
        self.assertEqual(self.cache.timeout, 1.0)
        self.assertEqual(self.cache.max_pool_size, 2)
        self.assertTrue(self.cache.enable_metrics)
        self.assertIsInstance(self.cache.metrics, CacheMetrics)

    def test_cache_initialization_invalid(self):
        """Test cache initialization with invalid parameters"""
        with self.assertRaises(ValueError):
            ConnectionCache(timeout=0)
        with self.assertRaises(ValueError):
            ConnectionCache(max_pool_size=0)

    def test_get_new_connection(self):
        """Test getting new connection"""
        connection = self.cache.get("example.com", 80, "http")
        self.assertIsNone(connection)

    def test_get_invalid_parameters(self):
        """Test getting connection with invalid parameters"""
        with self.assertRaises(ValueError):
            self.cache.get("", 80, "http")
        with self.assertRaises(ValueError):
            self.cache.get("example.com", 0, "http")
        with self.assertRaises(ValueError):
            self.cache.get("example.com", 80, "ftp")

    def test_store_and_get_connection(self):
        """Test storing and getting connection"""
        self.cache.store("example.com", 80, "http", self.test_socket)
        connection = self.cache.get("example.com", 80, "http")
        self.assertEqual(connection, self.test_socket)
        self.assertEqual(self.cache.metrics.hits, 1)

    def test_store_invalid_connection(self):
        """Test storing invalid connection"""
        invalid_socket = MagicMock()
        invalid_socket.send.side_effect = socket.error
        result = self.cache.store("example.com", 80, "http", invalid_socket)
        self.assertFalse(result)
        self.assertEqual(self.cache.metrics.failed_connections, 1)

    def test_connection_timeout(self):
        """Test connection timeout"""
        self.cache.store("example.com", 80, "http", self.test_socket)
        time.sleep(1.1)
        connection = self.cache.get("example.com", 80, "http")
        self.assertIsNone(connection)
        self.assertEqual(self.cache.metrics.evictions, 1)

    def test_max_pool_size(self):
        """Test maximum pool size"""
        for i in range(3):
            host = f"example{i}.com"
            self.cache.store(host, 80, "http", self.test_socket)
        
        self.assertEqual(len(self.cache.cache), 2)
        self.assertEqual(self.cache.metrics.evictions, 1)

    def test_http2_connection(self):
        """Test HTTP/2 connection handling"""
        self.cache.store("example.com", 443, "https", self.test_http2)
        connection = self.cache.get("example.com", 443, "https")
        self.assertEqual(connection, self.test_http2)

    def test_unsupported_connection(self):
        """Test handling of unsupported connection type"""
        with self.assertRaises(CacheError):
            self.cache._is_connection_alive(MagicMock())

    def test_metrics_collection(self):
        """Test metrics collection"""
        # Make some requests
        self.cache.get("example.com", 80, "http")  # miss
        self.cache.store("example.com", 80, "http", self.test_socket)
        self.cache.get("example.com", 80, "http")  # hit
        self.cache.get("example.com", 80, "http")  # hit

        metrics = self.cache.get_metrics()
        self.assertEqual(metrics['hits'], 2)
        self.assertEqual(metrics['misses'], 1)
        self.assertEqual(metrics['total_connections'], 1)
        self.assertEqual(metrics['size'], 1)

    def test_connection_lifetime(self):
        """Test connection lifetime tracking"""
        self.cache.store("example.com", 80, "http", self.test_socket)
        time.sleep(0.5)
        self.cache._remove_connection(("example.com", 80, "http"))
        
        metrics = self.cache.get_metrics()
        self.assertGreater(metrics['avg_connection_lifetime'], 0)

    def test_thread_safety(self):
        """Test thread safety of cache operations"""
        import threading
        
        def worker():
            for _ in range(100):
                self.cache.store("example.com", 80, "http", self.test_socket)
                self.cache.get("example.com", 80, "http")
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertLessEqual(len(self.cache.cache), self.cache.max_pool_size)

    def test_context_manager(self):
        """Test cache as context manager"""
        with ConnectionCache() as cache:
            cache.store("example.com", 80, "http", self.test_socket)
            self.assertEqual(len(cache.cache), 1)
        self.assertEqual(len(cache.cache), 0)

if __name__ == '__main__':
    unittest.main() 