"""
Test cases for Rate Limiter implementations
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from day1.rate_limiter import (
    SlidingWindowRateLimiter, 
    TokenBucketRateLimiter,
    RateLimitResult
)


class TestSlidingWindowRateLimiter:
    
    def test_basic_rate_limiting(self):
        """Test basic rate limiting functionality"""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_size_seconds=1)
        
        # First 3 requests should be allowed
        for i in range(3):
            result = limiter.is_allowed("user1")
            assert result.allowed == True
            assert result.remaining_requests == 2 - i
        
        # 4th request should be denied
        result = limiter.is_allowed("user1")
        assert result.allowed == False
        assert result.remaining_requests == 0
        assert result.retry_after is not None
    
    def test_window_reset(self):
        """Test that window resets after time period"""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_size_seconds=1)
        
        # Use up quota
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        result = limiter.is_allowed("user1")
        assert result.allowed == False
        
        # Wait for window to reset
        time.sleep(1.1)
        result = limiter.is_allowed("user1")
        assert result.allowed == True
    
    def test_different_users(self):
        """Test that different users have separate limits"""
        limiter = SlidingWindowRateLimiter(max_requests=1, window_size_seconds=1)
        
        result1 = limiter.is_allowed("user1")
        result2 = limiter.is_allowed("user2")
        
        assert result1.allowed == True
        assert result2.allowed == True
        
        # Both users should now be at limit
        result1 = limiter.is_allowed("user1")
        result2 = limiter.is_allowed("user2")
        
        assert result1.allowed == False
        assert result2.allowed == False
    
    def test_thread_safety(self):
        """Test thread safety with concurrent requests"""
        limiter = SlidingWindowRateLimiter(max_requests=10, window_size_seconds=1)
        
        def make_request():
            return limiter.is_allowed("user1")
        
        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in futures]
        
        allowed_count = sum(1 for r in results if r.allowed)
        denied_count = sum(1 for r in results if not r.allowed)
        
        assert allowed_count == 10
        assert denied_count == 10
    
    def test_sliding_window_behavior(self):
        """Test that sliding window allows gradual request flow"""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_size_seconds=2)
        
        # Make 2 requests at t=0
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        
        # Should be at limit
        result = limiter.is_allowed("user1")
        assert result.allowed == False
        
        # Wait 1 second (half window), still at limit
        time.sleep(1)
        result = limiter.is_allowed("user1")
        assert result.allowed == False
        
        # Wait another 1.1 seconds (past first requests), should allow new request
        time.sleep(1.1)
        result = limiter.is_allowed("user1")
        assert result.allowed == True


class TestTokenBucketRateLimiter:
    
    def test_basic_token_consumption(self):
        """Test basic token bucket functionality"""
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
        
        # Should have full capacity initially
        result = limiter.is_allowed("user1", tokens_requested=5)
        assert result.allowed == True
        assert result.remaining_requests == 0
        
        # No tokens left
        result = limiter.is_allowed("user1", tokens_requested=1)
        assert result.allowed == False
    
    def test_token_refill(self):
        """Test that tokens refill over time"""
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate=2.0)  # 2 tokens per second
        
        # Use all tokens
        limiter.is_allowed("user1", tokens_requested=2)
        
        # Should be empty
        result = limiter.is_allowed("user1", tokens_requested=1)
        assert result.allowed == False
        
        # Wait for refill
        time.sleep(1.1)  # Should get ~2 tokens back
        result = limiter.is_allowed("user1", tokens_requested=2)
        assert result.allowed == True
    
    def test_burst_handling(self):
        """Test that bucket handles burst traffic correctly"""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        
        # Should allow burst up to capacity
        for i in range(10):
            result = limiter.is_allowed("user1", tokens_requested=1)
            assert result.allowed == True
        
        # Next request should be denied
        result = limiter.is_allowed("user1", tokens_requested=1)
        assert result.allowed == False
    
    def test_partial_token_consumption(self):
        """Test requesting different amounts of tokens"""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        
        # Request 3 tokens
        result = limiter.is_allowed("user1", tokens_requested=3)
        assert result.allowed == True
        assert result.remaining_requests == 7
        
        # Request 8 tokens (more than remaining)
        result = limiter.is_allowed("user1", tokens_requested=8)
        assert result.allowed == False
        
        # Request 7 tokens (exactly remaining)
        result = limiter.is_allowed("user1", tokens_requested=7)
        assert result.allowed == True
    
    def test_thread_safety(self):
        """Test thread safety of token bucket"""
        limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10.0)
        
        def consume_tokens():
            return limiter.is_allowed("user1", tokens_requested=1)
        
        # 200 threads trying to consume 1 token each
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(consume_tokens) for _ in range(200)]
            results = [f.result() for f in futures]
        
        allowed_count = sum(1 for r in results if r.allowed)
        
        # Should allow exactly 100 (initial capacity)
        assert allowed_count == 100


class TestRateLimiterComparison:
    """Compare behavior of both algorithms"""
    
    def test_algorithm_differences(self):
        """Test key differences between sliding window and token bucket"""
        sliding = SlidingWindowRateLimiter(max_requests=10, window_size_seconds=1)
        bucket = TokenBucketRateLimiter(capacity=10, refill_rate=10.0)
        
        # Both should allow initial burst
        for i in range(10):
            s_result = sliding.is_allowed("user1")
            b_result = bucket.is_allowed("user2")
            assert s_result.allowed == True
            assert b_result.allowed == True
        
        # Both should deny next request
        s_result = sliding.is_allowed("user1")
        b_result = bucket.is_allowed("user2")
        assert s_result.allowed == False
        assert b_result.allowed == False
        
        # After waiting, sliding window should reset completely
        # while token bucket refills gradually
        time.sleep(1.1)
        
        # Sliding window should allow full burst again
        for i in range(10):
            result = sliding.is_allowed("user1")
            assert result.allowed == True
        
        # Token bucket should also allow full burst again (with 10/sec refill rate)
        for i in range(10):
            result = bucket.is_allowed("user2")
            assert result.allowed == True


# Performance benchmarks (optional)
class TestPerformance:
    
    def test_sliding_window_performance(self):
        """Benchmark sliding window performance"""
        limiter = SlidingWindowRateLimiter(max_requests=1000, window_size_seconds=60)
        
        start_time = time.time()
        for i in range(1000):
            limiter.is_allowed(f"user{i % 100}")
        duration = time.time() - start_time
        
        # Should handle 1000 requests quickly
        assert duration < 1.0
    
    def test_token_bucket_performance(self):
        """Benchmark token bucket performance"""
        limiter = TokenBucketRateLimiter(capacity=1000, refill_rate=100.0)
        
        start_time = time.time()
        for i in range(1000):
            limiter.is_allowed(f"user{i % 100}")
        duration = time.time() - start_time
        
        # Should handle 1000 requests quickly
        assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])