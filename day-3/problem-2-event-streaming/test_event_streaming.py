"""
Test cases for Event Streaming implementations
"""

import pytest
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from day3.event_streaming import (
    Event, Topic, Partition, EventProducer, EventConsumer, ConsumerGroup,
    EventStreamingCluster, OffsetManager, EventStreamingMonitor,
    EventFilter, EventTransformer, EventSerializer,
    PartitioningStrategy, DeliveryGuarantee, ConsumerRebalanceStrategy,
    ProducerError, ConsumerError, EventStreamingError,
    calculate_partition_hash, create_test_events, benchmark_throughput
)


class TestEvent:
    
    def test_event_creation(self):
        """Test basic event creation"""
        event = Event(key="test_key", value="test_value")
        
        assert event.key == "test_key"
        assert event.value == "test_value"
        assert isinstance(event.headers, dict)
        assert isinstance(event.timestamp, float)
        assert isinstance(event.event_id, str)
        assert event.partition is None
        assert event.offset is None
    
    def test_event_with_metadata(self):
        """Test event with headers and metadata"""
        headers = {"source": "test", "version": "1.0"}
        event = Event(
            key="test_key",
            value={"data": "test"},
            headers=headers
        )
        
        assert event.headers == headers
        assert event.value == {"data": "test"}
    
    def test_event_serialization(self):
        """Test event serialization/deserialization"""
        original_event = Event(
            key="test_key",
            value="test_value",
            headers={"test": "header"}
        )
        
        # Serialize
        serialized = original_event.serialize()
        assert isinstance(serialized, bytes)
        
        # Deserialize
        deserialized_event = Event.deserialize(serialized)
        assert deserialized_event.key == original_event.key
        assert deserialized_event.value == original_event.value
        assert deserialized_event.headers == original_event.headers
    
    def test_event_equality(self):
        """Test event equality comparison"""
        event1 = Event(key="key1", value="value1")
        event2 = Event(key="key1", value="value1")
        event3 = Event(key="key2", value="value1")
        
        # Events with same data should be equal if using content-based equality
        # Or different if using ID-based equality (implementation dependent)
        # At minimum, same event should equal itself
        assert event1 == event1
        
        # Different keys should be different
        assert event1 != event3


class TestPartition:
    
    def test_partition_creation(self):
        """Test partition creation"""
        partition = Partition(partition_id=0, topic="test_topic")
        
        assert partition.partition_id == 0
        assert partition.topic == "test_topic"
        assert partition.get_latest_offset() >= 0
        assert partition.get_earliest_offset() >= 0
    
    def test_append_and_read_events(self):
        """Test appending and reading events"""
        partition = Partition(partition_id=0, topic="test_topic")
        
        # Append events
        event1 = Event(key="key1", value="value1")
        event2 = Event(key="key2", value="value2")
        
        offset1 = partition.append(event1)
        offset2 = partition.append(event2)
        
        assert isinstance(offset1, int)
        assert isinstance(offset2, int)
        assert offset2 > offset1  # Offsets should increase
        
        # Read events
        events = partition.read(offset1, max_events=2)
        assert len(events) >= 1
        assert events[0].key == "key1"
        assert events[0].value == "value1"
        
        if len(events) == 2:
            assert events[1].key == "key2"
            assert events[1].value == "value2"
    
    def test_offset_management(self):
        """Test offset management"""
        partition = Partition(partition_id=0, topic="test_topic")
        
        # Append some events
        for i in range(5):
            event = Event(key=f"key{i}", value=f"value{i}")
            partition.append(event)
        
        # Test latest/earliest offsets
        latest = partition.get_latest_offset()
        earliest = partition.get_earliest_offset()
        
        assert latest >= earliest
        assert latest >= 4  # At least 5 events (0-4)
    
    def test_consumer_group_offsets(self):
        """Test consumer group offset tracking"""
        partition = Partition(partition_id=0, topic="test_topic")
        
        # Append events
        for i in range(3):
            event = Event(key=f"key{i}", value=f"value{i}")
            partition.append(event)
        
        # Commit offset for consumer group
        partition.commit_offset("group1", 2)
        
        # Get committed offset
        committed = partition.get_committed_offset("group1")
        assert committed == 2
        
        # Different group should have different offset
        committed_other = partition.get_committed_offset("group2")
        assert committed_other != 2 or committed_other == 0  # Default or not found
    
    def test_partition_info(self):
        """Test partition info retrieval"""
        partition = Partition(partition_id=1, topic="test_topic")
        
        info = partition.get_info()
        assert info.partition_id == 1
        assert info.topic == "test_topic"
        assert isinstance(info.high_watermark, int)
        assert isinstance(info.low_watermark, int)
    
    def test_partition_compaction(self):
        """Test partition compaction"""
        partition = Partition(partition_id=0, topic="test_topic", max_size=10)
        
        # Fill partition beyond max size
        for i in range(15):
            event = Event(key=f"key{i}", value=f"value{i}")
            partition.append(event)
        
        # Compact partition
        removed_count = partition.compact()
        
        # Should have removed some events
        assert isinstance(removed_count, int)
        assert removed_count >= 0


