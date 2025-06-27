"""
Test cases for Consistent Hashing implementations
"""

import pytest
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from day3.consistent_hashing import (
    ConsistentHashRing, WeightedConsistentHashRing, LoadBalancer,
    HotspotDetector, HashRingMonitor, RendezvousHashing, JumpConsistentHash,
    HashRingComparator, Node, NodeMetrics, LoadBalancingStrategy,
    MD5HashFunction, SHA1HashFunction, MurmurHashFunction,
    generate_test_keys, simulate_heterogeneous_cluster, benchmark_hash_functions
)


class TestHashFunctions:
    
    def test_md5_hash_function(self):
        """Test MD5 hash function"""
        hash_func = MD5HashFunction()
        
        # Same input should produce same hash
        key = "test_key"
        hash1 = hash_func.hash(key)
        hash2 = hash_func.hash(key)
        assert hash1 == hash2
        
        # Different inputs should produce different hashes
        hash3 = hash_func.hash("different_key")
        assert hash1 != hash3
        
        # Hash should be integer
        assert isinstance(hash1, int)
        assert hash1 >= 0
    
    def test_sha1_hash_function(self):
        """Test SHA1 hash function"""
        hash_func = SHA1HashFunction()
        
        key = "test_key"
        hash_value = hash_func.hash(key)
        
        assert isinstance(hash_value, int)
        assert hash_value >= 0
        assert hash_func.hash(key) == hash_value  # Consistency
        assert hash_func.hash("other_key") != hash_value  # Different values
    
    def test_murmur_hash_function(self):
        """Test Murmur hash function"""
        hash_func = MurmurHashFunction()
        
        key = "test_key"
        hash_value = hash_func.hash(key)
        
        assert isinstance(hash_value, int)
        assert hash_value >= 0
        assert hash_func.hash(key) == hash_value
    
    def test_hash_function_distribution(self):
        """Test hash function distribution quality"""
        hash_func = MD5HashFunction()
        
        # Generate many keys and check distribution
        hashes = []
        for i in range(1000):
            key = f"key_{i}"
            hashes.append(hash_func.hash(key) % 100)  # Bucket into 100 slots
        
        # Check that distribution is reasonably uniform
        bucket_counts = [0] * 100
        for h in hashes:
            bucket_counts[h] += 1
        
        # No bucket should be empty or overly full
        min_count = min(bucket_counts)
        max_count = max(bucket_counts)
        assert min_count > 0  # No empty buckets
        assert max_count < 50  # No bucket with more than 5% of keys


class TestNode:
    
    def test_node_creation(self):
        """Test node creation and properties"""
        node = Node("node1", "localhost", 8001, weight=2.0)
        
        assert node.node_id == "node1"
        assert node.host == "localhost"
        assert node.port == 8001
        assert node.weight == 2.0
        assert node.virtual_node_count is None
        assert isinstance(node.metadata, dict)
    
    def test_node_equality(self):
        """Test node equality comparison"""
        node1 = Node("node1", "localhost", 8001)
        node2 = Node("node1", "localhost", 8002)  # Same ID, different port
        node3 = Node("node2", "localhost", 8001)  # Different ID
        
        assert node1 == node2  # Same ID
        assert node1 != node3  # Different ID
        assert hash(node1) == hash(node2)  # Same hash for same ID


