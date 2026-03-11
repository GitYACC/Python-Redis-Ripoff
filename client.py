import socket

class RedisClient:
    HOST = socket.gethostbyname("localhost")
    PORT = 6543

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.HOST, self.PORT))

    def set(self, key: str, value: str):
        self.client.sendall(bytes(f"SET {key} {value}", "utf-8"))
        return self.client.recv(len(value))
    
    def get(self, key: str):
        self.client.sendall(bytes(f"GET {key}", "utf-8"))
        return self.client.recv(1024)
    
    def incr(self, key: str):
        self.client.sendall(bytes(f"INCR {key}", "utf-8"))
        return self.client.recv(1024)
    
    def decr(self, key: str):
        self.client.sendall(bytes(f"DECR {key}", "utf-8"))
        return self.client.recv(1024)
    
    def lpush(self, key: str, *values):
        values = " ".join(map(lambda x: str(x), values))
        self.client.sendall(bytes(f"LPUSH {key} {values}", "utf-8"))
        return self.client.recv(1024)
    
    def rpush(self, key: str, *values):
        values = " ".join(map(lambda x: str(x), values))
        self.client.sendall(bytes(f"RPUSH {key} {values}", "utf-8"))
        return self.client.recv(1024)

    def delete(self, *keys):
        keys_str = " ".join(keys)
        self.client.sendall(bytes(f"DEL {keys_str}", "utf-8"))
        return self.client.recv(1024)

    def exists(self, key: str):
        self.client.sendall(bytes(f"EXISTS {key}", "utf-8"))
        return self.client.recv(1024)

    def lpop(self, key: str):
        self.client.sendall(bytes(f"LPOP {key}", "utf-8"))
        return self.client.recv(1024)

    def rpop(self, key: str):
        self.client.sendall(bytes(f"RPOP {key}", "utf-8"))
        return self.client.recv(1024)

    def llen(self, key: str):
        self.client.sendall(bytes(f"LLEN {key}", "utf-8"))
        return self.client.recv(1024)

    def lindex(self, key: str, index: int):
        self.client.sendall(bytes(f"LINDEX {key} {index}", "utf-8"))
        return self.client.recv(1024)

    def lrange(self, key: str, start: int, stop: int):
        self.client.sendall(bytes(f"LRANGE {key} {start} {stop}", "utf-8"))
        return self.client.recv(1024)

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    with RedisClient() as client:
        print(client.incr("bike"))