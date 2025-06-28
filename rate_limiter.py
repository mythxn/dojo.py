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
import threading
import time
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict


@dataclass
class RateLimitResult:
    allowed: bool
    remaining_requests: int
    reset_time: float # when will my quota fully reset
    retry_after: float # when can i make the next request


class PaymentRateLimiter:
    """Rate limiter for payment attempts using sliding window algorithm."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.bucket: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_payment_allowed(self, user_id: str) -> RateLimitResult:
        """
        Check if payment is allowed for user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            RateLimitResult with decision and metadata
        """
        now = time.time()

        with self.lock:
            q = self.bucket[user_id]
            self._clear_expired(user_id, now)

            if len(q) >= self.max_requests:
                oldest = q[0]
                retry_after = oldest + self.window_seconds - now
                reset_time = oldest + self.window_seconds
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=reset_time,
                    retry_after=retry_after
                )
            else:
                q.append(now)
                oldest = q[0]  # safe now — q has at least 1 element
                remaining = self.max_requests - len(q)
                reset_time = oldest + self.window_seconds
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=remaining,
                    reset_time=reset_time,
                    retry_after=0
                )

    
    def reset_user_limits(self, user_id: str) -> None:
        """Reset limits for a specific user (admin action)."""
        with self.lock:
            self.bucket[user_id].clear()

    def _clear_expired(self, user_id: str, cur_time) -> None:
        """Clear expired rate limits for a specific user (admin action)."""
        q = self.bucket[user_id]

        while q and q[0] <= cur_time - self.window_seconds:
            q.popleft()

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