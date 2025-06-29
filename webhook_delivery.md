# Webhook Delivery System - Step-by-Step Implementation Guide

## Problem Overview
Build a reliable webhook delivery system that can handle failures, retries, and scale for production use. This is a common interview question for fintech/payment companies.

## Key Requirements
1. Queue webhooks for delivery
2. Retry failed deliveries with exponential backoff
3. Track delivery attempts and status
4. Handle timeouts and network errors
5. Secure webhook signing (HMAC)

## Step 1: Design the Data Structures

Start by thinking about what data you need to track:

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

class WebhookStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class WebhookEvent:
    id: str
    url: str
    payload: Dict
    secret: str
    created_at: datetime
    max_attempts: int = 5
    timeout_seconds: int = 30

@dataclass
class DeliveryAttempt:
    attempt_number: int
    attempted_at: datetime
    response_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    success: bool
```

**Teaching Point:** Always start with clear data structures. This makes the rest of the implementation obvious.

## Step 2: Initialize Storage and Thread Safety

```python
import threading

class WebhookDeliverySystem:
    def __init__(self, max_concurrent_deliveries: int = 10):
        # Storage for webhook data
        self.webhooks: Dict[str, WebhookEvent] = {}
        self.webhook_status: Dict[str, WebhookStatus] = {}
        self.delivery_attempts: Dict[str, List[DeliveryAttempt]] = {}
        
        # Configuration
        self.max_concurrent = max_concurrent_deliveries
        
        # Thread safety
        self.lock = threading.Lock()
```

**Teaching Point:** In interviews, always mention thread safety. Use simple locks unless you need more complex synchronization.

## Step 3: Implement Queue Operations

Start with the simplest operations - adding webhooks to the queue:

```python
def enqueue_webhook(self, event: WebhookEvent) -> str:
    """Queue webhook for delivery."""
    with self.lock:
        self.webhooks[event.id] = event
        self.webhook_status[event.id] = WebhookStatus.PENDING
        self.delivery_attempts[event.id] = []
    return event.id

def get_webhook_status(self, webhook_id: str) -> Optional[WebhookStatus]:
    """Get current status of webhook delivery."""
    return self.webhook_status.get(webhook_id)

def get_delivery_attempts(self, webhook_id: str) -> List[DeliveryAttempt]:
    """Get all delivery attempts for a webhook."""
    return self.delivery_attempts.get(webhook_id, [])
```

**Teaching Point:** Implement the easy methods first. This builds confidence and gives you working code quickly.

## Step 4: Add Security (HMAC Signing)

```python
import hmac
import hashlib
import json

def _sign_payload(self, payload: str, secret: str) -> str:
    """Generate HMAC signature for webhook payload."""
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
```

**Teaching Point:** Security is critical for webhooks. HMAC with SHA-256 is the industry standard.

## Step 5: Implement HTTP Request Simulation

For interviews, you don't need real HTTP requests. Simulate them:

```python
import time
import random

def _make_http_request(self, url: str, payload: Dict, signature: str, timeout: int) -> tuple:
    """Make HTTP request to webhook endpoint."""
    try:
        # Simulate network delay
        time.sleep(0.1)
        
        # Simulate success/failure scenarios
        success_rate = 0.7  # 70% success rate
        if random.random() < success_rate:
            return (200, '{"status": "success"}', None)
        else:
            # Simulate various failures
            scenarios = [
                (500, '{"error": "internal_server_error"}', "Server Error"),
                (404, '{"error": "not_found"}', "Endpoint Not Found"),
                (0, None, "Connection Timeout"),
                (503, '{"error": "service_unavailable"}', "Service Unavailable")
            ]
            return random.choice(scenarios)
    except Exception as e:
        return (0, None, str(e))
```

**Teaching Point:** In interviews, simulation is better than complex HTTP libraries. Focus on the logic, not the implementation details.

## Step 6: Implement Core Delivery Logic

This is the heart of the system:

```python
def deliver_webhook(self, webhook_id: str) -> bool:
    """Attempt to deliver a specific webhook."""
    webhook = self.webhooks.get(webhook_id)
    if not webhook:
        return False

    # Check if already delivered or expired
    status = self.webhook_status.get(webhook_id)
    if status in [WebhookStatus.DELIVERED, WebhookStatus.EXPIRED]:
        return status == WebhookStatus.DELIVERED

    # Get current attempt count
    attempts = self.delivery_attempts.get(webhook_id, [])
    attempt_number = len(attempts) + 1

    # Check if max attempts exceeded
    if attempt_number > webhook.max_attempts:
        with self.lock:
            self.webhook_status[webhook_id] = WebhookStatus.EXPIRED
        return False

    # Prepare payload and signature
    payload_str = json.dumps(webhook.payload)
    signature = self._sign_payload(payload_str, webhook.secret)

    # Make HTTP request
    status_code, response_body, error_message = self._make_http_request(
        webhook.url, webhook.payload, signature, webhook.timeout_seconds
    )

    # Record attempt
    attempt = DeliveryAttempt(
        attempt_number=attempt_number,
        attempted_at=datetime.now(),
        response_code=status_code,
        response_body=response_body,
        error_message=error_message,
        success=status_code == 200
    )

    with self.lock:
        self.delivery_attempts[webhook_id].append(attempt)
        
        if attempt.success:
            self.webhook_status[webhook_id] = WebhookStatus.DELIVERED
            return True
        else:
            self.webhook_status[webhook_id] = WebhookStatus.FAILED
            return False