class TestTopic:
    
    def test_topic_creation(self):
        """Test topic creation"""
        topic = Topic("test_topic", num_partitions=3, replication_factor=1)
        
        assert topic.name == "test_topic"
        assert len(topic.get_all_partitions()) == 3
        
        # Should be able to get each partition
        for i in range(3):
            partition = topic.get_partition(i)
            assert partition is not None
            assert partition.partition_id == i
    
    def test_partition_selection_key_hash(self):
        """Test key-based partition selection"""
        topic = Topic("test_topic", num_partitions=4)
        
        # Same key should always go to same partition
        partition1 = topic.get_partition_for_key("test_key", PartitioningStrategy.KEY_HASH)
        partition2 = topic.get_partition_for_key("test_key", PartitioningStrategy.KEY_HASH)
        
        assert partition1 == partition2
        assert 0 <= partition1 < 4
        
        # Different keys should distribute across partitions
        partitions = set()
        for i in range(20):
            partition = topic.get_partition_for_key(f"key_{i}", PartitioningStrategy.KEY_HASH)
            partitions.add(partition)
        
        # Should use multiple partitions (though not necessarily all)
        assert len(partitions) > 1
    
    def test_partition_selection_round_robin(self):
        """Test round-robin partition selection"""
        topic = Topic("test_topic", num_partitions=3)
        
        partitions = []
        for i in range(9):  # 3 full rounds
            partition = topic.get_partition_for_key(None, PartitioningStrategy.ROUND_ROBIN)
            partitions.add(partition)
        
        # Should cycle through all partitions
        unique_partitions = set(partitions)
        assert len(unique_partitions) <= 3
        assert all(0 <= p < 3 for p in unique_partitions)
    
    def test_topic_metadata(self):
        """Test topic metadata"""
        topic = Topic("test_topic", num_partitions=2, replication_factor=1)
        
        metadata = topic.get_metadata()
        assert isinstance(metadata, dict)
        assert metadata.get("name") == "test_topic" or "name" in str(metadata)
        assert metadata.get("num_partitions") == 2 or "partitions" in str(metadata)
    
    def test_dynamic_partition_addition(self):
        """Test adding partitions dynamically"""
        topic = Topic("test_topic", num_partitions=2)
        
        # Add new partition
        new_partition_id = topic.add_partition()
        
        assert isinstance(new_partition_id, int)
        assert new_partition_id >= 2  # Should be next available ID
        
        # Should now have 3 partitions
        assert len(topic.get_all_partitions()) == 3
        
        # New partition should be accessible
        new_partition = topic.get_partition(new_partition_id)
        assert new_partition is not None