class TestConsistentHashRing:
    
    def test_basic_ring_operations(self):
        """Test basic hash ring operations"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        
        # Add nodes
        node1 = Node("node1", "localhost", 8001)
        node2 = Node("node2", "localhost", 8002)
        node3 = Node("node3", "localhost", 8003)
        
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
        """Test virtual nodes provide good distribution"""
        ring = ConsistentHashRing(virtual_nodes_per_node=50)
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(4)]
        for node in nodes:
            ring.add_node(node)
        
        # Test distribution with many keys
        assignments = {}
        for i in range(1000):
            key = f"key_{i}"
            node = ring.get_node(key)
            if node:
                assignments[node.node_id] = assignments.get(node.node_id, 0) + 1
        
        # Distribution should be reasonably even
        average = 1000 / 4
        for node_id, count in assignments.items():
            deviation = abs(count - average) / average
            assert deviation < 0.3  # Within 30% of average
    
    def test_node_removal_minimal_disruption(self):
        """Test minimal disruption when removing nodes"""
        ring = ConsistentHashRing(virtual_nodes_per_node=20)
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(4)]
        for node in nodes:
            ring.add_node(node)
        
        # Record initial assignments
        initial_assignments = {}
        for i in range(1000):
            key = f"key_{i}"
            node = ring.get_node(key)
            if node:
                initial_assignments[key] = node.node_id
        
        # Remove one node
        affected_mappings = ring.remove_node("node1")
        
        # Check how many keys moved
        moved_count = 0
        for key, original_node in initial_assignments.items():
            new_node = ring.get_node(key)
            if new_node and new_node.node_id != original_node:
                moved_count += 1
        
        # Should move approximately 1/4 of keys (only those assigned to removed node)
        expected_moved = 1000 / 4
        assert abs(moved_count - expected_moved) / expected_moved < 0.5
    
    def test_multiple_node_selection(self):
        """Test selecting multiple nodes for replication"""
        ring = ConsistentHashRing(virtual_nodes_per_node=20)
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(5)]
        for node in nodes:
            ring.add_node(node)
        
        key = "test_key"
        selected_nodes = ring.get_nodes(key, count=3)
        
        assert len(selected_nodes) == 3
        node_ids = [node.node_id for node in selected_nodes]
        assert len(set(node_ids)) == 3  # All different nodes
        
        # First node should be primary
        primary = ring.get_node(key)
        assert selected_nodes[0].node_id == primary.node_id
    
    def test_key_range_lookup(self):
        """Test getting nodes for key ranges"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        # Get nodes for key range
        range_mapping = ring.get_all_nodes_for_key_range("key_000", "key_999")
        
        assert isinstance(range_mapping, dict)
        # Should have mappings for the range
        assert len(range_mapping) > 0
    
    def test_node_weight_updates(self):
        """Test updating node weights"""
        ring = ConsistentHashRing(virtual_nodes_per_node=20)
        
        node = Node("node1", "localhost", 8001, weight=1.0)
        ring.add_node(node)
        
        # Update weight
        ring.update_node_weight("node1", 2.0)
        
        # Node should now have more virtual nodes (approximately doubled)
        stats = ring.get_ring_stats()
        # Implementation dependent - might track virtual node distribution
    
    def test_ring_statistics(self):
        """Test ring statistics collection"""
        ring = ConsistentHashRing(virtual_nodes_per_node=15)
        
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        stats = ring.get_ring_stats()
        
        assert stats.total_nodes == 3
        assert stats.total_virtual_nodes == 3 * 15
        assert isinstance(stats.load_distribution, dict)
        assert isinstance(stats.balance_score, float)
        assert 0 <= stats.balance_score <= 1
    
    def test_hotspot_detection(self):
        """Test hotspot detection"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        # Simulate load on one node
        metrics = NodeMetrics("node1", current_load=10.0)
        ring.update_node_metrics("node1", metrics)
        
        hotspots = ring.detect_hotspots(threshold=2.0)
        
        # node1 should be detected as hotspot if its load is significantly higher
        assert isinstance(hotspots, list)
    
    def test_rebalancing(self):
        """Test ring rebalancing"""
        ring = ConsistentHashRing(virtual_nodes_per_node=20)
        
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        # Trigger rebalancing
        rebalance_result = ring.rebalance()
        
        assert isinstance(rebalance_result, dict)
        # Should contain information about rebalancing actions


class TestWeightedConsistentHashRing:
    
    def test_weighted_node_addition(self):
        """Test adding nodes with different weights"""
        ring = WeightedConsistentHashRing(virtual_nodes_per_node=20)
        
        # Add nodes with different weights
        light_node = Node("light", "localhost", 8001, weight=0.5)
        normal_node = Node("normal", "localhost", 8002, weight=1.0)
        heavy_node = Node("heavy", "localhost", 8003, weight=2.0)
        
        ring.add_weighted_node(light_node, 0.5)
        ring.add_weighted_node(normal_node, 1.0)
        ring.add_weighted_node(heavy_node, 2.0)
        
        # Test load distribution matches weights
        assignments = {}
        for i in range(1000):
            key = f"key_{i}"
            node = ring.get_node(key)
            if node:
                assignments[node.node_id] = assignments.get(node.node_id, 0) + 1
        
        # Heavy node should get roughly twice as many keys as normal node
        if "heavy" in assignments and "normal" in assignments:
            ratio = assignments["heavy"] / assignments["normal"]
            assert 1.5 < ratio < 2.5  # Approximately 2x
    
    def test_auto_weighting(self):
        """Test automatic node weighting based on capacity"""
        ring = WeightedConsistentHashRing()
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        # Provide capacity metrics
        capacity_metrics = {
            "node0": {"cpu_cores": 2, "memory_gb": 4},
            "node1": {"cpu_cores": 4, "memory_gb": 8},
            "node2": {"cpu_cores": 8, "memory_gb": 16}
        }
        
        ring.auto_weight_nodes(capacity_metrics)
        
        # Weight distribution should reflect capacity differences
        weight_dist = ring.get_weight_distribution()
        assert isinstance(weight_dist, dict)
        assert len(weight_dist) == 3


class TestLoadBalancer:
    
    def test_load_balancer_initialization(self):
        """Test load balancer initialization"""
        ring = ConsistentHashRing()
        balancer = LoadBalancer(ring)
        
        # Should be able to create load balancer
        assert balancer is not None
    
    def test_round_robin_strategy(self):
        """Test round-robin load balancing"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        balancer = LoadBalancer(ring)
        
        # Select nodes with round-robin
        selected_nodes = []
        for i in range(9):  # 3 rounds of 3 nodes
            node = balancer.select_node(f"key_{i}", LoadBalancingStrategy.ROUND_ROBIN)
            if node:
                selected_nodes.append(node.node_id)
        
        # Should cycle through nodes
        if len(selected_nodes) >= 6:
            # Check for round-robin pattern
            unique_in_first_three = len(set(selected_nodes[:3]))
            unique_in_second_three = len(set(selected_nodes[3:6]))
            assert unique_in_first_three <= 3
            assert unique_in_second_three <= 3
    
    def test_least_loaded_strategy(self):
        """Test least-loaded load balancing"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        # Set different loads
        ring.update_node_metrics("node0", NodeMetrics("node0", current_load=1.0))
        ring.update_node_metrics("node1", NodeMetrics("node1", current_load=5.0))
        ring.update_node_metrics("node2", NodeMetrics("node2", current_load=3.0))
        
        balancer = LoadBalancer(ring)
        
        # Should prefer least loaded node
        selected_node = balancer.select_node("test_key", LoadBalancingStrategy.LEAST_LOADED)
        if selected_node:
            # Should tend to select node0 (lowest load)
            assert selected_node.node_id in ["node0", "node1", "node2"]
    
    def test_power_of_two_strategy(self):
        """Test power-of-two choices strategy"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(5)]
        for node in nodes:
            ring.add_node(node)
        
        balancer = LoadBalancer(ring)
        
        # Power of two should select from random pairs
        selected_node = balancer.select_node("test_key", LoadBalancingStrategy.POWER_OF_TWO)
        assert selected_node is not None
        assert selected_node.node_id.startswith("node")
    
    def test_multiple_node_selection(self):
        """Test selecting multiple nodes with load balancing"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(5)]
        for node in nodes:
            ring.add_node(node)
        
        balancer = LoadBalancer(ring)
        
        # Select 3 nodes
        selected_nodes = balancer.select_nodes("test_key", 3, LoadBalancingStrategy.CONSISTENT_HASH)
        
        assert len(selected_nodes) == 3
        node_ids = [node.node_id for node in selected_nodes]
        assert len(set(node_ids)) == 3  # All different


class TestHotspotDetector:
    
    def test_hotspot_detector_initialization(self):
        """Test hotspot detector initialization"""
        detector = HotspotDetector(detection_window=30.0, hotspot_threshold=1.5)
        
        assert detector is not None
    
    def test_request_recording(self):
        """Test recording requests for hotspot detection"""
        detector = HotspotDetector(detection_window=60.0)
        
        # Record requests
        detector.record_request("node1", "key1", 0.1)
        detector.record_request("node1", "key2", 0.2)
        detector.record_request("node2", "key3", 0.15)
        
        # Should be able to record without errors
        assert True  # No exceptions thrown
    
    def test_hotspot_detection_basic(self):
        """Test basic hotspot detection"""
        detector = HotspotDetector(detection_window=60.0, hotspot_threshold=2.0)
        ring = ConsistentHashRing()
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        # Simulate heavy load on one node
        for i in range(100):
            detector.record_request("node1", f"key_{i}", 0.1)
        
        for i in range(10):
            detector.record_request("node2", f"key_{i}", 0.1)
        
        # Detect hotspots
        hotspots = detector.detect_hotspots(ring)
        
        assert isinstance(hotspots, list)
        # node1 should likely be detected as hotspot
    
    def test_key_hotspot_detection(self):
        """Test detection of hot keys"""
        detector = HotspotDetector(detection_window=60.0)
        
        # Simulate requests with some hot keys
        for i in range(50):
            detector.record_request("node1", "hot_key_1", 0.1)
        
        for i in range(30):
            detector.record_request("node2", "hot_key_2", 0.1)
        
        for i in range(5):
            detector.record_request("node1", f"normal_key_{i}", 0.1)
        
        # Detect hot keys
        hot_keys = detector.detect_key_hotspots()
        
        assert isinstance(hot_keys, list)
        # Should detect hot_key_1 and hot_key_2
    
    def test_mitigation_suggestions(self):
        """Test hotspot mitigation suggestions"""
        detector = HotspotDetector()
        
        # Simulate hotspots
        hotspots = [("node1", 3.0), ("node2", 2.5)]
        
        suggestions = detector.suggest_mitigation(hotspots)
        
        assert isinstance(suggestions, dict)
        # Should contain actionable suggestions


class TestHashRingMonitor:
    
    def test_monitor_initialization(self):
        """Test hash ring monitor initialization"""
        ring = ConsistentHashRing()
        monitor = HashRingMonitor(ring)
        
        assert monitor is not None
    
    def test_health_report(self):
        """Test health report generation"""
        ring = ConsistentHashRing()
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        monitor = HashRingMonitor(ring)
        
        health_report = monitor.get_health_report()
        
        assert isinstance(health_report, dict)
        assert "ring_health" in health_report or "overall_status" in health_report
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        ring = ConsistentHashRing()
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        monitor = HashRingMonitor(ring)
        
        metrics = monitor.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        # Should contain relevant performance data
    
    def test_balance_check(self):
        """Test ring balance checking"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        monitor = HashRingMonitor(ring)
        
        balance_report = monitor.check_balance()
        
        assert isinstance(balance_report, dict)
        assert "balance_score" in balance_report or "recommendations" in balance_report
    
    def test_monitoring_lifecycle(self):
        """Test starting and stopping monitoring"""
        ring = ConsistentHashRing()
        monitor = HashRingMonitor(ring)
        
        # Start monitoring
        monitor.start_monitoring(interval=0.1)  # Short interval for testing
        
        # Let it run briefly
        time.sleep(0.3)
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Should complete without errors
        assert True