```

**Teaching Point:** Break down complex logic into clear steps. Each step should be easy to understand and explain.

## Step 7: Add Exponential Backoff

```python
from datetime import timedelta

def _calculate_next_retry_time(self, attempt_number: int) -> datetime:
    """Calculate when to retry based on attempt number (exponential backoff)."""
    # Exponential backoff: 1s, 2s, 4s, 8s, 16s...
    base_delay = 1
    max_delay = 300  # 5 minutes max
    delay = min(base_delay * (2 ** (attempt_number - 1)), max_delay)
    return datetime.now() + timedelta(seconds=delay)
```

**Teaching Point:** Exponential backoff is crucial for production systems. Always cap the maximum delay.

## Step 8: Implement Retry Logic

```python
def retry_failed_webhooks(self) -> int:
    """Retry all failed webhooks that are eligible for retry."""
    retried_count = 0
    current_time = datetime.now()

    for webhook_id, status in self.webhook_status.items():
        if status != WebhookStatus.FAILED:
            continue

        webhook = self.webhooks.get(webhook_id)
        attempts = self.delivery_attempts.get(webhook_id, [])

        if not webhook or not attempts:
            continue

        # Check if we can retry (haven't exceeded max attempts)
        if len(attempts) >= webhook.max_attempts:
            with self.lock:
                self.webhook_status[webhook_id] = WebhookStatus.EXPIRED
            continue

        # Check if enough time has passed for retry (exponential backoff)
        next_retry_time = self._calculate_next_retry_time(len(attempts))

        if current_time >= next_retry_time:
            if self.deliver_webhook(webhook_id):
                retried_count += 1

    return retried_count
```

**Teaching Point:** Retry logic ties everything together. This method would typically be called by a background job.

## Interview Tips

### 1. Start Simple, Add Complexity
- Begin with basic queuing
- Add delivery logic
- Then add retries and error handling
- Finally add security and optimizations

### 2. Think About Edge Cases
- What if a webhook URL is invalid?
- What if the secret is empty?
- What if two threads try to deliver the same webhook?
- What happens to webhooks that never succeed?

### 3. Discuss Scaling
- How would you handle millions of webhooks?
- How would you distribute across multiple workers?
- How would you persist state across restarts?
- How would you monitor webhook health?

### 4. Production Considerations
- **Dead Letter Queue**: Move permanently failed webhooks
- **Rate Limiting**: Don't overwhelm recipient servers
- **Metrics**: Track success rates, latency, queue depth
- **Persistence**: Use database instead of in-memory storage
- **Circuit Breaker**: Stop trying endpoints that are consistently down

## Common Follow-up Questions

**Q: How do you prevent duplicate deliveries?**
A: Use idempotency keys in the webhook payload and track them.

**Q: How do you handle webhooks that take too long to process?**
A: Implement timeouts in the HTTP client and treat timeouts as failures.

**Q: How would you scale this across multiple servers?**
A: Use a message queue (Redis, RabbitMQ) and database for shared state.

**Q: How do you handle webhook endpoints that are permanently down?**
A: Implement circuit breaker pattern - stop trying after consecutive failures, then gradually test again.

## Testing Your Implementation

```python
# Test basic functionality
delivery_system = WebhookDeliverySystem()

webhook = WebhookEvent(
    id="test_123",
    url="https://example.com/webhook",
    payload={"event": "payment.completed", "amount": 100},
    secret="secret_key",
    created_at=datetime.now()
)

# Queue and deliver
webhook_id = delivery_system.enqueue_webhook(webhook)
success = delivery_system.deliver_webhook(webhook_id)
attempts = delivery_system.get_delivery_attempts(webhook_id)

print(f"Success: {success}, Attempts: {len(attempts)}")
```

This step-by-step approach ensures you build a robust webhook delivery system while clearly explaining your thought process to the interviewer.