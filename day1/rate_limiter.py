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

import time
import threading
from typing import Dict, Optional
from collections import deque
from dataclasses import dataclass


@dataclass
class RateLimitResult:
    allowed: bool
    remaining_requests: int
    reset_time: float
    retry_after: Optional[float] = None


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_size_seconds: int):
        """
        Initialize sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_size_seconds: Time window in seconds
        """
        pass  # TODO: Implement
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """
        Check if request is allowed for given key.
        
        Args:
            key: Identifier (user_id, ip_address, etc.)
            
        Returns:
            RateLimitResult with decision and metadata
        """
        pass  # TODO: Implement
    
    def _cleanup_expired(self, key: str, current_time: float):
        """Remove expired entries for given key."""
        pass  # TODO: Implement


class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket rate limiter.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        pass  # TODO: Implement
    
    def is_allowed(self, key: str, tokens_requested: int = 1) -> RateLimitResult:
        """
        Check if request is allowed and consume tokens.
        
        Args:
            key: Identifier (user_id, ip_address, etc.)
            tokens_requested: Number of tokens to consume
            
        Returns:
            RateLimitResult with decision and metadata
        """
        pass  # TODO: Implement
    
    def _refill_tokens(self, bucket_info: dict, current_time: float):
        """Refill tokens based on elapsed time."""
        pass  # TODO: Implement


class DistributedRateLimiter:
    """Redis-based distributed rate limiter (bonus implementation)"""
    
    def __init__(self, redis_client, max_requests: int, window_size_seconds: int):
        pass  # TODO: Implement
    
    def is_allowed(self, key: str) -> RateLimitResult:
        pass  # TODO: Implement