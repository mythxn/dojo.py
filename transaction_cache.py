"""
PROBLEM: Transaction Cache (15-20 minutes)

BUSINESS CONTEXT:
Your payment system needs to cache recent transactions for quick lookup.
Users frequently check "did my payment go through?" so you need fast access.

REQUIREMENTS:
1. Store transactions with automatic expiration (TTL)
2. O(1) get/put operations
3. LRU eviction when cache is full
4. Thread-safe for concurrent access
5. Return transaction status and metadata

FOLLOW-UP QUESTIONS:
- How do you handle cache misses?
- What happens when a transaction is updated?
- How do you ensure data consistency with the database?
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import threading


@dataclass
class Transaction:
    id: str
    amount: float
    currency: str
    status: str  # 'pending', 'completed', 'failed'
    created_at: datetime
    metadata: Dict[str, Any]


class TransactionCache:
    """LRU cache with TTL for transaction data."""
    
    def __init__(self, max_size: int, ttl_seconds: int):
        """
        Initialize transaction cache.
        
        Args:
            max_size: Maximum number of transactions to cache
            ttl_seconds: Time-to-live for cached transactions
        """
        # TODO: Implement cache initialization
        pass
    
    def put(self, transaction: Transaction) -> None:
        """
        Store transaction in cache.
        
        Args:
            transaction: Transaction object to cache
        """
        # TODO: Implement put logic with LRU and TTL
        pass
    
    def get(self, transaction_id: str) -> Optional[Transaction]:
        """
        Retrieve transaction from cache.
        
        Args:
            transaction_id: ID of transaction to retrieve
            
        Returns:
            Transaction if found and not expired, None otherwise
        """
        # TODO: Implement get logic with TTL check
        pass
    
    def update_status(self, transaction_id: str, new_status: str) -> bool:
        """
        Update transaction status if it exists in cache.
        
        Args:
            transaction_id: ID of transaction to update
            new_status: New status to set
            
        Returns:
            True if updated, False if not found
        """
        # TODO: Implement status update
        pass
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache statistics (hits, misses, size, etc.)."""
        # TODO: Implement stats collection
        pass


# Example usage and test cases
if __name__ == "__main__":
    cache = TransactionCache(max_size=100, ttl_seconds=300)  # 5 minutes TTL
    
    # Create test transaction
    txn = Transaction(
        id="txn_123",
        amount=50.00,
        currency="USD",
        status="pending",
        created_at=datetime.now(),
        metadata={"user_id": "user_456", "payment_method": "card"}
    )
    
    # Test put/get
    cache.put(txn)
    retrieved = cache.get("txn_123")
    print(f"Retrieved: {retrieved}")
    
    # Test status update
    updated = cache.update_status("txn_123", "completed")
    print(f"Updated: {updated}")
    
    # Test cache miss
    missing = cache.get("txn_999")
    print(f"Missing: {missing}")
    
    # Test stats
    stats = cache.get_cache_stats()
    print(f"Stats: {stats}")