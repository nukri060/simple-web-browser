import socket
import time
import threading
from collections import OrderedDict
from typing import Dict, Tuple, Optional, Union, Any
import logging
from datetime import datetime
from .http2 import HTTP2Connection

class ConnectionCache:
    def __init__(
        self,
        timeout: float = 30.0,
        max_pool_size: int = 5,
        enable_metrics: bool = True,
        enable_logging: bool = True,
        enable_http2: bool = True
    ):
        self.cache: OrderedDict[Tuple[str, int, str], Tuple[Any, float]] = OrderedDict()
        self.lock = threading.Lock()
        self.timeout = timeout
        self.max_pool_size = max_pool_size
        self.enable_http2 = enable_http2
        
        self.enable_metrics = enable_metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        self.logger = logging.getLogger(__name__)
        self.enable_logging = enable_logging
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
        
        self._cleaner_running = True
        self.cleaner_thread = threading.Thread(
            target=self._cleanup_expired,
            daemon=True
        )
        self.cleaner_thread.start()

    def _log(self, message: str, level: str = "info"):
        """Helper for logging"""
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

    def _is_connection_alive(self, conn: Any) -> bool:
        """Check if connection is still alive"""
        try:
            if isinstance(conn, socket.socket):
                conn.settimeout(0.1)
                conn.send(b'\x00')
                return True
            elif isinstance(conn, HTTP2Connection):
                # For HTTP/2, we'll consider it alive if we can get a new stream ID
                return conn.h2_conn is not None and conn.h2_conn.get_next_available_stream_id() is not None
            return False
        except (socket.error, OSError, TimeoutError):
            return False

    def get(self, host: str, port: int, scheme: str) -> Optional[Any]:
        """
        Get cached connection if available and alive.
        """
        key = (host, port, scheme)
        
        with self.lock:
            if key in self.cache:
                conn, timestamp = self.cache[key]
                
                if (time.time() - timestamp < self.timeout and 
                    self._is_connection_alive(conn)):
                    self.cache.move_to_end(key)
                    if self.enable_metrics:
                        self.hits += 1
                    self._log(f"Cache hit for {key}")
                    return conn
                
                self._remove_connection(key)
                if self.enable_metrics:
                    self.misses += 1
                self._log(f"Cache miss (stale/dead) for {key}")
            else:
                if self.enable_metrics:
                    self.misses += 1
                self._log(f"Cache miss (not found) for {key}")
            
            return None

    def store(self, host: str, port: int, scheme: str, conn: Any) -> bool:
        """
        Store connection in cache.
        """
        key = (host, port, scheme)
        
        with self.lock:
            if key in self.cache:
                self._log(f"Duplicate connection for {key}, replacing")
                self._remove_connection(key)
            
            if len(self.cache) >= self.max_pool_size:
                self._remove_oldest()
            
            if not self._is_connection_alive(conn):
                self._log(f"Connection not alive, not storing {key}", "warning")
                return False
                
            self.cache[key] = (conn, time.time())
            self._log(f"Stored connection for {key}")
            return True

    def _remove_oldest(self):
        """Remove least recently used connection"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            self._remove_connection(oldest_key)
            if self.enable_metrics:
                self.evictions += 1

    def _remove_connection(self, key: Tuple[str, int, str]):
        """Safely remove and close connection"""
        conn, _ = self.cache.pop(key, (None, None))
        if conn:
            try:
                if isinstance(conn, socket.socket):
                    conn.close()
                elif isinstance(conn, HTTP2Connection):
                    conn.close()
                self._log(f"Closed connection for {key}")
            except Exception as e:
                self._log(f"Error closing connection for {key}: {str(e)}", "error")

    def print_stats(self) -> None:
        """Print human-readable cache statistics"""
        stats = self.get_metrics()
        print("\n=== Connection Cache Statistics ===")
        print(f"Active connections: {stats['size']}/{stats['max_size']}")
        print(f"Total hits: {stats['hits']}")
        print(f"Total misses: {stats['misses']}")
        print(f"Hit ratio: {stats['hit_ratio']:.1%}")
        print(f"Evictions: {stats['evictions']}")
        print(f"HTTP/2 enabled: {self.enable_http2}")

    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """Get cache performance metrics"""
        with self.lock:
            return {
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'size': len(self.cache),
                'max_size': self.max_pool_size,
                'hit_ratio': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
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