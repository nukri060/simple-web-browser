#!/usr/bin/env python3
"""
Advanced usage examples for RivaBrowser.

This script demonstrates more complex use cases:
- Custom URL schemes
- Advanced caching
- Error handling
- Performance optimization
"""

import time
from typing import Dict, Any
from riva import URL, HTTP2Connection
from riva.cache import ConnectionCache
from riva.utils import show
from riva.http2 import HTTP2Error

class CustomURL(URL):
    """Custom URL handler with additional features."""
    
    def __init__(self, url: str, custom_headers: Dict[str, str] = None):
        super().__init__(url)
        self.custom_headers = custom_headers or {}
    
    def request(self) -> str:
        """Make request with custom headers."""
        headers = {
            "user-agent": "RivaBrowser/1.0",
            **self.custom_headers
        }
        return super().request(headers=headers)

def benchmark_requests():
    """Benchmark different request methods."""
    url = "https://example.com"
    iterations = 5
    
    # Test standard URL
    start = time.time()
    for _ in range(iterations):
        URL(url).request()
    standard_time = time.time() - start
    
    # Test HTTP/2
    start = time.time()
    for _ in range(iterations):
        conn = HTTP2Connection("example.com", 443)
        try:
            conn.connect()
            conn.send_request("GET", "/")
            conn.receive_response()
        finally:
            conn.close()
    http2_time = time.time() - start
    
    show(f"Standard requests: {standard_time:.2f}s")
    show(f"HTTP/2 requests: {http2_time:.2f}s")
    show(f"Improvement: {((standard_time - http2_time) / standard_time) * 100:.1f}%")

def custom_scheme_example():
    """Demonstrate custom URL scheme handling."""
    class CustomSchemeURL(URL):
        def _handle_custom_scheme(self, url: str) -> str:
            if url.startswith("custom://"):
                return f"Custom scheme handled: {url}"
            return super()._handle_custom_scheme(url)
    
    url = CustomSchemeURL("custom://example")
    show(url.request())

def error_handling_example():
    """Demonstrate error handling."""
    try:
        # Invalid URL
        URL("invalid-url").request()
    except ValueError as e:
        show(f"URL Error: {e}")
    
    try:
        # HTTP/2 connection error
        conn = HTTP2Connection("nonexistent.example.com", 443)
        conn.connect()
    except HTTP2Error as e:
        show(f"HTTP/2 Error: {e}")

def advanced_cache_example():
    """Demonstrate advanced caching features."""
    cache = ConnectionCache(
        timeout=60.0,
        max_pool_size=20,
        enable_metrics=True,
        cleanup_interval=300.0
    )
    
    # Make requests with different timeouts
    urls = [
        ("https://example.com", 5.0),
        ("https://example.org", 10.0),
        ("https://example.net", 15.0)
    ]
    
    for url, timeout in urls:
        URL(url).request(timeout=timeout)
    
    # Show detailed metrics
    stats = cache.get_stats()
    show("\nCache Statistics:")
    show(f"Total Requests: {stats.total_requests}")
    show(f"Cache Hits: {stats.hits}")
    show(f"Cache Misses: {stats.misses}")
    show(f"Hit Rate: {stats.hit_rate:.1%}")
    show(f"Average Connection Lifetime: {stats.avg_connection_lifetime:.1f}s")

if __name__ == "__main__":
    print("Benchmark Example:")
    benchmark_requests()
    
    print("\nCustom Scheme Example:")
    custom_scheme_example()
    
    print("\nError Handling Example:")
    error_handling_example()
    
    print("\nAdvanced Cache Example:")
    advanced_cache_example() 