"""
PROBLEM: Webhook Delivery System (20-25 minutes)

BUSINESS CONTEXT:
Your payment platform needs to notify merchants when payments complete.
Webhooks must be delivered reliably even if merchant servers are down.

REQUIREMENTS:
1. Deliver webhooks with exponential backoff retry
2. Track delivery attempts and success/failure
3. Handle timeouts and network errors gracefully
4. Support webhook signing for security
5. Queue webhooks for batch processing

FOLLOW-UP QUESTIONS:
- How do you handle webhooks that never succeed?
- What if a merchant's endpoint is temporarily down?
- How do you prevent duplicate webhook deliveries?
- How do you scale webhook delivery across multiple workers?
"""

import hashlib
import hmac
import json
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
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


class WebhookDeliverySystem:
    """Reliable webhook delivery with retries and failure handling."""

    def __init__(self, max_concurrent_deliveries: int = 10):
        """
        Initialize webhook delivery system.
        
        Args:
            max_concurrent_deliveries: Maximum concurrent webhook deliveries
        """
        self.webhooks: Dict[str, WebhookEvent] = {}
        self.webhook_status: Dict[str, WebhookStatus] = {}
        self.delivery_attempts: Dict[str, List[DeliveryAttempt]] = {}
        self.max_concurrent = max_concurrent_deliveries
        self.lock = threading.Lock()

    def enqueue_webhook(self, event: WebhookEvent) -> str:
        """
        Queue webhook for delivery.
        
        Args:
            event: Webhook event to deliver
            
        Returns:
            Webhook delivery ID for tracking
        """
        with self.lock:
            self.webhooks[event.id] = event
            self.webhook_status[event.id] = WebhookStatus.PENDING
            self.delivery_attempts[event.id] = []
        return event.id

    def deliver_webhook(self, webhook_id: str) -> bool:
        """
        Attempt to deliver a specific webhook.
        
        Args:
            webhook_id: ID of webhook to deliver
            
        Returns:
            True if delivery successful, False otherwise
        """
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

    def get_webhook_status(self, webhook_id: str) -> Optional[WebhookStatus]:
        """Get current status of webhook delivery."""
        return self.webhook_status.get(webhook_id)

    def get_delivery_attempts(self, webhook_id: str) -> List[DeliveryAttempt]:
        """Get all delivery attempts for a webhook."""
        return self.delivery_attempts.get(webhook_id, [])

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
            last_attempt = attempts[-1]
            next_retry_time = self._calculate_next_retry_time(len(attempts))

            if current_time >= next_retry_time:
                if self.deliver_webhook(webhook_id):
                    retried_count += 1

        return retried_count

    def _calculate_next_retry_time(self, attempt_number: int) -> datetime:
        """Calculate when to retry based on attempt number (exponential backoff)."""
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s...
        base_delay = 1
        max_delay = 300  # 5 minutes max
        delay = min(base_delay * (2 ** (attempt_number - 1)), max_delay)
        return datetime.now() + timedelta(seconds=delay)

    def _sign_payload(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _make_http_request(self, url: str, payload: Dict, signature: str, timeout: int) -> tuple:
        """Make HTTP request to webhook endpoint."""
        try:
            # Simulate HTTP request for interview purposes
            time.sleep(0.1)  # Simulate network delay

            # Simulate different response scenarios
            success_rate = 0.7  # 70% success rate for demo
            if random.random() < success_rate:
                return (200, '{"status": "success"}', None)
            else:
                # Simulate various failure scenarios
                scenarios = [
                    (500, '{"error": "internal_server_error"}', "Server Error"),
                    (404, '{"error": "not_found"}', "Endpoint Not Found"),
                    (0, None, "Connection Timeout"),
                    (503, '{"error": "service_unavailable"}', "Service Unavailable")
                ]
                return random.choice(scenarios)
        except Exception as e:
            return (0, None, str(e))


# Example usage and test cases
if __name__ == "__main__":
    delivery_system = WebhookDeliverySystem(max_concurrent_deliveries=5)

    # Create test webhook
    webhook = WebhookEvent(
        id="webhook_123",
        url="https://merchant.example.com/webhooks/payment",
        payload={
            "event": "payment.completed",
            "payment_id": "pay_456",
            "amount": 100.00,
            "currency": "USD"
        },
        secret="webhook_secret_key",
        created_at=datetime.now()
    )

    # Queue webhook for delivery
    delivery_id = delivery_system.enqueue_webhook(webhook)
    print(f"Queued webhook: {delivery_id}")

    # Check delivery status
    status = delivery_system.get_webhook_status(delivery_id)
    print(f"Status: {status}")

    # Attempt delivery
    success = delivery_system.deliver_webhook(delivery_id)
    print(f"Delivery success: {success}")

    # Get delivery attempts
    attempts = delivery_system.get_delivery_attempts(delivery_id)
    print(f"Attempts: {len(attempts)}")

    # Retry failed webhooks
    retried_count = delivery_system.retry_failed_webhooks()
    print(f"Retried {retried_count} webhooks")
