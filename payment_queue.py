import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Callable, Optional


class PaymentPriority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


PRIORITY_ORDER = [PaymentPriority.HIGH, PaymentPriority.MEDIUM, PaymentPriority.LOW]


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
    def __init__(self, num_workers: int = 3):
        self.num_workers = num_workers
        self.queues = {priority: queue.Queue() for priority in PRIORITY_ORDER}
        self.processor_registry: dict[str, Callable] = {}
        self.dead_letter_queue: List[PaymentTask] = []
        self.lock = threading.Lock()
        self.workers: List[threading.Thread] = []
        self.stop_event = threading.Event()
        self.processed_tasks = 0

    def register_processor(self, task_type: str, processor_func: Callable) -> None:
        self.processor_registry[task_type] = processor_func

    def enqueue_payment(self, task: PaymentTask) -> bool:
        self.queues[task.priority].put(task)
        return True

    def start_workers(self) -> None:
        for i in range(self.num_workers):
            thread = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            thread.start()
            self.workers.append(thread)

    def stop_workers(self, timeout_seconds: int = 30) -> None:
        self.stop_event.set()
        for thread in self.workers:
            thread.join(timeout=timeout_seconds)

    def get_queue_stats(self) -> dict:
        return {
            "high": self.queues[PaymentPriority.HIGH].qsize(),
            "medium": self.queues[PaymentPriority.MEDIUM].qsize(),
            "low": self.queues[PaymentPriority.LOW].qsize(),
            "processed": self.processed_tasks,
            "dead_letter": len(self.dead_letter_queue)
        }

    def get_failed_tasks(self) -> List[PaymentTask]:
        return list(self.dead_letter_queue)

    def retry_failed_task(self, task_id: str) -> bool:
        for i, task in enumerate(self.dead_letter_queue):
            if task.id == task_id:
                del self.dead_letter_queue[i]
                task.retry_count = 0
                return self.enqueue_payment(task)
        return False

    def _worker_loop(self, worker_id: int) -> None:
        while not self.stop_event.is_set():
            task = self._get_next_task()
            if not task:
                continue

            success = self._process_task(task)
            if success:
                with self.lock:
                    self.processed_tasks += 1
            else:
                self._handle_failure(task)

    def _get_next_task(self) -> Optional[PaymentTask]:
        for priority in PRIORITY_ORDER:
            try:
                return self.queues[priority].get(timeout=0.1)
            except queue.Empty:
                continue
        return None

    def _process_task(self, task: PaymentTask) -> bool:
        func = self.processor_registry.get(task.task_type)
        if not func:
            return False
        try:
            return func(task)
        except Exception:
            return False

    def _handle_failure(self, task: PaymentTask):
        task.retry_count += 1
        if task.retry_count <= task.max_retries:
            self.enqueue_payment(task)
        else:
            with self.lock:
                self.dead_letter_queue.append(task)


# Example processors
def charge_card_processor(task: PaymentTask) -> bool:
    print(f"Processing card charge: {task.payment_id}")
    time.sleep(0.1)
    return True


def send_notification_processor(task: PaymentTask) -> bool:
    print(f"Sending notification for: {task.payment_id}")
    time.sleep(0.05)
    return True


def fraud_check_processor(task: PaymentTask) -> bool:
    print(f"Fraud check for: {task.payment_id}")
    time.sleep(0.2)
    return True


# Usage example
if __name__ == "__main__":
    payment_queue = PaymentProcessingQueue(num_workers=2)

    payment_queue.register_processor("charge_card", charge_card_processor)
    payment_queue.register_processor("send_notification", send_notification_processor)
    payment_queue.register_processor("fraud_check", fraud_check_processor)

    payment_queue.start_workers()

    now = datetime.now()
    tasks = [
        PaymentTask("task_1", "pay_123", "fraud_check", PaymentPriority.HIGH, {"amount": 10000}, now),
        PaymentTask("task_2", "pay_124", "charge_card", PaymentPriority.MEDIUM, {"amount": 50}, now),
        PaymentTask("task_3", "pay_125", "send_notification", PaymentPriority.LOW, {"email": "user@example.com"}, now)
    ]

    for task in tasks:
        payment_queue.enqueue_payment(task)
        print(f"Queued: {task.id}")

    time.sleep(2)
    print(f"Stats: {payment_queue.get_queue_stats()}")
    payment_queue.stop_workers()
    print("Workers stopped")
