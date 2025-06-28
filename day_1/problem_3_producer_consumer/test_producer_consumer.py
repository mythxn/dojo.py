"""
Test cases for Producer-Consumer implementations
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from day_1.problem_3_producer_consumer.producer_consumer import (
    BoundedBuffer, Producer, Consumer, ProducerConsumerSystem,
    BufferStrategy, PriorityItem, WorkStealingSystem
)


class TestBoundedBuffer:
    
    def test_basic_fifo_operations(self):
        """Test basic FIFO buffer operations"""
        buffer = BoundedBuffer(capacity=3, strategy=BufferStrategy.FIFO)
        
        # Test put operations
        assert buffer.put_nowait("item1") == True
        assert buffer.put_nowait("item2") == True
        assert buffer.put_nowait("item3") == True
        assert buffer.size() == 3
        assert buffer.is_full() == True
        
        # Buffer is full, next put should fail
        assert buffer.put_nowait("item4") == False
        
        # Test get operations (FIFO order)
        assert buffer.get_nowait() == "item1"
        assert buffer.get_nowait() == "item2"
        assert buffer.get_nowait() == "item3"
        assert buffer.is_empty() == True
        
        # Buffer is empty, next get should return None
        assert buffer.get_nowait() is None
    
    def test_lifo_buffer(self):
        """Test LIFO (stack) buffer behavior"""
        buffer = BoundedBuffer(capacity=3, strategy=BufferStrategy.LIFO)
        
        buffer.put_nowait("item1")
        buffer.put_nowait("item2")
        buffer.put_nowait("item3")
        
        # LIFO order: last in, first out
        assert buffer.get_nowait() == "item3"
        assert buffer.get_nowait() == "item2"
        assert buffer.get_nowait() == "item1"
    
    def test_priority_buffer(self):
        """Test priority queue buffer"""
        buffer = BoundedBuffer(capacity=5, strategy=BufferStrategy.PRIORITY)
        
        # Add items with different priorities (lower = higher priority)
        buffer.put_nowait("low_priority", priority=10)
        buffer.put_nowait("high_priority", priority=1)
        buffer.put_nowait("medium_priority", priority=5)
        buffer.put_nowait("highest_priority", priority=0)
        
        # Should come out in priority order
        assert buffer.get_nowait() == "highest_priority"
        assert buffer.get_nowait() == "high_priority"
        assert buffer.get_nowait() == "medium_priority"
        assert buffer.get_nowait() == "low_priority"
    
    def test_blocking_put_timeout(self):
        """Test blocking put with timeout"""
        buffer = BoundedBuffer(capacity=1)
        
        # Fill buffer
        assert buffer.put("item1") == True
        
        # Next put should timeout
        start_time = time.time()
        result = buffer.put("item2", timeout=0.5)
        elapsed = time.time() - start_time
        
        assert result == False
        assert 0.4 < elapsed < 0.6  # Should timeout around 0.5 seconds
    
    def test_blocking_get_timeout(self):
        """Test blocking get with timeout"""
        buffer = BoundedBuffer(capacity=3)
        
        # Empty buffer, get should timeout
        start_time = time.time()
        result = buffer.get(timeout=0.5)
        elapsed = time.time() - start_time
        
        assert result is None
        assert 0.4 < elapsed < 0.6
    
    def test_concurrent_producers_consumers(self):
        """Test multiple producers and consumers"""
        buffer = BoundedBuffer(capacity=10)
        results = []
        
        def producer(items):
            for item in items:
                buffer.put(item)
        
        def consumer(num_items):
            consumed = []
            for _ in range(num_items):
                item = buffer.get()
                if item is not None:
                    consumed.append(item)
            results.extend(consumed)
        
        # Start producers and consumers
        with ThreadPoolExecutor(max_workers=6) as executor:
            # 2 producers
            executor.submit(producer, [f"p1_item_{i}" for i in range(10)])
            executor.submit(producer, [f"p2_item_{i}" for i in range(10)])
            
            # 2 consumers
            executor.submit(consumer, 10)
            executor.submit(consumer, 10)
        
        assert len(results) == 20
        assert len(set(results)) == 20  # All items should be unique
    
    def test_shutdown_mechanism(self):
        """Test graceful shutdown wakes up blocked threads"""
        # Use two separate buffers to test both scenarios independently
        full_buffer = BoundedBuffer(capacity=1)
        empty_buffer = BoundedBuffer(capacity=1)
        
        # Fill one buffer, leave other empty
        full_buffer.put("item1")
        
        results = {}
        
        def blocked_producer():
            # This will block since buffer is full
            result = full_buffer.put("item2", timeout=10)  # Long timeout
            results['producer_result'] = result
        
        def blocked_consumer():
            # This will block since buffer is empty
            result = empty_buffer.get(timeout=10)  # Long timeout  
            results['consumer_result'] = result
        
        # Start blocked threads  
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(blocked_producer)
            executor.submit(blocked_consumer)
            
            # Let threads start and block
            time.sleep(0.1)
            
            # Shutdown should wake up blocked threads
            full_buffer.shutdown()   # Wake up producer
            empty_buffer.shutdown()  # Wake up consumer
        
        # Blocked operations should return False/None after shutdown
        assert results.get('producer_result') == False
        assert results.get('consumer_result') is None


class TestProducer:
    
    def test_producer_basic_functionality(self):
        """Test basic producer functionality"""
        buffer = BoundedBuffer(capacity=10)
        producer = Producer(buffer, "producer1")
        
        items = []
        def item_generator():
            for i in range(5):
                item = f"item_{i}"
                items.append(item)
                return item
        
        # Produce 5 items
        producer.produce(item_generator, count=5)
        
        # Check items are in buffer
        assert buffer.size() == 5
        for i in range(5):
            assert buffer.get_nowait() == f"item_{i}"
    
    def test_producer_batch_production(self):
        """Test batch production"""
        buffer = BoundedBuffer(capacity=10)
        producer = Producer(buffer, "producer1")
        
        items = ["item1", "item2", "item3", "item4", "item5"]
        producer.produce_batch(items)
        
        assert buffer.size() == 5
        for item in items:
            assert buffer.get_nowait() == item
    
    def test_producer_stop_mechanism(self):
        """Test producer stop mechanism"""
        buffer = BoundedBuffer(capacity=100)
        producer = Producer(buffer, "producer1")
        
        def slow_generator():
            i = 0
            while True:
                time.sleep(0.1)  # Slow generation
                yield f"item_{i}"
                i += 1
        
        # Start producer in background
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(producer.produce, slow_generator)
            
            # Let it produce a few items
            time.sleep(0.3)
            
            # Stop producer
            producer.stop()
            
            # Should complete quickly after stop
            future.result(timeout=1.0)
        
        assert not producer.is_running()


class TestConsumer:
    
    def test_consumer_basic_functionality(self):
        """Test basic consumer functionality"""
        buffer = BoundedBuffer(capacity=10)
        consumer = Consumer(buffer, "consumer1")
        
        # Add items to buffer
        items = ["item1", "item2", "item3"]
        for item in items:
            buffer.put_nowait(item)
        
        processed_items = []
        def processor(item):
            processed_items.append(item)
        
        # Start consumer in background and let it process
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(consumer.consume, processor)
            
            # Let it consume items
            time.sleep(0.1)
            
            # Stop consumer
            consumer.stop()
            buffer.shutdown()  # Wake up blocked consumer
            
            future.result(timeout=1.0)
        
        assert len(processed_items) == 3
        assert set(processed_items) == set(items)
    
    def test_consumer_batch_processing(self):
        """Test batch processing"""
        buffer = BoundedBuffer(capacity=20)
        consumer = Consumer(buffer, "consumer1")
        
        # Add items to buffer
        for i in range(15):
            buffer.put_nowait(f"item_{i}")
        
        processed_batches = []
        def batch_processor(batch):
            processed_batches.append(list(batch))
        
        # Process in batches of 5
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                consumer.consume_batch, 
                batch_processor, 
                batch_size=5, 
                batch_timeout=0.5
            )
            
            time.sleep(0.2)  # Let it process
            consumer.stop()
            buffer.shutdown()
            
            future.result(timeout=2.0)
        
        # Should have processed 3 batches of 5 items each
        assert len(processed_batches) == 3
        total_items = sum(len(batch) for batch in processed_batches)
        assert total_items == 15
    
    def test_consumer_exception_handling(self):
        """Test consumer handles processor exceptions gracefully"""
        buffer = BoundedBuffer(capacity=10)
        consumer = Consumer(buffer, "consumer1")
        
        # Add items that will cause processor to fail
        buffer.put_nowait("good_item")
        buffer.put_nowait("error_item")
        buffer.put_nowait("another_good_item")
        
        processed_items = []
        def failing_processor(item):
            if "error" in item:
                raise ValueError(f"Processing failed for {item}")
            processed_items.append(item)
        
        # Consumer should continue despite exceptions
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(consumer.consume, failing_processor)
            
            time.sleep(0.1)
            consumer.stop()
            buffer.shutdown()
            
            future.result(timeout=1.0)
        
        # Should have processed good items despite the error
        assert "good_item" in processed_items
        assert "another_good_item" in processed_items
        assert "error_item" not in processed_items


class TestProducerConsumerSystem:
    
    def test_system_basic_operation(self):
        """Test complete producer-consumer system"""
        system = ProducerConsumerSystem(buffer_capacity=20)
        
        # Track processed items
        processed_items = []
        
        def item_generator():
            for i in range(10):
                yield f"item_{i}"
        
        def processor(item):
            processed_items.append(item)
        
        # Add producer and consumer
        producer = system.add_producer("p1", item_generator, count=10)
        consumer = system.add_consumer("c1", processor)
        
        # Start system
        system.start()
        
        # Wait for completion
        assert system.wait_for_completion(timeout=5.0) == True
        
        # Stop system
        system.stop()
        
        # Verify all items were processed
        assert len(processed_items) == 10
        assert set(processed_items) == {f"item_{i}" for i in range(10)}
    
    def test_multiple_producers_consumers(self):
        """Test system with multiple producers and consumers"""
        system = ProducerConsumerSystem(buffer_capacity=50)
        
        processed_items = []
        lock = threading.Lock()
        
        def producer_generator(producer_id):
            for i in range(20):
                yield f"p{producer_id}_item_{i}"
        
        def processor(item):
            with lock:
                processed_items.append(item)
        
        # Add multiple producers and consumers
        for i in range(3):
            system.add_producer(f"p{i}", lambda pid=i: producer_generator(pid), count=20)
        
        for i in range(2):
            system.add_consumer(f"c{i}", processor)
        
        system.start()
        assert system.wait_for_completion(timeout=10.0) == True
        system.stop()
        
        # Should have processed 60 items total (3 producers × 20 items)
        assert len(processed_items) == 60
        assert len(set(processed_items)) == 60  # All unique
    
    def test_system_statistics(self):
        """Test system statistics collection"""
        system = ProducerConsumerSystem(buffer_capacity=10)
        
        def item_generator():
            for i in range(5):
                yield f"item_{i}"
        
        def processor(item):
            pass  # Just consume
        
        system.add_producer("p1", item_generator, count=5)
        system.add_consumer("c1", processor)
        
        system.start()
        system.wait_for_completion(timeout=5.0)
        system.stop()
        
        stats = system.get_stats()
        assert stats.items_produced == 5
        assert stats.items_consumed == 5
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown of system"""
        system = ProducerConsumerSystem(buffer_capacity=100)
        
        def slow_generator():
            i = 0
            while True:
                time.sleep(0.1)
                yield f"item_{i}"
                i += 1
        
        def slow_processor(item):
            time.sleep(0.05)  # Slow processing
        
        system.add_producer("p1", slow_generator)  # Infinite producer
        system.add_consumer("c1", slow_processor)
        
        system.start()
        
        # Let it run briefly
        time.sleep(0.5)
        
        # Should shutdown gracefully within timeout
        start_time = time.time()
        system.stop(timeout=2.0)
        shutdown_time = time.time() - start_time
        
        assert shutdown_time < 2.5  # Should shutdown within timeout


