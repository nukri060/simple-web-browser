import socket
import time

class ConnectionCache:
    CONNECTION_TIMEOUT = 30  # seconds
    
    def __init__(self):
        self.cache = {}  # {(host,port,scheme): (socket, timestamp)}
    
    def get(self, host, port, scheme):
        key = (host, port, scheme)
        if key in self.cache:
            sock, timestamp = self.cache[key]
            if time.time() - timestamp < self.CONNECTION_TIMEOUT:
                return sock
            self._remove_connection(key)
        return None
    
    def store(self, host, port, scheme, sock):
        key = (host, port, scheme)
        self.cache[key] = (sock, time.time())
    
    def _remove_connection(self, key):
        sock, _ = self.cache.pop(key, (None, None))
        if sock:
            try:
                sock.close()
            except:
                pass
    
    def close_all(self):
        for key in list(self.cache.keys()):
            self._remove_connection(key)