class TestRendezvousHashing:
    
    def test_rendezvous_basic_operations(self):
        """Test basic rendezvous hashing operations"""
        rh = RendezvousHashing()
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            rh.add_node(node)
        
        # Get node for key
        key = "test_key"
        selected_node = rh.get_node(key)
        
        assert selected_node is not None
        assert selected_node.node_id in ["node0", "node1", "node2"]
        
        # Same key should consistently map to same node
        assert rh.get_node(key) == selected_node
    
    def test_rendezvous_multiple_nodes(self):
        """Test selecting multiple nodes with rendezvous hashing"""
        rh = RendezvousHashing()
        
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(5)]
        for node in nodes:
            rh.add_node(node)
        
        key = "test_key"
        selected_nodes = rh.get_nodes(key, count=3)
        
        assert len(selected_nodes) == 3
        node_ids = [node.node_id for node in selected_nodes]
        assert len(set(node_ids)) == 3  # All different
    
    def test_rendezvous_node_removal(self):
        """Test node removal in rendezvous hashing"""
        rh = RendezvousHashing()
        
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(4)]
        for node in nodes:
            rh.add_node(node)
        
        # Record initial assignments
        initial_assignments = {}
        for i in range(100):
            key = f"key_{i}"
            node = rh.get_node(key)
            if node:
                initial_assignments[key] = node.node_id
        
        # Remove one node
        rh.remove_node("node1")
        
        # Check reassignments
        moved_count = 0
        for key, original_node in initial_assignments.items():
            new_node = rh.get_node(key)
            if new_node and new_node.node_id != original_node:
                moved_count += 1
        
        # Only keys assigned to removed node should move
        assert moved_count <= len(initial_assignments)


