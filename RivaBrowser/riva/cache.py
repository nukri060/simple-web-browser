import socket
import time
import threading
from collections import OrderedDict
from typing import Dict, Tuple, Optional, Union
import logging

class ConnectionCache:
    def __init__(
        self,
        timeout: float = 30.0,
        max_pool_size: int = 5,
        enable_metrics: bool = True,
        enable_logging: bool = True
    ):
        """
        Improved connection cache with thread safety, LRU eviction and metrics
        
        :param timeout: Connection timeout in seconds
        :param max_pool_size: Maximum number of connections to cache
        :param enable_metrics: Track cache hits/misses
        :param enable_logging: Enable debug logging
        """
        self.cache: OrderedDict[Tuple[str, int, str], Tuple[socket.socket, float]] = OrderedDict()
        self.lock = threading.Lock()
        self.timeout = timeout
        self.max_pool_size = max_pool_size
        
        # Metrics
        self.enable_metrics = enable_metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Logging
        self.logger = logging.getLogger(__name__)
        self.enable_logging = enable_logging
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
        
        # Background cleaner thread
        self._cleaner_running = True
        self.cleaner_thread = threading.Thread(
            target=self._cleanup_expired,
            daemon=True
        )
        self.cleaner_thread.start()

    def _log(self, message: str, level: str = "info"):
        if self.enable_logging:
            getattr(self.logger, level)(message)

    def _cleanup_expired(self):
        """Background thread to periodically clean expired connections"""
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

    def _is_connection_alive(self, sock: socket.socket) -> bool:
        """Enhanced connection health check"""
        try:
            # Test if socket is still writable
            sock.settimeout(0.1)
            sock.send(b'\x00')  # Zero-length test packet
            return True
        except (socket.error, OSError, TimeoutError):
            return False

    def get(self, host: str, port: int, scheme: str) -> Optional[socket.socket]:
        """
        Get cached connection if available and alive
        
        :return: Socket if found and valid, None otherwise
        """
        key = (host, port, scheme)
        
        with self.lock:
            if key in self.cache:
                sock, timestamp = self.cache[key]
                
                if (time.time() - timestamp < self.timeout and 
                    self._is_connection_alive(sock)):
                    # Move to end as most recently used
                    self.cache.move_to_end(key)
                    if self.enable_metrics:
                        self.hits += 1
                    self._log(f"Cache hit for {key}")
                    return sock
                
                # Connection is stale or dead
                self._remove_connection(key)
                if self.enable_metrics:
                    self.misses += 1
                self._log(f"Cache miss (stale/dead) for {key}")
            else:
                if self.enable_metrics:
                    self.misses += 1
                self._log(f"Cache miss (not found) for {key}")
            
            return None

    def store(self, host: str, port: int, scheme: str, sock: socket.socket) -> bool:
        """
        Store connection in cache
        
        :return: True if stored successfully, False if rejected
        """
        key = (host, port, scheme)
        
        with self.lock:
            # Check if connection already exists
            if key in self.cache:
                self._log(f"Duplicate connection for {key}, replacing")
                self._remove_connection(key)
            
            # Enforce max pool size
            if len(self.cache) >= self.max_pool_size:
                self._remove_oldest()
            
            # Verify connection is still good before storing
            if not self._is_connection_alive(sock):
                self._log(f"Connection not alive, not storing {key}", "warning")
                return False
                
            self.cache[key] = (sock, time.time())
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
        sock, _ = self.cache.pop(key, (None, None))
        if sock:
            try:
                sock.close()
                self._log(f"Closed connection for {key}")
            except Exception as e:
                self._log(f"Error closing socket for {key}: {str(e)}", "error")

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