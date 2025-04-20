import socket
import ssl
import h2.connection
import h2.events
from typing import Optional, Tuple, Dict
import logging

class HTTP2Connection:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.conn = None
        self.h2_conn = None
        self.stream_id = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Establish HTTP/2 connection"""
        try:
            # Create socket
            sock = socket.create_connection((self.host, self.port))
            
            # Wrap with SSL
            context = ssl.create_default_context()
            context.set_alpn_protocols(['h2'])
            self.conn = context.wrap_socket(sock, server_hostname=self.host)
            
            # Initialize HTTP/2 connection
            self.h2_conn = h2.connection.H2Connection()
            self.h2_conn.initiate_connection()
            self.conn.send(self.h2_conn.data_to_send())
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to establish HTTP/2 connection: {str(e)}")
            return False

    def send_request(self, method: str, path: str, headers: Dict[str, str]) -> Optional[int]:
        """Send HTTP/2 request and return stream ID"""
        try:
            if not self.h2_conn or not self.conn:
                if not self.connect():
                    return None

            # Prepare headers
            request_headers = [
                (':method', method),
                (':path', path),
                (':authority', self.host),
                (':scheme', 'https'),
            ]
            for key, value in headers.items():
                request_headers.append((key.lower(), value))

            # Send request
            self.stream_id = self.h2_conn.get_next_available_stream_id()
            self.h2_conn.send_headers(self.stream_id, request_headers)
            self.conn.send(self.h2_conn.data_to_send())
            
            return self.stream_id
        except Exception as e:
            self.logger.error(f"Failed to send HTTP/2 request: {str(e)}")
            return None

    def receive_response(self) -> Tuple[Optional[int], Optional[bytes]]:
        """Receive HTTP/2 response"""
        try:
            if not self.h2_conn or not self.conn or not self.stream_id:
                return None, None

            data = self.conn.recv(65535)
            if not data:
                return None, None
                
            events = self.h2_conn.receive_data(data)
            
            for event in events:
                if hasattr(event, 'stream_id') and hasattr(event, 'data'):
                    self.h2_conn.acknowledge_received_data(
                        len(event.data),
                        event.stream_id
                    )
                    return event.stream_id, event.data
                elif hasattr(event, 'stream_id') and isinstance(event, h2.events.StreamEnded):
                    return event.stream_id, None

            return self.stream_id, None
        except Exception as e:
            self.logger.error(f"Failed to receive HTTP/2 response: {str(e)}")
            return None, None

    def close(self):
        """Close HTTP/2 connection"""
        try:
            if self.h2_conn:
                self.h2_conn.close_connection()
                self.conn.send(self.h2_conn.data_to_send())
            if self.conn:
                self.conn.close()
        except Exception as e:
            self.logger.error(f"Error closing HTTP/2 connection: {str(e)}") 