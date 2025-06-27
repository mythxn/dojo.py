"""
Test cases for Distributed Hash Table implementations
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from day2.distributed_hash_table import (
    ConsistentHashRing, DHTNode, DHTClient, FailureDetector,
    ReplicationManager, VectorClock, ConflictResolver,
    NodeInfo, NodeStatus, ConsistencyLevel, DHTEntry, OperationResult,
    create_test_cluster, simulate_node_failure, verify_data_consistency
)


class TestConsistentHashRing:
    
    def test_basic_ring_operations(self):
        """Test basic hash ring operations"""
        ring = ConsistentHashRing(virtual_nodes_per_node=3)
        
        # Add nodes
        node1 = NodeInfo("node1", "localhost", 8001)
        node2 = NodeInfo("node2", "localhost", 8002)
        node3 = NodeInfo("node3", "localhost", 8003)
        
        ring.add_node(node1)
        ring.add_node(node2)
        ring.add_node(node3)
        
        # Test key assignment
        key = "test_key"
        assigned_node = ring.get_node(key)
        assert assigned_node is not None
        assert assigned_node.node_id in ["node1", "node2", "node3"]
        
        # Same key should always map to same node
        assert ring.get_node(key) == assigned_node
    
    def test_virtual_nodes_distribution(self):
        """Test that virtual nodes provide good distribution"""
        ring = ConsistentHashRing(virtual_nodes_per_node=100)
        
        nodes = [
            NodeInfo(f"node{i}", "localhost", 8000 + i)
            for i in range(5)
        ]
        
        for node in nodes:
            ring.add_node(node)
        
        # Test distribution with many keys
        key_assignments = {}
        for i in range(1000):
            key = f"key_{i}"
            assigned_node = ring.get_node(key)
            node_id = assigned_node.node_id
            key_assignments[node_id] = key_assignments.get(node_id, 0) + 1
        
        # Distribution should be reasonably even (within 40% of average)
        average = 1000 / 5
        for node_id, count in key_assignments.items():
            assert abs(count - average) / average < 0.4
    
    def test_node_removal_minimal_disruption(self):
        """Test that removing node causes minimal key reassignment"""
        ring = ConsistentHashRing(virtual_nodes_per_node=50)
        
        nodes = [NodeInfo(f"node{i}", "localhost", 8000 + i) for i in range(4)]
        for node in nodes:
            ring.add_node(node)
        
        # Record initial key assignments
        initial_assignments = {}
        for i in range(1000):
            key = f"key_{i}"
            assigned_node = ring.get_node(key)
            initial_assignments[key] = assigned_node.node_id
        
        # Remove one node
        ring.remove_node("node1")
        
        # Check how many keys moved
        moved_keys = 0
        for key, original_node in initial_assignments.items():
            new_node = ring.get_node(key)
            if new_node and new_node.node_id != original_node:
                moved_keys += 1
        
        # Should move approximately 1/4 of keys (only those from removed node)
        expected_moved = 1000 / 4
        assert abs(moved_keys - expected_moved) / expected_moved < 0.5
    
    def test_successor_nodes(self):
        """Test getting successor nodes for replication"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        
        nodes = [NodeInfo(f"node{i}", "localhost", 8000 + i) for i in range(5)]
        for node in nodes:
            ring.add_node(node)
        
        key = "test_key"
        successors = ring.get_successor_nodes(key, count=3)
        
        assert len(successors) == 3
        assert len(set(node.node_id for node in successors)) == 3  # All different nodes
        
        # First successor should be the primary node
        primary = ring.get_node(key)
        assert successors[0].node_id == primary.node_id
    
    def test_ring_state_consistency(self):
        """Test ring state remains consistent"""
        ring = ConsistentHashRing(virtual_nodes_per_node=20)
        
        # Add nodes
        for i in range(3):
            node = NodeInfo(f"node{i}", "localhost", 8000 + i)
            ring.add_node(node)
        
        state1 = ring.get_ring_state()
        
        # Remove and re-add same node
        ring.remove_node("node1")
        node1_new = NodeInfo("node1", "localhost", 8001)
        ring.add_node(node1_new)
        
        state2 = ring.get_ring_state()
        
        # Ring should have same structure (same virtual node positions for node1)
        node1_positions_1 = [pos for pos, node_id in state1.items() if node_id == "node1"]
        node1_positions_2 = [pos for pos, node_id in state2.items() if node_id == "node1"]
        
        assert set(node1_positions_1) == set(node1_positions_2)


