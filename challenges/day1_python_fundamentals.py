"""
Day 1 Challenge 1: Python Fundamentals Assessment
================================================

Test your Python skills with these core concepts.
Complete each function and run the file to test your solutions.

Topics: Functions, decorators, context managers, generators
"""
import sqlite3
import time


# Challenge 1: Decorator Implementation
def timing_decorator(func):
    """Create a decorator that measures and prints execution time"""
    def wrapper():
        start_time = time.time()
        func()
        end_time = time.time()
        print(f"Execution took {end_time - start_time} seconds.")
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(0.1)
    return "completed"

# Challenge 2: Context Manager
class DatabaseConnection:
    """Implement a context manager for database connections"""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        print("Connecting to database...")
        self.connection = f"connected to database {self.db_name}"
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting from database...")
        self.connection = None


# Challenge 3: Generator Function
def fibonacci_generator(n):
    """Generate fibonacci sequence up to n numbers"""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1


# Challenge 4: List Comprehension with Filtering
def process_data(data_list):
    """
    Filter and transform data:
    - Keep only positive numbers
    - Square each number
    - Return as list
    """
    return [x * x for x in data_list if x > 0]


# Test your implementations
if __name__ == "__main__":
    print("Testing Python Fundamentals...")
    
    # Test 1: Decorator
    print("\n1. Testing timing decorator:")
    result = slow_function()
    
    # Test 2: Context Manager
    print("\n2. Testing context manager:")
    with DatabaseConnection("test_db") as db:
        print(f"Connected to {db.db_name if hasattr(db, 'db_name') else 'database'}")
    
    # Test 3: Generator
    print("\n3. Testing fibonacci generator:")
    fib_gen = fibonacci_generator(8)
    fib_list = list(fib_gen)
    print(f"Fibonacci sequence: {fib_list}")
    
    # Test 4: List comprehension
    print("\n4. Testing data processing:")
    test_data = [-2, -1, 0, 1, 2, 3, 4, 5]
    processed = process_data(test_data)
    print(f"Processed data: {processed}")
    
    print("\n✅ All tests completed! Check your implementations.")
