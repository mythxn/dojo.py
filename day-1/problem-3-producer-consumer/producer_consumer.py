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
        pass  # TODO: Implement
    
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
        pass  # TODO: Implement
    
    def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get item from buffer, blocking if empty.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Item if available, None if timeout or shutdown
        """
        pass  # TODO: Implement
    
    def put_nowait(self, item: Any, priority: int = 0) -> bool:
        """
        Put item without blocking.
        
        Returns:
            True if item was added, False if buffer full
        """
        pass  # TODO: Implement
    
    def get_nowait(self) -> Optional[Any]:
        """
        Get item without blocking.
        
        Returns:
            Item if available, None if empty
        """
        pass  # TODO: Implement
    
    def size(self) -> int:
        """Get current buffer size."""
        pass  # TODO: Implement
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        pass  # TODO: Implement
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        pass  # TODO: Implement
    
    def shutdown(self) -> None:
        """Signal shutdown to wake up blocked threads."""
        pass  # TODO: Implement


class Producer:
    def __init__(self, buffer: BoundedBuffer, producer_id: str):
        """
        Initialize producer.
        
        Args:
            buffer: Shared buffer
            producer_id: Unique producer identifier
        """
        pass  # TODO: Implement
    
    def produce(self, item_generator: Callable, count: int = None) -> None:
        """
        Produce items using generator function.
        
        Args:
            item_generator: Function that generates items
            count: Number of items to produce (None = infinite)
        """
        pass  # TODO: Implement
    
    def produce_batch(self, items: List[Any]) -> None:
        """Produce a batch of items."""
        pass  # TODO: Implement
    
    def stop(self) -> None:
        """Stop the producer."""
        pass  # TODO: Implement
    
    def is_running(self) -> bool:
        """Check if producer is running."""
        pass  # TODO: Implement


class Consumer:
    def __init__(self, buffer: BoundedBuffer, consumer_id: str):
        """
        Initialize consumer.
        
        Args:
            buffer: Shared buffer
            consumer_id: Unique consumer identifier
        """
        pass  # TODO: Implement
    
    def consume(self, processor: Callable[[Any], None]) -> None:
        """
        Consume items and process them.
        
        Args:
            processor: Function to process each item
        """
        pass  # TODO: Implement
    
    def consume_batch(self, processor: Callable[[List[Any]], None], 
                     batch_size: int = 10, batch_timeout: float = 1.0) -> None:
        """
        Consume items in batches.
        
        Args:
            processor: Function to process batch of items
            batch_size: Maximum batch size
            batch_timeout: Maximum time to wait for full batch
        """
        pass  # TODO: Implement
    
    def stop(self) -> None:
        """Stop the consumer."""
        pass  # TODO: Implement
    
    def is_running(self) -> bool:
        """Check if consumer is running."""
        pass  # TODO: Implement


class ProducerConsumerSystem:
    def __init__(self, buffer_capacity: int, strategy: BufferStrategy = BufferStrategy.FIFO):
        """
        Initialize producer-consumer system.
        
        Args:
            buffer_capacity: Buffer capacity
            strategy: Buffer strategy
        """
        pass  # TODO: Implement
    
    def add_producer(self, producer_id: str, item_generator: Callable, 
                    count: Optional[int] = None) -> Producer:
        """Add a producer to the system."""
        pass  # TODO: Implement
    
    def add_consumer(self, consumer_id: str, processor: Callable) -> Consumer:
        """Add a consumer to the system."""
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start all producers and consumers."""
        pass  # TODO: Implement
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop all producers and consumers gracefully."""
        pass  # TODO: Implement
    
    def get_stats(self) -> ProducerConsumerStats:
        """Get system statistics."""
        pass  # TODO: Implement
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all producers to finish and buffer to be consumed.
        
        Returns:
            True if completed, False if timeout
        """
        pass  # TODO: Implement


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