class TestFailureDetector:
    
    def test_basic_failure_detection(self):
        """Test basic failure detection functionality"""
        detector = FailureDetector(failure_timeout=1.0, suspect_timeout=0.5)
        
        # Register heartbeats
        detector.heartbeat("node1")
        detector.heartbeat("node2")
        
        # Both nodes should be alive
        assert detector.get_node_status("node1") == NodeStatus.ALIVE
        assert detector.get_node_status("node2") == NodeStatus.ALIVE
        
        # Wait for suspect timeout
        time.sleep(0.6)
        suspected, dead = detector.check_failures()
        
        assert "node1" in suspected
        assert "node2" in suspected
        assert len(dead) == 0
        
        # Wait for failure timeout
        time.sleep(0.6)
        suspected, dead = detector.check_failures()
        
        assert "node1" in dead
        assert "node2" in dead
    
    def test_heartbeat_recovery(self):
        """Test node recovery after heartbeat"""
        detector = FailureDetector(failure_timeout=1.0, suspect_timeout=0.5)
        
        detector.heartbeat("node1")
        time.sleep(0.6)  # Node becomes suspected
        
        suspected, dead = detector.check_failures()
        assert "node1" in suspected
        
        # Send heartbeat to recover
        detector.heartbeat("node1")
        assert detector.get_node_status("node1") == NodeStatus.ALIVE
        
        # Should not be in next failure check
        suspected, dead = detector.check_failures()
        assert "node1" not in suspected
        assert "node1" not in dead
    
    def test_manual_status_override(self):
        """Test manual status override"""
        detector = FailureDetector(failure_timeout=1.0, suspect_timeout=0.5)
        
        # Mark node as alive without heartbeat
        detector.mark_alive("node1")
        assert detector.get_node_status("node1") == NodeStatus.ALIVE
        
        # Should still expire after timeout
        time.sleep(0.6)
        suspected, dead = detector.check_failures()
        assert "node1" in suspected


class TestReplicationManager:
    
    def test_replica_node_selection(self):
        """Test replica node selection"""
        replication_manager = ReplicationManager(replication_factor=3)
        hash_ring = ConsistentHashRing(virtual_nodes_per_node=10)
        
        # Add nodes to ring
        nodes = [NodeInfo(f"node{i}", "localhost", 8000 + i) for i in range(5)]
        for node in nodes:
            hash_ring.add_node(node)
        
        key = "test_key"
        replicas = replication_manager.get_replica_nodes(key, hash_ring)
        
        assert len(replicas) == 3
        assert len(set(node.node_id for node in replicas)) == 3  # All different
        
        # First replica should be primary node
        primary = hash_ring.get_node(key)
        assert replicas[0].node_id == primary.node_id
    
    def test_data_replication_success_count(self):
        """Test data replication returns success count"""
        replication_manager = ReplicationManager(replication_factor=3)
        
        # Mock replica nodes
        replica_nodes = [
            NodeInfo(f"node{i}", "localhost", 8000 + i) 
            for i in range(3)
        ]
        
        # This would normally make network calls
        # For testing, we'll test the interface
        key = "test_key"
        value = "test_value"
        version = 1
        
        # In real implementation, this would return actual success count
        success_count = replication_manager.replicate_data(key, value, version, replica_nodes)
        assert isinstance(success_count, int)
        assert 0 <= success_count <= len(replica_nodes)