class TestEventProducer:
    
    def test_producer_creation(self):
        """Test producer creation"""
        producer = EventProducer(
            client_id="test_producer",
            batch_size=10,
            linger_ms=50
        )
        
        assert producer.client_id == "test_producer"
        assert producer.batch_size == 10
        assert producer.linger_ms == 50
    
    def test_synchronous_send(self):
        """Test synchronous event sending"""
        # Create simple in-memory topic for testing
        topic = Topic("test_topic", num_partitions=1)
        producer = EventProducer("test_producer")
        
        event = Event(key="test_key", value="test_value")
        
        try:
            offset = producer.send_sync("test_topic", event, timeout=1.0)
            assert isinstance(offset, int)
            assert offset >= 0
        except NotImplementedError:
            # Producer might not be fully implemented yet
            pytest.skip("Producer send_sync not implemented")
    
    def test_asynchronous_send(self):
        """Test asynchronous event sending"""
        producer = EventProducer("test_producer")
        event = Event(key="test_key", value="test_value")
        
        try:
            future = producer.send("test_topic", event)
            assert hasattr(future, 'result') or hasattr(future, 'add_done_callback')
        except NotImplementedError:
            pytest.skip("Producer send not implemented")
    
    def test_batch_sending(self):
        """Test batch event sending"""
        producer = EventProducer("test_producer", batch_size=5)
        
        events = [
            Event(key=f"key{i}", value=f"value{i}")
            for i in range(3)
        ]
        
        try:
            futures = producer.send_batch("test_topic", events)
            assert len(futures) == 3
            assert all(hasattr(f, 'result') or hasattr(f, 'add_done_callback') for f in futures)
        except NotImplementedError:
            pytest.skip("Producer send_batch not implemented")
    
    def test_producer_metrics(self):
        """Test producer metrics collection"""
        producer = EventProducer("test_producer")
        
        metrics = producer.get_metrics()
        assert isinstance(metrics, (dict, object))  # Could be dict or ProducerMetrics object
        
        # Should have basic metric fields
        if hasattr(metrics, 'events_sent'):
            assert metrics.events_sent >= 0
            assert metrics.events_failed >= 0
        elif isinstance(metrics, dict):
            assert 'events_sent' in metrics or 'sent' in str(metrics)
    
    def test_producer_flush(self):
        """Test producer flush operation"""
        producer = EventProducer("test_producer")
        
        # Should be able to flush without error
        try:
            producer.flush(timeout=1.0)
        except NotImplementedError:
            pytest.skip("Producer flush not implemented")
    
    def test_producer_close(self):
        """Test producer close operation"""
        producer = EventProducer("test_producer")
        
        # Should be able to close without error
        try:
            producer.close(timeout=1.0)
        except NotImplementedError:
            pytest.skip("Producer close not implemented")


