"""
Connection caching implementation for RivaBrowser.

This module provides a connection caching system that manages and reuses
HTTP and HTTP/2 connections. Features include:
- Connection pooling with configurable size limits
- Automatic cleanup of expired connections
- Connection health checking
- Performance metrics collection
- Thread-safe operations
- Support for both HTTP and HTTP/2 connections

Example usage:
    >>> from riva.cache import ConnectionCache
    >>> cache = ConnectionCache(timeout=30.0, max_pool_size=5)
    >>> with cache:
    ...     conn = cache.get("example.com", 443, "https")
    ...     if conn is None:
    ...         conn = create_new_connection()
    ...         cache.store("example.com", 443, "https", conn)
"""

import socket
import time
import threading
from collections import OrderedDict
from typing import Dict, Tuple, Optional, Union, Any, TypeVar, Generic
from dataclasses import dataclass
import logging
from datetime import datetime
from .http2 import HTTP2Connection
from .exceptions import CacheError, ConnectionError

# Type variable for connection objects
T = TypeVar('T', socket.socket, HTTP2Connection)

@dataclass
class CacheMetrics:
    """Metrics for cache performance."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    hit_ratio: float = 0.0
    total_connections: int = 0
    failed_connections: int = 0
    avg_connection_lifetime: float = 0.0

class ConnectionCache(Generic[T]):
    """
    Thread-safe connection cache with automatic cleanup.
    
    This class manages a pool of connections, reusing them when possible
    and automatically cleaning up expired or dead connections.
    
    Args:
        timeout: Connection timeout in seconds (default: 30.0)
        max_pool_size: Maximum number of connections to cache (default: 5)
        enable_metrics: Whether to collect performance metrics (default: True)
        enable_logging: Whether to enable logging (default: True)
        enable_http2: Whether to support HTTP/2 connections (default: True)
        
    Attributes:
        cache: Ordered dictionary storing connections and their timestamps
        lock: Thread lock for thread-safe operations
        timeout: Connection timeout in seconds
        max_pool_size: Maximum number of connections to cache
        enable_http2: Whether HTTP/2 connections are supported
        metrics: Cache performance metrics
        logger: Logger instance for logging operations
    """
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_pool_size: int = 5,
        enable_metrics: bool = True,
        enable_logging: bool = True,
        enable_http2: bool = True
    ):
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        if max_pool_size <= 0:
            raise ValueError("Max pool size must be positive")
            
        self.cache: OrderedDict[Tuple[str, int, str], Tuple[T, float]] = OrderedDict()
        self.lock = threading.Lock()
        self.timeout = timeout
        self.max_pool_size = max_pool_size
        self.enable_http2 = enable_http2
        
        self.metrics = CacheMetrics(max_size=max_pool_size)
        self.enable_metrics = enable_metrics
        
        self.logger = logging.getLogger(__name__)
        self.enable_logging = enable_logging
        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self._cleaner_running = True
        self.cleaner_thread = threading.Thread(
            target=self._cleanup_expired,
            daemon=True
        )
        self.cleaner_thread.start()
        self._connection_times: Dict[Tuple[str, int, str], float] = {}

    def _log(self, message: str, level: str = "info"):
        """Helper for logging with timestamp"""
        if self.enable_logging:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            getattr(self.logger, level)(f"[{timestamp}] {message}")

    def _cleanup_expired(self):
        """Background thread to clean expired connections"""
        while self._cleaner_running:
            time.sleep(self.timeout / 2)
            with self.lock:
                now = time.time()
                expired_keys = [
                    key for key, (_, timestamp) in self.cache.items()
                    if now - timestamp > self.timeout
                ]
                for key in expired_keys:
                    self._remove_connection(key)
                    self._log(f"Expired connection removed: {key}")
                    if self.enable_metrics:
                        self.metrics.evictions += 1

    def _is_connection_alive(self, conn: T) -> bool:
        """
        Check if connection is still alive.
        
        Args:
            conn: The connection to check
            
        Returns:
            bool: True if connection is alive, False otherwise
            
        Raises:
            CacheError: If connection type is not supported
        """
        try:
            if isinstance(conn, socket.socket):
                conn.settimeout(0.1)
                conn.send(b'\x00')
                return True
            elif isinstance(conn, HTTP2Connection):
                return conn.h2_conn is not None and conn.h2_conn.get_next_available_stream_id() is not None
            else:
                raise CacheError(f"Unsupported connection type: {type(conn)}")
        except (socket.error, OSError, TimeoutError) as e:
            self._log(f"Connection check failed: {str(e)}", "warning")
            return False

    def get(self, host: str, port: int, scheme: str) -> Optional[T]:
        """
        Get cached connection if available and alive.
        
        Args:
            host: Target host
            port: Target port
            scheme: Connection scheme (http/https)
            
        Returns:
            Optional[T]: Cached connection if available and alive, None otherwise
            
        Raises:
            ValueError: If host, port, or scheme is invalid
        """
        if not host or not isinstance(host, str):
            raise ValueError("Invalid host")
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError("Invalid port")
        if scheme not in ("http", "https"):
            raise ValueError("Invalid scheme")
            
        key = (host, port, scheme)
        
        with self.lock:
            if key in self.cache:
                conn, timestamp = self.cache[key]
                
                if (time.time() - timestamp < self.timeout and 
                    self._is_connection_alive(conn)):
                    self.cache.move_to_end(key)
                    if self.enable_metrics:
                        self.metrics.hits += 1
                    self._log(f"Cache hit for {key}")
                    return conn
                
                self._remove_connection(key)
                if self.enable_metrics:
                    self.metrics.misses += 1
                    self.metrics.failed_connections += 1
                self._log(f"Cache miss (stale/dead) for {key}")
            else:
                if self.enable_metrics:
                    self.metrics.misses += 1
                self._log(f"Cache miss (not found) for {key}")
            
            return None

    def store(self, host: str, port: int, scheme: str, conn: T) -> bool:
        """
        Store connection in cache.
        
        Args:
            host: Target host
            port: Target port
            scheme: Connection scheme (http/https)
            conn: Connection to store
            
        Returns:
            bool: True if connection was stored, False otherwise
            
        Raises:
            ValueError: If host, port, or scheme is invalid
            CacheError: If connection is not alive or cache is full
        """
        if not host or not isinstance(host, str):
            raise ValueError("Invalid host")
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError("Invalid port")
        if scheme not in ("http", "https"):
            raise ValueError("Invalid scheme")
            
        key = (host, port, scheme)
        
        with self.lock:
            if key in self.cache:
                self._log(f"Duplicate connection for {key}, replacing")
                self._remove_connection(key)
            
            if len(self.cache) >= self.max_pool_size:
                self._remove_oldest()
            
            if not self._is_connection_alive(conn):
                self._log(f"Connection not alive, not storing {key}", "warning")
                if self.enable_metrics:
                    self.metrics.failed_connections += 1
                return False
                
            self.cache[key] = (conn, time.time())
            self._connection_times[key] = time.time()
            if self.enable_metrics:
                self.metrics.size = len(self.cache)
                self.metrics.total_connections += 1
            self._log(f"Stored connection for {key}")
            return True

    def _remove_oldest(self):
        """Remove least recently used connection"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            self._remove_connection(oldest_key)
            if self.enable_metrics:
                self.metrics.evictions += 1

    def _remove_connection(self, key: Tuple[str, int, str]):
        """
        Safely remove and close connection.
        
        Args:
            key: Connection key (host, port, scheme)
        """
        conn, _ = self.cache.pop(key, (None, None))
        if conn:
            try:
                if isinstance(conn, socket.socket):
                    conn.close()
                elif isinstance(conn, HTTP2Connection):
                    conn.close()
                self._log(f"Closed connection for {key}")
                
                if self.enable_metrics and key in self._connection_times:
                    lifetime = time.time() - self._connection_times.pop(key)
                    self.metrics.avg_connection_lifetime = (
                        (self.metrics.avg_connection_lifetime * (self.metrics.total_connections - 1) + lifetime)
                        / self.metrics.total_connections
                    )
            except Exception as e:
                self._log(f"Error closing connection for {key}: {str(e)}", "error")
                if self.enable_metrics:
                    self.metrics.failed_connections += 1

    def print_stats(self) -> None:
        """Print human-readable cache statistics"""
        stats = self.get_metrics()
        print("\n=== Connection Cache Statistics ===")
        print(f"Active connections: {stats['size']}/{stats['max_size']}")
        print(f"Total hits: {stats['hits']}")
        print(f"Total misses: {stats['misses']}")
        print(f"Hit ratio: {stats['hit_ratio']:.1%}")
        print(f"Evictions: {stats['evictions']}")
        print(f"Total connections: {stats['total_connections']}")
        print(f"Failed connections: {stats['failed_connections']}")
        print(f"Average connection lifetime: {stats['avg_connection_lifetime']:.2f}s")
        print(f"HTTP/2 enabled: {self.enable_http2}")

    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """
        Get cache performance metrics.
        
        Returns:
            Dict[str, Union[int, float]]: Dictionary of metrics
        """
        with self.lock:
            total = self.metrics.hits + self.metrics.misses
            return {
                'hits': self.metrics.hits,
                'misses': self.metrics.misses,
                'evictions': self.metrics.evictions,
                'size': self.metrics.size,
                'max_size': self.metrics.max_size,
                'hit_ratio': self.metrics.hits / total if total > 0 else 0,
                'total_connections': self.metrics.total_connections,
                'failed_connections': self.metrics.failed_connections,
                'avg_connection_lifetime': self.metrics.avg_connection_lifetime
            }

    def close_all(self):
        """Close all connections and stop cleaner thread"""
        self._cleaner_running = False
        if self.cleaner_thread.is_alive():
            self.cleaner_thread.join()
        
        with self.lock:
            for key in list(self.cache.keys()):
                self._remove_connection(key)
            self._log("All connections closed")

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()

# Global instance with default settings
connection_cache = ConnectionCache()