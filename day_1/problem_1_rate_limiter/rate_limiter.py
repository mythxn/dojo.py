"""
Rate Limiter Implementation
==========================

Implement both sliding window and token bucket rate limiting algorithms.

Requirements:
- Support per-user and per-IP rate limiting
- Thread-safe implementation
- Configurable time windows and request limits
- Clean up expired entries automatically

Your Tasks:
1. Implement SlidingWindowRateLimiter
2. Implement TokenBucketRateLimiter  
3. Make both thread-safe
4. Add proper error handling
5. Implement automatic cleanup

Interview Focus:
- Explain time/space complexity
- Discuss trade-offs between algorithms
- Handle edge cases (clock skew, burst traffic)
"""

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional, Deque


@dataclass
class RateLimitResult:
    allowed: bool
    remaining_requests: int
    reset_time: float
    retry_after: Optional[float] = None


@dataclass
class TokenBucket:
    tokens: int
    last_refill_time: float


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_size_seconds: int):
        """
        Initialize sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_size_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size_seconds
        self.lock = threading.Lock()
        self.requests: Dict[str, Deque[float]] = {}
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """
        Check if request is allowed for given key.
        
        Args:
            key: Identifier (user_id, ip_address, etc.)
            
        Returns:
            RateLimitResult with decision and metadata
        """
        current_time = time.time()

        with self.lock:
            if key not in self.requests:
                self.requests[key] = deque()

            self._cleanup_expired(key, current_time)
            dq = self.requests[key]

            if len(dq) < self.max_requests:
                dq.append(current_time)
                remaining = self.max_requests - len(dq)
                reset = self.window_size - (current_time - dq[0]) if dq else self.window_size
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=remaining,
                    reset_time=current_time + reset
                )
            else:
                retry_after = self.window_size - (current_time - dq[0])
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=current_time + retry_after,
                    retry_after=retry_after
                )

    def _cleanup_expired(self, key: str, current_time: float):
        """Remove expired entries for given key."""
        window_start = current_time - self.window_size
        if key in self.requests:
            dq = self.requests[key]
            while dq and dq[0] < window_start:
                dq.popleft()


class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket rate limiter.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.lock = threading.Lock()
        self.buckets: Dict[str, TokenBucket] = {}
    
    def is_allowed(self, key: str, tokens_requested: int = 1) -> RateLimitResult:
        """
        Check if request is allowed and consume tokens.
        
        Args:
            key: Identifier (user_id, ip_address, etc.)
            tokens_requested: Number of tokens to consume
            
        Returns:
            RateLimitResult with decision and metadata
        """
        current_time = time.time()

        with self.lock:
            if key not in self.buckets:
                self.buckets[key] = TokenBucket(
                    tokens=self.capacity,
                    last_refill_time=current_time
                )

            bucket = self.buckets[key]
            self._refill_tokens(bucket, current_time)

            if bucket.tokens >= tokens_requested:
                bucket.tokens -= tokens_requested
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=int(bucket.tokens),
                    reset_time=current_time
                )
            else:
                needed_tokens = tokens_requested - bucket.tokens
                retry_after = needed_tokens / self.refill_rate
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=current_time + retry_after,
                    retry_after=retry_after
                )

    def _refill_tokens(self, bucket: TokenBucket, current_time: float):
        """Refill tokens based on elapsed time."""
        elapsed = current_time - bucket.last_refill_time
        refill = elapsed * self.refill_rate
        bucket.tokens = min(self.capacity, bucket.tokens + refill)
        bucket.last_refill_time = current_time
