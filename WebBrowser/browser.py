import socket
import ssl
import os
import sys

class URL:
    def __init__(self, url): 
        # Check if this is a Windows path (contains \ or starts with a drive letter)
        is_windows_path = '\\' in url or (len(url) > 1 and url[1] == ':')
        
        if is_windows_path:
            # Treat as a file path
            self.scheme = "file"
            self.path = url
        elif "://" not in url:
            # Default to file scheme if no scheme is provided and not a Windows path
            self.scheme = "file"
            self.path = url
        else:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in ["http", "https", "file"]
        
        if self.scheme in ["http", "https"]:
            # Set default ports
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443
            
            if '/' not in url:
                url += "/"
            
            self.host, self.path = url.split("/", 1)
            self.path = "/" + self.path

            # Handle custom ports
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
        elif self.scheme == "file":
            # For file URLs, handle both Unix-style and Windows paths
            if not is_windows_path and url.startswith('/'):
                self.path = url
            elif not is_windows_path:
                self.path = url.replace('file://', '')
                while self.path.startswith('/'):
                    self.path = self.path[1:]
    
    def request(self):
        if self.scheme in ["http", "https"]:
            return self._request_http()
        elif self.scheme == "file":
            return self._request_file()
        else:
            raise ValueError("Unsupported scheme: " + self.scheme)
    
    def _request_http(self):
        # Create a socket and connect to the server
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        s.connect((self.host, self.port))
        
        # Wrap the socket with SSL if HTTPS
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: close\r\n"
        request += "User-Agent: myFirstBrowser\r\n"
        request += "\r\n" 
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": 
                break  

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        body = response.read()
        s.close()
        return body
    
    def _request_file(self):
        # Open the local file and return its contents
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
                # Try opening the file with a different encoding (latin-1)
                with open(self.path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file (tried utf-8 and latin-1): {str(e)}"

def show(body):
    in_tag = False
    # Simple function to strip HTML tags
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    # Default file path if no URL is provided
    DEFAULT_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "ex", "index.html")
    
    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        # If no URL is provided, use the default file
        print(f"No URL provided, using default file: {DEFAULT_FILE}")
        url = URL(DEFAULT_FILE)
    
    load(url)