"""
PROBLEM: Idempotency Handler (15-20 minutes)

BUSINESS CONTEXT:
Payment APIs must be idempotent - if a user clicks "Pay" twice due to network
issues, only one payment should process. Implement an idempotency system
using request IDs to prevent duplicate operations.

REQUIREMENTS:
1. Store operation results by idempotency key
2. Return cached result for duplicate requests
3. Handle concurrent requests with same key
4. TTL for stored results (24 hours typical)
5. Different behavior for different HTTP methods

FOLLOW-UP QUESTIONS:
- What happens if the original request is still processing?
- How do you handle partial failures?
- Should GET requests be idempotent differently than POST?
- How do you clean up old idempotency records?
"""

from dataclasses import dataclass
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
import threading
import time
import json
import hashlib


@dataclass
class IdempotencyRecord:
    key: str
    result: Any
    created_at: datetime
    status: str  # 'processing', 'completed', 'failed'
    fingerprint: str  # Hash of request body
    

class IdempotencyHandler:
    """Handles idempotent operations for payment APIs."""
    
    def __init__(self, ttl_hours: int = 24):
        """
        Initialize idempotency handler.
        
        Args:
            ttl_hours: Time to live for idempotency records
        """
        # TODO: Initialize storage and locks
        pass
    
    def execute_idempotent(self, 
                          idempotency_key: str, 
                          request_body: Dict,
                          operation: Callable) -> Any:
        """
        Execute operation idempotently.
        
        Args:
            idempotency_key: Unique key for this operation
            request_body: Request payload for fingerprinting
            operation: Function to execute if not cached
            
        Returns:
            Operation result (cached or fresh)
            
        Raises:
            ConflictError: If same key used with different request body
            ProcessingError: If original request still processing
        """
        # TODO: Implement idempotent execution logic
        pass
    
    def get_record(self, idempotency_key: str) -> Optional[IdempotencyRecord]:
        """Get idempotency record if it exists."""
        # TODO: Return record or None
        pass
    
    def cleanup_expired_records(self) -> int:
        """Remove expired idempotency records."""
        # TODO: Clean up old records, return count removed
        pass
    
    def _generate_fingerprint(self, request_body: Dict) -> str:
        """Generate fingerprint for request body."""
        # TODO: Create consistent hash of request
        pass
    
    def _is_expired(self, record: IdempotencyRecord) -> bool:
        """Check if record has expired."""
        # TODO: Check if record is beyond TTL
        pass


class ConflictError(Exception):
    """Raised when idempotency key conflicts with different request."""
    pass


class ProcessingError(Exception):
    """Raised when original request is still processing."""
    pass


# Example operations
def process_payment(payment_data: Dict) -> Dict:
    """Simulate payment processing."""
    print(f"Processing payment: {payment_data['amount']}")
    time.sleep(0.5)  # Simulate processing time
    
    return {
        "payment_id": f"pay_{int(time.time())}",
        "amount": payment_data["amount"],
        "status": "completed"
    }


def send_money_transfer(transfer_data: Dict) -> Dict:
    """Simulate money transfer."""
    print(f"Transferring {transfer_data['amount']} to {transfer_data['recipient']}")
    time.sleep(0.3)
    
    return {
        "transfer_id": f"xfer_{int(time.time())}",
        "amount": transfer_data["amount"],
        "recipient": transfer_data["recipient"],
        "status": "sent"
    }


# Example usage and test cases
if __name__ == "__main__":
    handler = IdempotencyHandler(ttl_hours=24)
    
    # Test basic idempotency
    payment_request = {
        "amount": 100.00,
        "currency": "USD",
        "user_id": "user_123"
    }
    
    # First request
    print("=== First Payment Request ===")
    result1 = handler.execute_idempotent(
        "payment_key_1",
        payment_request,
        lambda: process_payment(payment_request)
    )
    print(f"Result 1: {result1}")
    
    # Duplicate request (should return cached result)
    print("\n=== Duplicate Payment Request ===")
    result2 = handler.execute_idempotent(
        "payment_key_1", 
        payment_request,
        lambda: process_payment(payment_request)
    )
    print(f"Result 2: {result2}")
    print(f"Same result: {result1 == result2}")
    
    # Conflicting request (same key, different body)
    print("\n=== Conflicting Request ===")
    conflicting_request = {
        "amount": 200.00,  # Different amount!
        "currency": "USD",
        "user_id": "user_123"
    }
    
    try:
        result3 = handler.execute_idempotent(
            "payment_key_1",  # Same key
            conflicting_request,  # Different body
            lambda: process_payment(conflicting_request)
        )
        print(f"Result 3: {result3}")
    except ConflictError as e:
        print(f"Conflict detected: {e}")
    
    # Test concurrent requests
    print("\n=== Concurrent Requests ===")
    
    def concurrent_payment(thread_id: int):
        try:
            result = handler.execute_idempotent(
                "concurrent_key",
                {"amount": 50.0, "user_id": "user_456"},
                lambda: process_payment({"amount": 50.0, "user_id": "user_456"})
            )
            print(f"Thread {thread_id}: {result}")
        except Exception as e:
            print(f"Thread {thread_id} error: {e}")
    
    # Start multiple threads with same idempotency key
    threads = []
    for i in range(3):
        thread = threading.Thread(target=concurrent_payment, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    # Check record
    record = handler.get_record("concurrent_key")
    print(f"\nStored record: {record}")
    
    # Test cleanup
    print(f"\nCleaned up {handler.cleanup_expired_records()} records")