"""
PROBLEM: Payment API Client with Retries (20-25 minutes)

BUSINESS CONTEXT:
Payment systems integrate with external APIs (banks, card processors, compliance services).
These APIs can be unreliable, so you need smart retry logic and error handling.

REQUIREMENTS:
1. HTTP client wrapper with automatic retries
2. Different retry strategies for different error types
3. Exponential backoff with jitter
4. Circuit breaker for failing endpoints
5. Request/response logging for compliance
6. Timeout handling and connection pooling

FOLLOW-UP QUESTIONS:
- How do you handle rate limiting from external APIs?
- What errors should you retry vs. fail immediately?
- How do you prevent thundering herd when retrying?
- How would you implement request deduplication?
- How do you handle authentication token refresh?
"""

import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from enum import Enum
from dataclasses import dataclass
import json


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class RetryStrategy(Enum):
    EXPONENTIAL_BACKOFF = "exponential"
    FIXED_DELAY = "fixed"
    LINEAR_BACKOFF = "linear"


@dataclass
class APIRequest:
    method: HTTPMethod
    url: str
    headers: Dict[str, str]
    body: Optional[Dict] = None
    timeout: int = 30
    retry_count: int = 0


@dataclass
class APIResponse:
    status_code: int
    headers: Dict[str, str]
    body: Optional[str]
    response_time_ms: int
    error: Optional[str] = None


@dataclass
class RetryConfig:
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    backoff_multiplier: float = 2.0
    jitter: bool = True


class APIClient:
    """HTTP client with intelligent retry logic for payment APIs."""
    
    def __init__(self, base_url: str, retry_config: RetryConfig = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for all requests
            retry_config: Retry configuration
        """
        # TODO: Initialize client with configuration
        pass
    
    def get(self, endpoint: str, headers: Dict[str, str] = None) -> APIResponse:
        """Make GET request with retries."""
        # TODO: Implement GET request
        pass
    
    def post(self, endpoint: str, data: Dict = None, headers: Dict[str, str] = None) -> APIResponse:
        """Make POST request with retries."""
        # TODO: Implement POST request
        pass
    
    def put(self, endpoint: str, data: Dict = None, headers: Dict[str, str] = None) -> APIResponse:
        """Make PUT request with retries."""
        # TODO: Implement PUT request
        pass
    
    def delete(self, endpoint: str, headers: Dict[str, str] = None) -> APIResponse:
        """Make DELETE request with retries."""
        # TODO: Implement DELETE request
        pass
    
    def _make_request(self, request: APIRequest) -> APIResponse:
        """Make HTTP request with retry logic."""
        # TODO: Implement core request logic with retries
        pass
    
    def _should_retry(self, response: APIResponse, attempt: int) -> bool:
        """Determine if request should be retried."""
        # TODO: Implement retry decision logic
        # Retry on: 5xx errors, timeouts, rate limits (429)
        # Don't retry on: 4xx client errors (except 429), auth errors
        pass
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt."""
        # TODO: Implement delay calculation based on strategy
        pass
    
    def _add_jitter(self, delay_ms: int) -> float:
        """Add random jitter to prevent thundering herd."""
        # TODO: Add random jitter (±25% of delay)
        pass
    
    def _simulate_http_request(self, request: APIRequest) -> APIResponse:
        """Simulate HTTP request for interview purposes."""
        # TODO: Simulate various response scenarios
        # Include: success, server errors, timeouts, rate limits
        pass
    
    def _log_request(self, request: APIRequest, response: APIResponse):
        """Log request/response for compliance and debugging."""
        # TODO: Log request/response with PII masking
        pass


class PaymentAPIClient(APIClient):
    """Specialized client for payment processor APIs."""
    
    def __init__(self, base_url: str, api_key: str, retry_config: RetryConfig = None):
        """
        Initialize payment API client.
        
        Args:
            base_url: Payment processor base URL
            api_key: API authentication key
            retry_config: Retry configuration
        """
        # TODO: Initialize with payment-specific configuration
        pass
    
    def charge_card(self, card_token: str, amount_cents: int, currency: str = "USD") -> APIResponse:
        """Charge a credit card."""
        # TODO: Implement card charging with proper error handling
        pass
    
    def refund_payment(self, payment_id: str, amount_cents: int = None) -> APIResponse:
        """Refund a payment (full or partial)."""
        # TODO: Implement refund with idempotency
        pass
    
    def get_payment_status(self, payment_id: str) -> APIResponse:
        """Get current status of a payment."""
        # TODO: Implement status check
        pass
    
    def create_customer(self, email: str, name: str) -> APIResponse:
        """Create a new customer."""
        # TODO: Implement customer creation
        pass
    
    def _add_auth_header(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Add authentication header to request."""
        # TODO: Add API key or Bearer token
        pass
    
    def _generate_idempotency_key(self, request_data: Dict) -> str:
        """Generate idempotency key for payment requests."""
        # TODO: Generate unique key based on request content
        pass


class APIHealthMonitor:
    """Monitor API health and implement circuit breaker pattern."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize health monitor.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
        """
        # TODO: Initialize circuit breaker state
        pass
    
    def record_success(self, endpoint: str):
        """Record successful API call."""
        # TODO: Reset failure count for endpoint
        pass
    
    def record_failure(self, endpoint: str):
        """Record failed API call."""
        # TODO: Increment failure count, open circuit if threshold reached
        pass
    
    def is_circuit_open(self, endpoint: str) -> bool:
        """Check if circuit breaker is open for endpoint."""
        # TODO: Check if endpoint is currently blocked
        pass
    
    def get_endpoint_health(self, endpoint: str) -> Dict[str, Any]:
        """Get health statistics for endpoint."""
        # TODO: Return success rate, failure count, circuit state
        pass


# Example usage and test cases
if __name__ == "__main__":
    # Configure retry settings
    retry_config = RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay_ms=1000,
        max_delay_ms=10000,
        jitter=True
    )
    
    # Test basic API client
    client = APIClient("https://api.example.com", retry_config)
    response = client.get("/health")
    print(f"Health check: {response.status_code}")
    
    # Test payment API client
    payment_client = PaymentAPIClient(
        "https://api.stripe.com/v1",
        "sk_test_123456789",
        retry_config
    )
    
    # Test card charge
    charge_response = payment_client.charge_card(
        card_token="tok_visa",
        amount_cents=1000,
        currency="USD"
    )
    print(f"Charge result: {charge_response.status_code}")
    
    # Test health monitoring
    monitor = APIHealthMonitor(failure_threshold=3, recovery_timeout=30)
    monitor.record_failure("/payments")
    monitor.record_failure("/payments")
    monitor.record_failure("/payments")
    
    is_blocked = monitor.is_circuit_open("/payments")
    print(f"Circuit open: {is_blocked}")
    
    health_stats = monitor.get_endpoint_health("/payments")
    print(f"Endpoint health: {health_stats}")