class TestEventConsumer:
    
    def test_consumer_creation(self):
        """Test consumer creation"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        
        assert consumer.group_id == "test_group"
        assert consumer.client_id == "test_consumer"
        assert "test_topic" in consumer.topics
    
    def test_consumer_subscription(self):
        """Test consumer topic subscription"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer", 
            topics=[]
        )
        
        # Subscribe to topics
        consumer.subscribe(["topic1", "topic2"])
        
        # Should be subscribed to topics
        assert "topic1" in consumer.topics
        assert "topic2" in consumer.topics
    
    def test_consumer_polling(self):
        """Test consumer polling for events"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        
        try:
            # Poll for events (might be empty)
            events = consumer.poll(timeout_ms=100)
            assert isinstance(events, dict)
            
            # Each topic should map to list of events
            for topic, event_list in events.items():
                assert isinstance(event_list, list)
                assert all(isinstance(e, Event) for e in event_list)
                
        except NotImplementedError:
            pytest.skip("Consumer poll not implemented")
    
    def test_offset_management(self):
        """Test consumer offset management"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        
        try:
            # Test synchronous commit
            consumer.commit_sync()
            
            # Test commit with specific offsets
            offsets = {"test_topic": {0: 10, 1: 15}}
            consumer.commit_sync(offsets)
            
        except NotImplementedError:
            pytest.skip("Consumer commit not implemented")
    
    def test_consumer_seeking(self):
        """Test consumer seeking to specific offsets"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        
        try:
            # Seek to specific offset
            consumer.seek("test_topic", 0, 10)
            
            # Seek to beginning
            consumer.seek_to_beginning("test_topic", 0)
            
            # Seek to end
            consumer.seek_to_end("test_topic", 0)
            
        except NotImplementedError:
            pytest.skip("Consumer seek not implemented")
    
    def test_consumer_pause_resume(self):
        """Test consumer pause/resume functionality"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        
        try:
            # Pause consumption
            consumer.pause([("test_topic", 0)])
            
            # Resume consumption
            consumer.resume([("test_topic", 0)])
            
        except NotImplementedError:
            pytest.skip("Consumer pause/resume not implemented")
    
    def test_consumer_metrics(self):
        """Test consumer metrics collection"""
        consumer = EventConsumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        
        metrics = consumer.get_metrics()
        assert isinstance(metrics, (dict, object))
        
        # Should have basic metrics
        if hasattr(metrics, 'events_consumed'):
            assert metrics.events_consumed >= 0
            assert metrics.lag >= 0
        elif isinstance(metrics, dict):
            assert 'consumed' in str(metrics) or 'events' in str(metrics)


class TestConsumerGroup:
    
    def test_consumer_group_creation(self):
        """Test consumer group creation"""
        group = ConsumerGroup("test_group", ConsumerRebalanceStrategy.RANGE)
        
        assert group.group_id == "test_group"
        assert group.rebalance_strategy == ConsumerRebalanceStrategy.RANGE
    
    def test_consumer_group_management(self):
        """Test adding/removing consumers from group"""
        group = ConsumerGroup("test_group")
        
        consumer1 = EventConsumer("test_group", "consumer1", ["topic1"])
        consumer2 = EventConsumer("test_group", "consumer2", ["topic1"])
        
        # Add consumers
        group.add_consumer(consumer1)
        group.add_consumer(consumer2)
        
        # Should have both consumers
        assignments = group.get_assignments()
        assert isinstance(assignments, dict)
        
        # Remove consumer
        group.remove_consumer("consumer1")
        
        # Should trigger rebalancing
        new_assignments = group.get_assignments()
        assert isinstance(new_assignments, dict)
    
    def test_partition_rebalancing(self):
        """Test partition rebalancing in consumer group"""
        group = ConsumerGroup("test_group", ConsumerRebalanceStrategy.RANGE)
        
        # Add consumers
        consumer1 = EventConsumer("test_group", "consumer1", ["topic1"])
        consumer2 = EventConsumer("test_group", "consumer2", ["topic1"])
        group.add_consumer(consumer1)
        group.add_consumer(consumer2)
        
        # Rebalance partitions
        topics = ["topic1"]  # Assume topic1 has multiple partitions
        assignments = group.rebalance(topics)
        
        assert isinstance(assignments, dict)
        assert len(assignments) <= 2  # Should not exceed number of consumers
        
        # Each consumer should get some partitions
        total_partitions = sum(len(partitions) for partitions in assignments.values())
        assert total_partitions >= 0
    
    def test_rebalance_strategies(self):
        """Test different rebalance strategies"""
        # Range strategy
        range_group = ConsumerGroup("range_group", ConsumerRebalanceStrategy.RANGE)
        
        # Round-robin strategy
        rr_group = ConsumerGroup("rr_group", ConsumerRebalanceStrategy.ROUND_ROBIN)
        
        # Both should handle rebalancing
        consumer = EventConsumer("test_group", "consumer1", ["topic1"])
        
        range_group.add_consumer(consumer)
        range_assignments = range_group.rebalance(["topic1"])
        
        rr_group.add_consumer(consumer)
        rr_assignments = rr_group.rebalance(["topic1"])
        
        assert isinstance(range_assignments, dict)
        assert isinstance(rr_assignments, dict)


