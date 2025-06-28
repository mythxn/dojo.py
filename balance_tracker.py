"""
PROBLEM: Real-time Balance Tracker (20-25 minutes)

BUSINESS CONTEXT:
Users need to see their account balance in real-time as payments process.
Multiple transactions can happen simultaneously, and balance must always
be consistent. Implement a thread-safe balance tracking system.

REQUIREMENTS:
1. Thread-safe balance updates (credits/debits)
2. Prevent negative balances (overdraft protection)
3. Transaction history with timestamps
4. Balance holds/reserves for pending payments
5. Atomic operations for complex transactions

FOLLOW-UP QUESTIONS:
- How do you handle concurrent transfers between accounts?
- What happens if a hold expires?
- How do you ensure balance consistency across services?
- How do you handle currency conversion?
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
import threading
import time
from enum import Enum


class TransactionType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    HOLD = "hold"
    RELEASE_HOLD = "release_hold"
    CAPTURE_HOLD = "capture_hold"


@dataclass
class Transaction:
    id: str
    account_id: str
    amount: Decimal
    transaction_type: TransactionType
    timestamp: datetime
    reference_id: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Hold:
    id: str
    account_id: str
    amount: Decimal
    created_at: datetime
    expires_at: datetime
    reference_id: Optional[str] = None
    captured: bool = False


@dataclass
class AccountBalance:
    account_id: str
    available_balance: Decimal
    pending_balance: Decimal  # Includes holds
    total_balance: Decimal
    currency: str
    last_updated: datetime


class BalanceTracker:
    """Thread-safe real-time balance tracking system."""
    
    def __init__(self):
        """Initialize balance tracker."""
        # TODO: Initialize data structures and locks
        pass
    
    def create_account(self, account_id: str, currency: str = "USD", 
                      initial_balance: Decimal = Decimal('0')) -> bool:
        """
        Create new account with optional initial balance.
        
        Args:
            account_id: Unique account identifier
            currency: Account currency
            initial_balance: Starting balance
            
        Returns:
            True if account created, False if already exists
        """
        # TODO: Create new account
        pass
    
    def credit_account(self, account_id: str, amount: Decimal, 
                      reference_id: str, description: str = "") -> bool:
        """
        Add funds to account.
        
        Args:
            account_id: Account to credit
            amount: Amount to add
            reference_id: Transaction reference
            description: Transaction description
            
        Returns:
            True if successful
        """
        # TODO: Add funds to account
        pass
    
    def debit_account(self, account_id: str, amount: Decimal,
                     reference_id: str, description: str = "",
                     allow_overdraft: bool = False) -> bool:
        """
        Remove funds from account.
        
        Args:
            account_id: Account to debit
            amount: Amount to remove
            reference_id: Transaction reference
            description: Transaction description
            allow_overdraft: Whether to allow negative balance
            
        Returns:
            True if successful, False if insufficient funds
        """
        # TODO: Remove funds from account
        pass
    
    def place_hold(self, account_id: str, amount: Decimal,
                   hold_id: str, expires_in_minutes: int = 30,
                   reference_id: str = "") -> bool:
        """
        Place hold on account funds.
        
        Args:
            account_id: Account to place hold on
            amount: Amount to hold
            hold_id: Unique hold identifier
            expires_in_minutes: Hold expiration time
            reference_id: Reference for the hold
            
        Returns:
            True if hold placed successfully
        """
        # TODO: Place hold on funds
        pass
    
    def capture_hold(self, hold_id: str, capture_amount: Optional[Decimal] = None) -> bool:
        """
        Capture (convert to actual debit) a placed hold.
        
        Args:
            hold_id: Hold to capture
            capture_amount: Amount to capture (default: full hold amount)
            
        Returns:
            True if captured successfully
        """
        # TODO: Capture held funds
        pass
    
    def release_hold(self, hold_id: str) -> bool:
        """
        Release a hold without capturing.
        
        Args:
            hold_id: Hold to release
            
        Returns:
            True if released successfully
        """
        # TODO: Release held funds
        pass
    
    def transfer_funds(self, from_account: str, to_account: str,
                      amount: Decimal, reference_id: str) -> bool:
        """
        Transfer funds between accounts atomically.
        
        Args:
            from_account: Source account
            to_account: Destination account
            amount: Amount to transfer
            reference_id: Transaction reference
            
        Returns:
            True if transfer successful
        """
        # TODO: Implement atomic transfer
        pass
    
    def get_balance(self, account_id: str) -> Optional[AccountBalance]:
        """Get current account balance."""
        # TODO: Return account balance
        pass
    
    def get_transaction_history(self, account_id: str, 
                              limit: int = 50) -> List[Transaction]:
        """Get recent transactions for account."""
        # TODO: Return transaction history
        pass
    
    def get_active_holds(self, account_id: str) -> List[Hold]:
        """Get active holds for account."""
        # TODO: Return active holds
        pass
    
    def cleanup_expired_holds(self) -> int:
        """Clean up expired holds and return count."""
        # TODO: Remove expired holds
        pass
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        # TODO: Generate unique ID
        pass


# Example usage and test cases
if __name__ == "__main__":
    tracker = BalanceTracker()
    
    # Create test accounts
    tracker.create_account("user_123", "USD", Decimal('1000.00'))
    tracker.create_account("user_456", "USD", Decimal('500.00'))
    
    print("=== Initial Balances ===")
    balance1 = tracker.get_balance("user_123")
    balance2 = tracker.get_balance("user_456")
    print(f"User 123: {balance1}")
    print(f"User 456: {balance2}")
    
    # Test credit/debit
    print("\n=== Credit/Debit Operations ===")
    tracker.credit_account("user_123", Decimal('250.00'), "deposit_1", "Bank deposit")
    tracker.debit_account("user_123", Decimal('100.00'), "payment_1", "Coffee purchase")
    
    balance1 = tracker.get_balance("user_123")
    print(f"User 123 after ops: {balance1}")
    
    # Test holds
    print("\n=== Hold Operations ===")
    hold_success = tracker.place_hold("user_456", Decimal('200.00'), "hold_1", 60, "payment_auth")
    print(f"Hold placed: {hold_success}")
    
    balance2 = tracker.get_balance("user_456")
    print(f"User 456 with hold: {balance2}")
    
    # Test hold capture
    capture_success = tracker.capture_hold("hold_1", Decimal('150.00'))
    print(f"Hold captured: {capture_success}")
    
    balance2 = tracker.get_balance("user_456")
    print(f"User 456 after capture: {balance2}")
    
    # Test transfer
    print("\n=== Transfer Operation ===")
    transfer_success = tracker.transfer_funds("user_123", "user_456", Decimal('75.00'), "transfer_1")
    print(f"Transfer success: {transfer_success}")
    
    balance1 = tracker.get_balance("user_123")
    balance2 = tracker.get_balance("user_456")
    print(f"User 123 after transfer: {balance1}")
    print(f"User 456 after transfer: {balance2}")
    
    # Test transaction history
    print("\n=== Transaction History ===")
    history1 = tracker.get_transaction_history("user_123")
    for txn in history1:
        print(f"  {txn}")
    
    # Test active holds
    print("\n=== Active Holds ===")
    holds = tracker.get_active_holds("user_456")
    for hold in holds:
        print(f"  {hold}")
    
    # Test concurrent operations
    print("\n=== Concurrent Operations ===")
    
    def concurrent_operations(thread_id: int):
        for i in range(5):
            tracker.credit_account("user_123", Decimal('10.00'), f"concurrent_{thread_id}_{i}")
            tracker.debit_account("user_456", Decimal('5.00'), f"concurrent_{thread_id}_{i}")
            time.sleep(0.01)
    
    # Run concurrent operations
    threads = []
    for i in range(3):
        thread = threading.Thread(target=concurrent_operations, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("Final balances after concurrent ops:")
    balance1 = tracker.get_balance("user_123")
    balance2 = tracker.get_balance("user_456")
    print(f"User 123: {balance1}")
    print(f"User 456: {balance2}")
    
    # Cleanup
    expired_count = tracker.cleanup_expired_holds()
    print(f"\nCleaned up {expired_count} expired holds")