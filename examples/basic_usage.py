#!/usr/bin/env python3
"""
Basic usage examples for RivaBrowser.

This script demonstrates common use cases of RivaBrowser:
- Making simple requests
- Using different URL schemes
- Handling responses
- Using interactive commands
"""

from riva import URL, HTTP2Connection
from riva.cache import ConnectionCache
from riva.utils import show, print_links

def basic_request():
    """Demonstrate basic URL request."""
    url = URL("https://example.com")
    response = url.request()
    show(response)

def http2_example():
    """Demonstrate HTTP/2 usage."""
    conn = HTTP2Connection("example.com", 443)
    try:
        conn.connect()
        stream_id = conn.send_request(
            "GET",
            "/",
            {"user-agent": "RivaBrowser/1.0"}
        )
        status, data = conn.receive_response()
        show(f"Status: {status}")
        show(data.decode())
    finally:
        conn.close()

def cache_example():
    """Demonstrate connection caching."""
    cache = ConnectionCache(
        timeout=30.0,
        max_pool_size=10,
        enable_metrics=True
    )
    
    # Make multiple requests to same host
    for _ in range(3):
        url = URL("https://example.com")
        response = url.request()
        show(response[:100])  # Show first 100 chars
    
    # Show cache statistics
    stats = cache.get_stats()
    show(f"Cache hits: {stats.hits}")
    show(f"Cache misses: {stats.misses}")

def extract_links():
    """Demonstrate link extraction."""
    url = URL("https://example.com")
    response = url.request()
    links = print_links(response)
    show(f"Found {len(links)} links")

if __name__ == "__main__":
    print("Basic Request Example:")
    basic_request()
    
    print("\nHTTP/2 Example:")
    http2_example()
    
    print("\nCache Example:")
    cache_example()
    
    print("\nLink Extraction Example:")
    extract_links() 