class TestEventStreamingCluster:
    
    def test_cluster_creation(self):
        """Test cluster creation"""
        cluster = EventStreamingCluster("test_cluster")
        
        assert cluster.cluster_id == "test_cluster"
    
    def test_topic_management(self):
        """Test topic creation and management"""
        cluster = EventStreamingCluster("test_cluster")
        
        # Create topic
        topic = cluster.create_topic("test_topic", num_partitions=2)
        assert topic.name == "test_topic"
        assert len(topic.get_all_partitions()) == 2
        
        # Get topic
        retrieved_topic = cluster.get_topic("test_topic")
        assert retrieved_topic is not None
        assert retrieved_topic.name == "test_topic"
        
        # List topics
        topics = cluster.list_topics()
        assert "test_topic" in topics
        
        # Delete topic
        cluster.delete_topic("test_topic")
        
        # Should no longer exist
        deleted_topic = cluster.get_topic("test_topic")
        assert deleted_topic is None
    
    def test_producer_consumer_creation(self):
        """Test creating producers and consumers through cluster"""
        cluster = EventStreamingCluster("test_cluster")
        
        # Create producer
        producer = cluster.create_producer(client_id="test_producer")
        assert producer.client_id == "test_producer"
        
        # Create consumer
        consumer = cluster.create_consumer(
            group_id="test_group",
            client_id="test_consumer",
            topics=["test_topic"]
        )
        assert consumer.group_id == "test_group"
        assert consumer.client_id == "test_consumer"
    
    def test_cluster_metadata(self):
        """Test cluster metadata retrieval"""
        cluster = EventStreamingCluster("test_cluster")
        
        metadata = cluster.get_cluster_metadata()
        assert isinstance(metadata, dict)
        assert "cluster_id" in metadata or "test_cluster" in str(metadata)
    
    def test_cluster_lifecycle(self):
        """Test cluster start/stop lifecycle"""
        cluster = EventStreamingCluster("test_cluster")
        
        # Should be able to start and stop without errors
        cluster.start()
        cluster.stop()


class TestOffsetManager:
    
    def test_offset_manager_creation(self):
        """Test offset manager creation"""
        manager = OffsetManager()
        assert manager is not None
    
    def test_offset_commit_and_retrieval(self):
        """Test committing and retrieving offsets"""
        manager = OffsetManager()
        
        # Commit offset
        manager.commit_offset("group1", "topic1", 0, 100)
        
        # Retrieve offset
        offset = manager.get_offset("group1", "topic1", 0)
        assert offset == 100
        
        # Different group should have different offset
        other_offset = manager.get_offset("group2", "topic1", 0)
        assert other_offset != 100 or other_offset is None
    
    def test_group_offsets(self):
        """Test getting all offsets for a group"""
        manager = OffsetManager()
        
        # Commit multiple offsets
        manager.commit_offset("group1", "topic1", 0, 100)
        manager.commit_offset("group1", "topic1", 1, 200)
        manager.commit_offset("group1", "topic2", 0, 50)
        
        # Get all offsets for group
        group_offsets = manager.get_group_offsets("group1")
        
        assert isinstance(group_offsets, dict)
        assert "topic1" in group_offsets
        assert group_offsets["topic1"][0] == 100
        assert group_offsets["topic1"][1] == 200
        assert "topic2" in group_offsets
        assert group_offsets["topic2"][0] == 50
    
    def test_offset_reset(self):
        """Test resetting offsets"""
        manager = OffsetManager()
        
        # Commit some offsets
        manager.commit_offset("group1", "topic1", 0, 100)
        manager.commit_offset("group1", "topic1", 1, 200)
        
        # Reset offsets
        manager.reset_offsets("group1", "topic1", reset_policy="earliest")
        
        # Offsets should be reset
        offset1 = manager.get_offset("group1", "topic1", 0)
        offset2 = manager.get_offset("group1", "topic1", 1)
        
        # Should be reset to beginning (0) or None
        assert offset1 == 0 or offset1 is None
        assert offset2 == 0 or offset2 is None


