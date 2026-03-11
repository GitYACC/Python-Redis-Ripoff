#!/usr/bin/env python3
"""
Comprehensive test suite for Redis-like database implementation.
"""

import unittest
import threading
import time
import socket
from server import Database, Server
from client import RedisClient


class TestDatabase(unittest.TestCase):
    """Test the Database class directly."""

    def setUp(self):
        self.db = Database()

    def test_set_get_string(self):
        """Test SET and GET operations with strings."""
        result = self.db.parse(b'SET name "John"')
        self.assertEqual(result, "John")

        result = self.db.parse(b'GET name')
        self.assertEqual(result, "John")

    def test_set_get_number(self):
        """Test SET and GET operations with numbers."""
        self.db.parse(b'SET count 42')
        result = self.db.parse(b'GET count')
        self.assertEqual(result, 42)

        self.db.parse(b'SET price 19.99')
        result = self.db.parse(b'GET price')
        self.assertEqual(result, 19.99)

    def test_get_nonexistent_key(self):
        """Test GET with non-existent key returns nil."""
        result = self.db.parse(b'GET nonexistent')
        self.assertEqual(result, "(nil)")

    def test_incr_new_key(self):
        """Test INCR creates new key with value 1."""
        result = self.db.parse(b'INCR counter')
        self.assertEqual(result, 1)

        result = self.db.parse(b'GET counter')
        self.assertEqual(result, 1)

    def test_incr_existing_key(self):
        """Test INCR increments existing numeric key."""
        self.db.parse(b'SET counter 5')
        result = self.db.parse(b'INCR counter')
        self.assertEqual(result, 6)

    def test_incr_wrong_type(self):
        """Test INCR with non-numeric value returns error."""
        self.db.parse(b'SET name "John"')
        result = self.db.parse(b'INCR name')
        self.assertEqual(result, "ERR value is not an integer or out of range")

    def test_decr_new_key(self):
        """Test DECR creates new key with value -1."""
        result = self.db.parse(b'DECR countdown')
        self.assertEqual(result, -1)

    def test_decr_existing_key(self):
        """Test DECR decrements existing numeric key."""
        self.db.parse(b'SET countdown 10')
        result = self.db.parse(b'DECR countdown')
        self.assertEqual(result, 9)

    def test_del_single_key(self):
        """Test DEL removes a single key."""
        self.db.parse(b'SET key1 "value1"')
        result = self.db.parse(b'DEL key1')
        self.assertEqual(result, 1)

        result = self.db.parse(b'GET key1')
        self.assertEqual(result, "(nil)")

    def test_del_multiple_keys(self):
        """Test DEL removes multiple keys."""
        self.db.parse(b'SET key1 "value1"')
        self.db.parse(b'SET key2 "value2"')
        self.db.parse(b'SET key3 "value3"')

        result = self.db.parse(b'DEL key1 key2 nonexistent')
        self.assertEqual(result, 2)

    def test_exists(self):
        """Test EXISTS command."""
        self.db.parse(b'SET mykey "value"')

        result = self.db.parse(b'EXISTS mykey')
        self.assertEqual(result, 1)

        result = self.db.parse(b'EXISTS nonexistent')
        self.assertEqual(result, 0)

    def test_lpush_new_list(self):
        """Test LPUSH creates new list."""
        result = self.db.parse(b'LPUSH mylist item1 item2 item3')
        self.assertEqual(result, 3)

        # Check the order (LPUSH adds to front, so order should be reversed)
        items = self.db._storage['mylist']
        self.assertEqual(items, ['item3', 'item2', 'item1'])

    def test_lpush_existing_list(self):
        """Test LPUSH adds to existing list."""
        self.db.parse(b'LPUSH mylist item1')
        result = self.db.parse(b'LPUSH mylist item2')
        self.assertEqual(result, 2)

        items = self.db._storage['mylist']
        self.assertEqual(items, ['item2', 'item1'])

    def test_rpush_new_list(self):
        """Test RPUSH creates new list."""
        result = self.db.parse(b'RPUSH mylist item1 item2 item3')
        self.assertEqual(result, 3)

        items = self.db._storage['mylist']
        self.assertEqual(items, ['item1', 'item2', 'item3'])

    def test_rpush_existing_list(self):
        """Test RPUSH adds to existing list."""
        self.db.parse(b'RPUSH mylist item1')
        result = self.db.parse(b'RPUSH mylist item2')
        self.assertEqual(result, 2)

        items = self.db._storage['mylist']
        self.assertEqual(items, ['item1', 'item2'])

    def test_lpop(self):
        """Test LPOP removes first element."""
        self.db.parse(b'RPUSH mylist item1 item2 item3')

        result = self.db.parse(b'LPOP mylist')
        self.assertEqual(result, 'item1')

        items = self.db._storage['mylist']
        self.assertEqual(items, ['item2', 'item3'])

    def test_lpop_empty_list(self):
        """Test LPOP on empty/non-existent list returns nil."""
        result = self.db.parse(b'LPOP nonexistent')
        self.assertEqual(result, "(nil)")

        self.db.parse(b'RPUSH empty_list item1')
        self.db.parse(b'LPOP empty_list')
        result = self.db.parse(b'LPOP empty_list')
        self.assertEqual(result, "(nil)")

    def test_rpop(self):
        """Test RPOP removes last element."""
        self.db.parse(b'RPUSH mylist item1 item2 item3')

        result = self.db.parse(b'RPOP mylist')
        self.assertEqual(result, 'item3')

        items = self.db._storage['mylist']
        self.assertEqual(items, ['item1', 'item2'])

    def test_llen(self):
        """Test LLEN returns list length."""
        result = self.db.parse(b'LLEN nonexistent')
        self.assertEqual(result, 0)

        self.db.parse(b'RPUSH mylist item1 item2 item3')
        result = self.db.parse(b'LLEN mylist')
        self.assertEqual(result, 3)

    def test_lindex(self):
        """Test LINDEX returns element at index."""
        self.db.parse(b'RPUSH mylist item1 item2 item3')

        result = self.db.parse(b'LINDEX mylist 0')
        self.assertEqual(result, 'item1')

        result = self.db.parse(b'LINDEX mylist 2')
        self.assertEqual(result, 'item3')

        result = self.db.parse(b'LINDEX mylist -1')
        self.assertEqual(result, 'item3')

        result = self.db.parse(b'LINDEX mylist 10')
        self.assertEqual(result, "(nil)")

    def test_lrange(self):
        """Test LRANGE returns range of elements."""
        self.db.parse(b'RPUSH mylist item1 item2 item3 item4 item5')

        result = self.db.parse(b'LRANGE mylist 0 2')
        self.assertEqual(result, ['item1', 'item2', 'item3'])

        result = self.db.parse(b'LRANGE mylist 1 -1')
        self.assertEqual(result, ['item2', 'item3', 'item4', 'item5'])

        result = self.db.parse(b'LRANGE nonexistent 0 -1')
        self.assertEqual(result, [])

    def test_wrong_type_operations(self):
        """Test operations on wrong data types return appropriate errors."""
        self.db.parse(b'SET mystring "hello"')

        # Try list operations on string
        result = self.db.parse(b'LPUSH mystring item')
        self.assertEqual(result, "WRONGTYPE Operation against a key holding the wrong kind of value")

        result = self.db.parse(b'LLEN mystring')
        self.assertEqual(result, "WRONGTYPE Operation against a key holding the wrong kind of value")

    def test_invalid_command(self):
        """Test invalid command returns error."""
        result = self.db.parse(b'INVALID command')
        self.assertEqual(result, "ERR unknown command")