class TestWorkStealingSystem:
    
    def test_work_stealing_basic(self):
        """Test basic work-stealing functionality"""
        system = WorkStealingSystem(num_workers=3, buffer_capacity=10)
        
        processed_items = []
        lock = threading.Lock()
        
        def work_processor(item):
            with lock:
                processed_items.append(item)
            time.sleep(0.01)  # Small delay
        
        # Submit work items
        system.start()
        
        for i in range(20):
            system.submit_work(f"work_item_{i}")
        
        # Wait for processing
        time.sleep(1.0)
        system.stop()
        
        # All items should be processed
        assert len(processed_items) == 20
        assert len(set(processed_items)) == 20


class TestBufferStrategies:
    
    def test_strategy_comparison(self):
        """Compare different buffer strategies under load"""
        strategies = [BufferStrategy.FIFO, BufferStrategy.LIFO, BufferStrategy.PRIORITY]
        results = {}
        
        for strategy in strategies:
            buffer = BoundedBuffer(capacity=100, strategy=strategy)
            items_out = []
            
            # Add items
            if strategy == BufferStrategy.PRIORITY:
                for i in range(10):
                    buffer.put_nowait(f"item_{i}", priority=i)
            else:
                for i in range(10):
                    buffer.put_nowait(f"item_{i}")
            
            # Get all items
            while not buffer.is_empty():
                item = buffer.get_nowait()
                if item:
                    items_out.append(item)
            
            results[strategy] = items_out
        
        # Verify different ordering
        fifo_result = results[BufferStrategy.FIFO]
        lifo_result = results[BufferStrategy.LIFO]
        priority_result = results[BufferStrategy.PRIORITY]
        
        # FIFO should maintain input order
        assert fifo_result == [f"item_{i}" for i in range(10)]
        
        # LIFO should reverse order
        assert lifo_result == [f"item_{i}" for i in range(9, -1, -1)]
        
        # Priority should order by priority (0 is highest)
        assert priority_result[0] == "item_0"
        assert priority_result[-1] == "item_9"


class TestPerformance:
    
    def test_high_throughput(self):
        """Test system performance under high load"""
        system = ProducerConsumerSystem(buffer_capacity=1000)
        
        processed_count = [0]
        lock = threading.Lock()
        
        def fast_generator():
            for i in range(10000):
                yield f"item_{i}"
        
        def fast_processor(item):
            with lock:
                processed_count[0] += 1
        
        # Multiple producers and consumers for high throughput
        for i in range(3):
            system.add_producer(f"p{i}", fast_generator, count=10000)
        
        for i in range(5):
            system.add_consumer(f"c{i}", fast_processor)
        
        start_time = time.time()
        system.start()
        system.wait_for_completion(timeout=30.0)
        system.stop()
        duration = time.time() - start_time
        
        # Should process 30,000 items efficiently
        assert processed_count[0] == 30000
        throughput = processed_count[0] / duration
        assert throughput > 1000  # At least 1000 items/second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])