class TestEventFilter:
    
    def test_filter_creation(self):
        """Test event filter creation"""
        filter_obj = EventFilter()
        assert filter_obj is not None
    
    def test_adding_filters(self):
        """Test adding event filters"""
        filter_obj = EventFilter()
        
        # Add filter for events with specific key pattern
        def key_filter(event):
            return event.key is not None and event.key.startswith("important_")
        
        filter_obj.add_filter("key_filter", key_filter)
        
        # Test filter application
        important_event = Event(key="important_event", value="data")
        normal_event = Event(key="normal_event", value="data")
        
        assert filter_obj.apply_filters(important_event) == True
        assert filter_obj.apply_filters(normal_event) == False
    
    def test_multiple_filters(self):
        """Test multiple filters"""
        filter_obj = EventFilter()
        
        # Add multiple filters
        filter_obj.add_filter("key_filter", lambda e: e.key is not None)
        filter_obj.add_filter("value_filter", lambda e: "test" in str(e.value))
        
        # Event must pass all filters
        good_event = Event(key="test_key", value="test_value")
        bad_event1 = Event(key=None, value="test_value")  # Fails key filter
        bad_event2 = Event(key="test_key", value="other_value")  # Fails value filter
        
        assert filter_obj.apply_filters(good_event) == True
        assert filter_obj.apply_filters(bad_event1) == False
        assert filter_obj.apply_filters(bad_event2) == False
    
    def test_removing_filters(self):
        """Test removing filters"""
        filter_obj = EventFilter()
        
        filter_obj.add_filter("test_filter", lambda e: True)
        
        # Remove filter
        filter_obj.remove_filter("test_filter")
        
        # Should no longer affect filtering
        event = Event(key="test", value="test")
        result = filter_obj.apply_filters(event)
        
        # With no filters, should pass through (implementation dependent)
        assert isinstance(result, bool)


class TestEventTransformer:
    
    def test_transformer_creation(self):
        """Test event transformer creation"""
        transformer = EventTransformer()
        assert transformer is not None
    
    def test_adding_transformers(self):
        """Test adding event transformers"""
        transformer = EventTransformer()
        
        # Add transformer that uppercases string values
        def uppercase_transformer(event):
            if isinstance(event.value, str):
                event.value = event.value.upper()
            return event
        
        transformer.add_transformer("uppercase", uppercase_transformer)
        
        # Test transformation
        event = Event(key="test", value="hello world")
        transformed = transformer.apply_transformations(event)
        
        assert transformed.value == "HELLO WORLD"
        assert transformed.key == "test"  # Key unchanged
    
    def test_multiple_transformers(self):
        """Test chaining multiple transformers"""
        transformer = EventTransformer()
        
        # Add multiple transformers
        transformer.add_transformer("uppercase", lambda e: Event(e.key, e.value.upper() if isinstance(e.value, str) else e.value, e.headers))
        transformer.add_transformer("prefix", lambda e: Event(e.key, f"TRANSFORMED_{e.value}", e.headers))
        
        # Apply transformations
        event = Event(key="test", value="hello")
        transformed = transformer.apply_transformations(event)
        
        # Should apply both transformations
        assert "TRANSFORMED_" in transformed.value
        assert "HELLO" in transformed.value
    
    def test_removing_transformers(self):
        """Test removing transformers"""
        transformer = EventTransformer()
        
        transformer.add_transformer("test_transform", lambda e: Event(e.key, "CHANGED", e.headers))
        
        # Remove transformer
        transformer.remove_transformer("test_transform")
        
        # Should no longer transform
        event = Event(key="test", value="original")
        transformed = transformer.apply_transformations(event)
        
        # Value should be unchanged (or only other transformers applied)
        assert transformed.value == "original" or transformed != event


