"""
PROBLEM: Circuit Breaker (15-20 minutes)

BUSINESS CONTEXT:
Your payment system calls external services (banks, card networks).
When these services go down, you don't want to keep making failed calls.
Implement a circuit breaker to fail fast and recover gracefully.

REQUIREMENTS:
1. Three states: CLOSED, OPEN, HALF_OPEN
2. Open circuit after N consecutive failures
3. Try one request after timeout in HALF_OPEN state
4. Reset to CLOSED after successful request
5. Track failure rate and response times

FOLLOW-UP QUESTIONS:
- How do you handle partial failures?
- What metrics would you expose?
- How do you test circuit breaker behavior?
- What's the fallback when circuit is open?
"""

from dataclasses import dataclass
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
import threading
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5        # Failures before opening
    timeout_seconds: int = 60         # Time before trying HALF_OPEN
    success_threshold: int = 3        # Successes before closing
    response_timeout: int = 10        # Max response time


@dataclass
class CallResult:
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker.
        
        Args:
            name: Identifier for this circuit breaker
            config: Configuration parameters
        """
        # TODO: Initialize circuit breaker state
        pass
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function call through circuit breaker.
        
        Args:
            func: Function to call
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result if successful
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            TimeoutError: If call times out
            Exception: Original exception from function
        """
        # TODO: Implement circuit breaker logic
        pass
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        # TODO: Return current state
        pass
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        # TODO: Return stats (failure rate, call count, etc.)
        pass
    
    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        # TODO: Reset to CLOSED state
        pass
    
    def _record_success(self, response_time_ms: float) -> None:
        """Record successful call."""
        # TODO: Update success metrics and state if needed
        pass
    
    def _record_failure(self, error_message: str, response_time_ms: float) -> None:
        """Record failed call."""
        # TODO: Update failure metrics and state if needed
        pass
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset to HALF_OPEN."""
        # TODO: Check if timeout has passed
        pass
    
    def _can_execute(self) -> bool:
        """Check if calls are allowed in current state."""
        # TODO: Return True if calls are allowed
        pass


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Example external service simulators
def unreliable_payment_service(payment_id: str, fail_rate: float = 0.3) -> dict:
    """Simulate external payment service that sometimes fails."""
    import random
    time.sleep(0.1)  # Simulate network call
    
    if random.random() < fail_rate:
        raise ConnectionError("Payment service unavailable")
    
    return {"payment_id": payment_id, "status": "processed"}


def slow_fraud_service(transaction_id: str, delay_ms: int = 100) -> dict:
    """Simulate fraud detection service with variable response times."""
    time.sleep(delay_ms / 1000.0)
    return {"transaction_id": transaction_id, "risk_score": 0.1}


# Example usage and test cases
if __name__ == "__main__":
    # Configure circuit breaker for payment service
    config = CircuitBreakerConfig(
        failure_threshold=3,
        timeout_seconds=5,
        success_threshold=2,
        response_timeout=500  # 500ms
    )
    
    payment_breaker = CircuitBreaker("payment_service", config)
    
    # Test normal operation
    try:
        result = payment_breaker.call(unreliable_payment_service, "pay_123", 0.0)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with high failure rate to trigger opening
    for i in range(5):
        try:
            result = payment_breaker.call(unreliable_payment_service, f"pay_{i}", 0.8)
            print(f"Success {i}: {result}")
        except Exception as e:
            print(f"Error {i}: {e}")
        
        print(f"State: {payment_breaker.get_state()}")
        print(f"Stats: {payment_breaker.get_stats()}")
        print("---")
    
    # Try calling when circuit is open
    try:
        result = payment_breaker.call(unreliable_payment_service, "pay_final", 0.0)
        print(f"Final success: {result}")
    except CircuitBreakerOpenError as e:
        print(f"Circuit open: {e}")
    
    print(f"Final state: {payment_breaker.get_state()}")
    print(f"Final stats: {payment_breaker.get_stats()}")