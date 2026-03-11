import unittest
import threading
import time
import socket
from server import Server
from client import RedisClient


class TestRedisIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the server in a separate thread"""
        cls.server = Server()
        cls.server_thread = threading.Thread(target=cls.server.initialize, daemon=True)
        cls.server_thread.start()

        # Wait a moment for the server to start
        time.sleep(0.5)

        # Verify server is running by trying to connect
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.connect((Server.HOST, Server.PORT))
                test_socket.close()
                break
            except ConnectionRefusedError:
                if attempt == max_attempts - 1:
                    raise Exception("Server failed to start")
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        """Clean up server"""
        if hasattr(cls, 'server'):
            cls.server.close()

    def test_client_set_and_get(self):
        """Test basic SET and GET operations through client"""
        with RedisClient() as client:
            result = client.set("testkey", "testvalue")
            self.assertEqual(result, "testvalue")

            result = client.get("testkey")
            self.assertEqual(result, "testvalue")

    def test_client_get_nonexistent(self):
        """Test GET on non-existent key"""
        with RedisClient() as client:
            result = client.get("nonexistent_key_12345")
            self.assertIsNone(result)

    def test_client_incr_operations(self):
        """Test INCR operations through client"""
        with RedisClient() as client:
            # INCR on new key
            result = client.incr("counter1")
            self.assertEqual(result, "1")

            # INCR on existing key
            result = client.incr("counter1")
            self.assertEqual(result, "2")

    def test_client_decr_operations(self):
        """Test DECR operations through client"""
        with RedisClient() as client:
            # DECR on new key
            result = client.decr("counter2")
            self.assertEqual(result, "-1")

            # DECR on existing key
            result = client.decr("counter2")
            self.assertEqual(result, "-2")

    def test_client_incr_decr_sequence(self):
        """Test sequence of INCR and DECR operations"""
        with RedisClient() as client:
            client.set("mycounter", "10")

            # Increment
            result = client.incr("mycounter")
            self.assertEqual(result, "11")

            # Decrement
            result = client.decr("mycounter")
            self.assertEqual(result, "10")

    def test_client_list_operations(self):
        """Test LPUSH and RPUSH operations through client"""
        with RedisClient() as client:
            # LPUSH
            result = client.lpush("mylist", "a", "b", "c")
            self.assertIn("c", result)
            self.assertIn("b", result)
            self.assertIn("a", result)

            # RPUSH
            result = client.rpush("mylist2", "x", "y", "z")
            self.assertIn("x", result)
            self.assertIn("y", result)
            self.assertIn("z", result)

    def test_client_numeric_types(self):
        """Test numeric value handling"""
        with RedisClient() as client:
            # Integer
            client.set("int_val", "42")
            result = client.get("int_val")
            self.assertEqual(result, "42")

            # Float
            client.set("float_val", "3.14")
            result = client.get("float_val")
            self.assertEqual(result, "3.14")

    def test_client_error_handling(self):
        """Test client error handling"""
        with RedisClient() as client:
            # Test INCR on non-numeric value
            client.set("text_key", "hello")
            result = client.incr("text_key")
            self.assertIn("ERROR", result)

            # Test DECR on non-numeric value
            result = client.decr("text_key")
            self.assertIn("ERROR", result)

    def test_client_validation(self):
        """Test client input validation"""
        with RedisClient() as client:
            # Empty key should raise ValueError
            with self.assertRaises(ValueError):
                client.get("")

            with self.assertRaises(ValueError):
                client.set("", "value")

            with self.assertRaises(ValueError):
                client.incr("")

            with self.assertRaises(ValueError):
                client.decr("")

            # Empty values for list operations
            with self.assertRaises(ValueError):
                client.lpush("mylist")

            with self.assertRaises(ValueError):
                client.rpush("mylist")

    def test_multiple_clients(self):
        """Test that multiple clients can connect simultaneously"""
        clients = []
        try:
            # Create multiple clients
            for i in range(5):
                client = RedisClient()
                clients.append(client)
                client.set(f"client_{i}_key", f"client_{i}_value")

            # Verify each client can retrieve its data
            for i, client in enumerate(clients):
                result = client.get(f"client_{i}_key")
                self.assertEqual(result, f"client_{i}_value")

        finally:
            # Clean up clients
            for client in clients:
                client.close()

    def test_client_context_manager(self):
        """Test client context manager functionality"""
        # Test successful operation
        with RedisClient() as client:
            result = client.set("context_key", "context_value")
            self.assertEqual(result, "context_value")

        # Verify the connection is closed after exiting context
        # (client should be closed, but we can't easily test this directly)

    def test_server_persistence_across_connections(self):
        """Test that data persists across different client connections"""
        # Set data with one client
        with RedisClient() as client1:
            client1.set("persistent_key", "persistent_value")

        # Retrieve data with a different client
        with RedisClient() as client2:
            result = client2.get("persistent_key")
            self.assertEqual(result, "persistent_value")

    def test_large_data_transfer(self):
        """Test handling of larger data values"""
        large_value = "x" * 500  # 500 character string

        with RedisClient() as client:
            result = client.set("large_key", large_value)
            self.assertEqual(result, large_value)

            result = client.get("large_key")
            self.assertEqual(result, large_value)


class TestRedisClientConnectivity(unittest.TestCase):
    """Test client connectivity edge cases"""

    def test_connection_refused(self):
        """Test behavior when server is not available"""
        # Try to connect to a port where no server is running
        original_port = RedisClient.PORT
        RedisClient.PORT = 9999  # Assuming nothing is running on this port

        try:
            with self.assertRaises(ConnectionError):
                RedisClient()
        finally:
            RedisClient.PORT = original_port

    def test_connection_timeout(self):
        """Test connection with very short timeout"""
        # This test is harder to implement reliably without a slow server
        # but we can test that the timeout parameter is accepted
        try:
            client = RedisClient(timeout=1)
            client.close()
        except ConnectionError:
            # If server is not available, that's expected
            pass


if __name__ == '__main__':
    unittest.main()