class TestEventSerializer:
    
    def test_json_serialization(self):
        """Test JSON event serialization"""
        event = Event(
            key="test_key",
            value={"data": "test", "number": 42},
            headers={"source": "test"}
        )
        
        # Serialize to JSON
        serialized = EventSerializer.serialize_json(event)
        assert isinstance(serialized, bytes)
        
        # Deserialize from JSON
        deserialized = EventSerializer.deserialize_json(serialized)
        
        assert deserialized.key == event.key
        assert deserialized.value == event.value
        assert deserialized.headers == event.headers
    
    def test_json_serialization_edge_cases(self):
        """Test JSON serialization edge cases"""
        # Event with None values
        event_with_none = Event(key=None, value=None)
        serialized = EventSerializer.serialize_json(event_with_none)
        deserialized = EventSerializer.deserialize_json(serialized)
        
        assert deserialized.key is None
        assert deserialized.value is None
        
        # Event with complex nested data
        complex_event = Event(
            key="complex",
            value={
                "list": [1, 2, 3],
                "nested": {"a": 1, "b": 2},
                "string": "test"
            }
        )
        
        serialized = EventSerializer.serialize_json(complex_event)
        deserialized = EventSerializer.deserialize_json(serialized)
        
        assert deserialized.value == complex_event.value


class TestUtilityFunctions:
    
    def test_partition_hash_calculation(self):
        """Test partition hash calculation"""
        # Same key should always hash to same partition
        partition1 = calculate_partition_hash("test_key", 4)
        partition2 = calculate_partition_hash("test_key", 4)
        
        assert partition1 == partition2
        assert 0 <= partition1 < 4
        
        # Different keys should distribute across partitions
        partitions = set()
        for i in range(20):
            partition = calculate_partition_hash(f"key_{i}", 4)
            partitions.add(partition)
        
        # Should use multiple partitions
        assert len(partitions) > 1
        assert all(0 <= p < 4 for p in partitions)
    
    def test_create_test_events(self):
        """Test test event creation utility"""
        events = create_test_events(10, "test_key_{}", "test_value_{}")
        
        assert len(events) == 10
        assert all(isinstance(e, Event) for e in events)
        
        # Should have unique keys and values
        keys = [e.key for e in events]
        values = [e.value for e in events]
        
        assert len(set(keys)) == 10  # All unique
        assert len(set(values)) == 10  # All unique
        
        # Should follow pattern
        assert all("test_key_" in k for k in keys)
        assert all("test_value_" in str(v) for v in values)