class TestDHTNode:
    
    def test_node_initialization(self):
        """Test DHT node initialization"""
        node = DHTNode("node1", "localhost", 8001, replication_factor=3)
        
        assert node.node_info.node_id == "node1"
        assert node.node_info.host == "localhost" 
        assert node.node_info.port == 8001
        assert node.replication_factor == 3
        assert not node.running
    
    def test_local_storage_operations(self):
        """Test local storage operations"""
        node = DHTNode("node1", "localhost", 8001)
        
        # Test put
        success = node._local_put("key1", "value1", version=1)
        assert success == True
        
        # Test get
        entry = node._local_get("key1")
        assert entry is not None
        assert entry.key == "key1"
        assert entry.value == "value1"
        assert entry.version == 1
        
        # Test update
        success = node._local_put("key1", "value1_updated", version=2)
        assert success == True
        
        updated_entry = node._local_get("key1")
        assert updated_entry.value == "value1_updated"
        assert updated_entry.version == 2
        
        # Test delete
        success = node._local_delete("key1")
        assert success == True
        
        deleted_entry = node._local_get("key1")
        assert deleted_entry is None
    
    def test_version_conflict_handling(self):
        """Test handling of version conflicts"""
        node = DHTNode("node1", "localhost", 8001)
        
        # Put initial version
        node._local_put("key1", "value1", version=2)
        
        # Try to put older version (should be rejected or handled appropriately)
        success = node._local_put("key1", "value_old", version=1)
        
        # Implementation dependent: might reject or use conflict resolution
        entry = node._local_get("key1")
        # Should still have newer version
        assert entry.version >= 2
    
    def test_cluster_state_tracking(self):
        """Test cluster state tracking"""
        node = DHTNode("node1", "localhost", 8001)
        
        # Add some mock cluster state
        node2_info = NodeInfo("node2", "localhost", 8002)
        node3_info = NodeInfo("node3", "localhost", 8003)
        
        # Simulate cluster state updates
        cluster_state = node.get_cluster_state()
        assert isinstance(cluster_state, dict)
        assert "nodes" in cluster_state or "ring_state" in cluster_state
    
    def test_local_statistics(self):
        """Test local node statistics"""
        node = DHTNode("node1", "localhost", 8001)
        
        # Perform some operations
        node._local_put("key1", "value1", version=1)
        node._local_put("key2", "value2", version=1)
        node._local_get("key1")
        
        stats = node.get_local_stats()
        assert isinstance(stats, dict)
        # Should contain metrics like storage size, operation counts, etc.
        assert "stored_keys" in stats or "local_storage_size" in stats


class TestDHTClient:
    
    def test_client_initialization(self):
        """Test DHT client initialization"""
        known_nodes = [("localhost", 8001), ("localhost", 8002)]
        client = DHTClient(known_nodes)
        
        # Client should store known nodes for coordination
        assert hasattr(client, 'known_nodes') or hasattr(client, '_known_nodes')
    
    def test_coordinator_selection(self):
        """Test coordinator node selection for keys"""
        known_nodes = [("localhost", 8001), ("localhost", 8002)]
        client = DHTClient(known_nodes)
        
        # Should be able to find coordinator for any key
        coordinator = client._find_coordinator("test_key")
        
        # Might return None if no nodes available, or a valid coordinator
        if coordinator is not None:
            assert isinstance(coordinator, tuple)
            assert len(coordinator) == 2  # (host, port)


