"""
PROBLEM: Payment Rate Limiter (15-20 minutes)

BUSINESS CONTEXT:
You work at a fintech company. Users are trying to abuse the payment system by making
too many payment attempts. Implement a rate limiter to prevent abuse.

REQUIREMENTS:
1. Limit payment attempts per user per time window
2. Support different limits (e.g., 5 payments per minute, 100 per hour)
3. Return clear feedback when limit is exceeded
4. Handle concurrent requests safely

FOLLOW-UP QUESTIONS:
- How would you distribute this across multiple servers?
- What happens if the system restarts?
- How do you handle different payment types (card vs bank transfer)?
"""

from dataclasses import dataclass
from typing import Dict
import time
import threading


@dataclass
class RateLimitResult:
    allowed: bool
    remaining_requests: int
    reset_time: float
    

class PaymentRateLimiter:
    """Rate limiter for payment attempts using sliding window algorithm."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        # TODO: Implement initialization
        pass
    
    def is_payment_allowed(self, user_id: str) -> RateLimitResult:
        """
        Check if payment is allowed for user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            RateLimitResult with decision and metadata
        """
        # TODO: Implement sliding window logic
        pass
    
    def reset_user_limits(self, user_id: str) -> None:
        """Reset limits for a specific user (admin action)."""
        # TODO: Implement reset logic
        pass


# Example usage and test cases
if __name__ == "__main__":
    # Test basic functionality
    limiter = PaymentRateLimiter(max_requests=3, window_seconds=60)
    
    # First payment should be allowed
    result = limiter.is_payment_allowed("user123")
    print(f"Payment 1: {result}")
    
    # More payments...
    for i in range(2, 6):
        result = limiter.is_payment_allowed("user123")
        print(f"Payment {i}: {result}")
        
    # Test different user
    result = limiter.is_payment_allowed("user456")
    print(f"Different user: {result}")