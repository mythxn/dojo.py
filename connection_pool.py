"""
PROBLEM: Database Connection Pool (15-20 minutes)

BUSINESS CONTEXT:
Your payment system makes frequent database calls. Creating new connections
is expensive, but keeping too many open wastes resources. Implement a
connection pool to manage database connections efficiently.

REQUIREMENTS:
1. Pool with configurable min/max connections
2. Thread-safe connection checkout/checkin
3. Connection health checks and recovery
4. Timeout when pool is exhausted
5. Metrics for monitoring pool health

FOLLOW-UP QUESTIONS:
- How do you handle connection timeouts?
- What happens if a connection dies while in use?
- How do you scale the pool dynamically?
- How do you detect and recover from database failures?
"""

from dataclasses import dataclass
from typing import Optional, List, Protocol
from datetime import datetime, timedelta
import threading
import time
import queue
from contextlib import contextmanager


class DatabaseConnection(Protocol):
    """Protocol for database connection interface."""
    
    def execute(self, query: str) -> List[dict]:
        """Execute a database query."""
        ...
    
    def is_alive(self) -> bool:
        """Check if connection is still valid."""
        ...
    
    def close(self) -> None:
        """Close the connection."""
        ...


@dataclass
class PoolConfig:
    min_connections: int = 2
    max_connections: int = 10
    connection_timeout_seconds: int = 30
    idle_timeout_seconds: int = 300
    health_check_interval_seconds: int = 60


@dataclass
class PooledConnection:
    connection: DatabaseConnection
    created_at: datetime
    last_used: datetime
    checkout_count: int = 0
    
    def is_expired(self, idle_timeout: timedelta) -> bool:
        """Check if connection has been idle too long."""
        return datetime.now() - self.last_used > idle_timeout


class ConnectionPool:
    """Thread-safe database connection pool."""
    
    def __init__(self, connection_factory: callable, config: PoolConfig):
        """
        Initialize connection pool.
        
        Args:
            connection_factory: Function that creates new database connections
            config: Pool configuration parameters
        """
        # TODO: Initialize connection pool
        pass
    
    def get_connection(self, timeout_seconds: Optional[int] = None) -> DatabaseConnection:
        """
        Get connection from pool.
        
        Args:
            timeout_seconds: Maximum time to wait for connection
            
        Returns:
            Database connection
            
        Raises:
            TimeoutError: If no connection available within timeout
        """
        # TODO: Implement connection checkout
        pass
    
    def return_connection(self, connection: DatabaseConnection) -> None:
        """
        Return connection to pool.
        
        Args:
            connection: Connection to return to pool
        """
        # TODO: Implement connection checkin
        pass
    
    @contextmanager
    def connection(self):
        """Context manager for automatic connection management."""
        # TODO: Implement context manager
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_stats(self) -> dict:
        """Get pool statistics."""
        # TODO: Return pool stats (active, idle, total, etc.)
        pass
    
    def close_all(self) -> None:
        """Close all connections and shutdown pool."""
        # TODO: Implement pool shutdown
        pass
    
    def _create_connection(self) -> PooledConnection:
        """Create new pooled connection."""
        # TODO: Create and wrap new connection
        pass
    
    def _validate_connection(self, pooled_conn: PooledConnection) -> bool:
        """Check if connection is still valid."""
        # TODO: Validate connection health
        pass
    
    def _cleanup_expired_connections(self) -> None:
        """Remove expired connections from pool."""
        # TODO: Clean up idle connections
        pass
    
    def _health_check_loop(self) -> None:
        """Background thread for connection health checks."""
        # TODO: Implement health check background task
        pass


# Mock database connection for testing
class MockDatabaseConnection:
    """Mock database connection for testing."""
    
    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.is_closed = False
        self.query_count = 0
    
    def execute(self, query: str) -> List[dict]:
        """Execute mock query."""
        if self.is_closed:
            raise ConnectionError("Connection is closed")
        
        self.query_count += 1
        time.sleep(0.01)  # Simulate query time
        
        return [{"result": f"Query result for: {query}"}]
    
    def is_alive(self) -> bool:
        """Check if connection is alive."""
        return not self.is_closed
    
    def close(self) -> None:
        """Close connection."""
        self.is_closed = True
    
    def __str__(self):
        return f"MockConnection({self.connection_id})"


def create_mock_connection() -> MockDatabaseConnection:
    """Factory function for creating mock connections."""
    import uuid
    return MockDatabaseConnection(f"conn_{uuid.uuid4().hex[:8]}")


# Example usage and test cases
if __name__ == "__main__":
    # Configure connection pool
    config = PoolConfig(
        min_connections=2,
        max_connections=5,
        connection_timeout_seconds=10,
        idle_timeout_seconds=60
    )
    
    # Create connection pool
    pool = ConnectionPool(create_mock_connection, config)
    
    # Test basic connection checkout/checkin
    try:
        conn1 = pool.get_connection()
        print(f"Got connection: {conn1}")
        
        # Use connection
        result = conn1.execute("SELECT * FROM payments")
        print(f"Query result: {result}")
        
        # Return connection
        pool.return_connection(conn1)
        print("Returned connection")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test context manager
    try:
        with pool.connection() as conn:
            result = conn.execute("SELECT COUNT(*) FROM transactions")
            print(f"Context manager result: {result}")
    except Exception as e:
        print(f"Context manager error: {e}")
    
    # Test multiple concurrent connections
    def worker_thread(worker_id: int):
        try:
            with pool.connection() as conn:
                result = conn.execute(f"SELECT * FROM worker_{worker_id}")
                print(f"Worker {worker_id}: {result}")
                time.sleep(0.1)  # Simulate work
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
    
    # Start multiple workers
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for workers to complete
    for thread in threads:
        thread.join()
    
    # Show pool statistics
    stats = pool.get_stats()
    print(f"Pool stats: {stats}")
    
    # Clean up
    pool.close_all()
    print("Pool closed")