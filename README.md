# REDIS-like Database in Python

A comprehensive implementation of a Redis-like database utilizing sockets and threading. Works in the same way as Redis CLI, where commands can be sent to the server to execute actions. An interface in the form of the class `RedisClient` for this CLI implementation is included in `client.py`.

## Features

### Data Types Supported
- **Strings** - Basic key-value storage with automatic type interpretation
- **Numbers** - Integers and floats with arithmetic operations
- **Lists** - Dynamic arrays with push/pop operations

### Commands Implemented

#### String Operations
- `SET key value` - Set a key to a value
- `GET key` - Get the value of a key
- `INCR key` - Increment a numeric value (creates if doesn't exist)
- `DECR key` - Decrement a numeric value (creates if doesn't exist)
- `DEL key [key ...]` - Delete one or more keys
- `EXISTS key` - Check if a key exists

#### List Operations
- `LPUSH key element [element ...]` - Add elements to the head of a list
- `RPUSH key element [element ...]` - Add elements to the tail of a list
- `LPOP key` - Remove and return the first element of a list
- `RPOP key` - Remove and return the last element of a list
- `LLEN key` - Get the length of a list
- `LINDEX key index` - Get an element from a list by index
- `LRANGE key start stop` - Get a range of elements from a list

## Usage

### Starting the Server
```bash
python3 server.py
```

### Using the Client
```python
from client import RedisClient

# Context manager for automatic connection cleanup
with RedisClient() as client:
    # String operations
    client.set("mykey", "1")
    print(client.get("mykey"))  # b'1'

    client.incr("mykey")
    print(client.get("mykey"))  # b'2'

    # List operations
    client.lpush("fruits", "apple", "banana")
    print(client.llen("fruits"))  # b'2'

    client.rpush("fruits", "orange")
    print(client.lpop("fruits"))  # b'banana'
```

### Running Tests
```bash
python3 test_redis.py
```

### Running Demo
```bash
python3 demo.py
```

## Architecture

- **Server (`server.py`)**: Multi-threaded socket server handling concurrent client connections
- **Database**: In-memory storage with command parsing and execution
- **Client (`client.py`)**: Python interface with connection management and context manager support
- **Error Handling**: Proper Redis-like error messages for type mismatches and invalid operations
- **Testing**: Comprehensive test suite with 28+ tests covering all functionality

## Error Handling

The implementation includes proper error handling for:
- Non-existent keys (returns `(nil)`)
- Type mismatches (e.g., running INCR on a string)
- Invalid commands
- Empty lists
- Index out of bounds
