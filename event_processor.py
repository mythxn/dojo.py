"""
PROBLEM: Event Processing System (20-25 minutes)

BUSINESS CONTEXT:
Your payment system generates events (payment_created, payment_completed, etc.)
that need to be processed by different services (notifications, analytics, fraud).
Implement an event processing system with reliable delivery guarantees.

REQUIREMENTS:
1. Publish events to multiple subscribers
2. At-least-once delivery guarantee
3. Event ordering within same aggregate
4. Dead letter queue for failed events
5. Subscriber health monitoring

FOLLOW-UP QUESTIONS:
- How do you handle slow subscribers?
- What if a subscriber is down for hours?
- How do you replay events from a specific point?
- How do you handle event schema evolution?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
import threading
import time
import queue
import json
from enum import Enum
import uuid


class EventStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class Event:
    id: str
    event_type: str
    aggregate_id: str  # For ordering (e.g., payment_id, user_id)
    payload: Dict[str, Any]
    timestamp: datetime
    sequence_number: int = 0
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary for serialization."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "sequence_number": self.sequence_number,
            "correlation_id": self.correlation_id
        }


@dataclass
class Subscriber:
    id: str
    name: str
    handler: Callable[[Event], bool]
    event_types: List[str]
    max_retries: int = 3
    timeout_seconds: int = 30
    active: bool = True


@dataclass
class DeliveryAttempt:
    subscriber_id: str
    event_id: str
    attempt_number: int
    attempted_at: datetime
    success: bool
    error_message: Optional[str] = None
    processing_time_ms: int = 0


class EventProcessor:
    """Event processing system with reliable delivery."""
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize event processor.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        # TODO: Initialize event processor
        pass
    
    def register_subscriber(self, subscriber: Subscriber) -> bool:
        """
        Register event subscriber.
        
        Args:
            subscriber: Subscriber configuration
            
        Returns:
            True if registered successfully
        """
        # TODO: Register subscriber
        pass
    
    def publish_event(self, event: Event) -> str:
        """
        Publish event to all matching subscribers.
        
        Args:
            event: Event to publish
            
        Returns:
            Event ID for tracking
        """
        # TODO: Publish event to subscribers
        pass
    
    def start_processing(self) -> None:
        """Start event processing workers."""
        # TODO: Start worker threads
        pass
    
    def stop_processing(self, timeout_seconds: int = 30) -> None:
        """Stop event processing gracefully."""
        # TODO: Stop workers gracefully
        pass
    
    def get_event_status(self, event_id: str) -> Dict[str, EventStatus]:
        """Get delivery status for event across all subscribers."""
        # TODO: Return status per subscriber
        pass
    
    def get_failed_events(self, subscriber_id: str) -> List[Event]:
        """Get events that failed for a specific subscriber."""
        # TODO: Return failed events
        pass
    
    def retry_failed_events(self, subscriber_id: str) -> int:
        """Retry failed events for subscriber."""
        # TODO: Retry failed events
        pass
    
    def get_subscriber_health(self) -> Dict[str, Dict]:
        """Get health metrics for all subscribers."""
        # TODO: Return subscriber health stats
        pass
    
    def _worker_loop(self, worker_id: int) -> None:
        """Main processing loop for worker thread."""
        # TODO: Process events from queue
        pass
    
    def _deliver_to_subscriber(self, event: Event, subscriber: Subscriber) -> DeliveryAttempt:
        """Deliver event to specific subscriber."""
        # TODO: Deliver event and track attempt
        pass
    
    def _should_retry(self, event_id: str, subscriber_id: str) -> bool:
        """Check if event should be retried for subscriber."""
        # TODO: Check retry eligibility
        pass
    
    def _move_to_dead_letter(self, event_id: str, subscriber_id: str) -> None:
        """Move event to dead letter queue."""
        # TODO: Move to dead letter queue
        pass


# Example event handlers
def payment_notification_handler(event: Event) -> bool:
    """Handle payment events for notifications."""
    print(f"[NOTIFICATIONS] Processing {event.event_type}: {event.payload}")
    time.sleep(0.1)  # Simulate processing
    return True


def analytics_handler(event: Event) -> bool:
    """Handle events for analytics."""
    print(f"[ANALYTICS] Processing {event.event_type}: {event.aggregate_id}")
    time.sleep(0.05)
    return True


def fraud_detection_handler(event: Event) -> bool:
    """Handle events for fraud detection."""
    print(f"[FRAUD] Analyzing {event.event_type}: {event.payload.get('amount', 'N/A')}")
    time.sleep(0.2)
    
    # Simulate occasional failures
    import random
    if random.random() < 0.2:  # 20% failure rate
        raise Exception("Fraud service temporarily unavailable")
    
    return True


def slow_handler(event: Event) -> bool:
    """Simulate slow subscriber."""
    print(f"[SLOW] Processing {event.event_type}...")
    time.sleep(1.0)  # Very slow
    return True


# Example usage and test cases
if __name__ == "__main__":
    processor = EventProcessor(max_workers=3)
    
    # Register subscribers
    subscribers = [
        Subscriber(
            id="notifications",
            name="Payment Notifications",
            handler=payment_notification_handler,
            event_types=["payment.created", "payment.completed", "payment.failed"],
            max_retries=3
        ),
        Subscriber(
            id="analytics", 
            name="Analytics Service",
            handler=analytics_handler,
            event_types=["payment.created", "payment.completed", "transfer.created"],
            max_retries=2
        ),
        Subscriber(
            id="fraud_detection",
            name="Fraud Detection",
            handler=fraud_detection_handler,
            event_types=["payment.created", "transfer.created"],
            max_retries=5
        )
    ]
    
    for subscriber in subscribers:
        processor.register_subscriber(subscriber)
    
    # Start processing
    processor.start_processing()
    
    # Publish test events
    events = [
        Event(
            id=str(uuid.uuid4()),
            event_type="payment.created",
            aggregate_id="payment_123",
            payload={"amount": 100.0, "user_id": "user_456", "currency": "USD"},
            timestamp=datetime.now(),
            sequence_number=1
        ),
        Event(
            id=str(uuid.uuid4()),
            event_type="payment.completed", 
            aggregate_id="payment_123",
            payload={"amount": 100.0, "status": "completed"},
            timestamp=datetime.now(),
            sequence_number=2
        ),
        Event(
            id=str(uuid.uuid4()),
            event_type="transfer.created",
            aggregate_id="transfer_789",
            payload={"amount": 50.0, "from_user": "user_123", "to_user": "user_456"},
            timestamp=datetime.now(),
            sequence_number=1
        )
    ]
    
    print("=== Publishing Events ===")
    event_ids = []
    for event in events:
        event_id = processor.publish_event(event)
        event_ids.append(event_id)
        print(f"Published: {event.event_type} -> {event_id}")
    
    # Wait for processing
    time.sleep(2)
    
    # Check event status
    print("\n=== Event Status ===")
    for event_id in event_ids:
        status = processor.get_event_status(event_id)
        print(f"Event {event_id[:8]}: {status}")
    
    # Check subscriber health
    print("\n=== Subscriber Health ===")
    health = processor.get_subscriber_health()
    for subscriber_id, metrics in health.items():
        print(f"{subscriber_id}: {metrics}")
    
    # Test failed event retry
    print("\n=== Retry Failed Events ===")
    for subscriber_id in ["notifications", "analytics", "fraud_detection"]:
        retried = processor.retry_failed_events(subscriber_id)
        if retried > 0:
            print(f"Retried {retried} events for {subscriber_id}")
    
    # Wait a bit more for retries
    time.sleep(1)
    
    # Final health check
    print("\n=== Final Health Check ===")
    health = processor.get_subscriber_health()
    for subscriber_id, metrics in health.items():
        print(f"{subscriber_id}: {metrics}")
    
    # Stop processing
    processor.stop_processing()
    print("\nEvent processing stopped")