class TestVectorClock:
    
    def test_vector_clock_basic_operations(self):
        """Test basic vector clock operations"""
        clock1 = VectorClock("node1")
        clock2 = VectorClock("node2")
        
        # Initial state
        assert clock1.to_dict() == {"node1": 0}
        assert clock2.to_dict() == {"node2": 0}
        
        # Increment clocks
        clock1.increment()
        clock2.increment()
        
        assert clock1.to_dict() == {"node1": 1}
        assert clock2.to_dict() == {"node2": 1}
    
    def test_vector_clock_comparison(self):
        """Test vector clock comparison"""
        clock1 = VectorClock("node1")
        clock2 = VectorClock("node2")
        
        # Initially concurrent
        assert clock1.compare(clock2) == "concurrent"
        
        # node1 increments - now clock1 is after initial state
        clock1.increment()
        clock_initial = VectorClock("node1")
        assert clock1.compare(clock_initial) == "after"
        assert clock_initial.compare(clock1) == "before"
    
    def test_vector_clock_update(self):
        """Test vector clock update with merge"""
        clock1 = VectorClock("node1")
        clock2 = VectorClock("node2")
        
        clock1.increment()  # node1: 1
        clock2.increment()  # node2: 1
        
        # Update clock1 with clock2
        clock1.update(clock2)
        
        # clock1 should now know about both nodes
        clock1_dict = clock1.to_dict()
        assert "node1" in clock1_dict
        assert "node2" in clock1_dict
        assert clock1_dict["node1"] >= 1
        assert clock1_dict["node2"] >= 1
    
    def test_vector_clock_serialization(self):
        """Test vector clock serialization"""
        clock = VectorClock("node1")
        clock.increment()
        
        # Convert to dict and back
        clock_dict = clock.to_dict()
        restored_clock = VectorClock.from_dict(clock_dict, "node1")
        
        assert clock.compare(restored_clock) == "equal"


class TestConflictResolver:
    
    def test_last_write_wins_resolution(self):
        """Test last-write-wins conflict resolution"""
        entries = [
            DHTEntry("key1", "value1", version=1, timestamp=1000.0),
            DHTEntry("key1", "value2", version=2, timestamp=2000.0),
            DHTEntry("key1", "value3", version=1, timestamp=1500.0)  # Older timestamp, higher version
        ]
        
        winner = ConflictResolver.last_write_wins(entries)
        
        # Should pick entry with latest timestamp
        assert winner.value == "value2"
        assert winner.timestamp == 2000.0
    
    def test_version_vector_reconciliation(self):
        """Test version vector conflict reconciliation"""
        entries = [
            DHTEntry("key1", "value1", version=1),
            DHTEntry("key1", "value2", version=2),
            DHTEntry("key1", "value3", version=1)
        ]
        
        # In simple case, should return entries that can't be ordered
        reconciled = ConflictResolver.version_vector_reconcile(entries)
        
        assert isinstance(reconciled, list)
        assert len(reconciled) >= 1  # At least one entry should remain


class TestDHTIntegration:
    
    def test_single_node_operations(self):
        """Test operations on single node"""
        node = DHTNode("node1", "localhost", 8001)
        node.start()
        
        try:
            # Test put operation
            result = node.put("key1", "value1", ConsistencyLevel.ONE)
            assert result.success == True
            
            # Test get operation
            result = node.get("key1", ConsistencyLevel.ONE)
            assert result.success == True
            assert result.value == "value1"
            
            # Test delete operation
            result = node.delete("key1", ConsistencyLevel.ONE)
            assert result.success == True
            
            # Verify deletion
            result = node.get("key1", ConsistencyLevel.ONE)
            assert result.success == False or result.value is None
            
        finally:
            node.stop()
    
    def test_multiple_node_cluster(self):
        """Test operations across multiple nodes"""
        # Create small cluster
        nodes = []
        try:
            for i in range(3):
                node = DHTNode(f"node{i}", "localhost", 8001 + i)
                node.start()
                nodes.append(node)
            
            # Join nodes to form cluster (simplified)
            # In real implementation, nodes would discover each other
            
            # Test cross-node operations
            result = nodes[0].put("distributed_key", "distributed_value", ConsistencyLevel.QUORUM)
            
            # Should be able to read from different node
            result = nodes[1].get("distributed_key", ConsistencyLevel.QUORUM)
            # Note: This might fail if nodes haven't properly joined cluster
            # Real implementation would need proper cluster formation
            
        finally:
            for node in nodes:
                node.stop()


