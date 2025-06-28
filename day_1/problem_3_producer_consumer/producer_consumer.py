"""
Producer-Consumer with Bounded Buffer Implementation
==================================================

Implement thread-safe producer-consumer pattern with various buffer types.

Requirements:
- Thread-safe bounded buffer
- Multiple producers and consumers
- Graceful shutdown mechanism
- Backpressure handling when buffer is full
- Different buffer strategies (FIFO, Priority, etc.)

Your Tasks:
1. Implement BoundedBuffer with thread safety
2. Create Producer and Consumer classes
3. Add priority queue support
4. Implement graceful shutdown
5. Add monitoring and metrics

Interview Focus:
- Explain synchronization primitives (locks, conditions, semaphores)
- Discuss deadlock prevention
- Handle edge cases (shutdown, exceptions)
"""

import threading
import time
import queue
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import heapq
from concurrent.futures import ThreadPoolExecutor
from collections import deque


class BufferStrategy(Enum):
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"


@dataclass
class ProducerConsumerStats:
    items_produced: int = 0
    items_consumed: int = 0
    buffer_high_water_mark: int = 0
    producer_blocks: int = 0
    consumer_blocks: int = 0


@dataclass
class PriorityItem:
    priority: int
    item: Any
    
    def __lt__(self, other):
        return self.priority < other.priority


class BoundedBuffer:
    def __init__(self, capacity: int, strategy: BufferStrategy = BufferStrategy.FIFO):
        """
        Initialize bounded buffer.
        
        Args:
            capacity: Maximum buffer size
            strategy: Buffer strategy (FIFO, LIFO, PRIORITY)
        """
        self.capacity = capacity
        self.strategy = strategy
        self.buffer = [] if self.strategy == BufferStrategy.PRIORITY else deque()
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        self.shutdown_flag = False

    def put(self, item: Any, priority: int = 0, timeout: Optional[float] = None) -> bool:
        """
        Put item in buffer, blocking if full.
        
        Args:
            item: Item to add
            priority: Priority for priority queue (lower = higher priority)
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if item was added, False if timeout
        """
        with self.not_full:
            end_time = time.time() + timeout if timeout else None

            while len(self.buffer) >= self.capacity:
                if self.shutdown_flag:
                    return False
                remaining = end_time - time.time() if end_time else None
                if remaining is not None and remaining <= 0:
                    return False
                self.not_full.wait(timeout=remaining)

                if self.shutdown_flag:
                    return False

            # Final shutdown check before adding item
            if self.shutdown_flag:
                return False

            if self.strategy == BufferStrategy.PRIORITY:
                heapq.heappush(self.buffer, PriorityItem(priority, item))
            else:
                self.buffer.append(item)
            self.not_empty.notify()
            return True

    def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get item from buffer, blocking if empty.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Item if available, None if timeout or shutdown
        """
        with self.not_empty:
            end_time = time.time() + timeout if timeout else None

            while not self.buffer:
                if self.shutdown_flag:
                    return None
                remaining = end_time - time.time() if end_time else None
                if remaining is not None and remaining <= 0:
                    return None
                self.not_empty.wait(timeout=remaining)
                if self.shutdown_flag:
                    return None

            # Final shutdown check before removing item
            if self.shutdown_flag:
                return None

            if self.strategy == BufferStrategy.PRIORITY:
                item = heapq.heappop(self.buffer).item
            elif self.strategy == BufferStrategy.LIFO:
                item = self.buffer.pop()
            else:  # FIFO
                item = self.buffer.popleft()
            self.not_full.notify()
            return item
    
    def put_nowait(self, item: Any, priority: int = 0) -> bool:
        """
        Put item without blocking.
        
        Returns:
            True if item was added, False if buffer full
        """
        with self.lock:
            if len(self.buffer) >= self.capacity:
                return False
            else:
                if self.strategy == BufferStrategy.PRIORITY:
                    heapq.heappush(self.buffer, PriorityItem(priority, item))
                else:
                    self.buffer.append(item)
                    self.not_empty.notify()  # wake waiting consumers
                return True
    
    def get_nowait(self) -> Optional[Any]:
        """
        Get item without blocking.
        
        Returns:
            Item if available, None if empty
        """
        with self.lock:
            if not self.buffer:
                return None
            else:
                if self.strategy == BufferStrategy.PRIORITY:
                    item = heapq.heappop(self.buffer).item
                elif self.strategy == BufferStrategy.LIFO:
                    item = self.buffer.pop()
                else:  # FIFO
                    item = self.buffer.popleft()
                self.not_full.notify()  # wake waiting producers
                return item
    
    def size(self) -> int:
        """Get current buffer size."""
        with self.lock:
            return len(self.buffer)
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) >= self.capacity
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        with self.lock:
            return len(self.buffer) == 0
    
    def shutdown(self) -> None:
        """
        Shutdown the buffer, waking up all blocked threads.
        After shutdown, all put() operations return False and get() operations return None.
        """
        # Need to acquire both condition variable locks to notify properly
        with self.not_full:
            self.shutdown_flag = True
            self.not_full.notify_all()  # Wake up all blocked producers
        
        with self.not_empty:
            self.not_empty.notify_all()  # Wake up all blocked consumers


class Producer:
    def __init__(self, buffer: BoundedBuffer, producer_id: str):
        """
        Initialize producer.
        
        Args:
            buffer: Shared buffer
            producer_id: Unique producer identifier
        """
        self.buffer = buffer
        self.producer_id = producer_id
        self._running = threading.Event()
        self._running.set()
        self._thread = None
    
    def produce(self, item_generator: Callable, count: int = None) -> None:
        """
        Produce items using generator function.
        
        Args:
            item_generator: Function that generates items
            count: Number of items to produce (None = infinite)
        """
        def run():
            produced = 0
            gen = None
            
            # Initialize the generator if needed
            if callable(item_generator):
                gen = item_generator()
                # Check if calling it returned a generator
                if not hasattr(gen, '__next__'):
                    # It's not a generator, it's a function that returns values
                    gen = None
            else:
                # It's already a generator
                gen = item_generator
            
            while self._running.is_set() and (count is None or produced < count):
                try:
                    if gen is not None:
                        # Use the generator
                        item = next(gen)
                    else:
                        # Call the function each time
                        item = item_generator()
                        
                    success = self.buffer.put(item, timeout=1)
                    if success:
                        produced += 1
                    else:
                        time.sleep(0.01)
                except (StopIteration, TypeError):
                    break
            
            # Mark as not running when finished
            self._running.clear()
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
    
    def produce_batch(self, items: List[Any]) -> None:
        """Produce a batch of items."""
        for item in items:
            if not self._running.is_set():
                break
            self.buffer.put(item, timeout=1)
    
    def stop(self) -> None:
        """Stop the producer."""
        self._running.clear()
        if self._thread:
            self._thread.join()
    
    def is_running(self) -> bool:
        """Check if producer is running."""
        return self._running.is_set()


class Consumer:
    def __init__(self, buffer: BoundedBuffer, consumer_id: str):
        """
        Initialize consumer.
        
        Args:
            buffer: Shared buffer
            consumer_id: Unique consumer identifier
        """
        self.buffer = buffer
        self.consumer_id = consumer_id
        self._running = threading.Event()
        self._running.set()
        self._thread = None
    
    def consume(self, processor: Callable[[Any], None]) -> None:
        """
        Consume items and process them.
        
        Args:
            processor: Function to process each item
        """
        def run():
            while self._running.is_set():
                item = self.buffer.get(timeout=1)
                if item:
                    try:
                        processor(item)
                    except Exception as e:
                        # Log error but continue processing other items
                        print(f"Error processing item {item}: {e}")
                else:
                    time.sleep(0.01)
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def consume_batch(self, processor: Callable[[List[Any]], None], 
                     batch_size: int = 10, batch_timeout: float = 1.0) -> None:
        """
        Consume items in batches.
        
        Args:
            processor: Function to process batch of items
            batch_size: Maximum batch size
            batch_timeout: Maximum time to wait for full batch
        """

        def run():
            batch = []
            start_time = time.time()
            while self._running.is_set():
                item = self.buffer.get(timeout=batch_timeout)
                if item is not None:
                    batch.append(item)
                if len(batch) >= batch_size or (time.time() - start_time >= batch_timeout and batch):
                    processor(batch)
                    batch = []
                    start_time = time.time()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the consumer."""
        self._running.clear()
        if self._thread:
            self._thread.join()
    
    def is_running(self) -> bool:
        """Check if consumer is running."""
        return self._running.is_set()


