import socket

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