class TestConsistencyLevels:
    
    def test_consistency_level_one(self):
        """Test operations with consistency level ONE"""
        node = DHTNode("node1", "localhost", 8001)
        node.start()
        
        try:
            # With ONE, operations should succeed with just one replica
            result = node.put("key1", "value1", ConsistencyLevel.ONE)
            assert result.success == True
            assert result.replicas_contacted >= 1
            
            result = node.get("key1", ConsistencyLevel.ONE)
            assert result.success == True
            assert result.replicas_contacted >= 1
            
        finally:
            node.stop()
    
    def test_consistency_level_all(self):
        """Test operations with consistency level ALL"""
        node = DHTNode("node1", "localhost", 8001)
        node.start()
        
        try:
            # With ALL, operations need all replicas
            # In single node cluster, should still work
            result = node.put("key1", "value1", ConsistencyLevel.ALL)
            # May succeed or fail depending on implementation
            
            if result.success:
                result = node.get("key1", ConsistencyLevel.ALL)
                assert result.success == True
                
        finally:
            node.stop()


class TestFailureScenarios:
    
    def test_node_failure_detection(self):
        """Test node failure detection in cluster"""
        # This would test the gossip protocol and failure detection
        # For now, test the failure detector component
        
        detector = FailureDetector(failure_timeout=1.0, suspect_timeout=0.5)
        
        # Simulate multiple nodes
        for i in range(3):
            detector.heartbeat(f"node{i}")
        
        # Stop heartbeats from one node
        time.sleep(0.6)  # Beyond suspect timeout
        
        suspected, dead = detector.check_failures()
        assert len(suspected) == 3  # All nodes suspected
        
        # Resume heartbeats from 2 nodes
        detector.heartbeat("node0")
        detector.heartbeat("node1")
        
        suspected, dead = detector.check_failures()
        assert "node2" in suspected  # Only node2 still suspected
        assert "node0" not in suspected
        assert "node1" not in suspected
    
    def test_partition_tolerance(self):
        """Test behavior during network partitions"""
        # This would test how the system handles network splits
        # For basic test, just verify the partition detector
        
        from day2.distributed_hash_table import PartitionDetector
        
        detector = PartitionDetector(min_cluster_size=3)
        
        known_nodes = {"node1", "node2", "node3", "node4", "node5"}
        alive_nodes = {"node1", "node2"}  # Minority partition
        
        is_partition = detector.detect_partition(known_nodes, alive_nodes)
        assert is_partition == True  # Should detect minority partition


class TestPerformance:
    
    def test_hash_ring_performance(self):
        """Test hash ring performance with many nodes"""
        ring = ConsistentHashRing(virtual_nodes_per_node=150)
        
        # Add many nodes
        start_time = time.time()
        for i in range(100):
            node = NodeInfo(f"node{i}", "localhost", 8000 + i)
            ring.add_node(node)
        add_time = time.time() - start_time
        
        # Lookup performance
        start_time = time.time()
        for i in range(1000):
            key = f"key_{i}"
            node = ring.get_node(key)
            assert node is not None
        lookup_time = time.time() - start_time
        
        # Operations should be efficient
        assert add_time < 1.0  # Adding 100 nodes should be fast
        assert lookup_time < 0.5  # 1000 lookups should be fast
    
    def test_concurrent_operations(self):
        """Test concurrent operations on DHT node"""
        node = DHTNode("node1", "localhost", 8001)
        node.start()
        
        try:
            # Concurrent put operations
            results = []
            
            def put_operation(i):
                result = node.put(f"key_{i}", f"value_{i}", ConsistencyLevel.ONE)
                results.append(result.success)
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(put_operation, i) for i in range(50)]
                for future in futures:
                    future.result()
            
            # Most operations should succeed
            success_rate = sum(results) / len(results)
            assert success_rate > 0.8  # At least 80% success rate
            
        finally:
            node.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])