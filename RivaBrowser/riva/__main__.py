from .url import URL
from .cache import connection_cache

def main():
    try:
        test_urls = [
            "https://httpbin.org/get?request=1",
            "https://httpbin.org/get?request=2", 
            "https://httpbin.org/connection/close",  
            "https://httpbin.org/get?request=3" 
        ]

        for url in test_urls:
            print(f"\n=== RivaBrowser requesting: {url} ===")
            url_obj = URL(url)
            body = url_obj.request()
            
            # Print first 200 chars of response
            print(body[:200] + ("..." if len(body) > 200 else ""))
            
            # Show cache status (исправленная версия)
            print("\nConnection cache contents:")
            for (host, port, scheme), (sock, _) in connection_cache.cache.items():
                try:
                    print(f"- {scheme}://{host}:{port} (socket: {sock.fileno()})")
                except (AttributeError, OSError):
                    print(f"- {scheme}://{host}:{port} (socket: closed)")
            
            input("Press Enter to continue...")

    finally:
        connection_cache.close_all()
        print("\nRivaBrowser: all connections closed")

if __name__ == "__main__":
    main()