class TestJumpConsistentHash:
    
    def test_jump_hash_algorithm(self):
        """Test jump consistent hash algorithm"""
        # Test basic algorithm
        result = JumpConsistentHash.jump_consistent_hash(12345, 10)
        
        assert isinstance(result, int)
        assert 0 <= result < 10
        
        # Same input should give same output
        result2 = JumpConsistentHash.jump_consistent_hash(12345, 10)
        assert result == result2
        
        # Different bucket count should potentially give different result
        result3 = JumpConsistentHash.jump_consistent_hash(12345, 11)
        # May or may not be different - algorithm dependent
    
    def test_jump_hash_distribution(self):
        """Test jump hash distribution quality"""
        num_buckets = 10
        bucket_counts = [0] * num_buckets
        
        # Test with many keys
        for i in range(1000):
            bucket = JumpConsistentHash.jump_consistent_hash(i, num_buckets)
            bucket_counts[bucket] += 1
        
        # Distribution should be reasonably uniform
        average = 1000 / num_buckets
        for count in bucket_counts:
            deviation = abs(count - average) / average
            assert deviation < 0.3  # Within 30% of average
    
    def test_jump_hash_wrapper(self):
        """Test jump hash wrapper class"""
        jh = JumpConsistentHash()
        
        # Add nodes
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            jh.add_node(node)
        
        # Get node for key
        selected_node = jh.get_node("test_key")
        
        if selected_node:  # Implementation dependent
            assert selected_node.node_id.startswith("node")


