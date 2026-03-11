import unittest
from server import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Create a fresh Database instance for each test"""
        self.db = Database()

    def test_set_and_get_string(self):
        """Test SET and GET operations with string values"""
        result = self.db.parse(b'SET mykey "hello"')
        self.assertEqual(result, "hello")

        result = self.db.parse(b'GET mykey')
        self.assertEqual(result, "hello")

    def test_set_and_get_integer(self):
        """Test SET and GET operations with integer values"""
        result = self.db.parse(b'SET mynum 42')
        self.assertEqual(result, 42)

        result = self.db.parse(b'GET mynum')
        self.assertEqual(result, 42)

    def test_set_and_get_float(self):
        """Test SET and GET operations with float values"""
        result = self.db.parse(b'SET myfloat 3.14')
        self.assertEqual(result, 3.14)

        result = self.db.parse(b'GET myfloat')
        self.assertEqual(result, 3.14)

    def test_get_nonexistent_key(self):
        """Test GET on a key that doesn't exist"""
        result = self.db.parse(b'GET nonexistent')
        self.assertIsNone(result)

    def test_incr_new_key(self):
        """Test INCR on a new key (should start at 0)"""
        result = self.db.parse(b'INCR newcounter')
        self.assertEqual(result, 1)

    def test_incr_existing_key(self):
        """Test INCR on an existing numeric key"""
        self.db.parse(b'SET counter 5')
        result = self.db.parse(b'INCR counter')
        self.assertEqual(result, 6)

    def test_incr_non_numeric_key(self):
        """Test INCR on a non-numeric key (should return error)"""
        self.db.parse(b'SET textkey hello')
        result = self.db.parse(b'INCR textkey')
        self.assertIn("ERROR", str(result))

    def test_decr_new_key(self):
        """Test DECR on a new key (should start at 0)"""
        result = self.db.parse(b'DECR newcounter')
        self.assertEqual(result, -1)

    def test_decr_existing_key(self):
        """Test DECR on an existing numeric key"""
        self.db.parse(b'SET counter 5')
        result = self.db.parse(b'DECR counter')
        self.assertEqual(result, 4)

    def test_decr_non_numeric_key(self):
        """Test DECR on a non-numeric key (should return error)"""
        self.db.parse(b'SET textkey hello')
        result = self.db.parse(b'DECR textkey')
        self.assertIn("ERROR", str(result))

    def test_lpush_new_list(self):
        """Test LPUSH on a new list"""
        result = self.db.parse(b'LPUSH mylist 1 2 3')
        self.assertEqual(result, [3, 2, 1])

    def test_lpush_existing_list(self):
        """Test LPUSH on an existing list"""
        self.db.parse(b'LPUSH mylist 1 2')
        result = self.db.parse(b'LPUSH mylist 3 4')
        self.assertEqual(result, [4, 3, 2, 1])

    def test_rpush_new_list(self):
        """Test RPUSH on a new list"""
        result = self.db.parse(b'RPUSH mylist 1 2 3')
        self.assertEqual(result, [1, 2, 3])

    def test_rpush_existing_list(self):
        """Test RPUSH on an existing list"""
        self.db.parse(b'RPUSH mylist 1 2')
        result = self.db.parse(b'RPUSH mylist 3 4')
        self.assertEqual(result, [1, 2, 3, 4])

    def test_mixed_data_types(self):
        """Test storing different data types"""
        self.db.parse(b'SET string_key "hello"')
        self.db.parse(b'SET int_key 42')
        self.db.parse(b'SET float_key 3.14')
        self.db.parse(b'LPUSH list_key 1 2 3')

        self.assertEqual(self.db.parse(b'GET string_key'), "hello")
        self.assertEqual(self.db.parse(b'GET int_key'), 42)
        self.assertEqual(self.db.parse(b'GET float_key'), 3.14)
        self.assertEqual(self.db._get("list_key"), [3, 2, 1])

    def test_invalid_commands(self):
        """Test invalid command handling"""
        result = self.db.parse(b'INVALID command')
        self.assertIn("ERROR", str(result))

        result = self.db.parse(b'SET')  # Missing arguments
        self.assertIn("ERROR", str(result))

        result = self.db.parse(b'GET')  # Missing arguments
        self.assertIn("ERROR", str(result))

        result = self.db.parse(b'INCR')  # Missing arguments
        self.assertIn("ERROR", str(result))

    def test_unicode_handling(self):
        """Test handling of invalid unicode"""
        # Create invalid bytes that can't be decoded as UTF-8
        invalid_bytes = b'\xff\xfe'
        result = self.db.parse(invalid_bytes)
        self.assertIn("ERROR", str(result))

    def test_empty_command(self):
        """Test handling of empty commands"""
        result = self.db.parse(b'')
        self.assertIn("ERROR", str(result))

    def test_whitespace_handling(self):
        """Test commands with extra whitespace"""
        result = self.db.parse(b'  SET mykey value  ')
        self.assertEqual(result, "value")

        result = self.db.parse(b'  GET mykey  ')
        self.assertEqual(result, "value")


if __name__ == '__main__':
    unittest.main()