class TestServerClient(unittest.TestCase):
    """Test the Server and Client classes together."""

    @classmethod
    def setUpClass(cls):
        """Start the server in a separate thread."""
        cls.server = Server()
        cls.server_thread = threading.Thread(target=cls.server.initialize)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Give the server time to start
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        """Close the server."""
        cls.server.close()

    def setUp(self):
        """Create a fresh client for each test."""
        self.client = RedisClient()

    def tearDown(self):
        """Clean up the client."""
        self.client.close()

    def test_client_server_set_get(self):
        """Test SET and GET through client-server communication."""
        self.client.set("testkey", "testvalue")
        result = self.client.get("testkey")
        self.assertEqual(result, b"testvalue")

    def test_client_server_incr(self):
        """Test INCR through client-server communication."""
        result = self.client.incr("counter")
        self.assertEqual(result, b"1")

        result = self.client.incr("counter")
        self.assertEqual(result, b"2")

    def test_client_server_list_operations(self):
        """Test list operations through client-server communication."""
        result = self.client.lpush("mylist", "item1", "item2")
        self.assertEqual(result, b"2")

        result = self.client.rpush("mylist", "item3")
        self.assertEqual(result, b"3")

        result = self.client.llen("mylist")
        self.assertEqual(result, b"3")

        result = self.client.lpop("mylist")
        self.assertEqual(result, b"item2")

        result = self.client.rpop("mylist")
        self.assertEqual(result, b"item3")

    def test_client_context_manager(self):
        """Test client context manager functionality."""
        with RedisClient() as client:
            client.set("ctxkey", "ctxvalue")
            result = client.get("ctxkey")
            self.assertEqual(result, b"ctxvalue")

    def test_multiple_clients(self):
        """Test multiple clients can connect simultaneously."""
        client1 = RedisClient()
        client2 = RedisClient()

        try:
            client1.set("client1key", "value1")
            client2.set("client2key", "value2")

            result1 = client1.get("client2key")  # Client1 gets key set by client2
            result2 = client2.get("client1key")  # Client2 gets key set by client1

            self.assertEqual(result1, b"value2")
            self.assertEqual(result2, b"value1")
        finally:
            client1.close()
            client2.close()


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)