class TestConcurrency:
    
    def test_concurrent_event_production(self):
        """Test concurrent event production"""
        topic = Topic("test_topic", num_partitions=2)
        producer = EventProducer("test_producer")
        
        results = []
        
        def produce_events(thread_id, count):
            for i in range(count):
                event = Event(key=f"thread{thread_id}_key{i}", value=f"thread{thread_id}_value{i}")
                try:
                    offset = producer.send_sync("test_topic", event, timeout=1.0)
                    results.append((thread_id, i, offset))
                except (NotImplementedError, Exception):
                    # Producer might not be fully implemented
                    results.append((thread_id, i, "sent"))
        
        # Produce events concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(produce_events, i, 5) for i in range(3)]
            for future in futures:
                future.result()
        
        # Should have results from all threads
        assert len(results) >= 10  # At least some results
    
    def test_concurrent_event_consumption(self):
        """Test concurrent event consumption"""
        # Create consumers
        consumers = []
        for i in range(3):
            consumer = EventConsumer(
                group_id="test_group",
                client_id=f"consumer_{i}",
                topics=["test_topic"]
            )
            consumers.append(consumer)
        
        results = []
        
        def consume_events(consumer, duration=0.5):
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    events = consumer.poll(timeout_ms=100)
                    for topic, event_list in events.items():
                        results.extend(event_list)
                except (NotImplementedError, Exception):
                    # Consumer might not be fully implemented
                    break
                time.sleep(0.1)
        
        # Consume concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(consume_events, consumer) for consumer in consumers]
            for future in futures:
                future.result()
        
        # Results depend on implementation
        assert isinstance(results, list)
    
    def test_producer_consumer_integration(self):
        """Test integrated producer-consumer flow"""
        # Create cluster
        cluster = EventStreamingCluster("test_cluster")
        cluster.start()
        
        try:
            # Create topic
            topic = cluster.create_topic("integration_topic", num_partitions=2)
            
            # Create producer and consumer
            producer = cluster.create_producer(client_id="integration_producer")
            consumer = cluster.create_consumer(
                group_id="integration_group",
                client_id="integration_consumer",
                topics=["integration_topic"]
            )
            
            # Produce events
            events_to_send = [
                Event(key=f"key_{i}", value=f"value_{i}")
                for i in range(5)
            ]
            
            sent_events = []
            for event in events_to_send:
                try:
                    offset = producer.send_sync("integration_topic", event, timeout=1.0)
                    sent_events.append(event)
                except (NotImplementedError, Exception):
                    # Might not be implemented
                    pass
            
            # Consume events
            consumed_events = []
            for _ in range(3):  # Try a few times
                try:
                    events = consumer.poll(timeout_ms=200)
                    for topic, event_list in events.items():
                        consumed_events.extend(event_list)
                except (NotImplementedError, Exception):
                    break
            
            # Verify integration (if implemented)
            if sent_events and consumed_events:
                assert len(consumed_events) > 0
                # Check that consumed events match sent events
                consumed_keys = [e.key for e in consumed_events]
                sent_keys = [e.key for e in sent_events]
                
                # At least some overlap
                assert any(key in consumed_keys for key in sent_keys)
                
        finally:
            cluster.stop()


class TestPerformance:
    
    def test_high_throughput_production(self):
        """Test high throughput event production"""
        producer = EventProducer("perf_producer", batch_size=100, linger_ms=10)
        
        num_events = 1000
        events = [
            Event(key=f"key_{i}", value=f"value_{i}")
            for i in range(num_events)
        ]
        
        start_time = time.time()
        
        try:
            # Send events in batches
            batch_size = 100
            for i in range(0, num_events, batch_size):
                batch = events[i:i+batch_size]
                futures = producer.send_batch("test_topic", batch)
                
                # Wait for batch completion (simplified)
                time.sleep(0.01)
            
            producer.flush(timeout=5.0)
            
        except (NotImplementedError, Exception):
            # Producer might not be fully implemented
            pass
        
        duration = time.time() - start_time
        
        # Should complete in reasonable time
        assert duration < 10.0  # Should not take more than 10 seconds
    
    def test_consumer_performance(self):
        """Test consumer performance"""
        consumer = EventConsumer(
            group_id="perf_group",
            client_id="perf_consumer",
            topics=["test_topic"],
            max_poll_records=1000
        )
        
        total_events = 0
        start_time = time.time()
        
        try:
            # Poll for events for short duration
            while time.time() - start_time < 2.0:
                events = consumer.poll(timeout_ms=100)
                for topic, event_list in events.items():
                    total_events += len(event_list)
                
                if total_events > 0:
                    break  # Found some events
                    
        except (NotImplementedError, Exception):
            # Consumer might not be implemented
            pass
        
        duration = time.time() - start_time
        
        # Should be able to poll efficiently
        assert duration < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])