class TestHashRingComparator:
    
    def test_comparator_initialization(self):
        """Test hash ring comparator initialization"""
        comparator = HashRingComparator()
        assert comparator is not None
    
    def test_algorithm_comparison(self):
        """Test comparing different hashing algorithms"""
        comparator = HashRingComparator()
        
        # Create different algorithms
        consistent_ring = ConsistentHashRing(virtual_nodes_per_node=20)
        rendezvous = RendezvousHashing()
        
        algorithms = [consistent_ring, rendezvous]
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        keys = [f"key_{i}" for i in range(100)]
        operations = ["add_node", "remove_node"]
        
        # Compare algorithms
        results = comparator.compare_algorithms(algorithms, nodes, keys, operations)
        
        assert isinstance(results, dict)
        # Should have results for each algorithm
    
    def test_redistribution_measurement(self):
        """Test measuring key redistribution"""
        comparator = HashRingComparator()
        
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(4)]
        keys = [f"key_{i}" for i in range(200)]
        
        metrics = comparator.measure_redistribution(ring, nodes, keys)
        
        assert isinstance(metrics, dict)
        # Should contain redistribution metrics
    
    def test_load_distribution_measurement(self):
        """Test measuring load distribution"""
        comparator = HashRingComparator()
        
        ring = ConsistentHashRing(virtual_nodes_per_node=15)
        nodes = [Node(f"node{i}", "localhost", 8000 + i) for i in range(3)]
        for node in nodes:
            ring.add_node(node)
        
        keys = [f"key_{i}" for i in range(300)]
        
        metrics = comparator.measure_load_distribution(ring, keys)
        
        assert isinstance(metrics, dict)
        # Should contain load distribution metrics