class ProducerConsumerSystem:
    def __init__(self, buffer_capacity: int, strategy: BufferStrategy = BufferStrategy.FIFO):
        """
        Initialize producer-consumer system.
        
        Args:
            buffer_capacity: Buffer capacity
            strategy: Buffer strategy
        """
        self.buffer = BoundedBuffer(capacity=buffer_capacity, strategy=strategy)
        self.producers = []
        self.consumers = []
    
    def add_producer(self, producer_id: str, item_generator: Callable, 
                    count: Optional[int] = None) -> Producer:
        """Add a producer to the system."""
        producer = Producer(self.buffer, producer_id)
        self.producers.append(producer)
        producer.produce(item_generator, count)
        return producer
    
    def add_consumer(self, consumer_id: str, processor: Callable) -> Consumer:
        """Add a consumer to the system."""
        consumer = Consumer(self.buffer, consumer_id)
        self.consumers.append(consumer)
        consumer.consume(processor)
        return consumer
    
    def start(self) -> None:
        """Start all producers and consumers."""
        pass  # already auto-started on add
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop all producers and consumers gracefully."""
        self.buffer.shutdown()

        for producer in self.producers:
            producer.stop()

        for consumer in self.consumers:
            consumer.stop()

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        start = time.time()
        while True:
            all_done = all(not p.is_running() for p in self.producers)
            buffer_empty = self.buffer.is_empty()

            if all_done and buffer_empty:
                return True

            if timeout and (time.time() - start > timeout):
                return False

            time.sleep(0.05)


class WorkStealingSystem:
    """Work-stealing variant where idle consumers can steal from busy ones"""
    
    def __init__(self, num_workers: int, buffer_capacity: int):
        pass  # TODO: Implement
    
    def submit_work(self, work_item: Any) -> None:
        """Submit work to be processed."""
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start work-stealing system."""
        pass  # TODO: Implement
    
    def stop(self) -> None:
        """Stop work-stealing system."""
        pass  # TODO: Implement


class BackpressureHandler:
    """Handle backpressure when producers are faster than consumers"""
    
    def __init__(self, buffer: BoundedBuffer):
        pass  # TODO: Implement
    
    def apply_backpressure(self, producer: Producer) -> None:
        """Apply backpressure to slow down producer."""
        pass  # TODO: Implement
    
    def monitor_buffer_levels(self) -> None:
        """Monitor buffer levels and apply backpressure."""
        pass  # TODO: Implement


# Example usage patterns
def example_simple_producer_consumer():
    """Example of basic producer-consumer setup"""
    pass  # TODO: Implement


def example_priority_queue():
    """Example using priority queue"""
    pass  # TODO: Implement


def example_batch_processing():
    """Example of batch processing"""
    pass  # TODO: Implement


def example_work_stealing():
    """Example of work-stealing pattern"""
    pass  # TODO: Implement