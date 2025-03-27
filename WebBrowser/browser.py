import socket
import ssl
import os
import sys
from urllib.parse import urlparse

class ConnectionCache:
    def __init__(self):
        # Stores open sockets: {(host, port, scheme): socket}
        self.cache = {}
    
    def get(self, host, port, scheme):
        # Unique identifier for each connection
        key = (host, port, scheme)
        return self.cache.get(key) 
    
    def store(self, host, port, scheme, sock):
        key = (host, port, scheme)
        self.cache[key] = sock # Save socket for future reuse
    
    def close_all(self):
        for sock in self.cache.values():
            try:
                sock.close()
            except:
                pass
        self.cache.clear()

connection_cache = ConnectionCache()

class URL:
    def __init__(self, url):
        # Handling 'view-source' URLs, extracting the inner URL and processing it recursively.
        if url.startswith("view-source:"):
            self.scheme = "view-source"
            inner_url = url[12:]
            self.inner_url = URL(inner_url)
            return
            
        # Handling 'data' URLs which contain raw data (e.g., text/html).
        if url.startswith("data:text/html,"):
            self.scheme = "data"
            self.path = url.split(",", 1)[1]
            return
        
        # Handling 'file' URLs, with special processing for Windows file paths.
        is_windows_path = '\\' in url or (len(url) > 1 and url[1] == ':')
        
        if is_windows_path:
            self.scheme = "file"
            self.path = url
        elif "://" not in url:
            self.scheme = "file"
            self.path = url
        else:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in ["http", "https", "file"]
        
        if self.scheme in ["http", "https"]:
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443
            
            # Ensure the URL has a trailing slash if none exists.
            if '/' not in url:
                url += "/"
            
            self.host, self.path = url.split("/", 1)
            self.path = "/" + self.path

            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
        elif self.scheme == "file":
            # Processing for non-Windows and Windows file paths
            if not is_windows_path and url.startswith('/'):
                self.path = url
            elif not is_windows_path:
                self.path = url.replace('file://', '')
                while self.path.startswith('/'):
                    self.path = self.path[1:]
    
    def request(self):
        # Redirecting based on the URL scheme.
        if self.scheme == "view-source":
            return self._request_view_source()
        elif self.scheme in ["http", "https"]:
            return self._request_http()
        elif self.scheme == "file":
            return self._request_file()
        elif self.scheme == "data":
            return self._request_data()
        else:
            raise ValueError("Unsupported scheme: " + self.scheme)
    
    def _request_view_source(self):
        # Handling requests for 'view-source' URLs by recursively fetching the inner URL.
        if self.inner_url.scheme in ["http", "https"]:
            return self.inner_url._request_http(source_mode=True)
        elif self.inner_url.scheme == "file":
            return self.inner_url._request_file()
        elif self.inner_url.scheme == "data":
            return self.inner_url._request_data()
        else:
            raise ValueError(f"Unsupported inner scheme: {self.inner_url.scheme}")
    
    def _get_socket(self):
        # Attempt to retrieve an existing cached socket for reuse, or create a new one.
        sock = connection_cache.get(self.host, self.port, self.scheme)
        
        if sock is None:
            # Creating a new socket and connecting to the specified host and port.
            sock = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )
            sock.connect((self.host, self.port))
            
            # Wrapping the socket with SSL if the scheme is 'https'.
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                sock = ctx.wrap_socket(sock, server_hostname=self.host)
        
        return sock
    
    def _request_http(self, source_mode=False):
        sock = self._get_socket()
        
        # Sending a basic HTTP GET request with necessary headers.
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "Connection: keep-alive\r\n"
        request += "User-Agent: myFirstBrowser\r\n"
        request += "\r\n"
        sock.send(request.encode("utf8"))

        # Reading the response in binary mode to ensure correct byte count.
        response = sock.makefile("rb", newline="\r\n")
        
        # Parsing the status line from the response.
        statusline = response.readline().decode('utf-8')
        version, status, explanation = statusline.split(" ", 2)

        content_length = None
        connection_close = False
        response_headers = {}
        
        # Reading headers until we reach the end of the header section.
        while True:
            line = response.readline().decode('utf-8')
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            header = header.casefold()
            value = value.strip()
            response_headers[header] = value
            
            if header == "content-length":
                content_length = int(value)
            elif header == "connection" and value.lower() == "close":
                connection_close = True

        if source_mode:
            # Returning the full response, including the status and headers.
            body = response.read().decode('utf-8', errors='replace')
            if connection_close:
                sock.close()
            else:
                connection_cache.store(self.host, self.port, self.scheme, sock)
            return f"{statusline}{''.join(f'{k}: {v}\r\n' for k, v in response_headers.items())}\r\n{body}"
        else:
            # Handling cases for responses without a 'Content-Length' header.
            if content_length is not None:
                body = response.read(content_length).decode('utf-8', errors='replace')
            else:
                # Default handling for servers without 'Content-Length' header.
                body = response.read().decode('utf-8', errors='replace')
                connection_close = True
            
            if connection_close:
                sock.close()
            else:
                connection_cache.store(self.host, self.port, self.scheme, sock)
            
            return body
    
    def _request_file(self):
        # Reading and returning the contents of a local file, handling common errors.
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File not found: {self.path}"
        except IsADirectoryError:
            return f"Path is a directory: {self.path}"
        except PermissionError:
            return f"Permission denied: {self.path}"
        except UnicodeDecodeError:
            try:
                # Trying to open the file with a different encoding if the first fails.
                with open(self.path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"

    def _request_data(self):
        # Handling 'data' URLs by returning the raw content after the comma.
        if self.path.startswith("text/html,"):
            return self.path[len("text/html,"):]

        return self.path

def show(body):
    # Displaying the response body, replacing HTML entities with proper characters.
    if body.startswith("HTTP/") or body.startswith("File not found") or body.startswith("Path is a directory") or body.startswith("Permission denied") or body.startswith("Error reading file"):
        print(body)
        return
        
    in_tag = False
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c == "&":
            # Handling HTML entities like &lt; and &gt; for proper output.
            if body.startswith("&lt;", i):
                print("<", end="")
                i += 4
            elif body.startswith("&gt;", i):
                print(">", end="")
                i += 4
            else:
                print(c, end="")
                i += 1
        elif c == "<":
            in_tag = True
            i += 1
        elif c == ">":
            in_tag = False
            i += 1
        elif not in_tag:
            print(c, end="")
            i += 1
        else:
            i += 1

def load(url):
    # Requesting and displaying the body content of a given URL.
    body = url.request()
    show(body)

if __name__ == "__main__":
    try:
        # Testing URLs with HTTP/HTTPS and connection-close scenarios.
        test_urls = [
            "https://httpbin.org/get?request=1",
            "https://httpbin.org/get?request=2", 
            "https://httpbin.org/connection/close",  
            "https://httpbin.org/get?request=3" 
        ]

        for url in test_urls:
            print(f"\n=== Requesting: {url} ===")
            url_obj = URL(url)
            body = url_obj.request()
            
            # Print first 200 chars of response
            print(body[:200] + ("..." if len(body) > 200 else ""))
            
            # Show cache status
            print("\nConnection cache contents:")
            for (host, port, scheme), sock in connection_cache.cache.items():
                print(f"- {scheme}://{host}:{port} (socket: {sock.fileno()})")
            
            input("Press Enter to continue...")

    finally:
        # Ensuring all connections are closed at the end.
        connection_cache.close_all()
        print("\nAll connections closed")