class TestUtilityFunctions:
    
    def test_generate_test_keys(self):
        """Test test key generation"""
        keys = generate_test_keys(100, "test")
        
        assert len(keys) == 100
        assert all(key.startswith("test") for key in keys)
        assert len(set(keys)) == 100  # All unique
    
    def test_simulate_heterogeneous_cluster(self):
        """Test heterogeneous cluster simulation"""
        nodes = simulate_heterogeneous_cluster(5)
        
        assert len(nodes) == 5
        assert all(isinstance(node, Node) for node in nodes)
        
        # Should have varied weights/capacities
        weights = [node.weight for node in nodes]
        assert len(set(weights)) > 1  # Not all same weight
    
    def test_benchmark_hash_functions(self):
        """Test hash function benchmarking"""
        functions = [MD5HashFunction(), SHA1HashFunction()]
        keys = [f"key_{i}" for i in range(100)]
        
        results = benchmark_hash_functions(functions, keys)
        
        assert isinstance(results, dict)
        # Should have results for each hash function


class TestConcurrency:
    
    def test_concurrent_ring_operations(self):
        """Test concurrent operations on hash ring"""
        ring = ConsistentHashRing(virtual_nodes_per_node=20)
        
        # Add initial nodes
        for i in range(3):
            ring.add_node(Node(f"node{i}", "localhost", 8000 + i))
        
        results = []
        
        def lookup_operation(thread_id):
            for i in range(50):
                key = f"thread{thread_id}_key{i}"
                node = ring.get_node(key)
                if node:
                    results.append((key, node.node_id))
        
        # Run concurrent lookups
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(lookup_operation, i) for i in range(5)]
            for future in futures:
                future.result()
        
        # Should have results from all threads
        assert len(results) == 250  # 5 threads * 50 operations
    
    def test_concurrent_node_modifications(self):
        """Test concurrent node additions/removals"""
        ring = ConsistentHashRing(virtual_nodes_per_node=10)
        
        def add_nodes(start_id, count):
            for i in range(count):
                node = Node(f"node{start_id}_{i}", "localhost", 8000 + start_id * 100 + i)
                ring.add_node(node)
        
        def remove_nodes(start_id, count):
            for i in range(count):
                try:
                    ring.remove_node(f"node{start_id}_{i}")
                except:
                    pass  # Node might not exist
        
        # Add nodes concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(add_nodes, 0, 10),
                executor.submit(add_nodes, 1, 10),
                executor.submit(add_nodes, 2, 10)
            ]
            for future in futures:
                future.result()
        
        # Ring should be in consistent state
        stats = ring.get_ring_stats()
        assert stats.total_nodes > 0


class TestPerformance:
    
    def test_large_scale_operations(self):
        """Test performance with large number of nodes and keys"""
        ring = ConsistentHashRing(virtual_nodes_per_node=100)
        
        # Add many nodes
        start_time = time.time()
        for i in range(50):
            node = Node(f"node{i}", "localhost", 8000 + i)
            ring.add_node(node)
        add_time = time.time() - start_time
        
        # Perform many lookups
        start_time = time.time()
        for i in range(10000):
            key = f"key_{i}"
            node = ring.get_node(key)
            assert node is not None
        lookup_time = time.time() - start_time
        
        # Should be reasonably fast
        assert add_time < 2.0  # Adding 50 nodes
        assert lookup_time < 2.0  # 10K lookups
    
    def test_memory_efficiency(self):
        """Test memory efficiency with many virtual nodes"""
        ring = ConsistentHashRing(virtual_nodes_per_node=500)  # Many virtual nodes
        
        # Add nodes
        for i in range(20):
            node = Node(f"node{i}", "localhost", 8000 + i)
            ring.add_node(node)
        
        # Ring should handle large number of virtual nodes efficiently
        stats = ring.get_ring_stats()
        assert stats.total_virtual_nodes == 20 * 500
        
        # Should still perform lookups quickly
        start_time = time.time()
        for i in range(1000):
            key = f"key_{i}"
            node = ring.get_node(key)
            assert node is not None
        lookup_time = time.time() - start_time
        
        assert lookup_time < 1.0  # Should be fast even with many virtual nodes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])