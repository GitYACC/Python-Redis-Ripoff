#!/usr/bin/env python3
"""
Demonstration of the Redis-like database implementation.
Run this after starting the server with: python3 server.py
"""

import time
from client import RedisClient


def demo_string_operations():
    """Demonstrate string operations."""
    print("=== String Operations ===")
    with RedisClient() as client:
        # SET and GET
        client.set("name", "Alice")
        print(f"SET name Alice -> GET name: {client.get('name').decode()}")

        # Numbers
        client.set("age", "25")
        print(f"SET age 25 -> GET age: {client.get('age').decode()}")

        # INCR and DECR
        client.set("counter", "10")
        print(f"Initial counter: {client.get('counter').decode()}")
        client.incr("counter")
        print(f"After INCR: {client.get('counter').decode()}")
        client.decr("counter")
        client.decr("counter")
        print(f"After 2 DECR: {client.get('counter').decode()}")

        # EXISTS and DEL
        print(f"EXISTS name: {client.exists('name').decode()}")
        client.delete("name")
        print(f"After DEL name, EXISTS name: {client.exists('name').decode()}")


def demo_list_operations():
    """Demonstrate list operations."""
    print("\n=== List Operations ===")
    with RedisClient() as client:
        # LPUSH and RPUSH
        client.lpush("fruits", "apple", "banana")
        print(f"After LPUSH fruits apple banana, LLEN: {client.llen('fruits').decode()}")

        client.rpush("fruits", "orange", "grape")
        print(f"After RPUSH fruits orange grape, LLEN: {client.llen('fruits').decode()}")

        # List access
        print(f"LINDEX fruits 0: {client.lindex('fruits', 0).decode()}")
        print(f"LINDEX fruits -1: {client.lindex('fruits', -1).decode()}")

        # LRANGE
        result = client.lrange("fruits", 0, -1)
        print(f"LRANGE fruits 0 -1: {result.decode()}")

        # LPOP and RPOP
        popped = client.lpop("fruits")
        print(f"LPOP fruits: {popped.decode()}")
        popped = client.rpop("fruits")
        print(f"RPOP fruits: {popped.decode()}")

        print(f"Final LLEN fruits: {client.llen('fruits').decode()}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n=== Error Handling ===")
    with RedisClient() as client:
        # Non-existent key
        result = client.get("nonexistent")
        print(f"GET nonexistent: {result.decode()}")

        # Type mismatch
        client.set("text", "hello")
        result = client.incr("text")
        print(f"INCR on string: {result.decode()}")

        # List operations on non-list
        result = client.lpush("text", "item")
        print(f"LPUSH on string: {result.decode()}")


if __name__ == "__main__":
    print("Redis-like Database Demo")
    print("Make sure to start the server first: python3 server.py")

    try:
        demo_string_operations()
        demo_list_operations()
        demo_error_handling()
        print("\nDemo completed successfully!")
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Make sure to run 'python3 server.py' first.")
    except Exception as e:
        print(f"Error during demo: {e}")