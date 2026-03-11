import socket
import time

class RedisClient:
    HOST = socket.gethostbyname("localhost")
    PORT = 6543

    def __init__(self, timeout=10):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(timeout)
            self.client.connect((self.HOST, self.PORT))
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to Redis server at {self.HOST}:{self.PORT} - {e}")

    def close(self):
        """Close the connection to the server"""
        if hasattr(self, 'client'):
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _send_command(self, command: str):
        """Send a command and receive response"""
        try:
            self.client.sendall(bytes(command, "utf-8"))
            response = self.client.recv(1024)
            return response.decode("utf-8")
        except socket.error as e:
            raise ConnectionError(f"Communication error with server: {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid response from server: {e}")

    def set(self, key: str, value: str):
        if not key:
            raise ValueError("Key cannot be empty")
        return self._send_command(f"SET {key} {value}")

    def get(self, key: str):
        if not key:
            raise ValueError("Key cannot be empty")
        response = self._send_command(f"GET {key}")
        return response if response != "None" else None

    def incr(self, key: str):
        if not key:
            raise ValueError("Key cannot be empty")
        return self._send_command(f"INCR {key}")

    def decr(self, key: str):
        if not key:
            raise ValueError("Key cannot be empty")
        return self._send_command(f"DECR {key}")

    def lpush(self, key: str, *values):
        if not key:
            raise ValueError("Key cannot be empty")
        if not values:
            raise ValueError("At least one value must be provided")
        values_str = " ".join(map(str, values))
        return self._send_command(f"LPUSH {key} {values_str}")

    def rpush(self, key: str, *values):
        if not key:
            raise ValueError("Key cannot be empty")
        if not values:
            raise ValueError("At least one value must be provided")
        values_str = " ".join(map(str, values))
        return self._send_command(f"RPUSH {key} {values_str}")


