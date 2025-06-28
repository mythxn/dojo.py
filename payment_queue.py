"""
PROBLEM: Payment Processing Queue (20-25 minutes)

BUSINESS CONTEXT:
Your payment system receives thousands of payment requests per minute.
Some payments are urgent (fraud alerts), others can wait (daily reports).
Implement a priority queue to process payments efficiently.

REQUIREMENTS:
1. Priority-based processing (HIGH, MEDIUM, LOW)
2. FIFO within same priority level
3. Thread-safe for multiple workers
4. Graceful shutdown without losing payments
5. Dead letter queue for failed payments

FOLLOW-UP QUESTIONS:
- How do you handle payments that keep failing?
- What if a worker crashes while processing a payment?
- How do you monitor queue health and backlog?
- How do you add more workers dynamically?
"""

from dataclasses import dataclass
from typing import Optional, List, Callable
from datetime import datetime
import threading
import queue
from enum import Enum
import time


class PaymentPriority(Enum):
    HIGH = 1    # Fraud alerts, chargebacks
    MEDIUM = 2  # Regular payments
    LOW = 3     # Reports, analytics


@dataclass
class PaymentTask:
    id: str
    payment_id: str
    task_type: str
    priority: PaymentPriority
    payload: dict
    created_at: datetime
    max_retries: int = 3
    retry_count: int = 0


class PaymentProcessingQueue:
    """Priority queue for processing payment tasks with worker pool."""
    
    def __init__(self, num_workers: int = 3):
        """
        Initialize payment processing queue.
        
        Args:
            num_workers: Number of worker threads to spawn
        """
        # TODO: Initialize queue and worker pool
        pass
    
    def enqueue_payment(self, task: PaymentTask) -> bool:
        """
        Add payment task to queue.
        
        Args:
            task: Payment task to process
            
        Returns:
            True if successfully queued
        """
        # TODO: Add task to priority queue
        pass
    
    def register_processor(self, task_type: str, processor_func: Callable) -> None:
        """
        Register a processor function for a specific task type.
        
        Args:
            task_type: Type of task (e.g., 'charge_card', 'send_notification')
            processor_func: Function to process the task
        """
        # TODO: Register processor function
        pass
    
    def start_workers(self) -> None:
        """Start worker threads to process queued tasks."""
        # TODO: Start worker threads
        pass
    
    def stop_workers(self, timeout_seconds: int = 30) -> None:
        """
        Gracefully stop all worker threads.
        
        Args:
            timeout_seconds: Maximum time to wait for workers to finish
        """
        # TODO: Implement graceful shutdown
        pass
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics (size, processed count, etc.)."""
        # TODO: Return queue statistics
        pass
    
    def get_failed_tasks(self) -> List[PaymentTask]:
        """Get tasks that have failed max retries (dead letter queue)."""
        # TODO: Return failed tasks
        pass
    
    def retry_failed_task(self, task_id: str) -> bool:
        """Manually retry a failed task."""
        # TODO: Retry specific failed task
        pass
    
    def _worker_loop(self, worker_id: int) -> None:
        """Main loop for worker thread."""
        # TODO: Implement worker processing loop
        pass
    
    def _process_task(self, task: PaymentTask) -> bool:
        """Process a single payment task."""
        # TODO: Execute the appropriate processor function
        pass


# Example processors
def charge_card_processor(task: PaymentTask) -> bool:
    """Process credit card charge."""
    print(f"Processing card charge: {task.payment_id}")
    # Simulate processing time
    time.sleep(0.1)
    return True


def send_notification_processor(task: PaymentTask) -> bool:
    """Send payment notification."""
    print(f"Sending notification for: {task.payment_id}")
    time.sleep(0.05)
    return True


def fraud_check_processor(task: PaymentTask) -> bool:
    """Perform fraud detection check."""
    print(f"Fraud check for: {task.payment_id}")
    time.sleep(0.2)
    return True


# Example usage and test cases
if __name__ == "__main__":
    # Initialize queue with 2 workers
    payment_queue = PaymentProcessingQueue(num_workers=2)
    
    # Register processors
    payment_queue.register_processor("charge_card", charge_card_processor)
    payment_queue.register_processor("send_notification", send_notification_processor)
    payment_queue.register_processor("fraud_check", fraud_check_processor)
    
    # Start workers
    payment_queue.start_workers()
    
    # Add some tasks
    tasks = [
        PaymentTask(
            id="task_1",
            payment_id="pay_123",
            task_type="fraud_check",
            priority=PaymentPriority.HIGH,
            payload={"amount": 10000, "user_id": "user_456"},
            created_at=datetime.now()
        ),
        PaymentTask(
            id="task_2", 
            payment_id="pay_124",
            task_type="charge_card",
            priority=PaymentPriority.MEDIUM,
            payload={"amount": 50, "card_id": "card_789"},
            created_at=datetime.now()
        ),
        PaymentTask(
            id="task_3",
            payment_id="pay_125", 
            task_type="send_notification",
            priority=PaymentPriority.LOW,
            payload={"user_email": "user@example.com"},
            created_at=datetime.now()
        )
    ]
    
    # Queue tasks
    for task in tasks:
        payment_queue.enqueue_payment(task)
        print(f"Queued: {task.id}")
    
    # Let workers process
    time.sleep(2)
    
    # Check stats
    stats = payment_queue.get_queue_stats()
    print(f"Queue stats: {stats}")
    
    # Stop workers
    payment_queue.stop_workers()
    print("Workers stopped")