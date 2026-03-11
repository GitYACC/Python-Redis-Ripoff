import socket
import threading
import re

"""
strings / numbers:
    INCR value      => increments value or creates value if not already created
    DECR value      => decrements value or creates value if not already created
    GET key         => returns value associated with key
    SET key value   => sets key value pair

lists:
    LPUSH list ...  => appends one or more items to head of list
    RPUSH list ...  => appends one or more items to tail of list
"""

class Database:
    def __init__(self):
        self._storage = {}

    def parse(self, query: bytes):
        try:
            query = query.decode("utf-8").strip()
        except UnicodeDecodeError:
            return "ERROR: Invalid encoding"

        print(query)

        try:
            if re.search("^INCR", query):
                match = re.findall(r"^INCR (\w+)$", query)
                if not match:
                    return "ERROR: Invalid INCR syntax"
                key = match[0]
                return self._incr(key)
            elif re.search("^DECR", query):
                match = re.findall(r"^DECR (\w+)$", query)
                if not match:
                    return "ERROR: Invalid DECR syntax"
                key = match[0]
                return self._decr(key)
            elif re.search("^GET", query):
                match = re.findall(r"^GET (\w+)$", query)
                if not match:
                    return "ERROR: Invalid GET syntax"
                key = match[0]
                return self._get(key)
            elif re.search("^SET", query):
                match = re.findall(r"^SET (\w+) (.+)$", query)
                if not match:
                    return "ERROR: Invalid SET syntax"
                key, value = match[0]
                return self._set(key, value)
            elif re.search("^LPUSH", query):
                match = re.findall(r"^LPUSH (\w+) (.+)$", query)
                if not match:
                    return "ERROR: Invalid LPUSH syntax"
                key, value = match[0]
                return self._lpush(key, value)
            elif re.search("^RPUSH", query):
                match = re.findall(r"^RPUSH (\w+) (.+)$", query)
                if not match:
                    return "ERROR: Invalid RPUSH syntax"
                key, value = match[0]
                return self._rpush(key, value)
            else:
                return "ERROR: Unknown command"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def __interpret(self, value: str):
        if re.search(r"^\d+(\.\d+)*", value):
            if re.search(r"\.", value):
                return float(value)
            else:
                return int(value)
        elif re.search(r"\".+\"", value):
            return value[1:len(value) - 1]
        else:
            return value
        
    def _incr(self, key: str):
        if key not in self._storage:
            self._storage[key] = 0
        try:
            current_val = self._storage[key]
            if not isinstance(current_val, (int, float)):
                return "ERROR: Value is not a number"
            self._storage[key] += 1
            return self._storage[key]
        except (TypeError, ValueError):
            return "ERROR: Cannot increment non-numeric value"
    
    def _decr(self, key: str):
        if key not in self._storage:
            self._storage[key] = 0
        try:
            current_val = self._storage[key]
            if not isinstance(current_val, (int, float)):
                return "ERROR: Value is not a number"
            self._storage[key] -= 1
            return self._storage[key]
        except (TypeError, ValueError):
            return "ERROR: Cannot decrement non-numeric value"

    def _get(self, key: str):
        return self._storage.get(key, None)
    
    def _set(self, key: str, value: str):
        self._storage[key] = self.__interpret(value)
        return self._storage[key]
    
    def _lpush(self, key: str, value: str):
        filtered = [self.__interpret(item) for item in value.split()]
        if self._storage.get(key):
            self._storage[key] = filtered[::-1] + self._storage[key]
        else:
            self._storage[key] = filtered[::-1]
        return self._storage[key]
    
    def _rpush(self, key: str, value: str):
        filtered = [self.__interpret(item) for item in value.split()]
        if self._storage.get(key):
            self._storage[key] += filtered
        else:
            self._storage[key] = filtered
        return self._storage[key]

class Server:
    HOST = socket.gethostbyname("localhost")
    PORT = 6543

    def __init__(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.HOST, self.PORT))
        self._db = Database()

    def handle_client(self, conn: socket.socket, addr):
        print(f"Client connected from {addr}")
        try:
            with conn:
                while True:
                    try:
                        query = conn.recv(1024)
                        if not query:
                            print(f"Client {addr} disconnected")
                            break
                        res = self._db.parse(query)
                        conn.sendall(bytes(str(res), "utf-8"))
                    except ConnectionResetError:
                        print(f"Client {addr} reset connection")
                        break
                    except socket.error as e:
                        print(f"Socket error with client {addr}: {e}")
                        break
        except Exception as e:
            print(f"Error handling client {addr}: {e}")


    def initialize(self):
        self._server.listen(10)
        while True:
            conn, addr = self._server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def close(self):
        self._server.close()

if __name__ == "__main__":
    server = Server()
    db = Database()
    try:
        server.initialize()
    except KeyboardInterrupt:
        server.close()