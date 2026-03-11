import socket
import threading
import re

"""
strings / numbers:
    INCR value      => increments value or creates value if not already created
    DECR value      => decrements value or creates value if not already created
    GET key         => returns value associated with key
    SET key value   => sets key value pair
    DEL key [key ...] => delete one or more keys
    EXISTS key      => check if key exists

lists:
    LPUSH list ...  => appends one or more items to head of list
    RPUSH list ...  => appends one or more items to tail of list
    LPOP list       => remove and return first element from list
    RPOP list       => remove and return last element from list
    LLEN list       => return length of list
    LINDEX list index => get element at index
    LRANGE list start stop => get range of elements
"""

class Database:
    def __init__(self):
        self._storage = {}

    def parse(self, query: bytes):
        query = query.decode("utf-8")

        print(query)
        if re.search("^INCR", query):
            key = re.findall(r"^INCR (\w+)", query)[0]
            return self._incr(key)
        elif re.search("^DECR", query):
            key = re.findall(r"^DECR (\w+)", query)[0]
            return self._decr(key)
        elif re.search("^GET", query):
            key = re.findall(r"GET (\w+)", query)[0]
            return self._get(key)
        elif re.search("^SET", query):
            kvpair = re.findall(r"SET (\w+) ([^\s]+|\".+\")", query)[0]
            return self._set(*kvpair)
        elif re.search("^LPUSH", query):
            ls = re.findall(r"LPUSH (\w+) (.+)", query)[0]
            return self._lpush(*ls)
        elif re.search("^RPUSH", query):
            ls = re.findall(r"RPUSH (\w+) (.+)", query)[0]
            return self._rpush(*ls)
        elif re.search("^DEL", query):
            keys = re.findall(r"DEL (.+)", query)[0].split()
            return self._del(*keys)
        elif re.search("^EXISTS", query):
            key = re.findall(r"EXISTS (\w+)", query)[0]
            return self._exists(key)
        elif re.search("^LPOP", query):
            key = re.findall(r"LPOP (\w+)", query)[0]
            return self._lpop(key)
        elif re.search("^RPOP", query):
            key = re.findall(r"RPOP (\w+)", query)[0]
            return self._rpop(key)
        elif re.search("^LLEN", query):
            key = re.findall(r"LLEN (\w+)", query)[0]
            return self._llen(key)
        elif re.search("^LINDEX", query):
            match = re.findall(r"LINDEX (\w+) (-?\d+)", query)[0]
            return self._lindex(match[0], int(match[1]))
        elif re.search("^LRANGE", query):
            match = re.findall(r"LRANGE (\w+) (-?\d+) (-?\d+)", query)[0]
            return self._lrange(match[0], int(match[1]), int(match[2]))
        else:
            return "ERR unknown command"

    def __interpret(self, value: str):
        if re.search(r"^\d+(\.\d+)?$", value):
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
        elif not isinstance(self._storage[key], (int, float)):
            return "ERR value is not an integer or out of range"
        self._storage[key] += 1
        return self._storage[key]

    def _decr(self, key: str):
        if key not in self._storage:
            self._storage[key] = 0
        elif not isinstance(self._storage[key], (int, float)):
            return "ERR value is not an integer or out of range"
        self._storage[key] -= 1
        return self._storage[key]

    def _get(self, key: str):
        return self._storage.get(key, "(nil)")
    
    def _set(self, key: str, value: str):
        self._storage[key] = self.__interpret(value)
        return self._storage[key]
    
    def _lpush(self, key: str, value: str):
        filtered = [self.__interpret(item) for item in value.split()]
        if self._storage.get(key):
            if not isinstance(self._storage[key], list):
                return "WRONGTYPE Operation against a key holding the wrong kind of value"
            self._storage[key] = filtered[::-1] + self._storage[key]
        else:
            self._storage[key] = filtered[::-1]
        return len(self._storage[key])
    
    def _rpush(self, key: str, value: str):
        filtered = [self.__interpret(item) for item in value.split()]
        if self._storage.get(key):
            if not isinstance(self._storage[key], list):
                return "WRONGTYPE Operation against a key holding the wrong kind of value"
            self._storage[key] += filtered
        else:
            self._storage[key] = filtered
        return len(self._storage[key])

    def _del(self, *keys):
        count = 0
        for key in keys:
            if key in self._storage:
                del self._storage[key]
                count += 1
        return count

    def _exists(self, key: str):
        return 1 if key in self._storage else 0

    def _lpop(self, key: str):
        if key not in self._storage:
            return "(nil)"
        if not isinstance(self._storage[key], list):
            return "WRONGTYPE Operation against a key holding the wrong kind of value"
        if not self._storage[key]:
            return "(nil)"
        return self._storage[key].pop(0)

    def _rpop(self, key: str):
        if key not in self._storage:
            return "(nil)"
        if not isinstance(self._storage[key], list):
            return "WRONGTYPE Operation against a key holding the wrong kind of value"
        if not self._storage[key]:
            return "(nil)"
        return self._storage[key].pop()

    def _llen(self, key: str):
        if key not in self._storage:
            return 0
        if not isinstance(self._storage[key], list):
            return "WRONGTYPE Operation against a key holding the wrong kind of value"
        return len(self._storage[key])

    def _lindex(self, key: str, index: int):
        if key not in self._storage:
            return "(nil)"
        if not isinstance(self._storage[key], list):
            return "WRONGTYPE Operation against a key holding the wrong kind of value"
        try:
            return self._storage[key][index]
        except IndexError:
            return "(nil)"

    def _lrange(self, key: str, start: int, stop: int):
        if key not in self._storage:
            return []
        if not isinstance(self._storage[key], list):
            return "WRONGTYPE Operation against a key holding the wrong kind of value"

        # Redis LRANGE behavior: negative indices count from the end
        lst = self._storage[key]
        if stop == -1:
            return lst[start:]
        else:
            return lst[start:stop+1]

class Server:
    HOST = socket.gethostbyname("localhost")
    PORT = 6543

    def __init__(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.HOST, self.PORT))
        self._db = Database()

    def handle_client(self, conn: socket.socket, addr):
        with conn:
            while True:
                query = conn.recv(1024)
                if not query:
                    break
                res = self._db.parse(query)
                conn.sendall(bytes(str(res), "utf-8"))


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