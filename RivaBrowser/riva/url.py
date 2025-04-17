import socket
import ssl
from urllib.parse import urlparse
from .cache import connection_cache
import base64
import logging
from colorama import Fore
from datetime import datetime

class URL:
    SCHEME_PORTS = {
        'http': 80,
        'https': 443,
        'file': None,
        'data': None,
        'view-source': None
    }

    def __init__(self, url, user_agent=None):
        self.original_url = url
        self.scheme = None
        self.host = None
        self.port = None
        self.path = None
        self.inner_url = None
        self.user_agent = user_agent or "RivaBrowser/1.0"
        self._parse_url(url)

    def _parse_url(self, url):
        """Main URL parsing dispatcher"""
        if not url or len(url) < 3:
            raise ValueError("URL too short")
            
        if url.startswith("view-source:"):
            self._handle_view_source(url)
        elif url.startswith("data:text/html,"):
            self._handle_data(url)
        elif self._is_windows_path(url):
            self._handle_file(url)
        else:
            if "://" not in url and not self._is_windows_path(url):
                raise ValueError("Invalid URL format: missing scheme")
            self._handle_generic(url)

    def _handle_view_source(self, url):
        """Process view-source: URLs"""
        self.scheme = "view-source"
        inner_url = url[12:]
        self.inner_url = URL(inner_url)

    def _handle_data(self, url):
        """Process data: URLs"""
        self.scheme = "data"
        self.path = url.split(",", 1)[1]

    def _handle_file(self, url):
        """Process file paths and URLs"""
        self.scheme = "file"
        if url.startswith("file://"):
            self.path = url[7:]
            while self.path.startswith('/'):
                self.path = self.path[1:]
        else:
            self.path = url

    def _handle_http(self, url):
        """Process http/https URLs"""
        if '@' in url:
            auth_part, rest = url.split('@', 1)
            self.auth = auth_part
            url = rest
        
        if len(url) < 3:
            raise ValueError("URL too short")
        
        if '/' not in url:
            url += "/"
        parts = url.split("/", 1)
        self.host = parts[0]
        self.path = "/" + parts[1] if len(parts) > 1 else "/"

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        else:
            self.port = self.SCHEME_PORTS[self.scheme]

    def _handle_generic(self, url):
        """Handle URLs without explicit scheme"""
        if "://" in url:
            self.scheme, rest = url.split("://", 1)
            if self.scheme not in self.SCHEME_PORTS:
                raise ValueError(f"Unsupported scheme: {self.scheme}")
            
            if self.scheme in ("http", "https"):
                self._handle_http(rest)
            elif self.scheme == "file":
                self._handle_file(rest)
        else:
            self._handle_file(url)

    @staticmethod
    def _is_windows_path(url):
        """Check if URL is a Windows path"""
        return '\\' in url or (len(url) > 1 and url[1] == ':')
    
    def request(self):
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
        if self.inner_url.scheme in ["http", "https"]:
            return self.inner_url._request_http(source_mode=True)
        elif self.inner_url.scheme == "file":
            return self.inner_url._request_file()
        elif self.inner_url.scheme == "data":
            return self.inner_url._request_data()
        else:
            raise ValueError(f"Unsupported inner scheme: {self.inner_url.scheme}")
    
    def _get_socket(self):
        sock = connection_cache.get(self.host, self.port, self.scheme)
        
        if sock is None:
            sock = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )
            sock.connect((self.host, self.port))
            
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                sock = ctx.wrap_socket(sock, server_hostname=self.host)
        
        return sock
    
    def _request_http(self, source_mode=False):
        sock = self._get_socket()
        
        auth_header = ""
        if hasattr(self, 'auth'):
            auth_header = f"Authorization: Basic {base64.b64encode(self.auth.encode()).decode()}\r\n"

        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "Connection: keep-alive\r\n"
        request += f"User-Agent: {self.user_agent}\r\n"
        request += auth_header
        request += "\r\n"
        
        try:
            sock.send(request.encode("utf8"))
        except Exception as e:
            logging.error(f"Failed to send request: {e}")
            raise

        response = sock.makefile("rb", newline="\r\n")
        statusline = response.readline().decode('utf-8')
        
        try:
            version, status, explanation = statusline.split(" ", 2)
            if int(status) >= 400:
                logging.error(f"HTTP Error {status}: {explanation.strip()}")
                print(Fore.RED + f"HTTP Error: {status} {explanation.strip()}")
        except ValueError:
            pass

        content_length = None
        connection_close = False
        response_headers = {}
        
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
            body = response.read().decode('utf-8', errors='replace')
            if connection_close:
                sock.close()
            else:
                connection_cache.store(self.host, self.port, self.scheme, sock)
            return f"{statusline}{''.join(f'{k}: {v}\r\n' for k, v in response_headers.items())}\r\n{body}"
        else:
            if content_length is not None:
                body = response.read(content_length).decode('utf-8', errors='replace')
            else:
                body = response.read().decode('utf-8', errors='replace')
                connection_close = True
            
            if connection_close:
                sock.close()
            else:
                connection_cache.store(self.host, self.port, self.scheme, sock)
            
            return body
    
    def _request_file(self):
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
                with open(self.path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"

    def _request_data(self):
        if self.path.startswith("text/html,"):
            return self.path[len("text/html,"):]
        return self.path