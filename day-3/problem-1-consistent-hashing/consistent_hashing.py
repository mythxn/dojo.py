"""
Consistent Hashing Implementation
=================================

Implement consistent hashing for distributed systems with advanced features.

Requirements:
- Efficient hash ring with virtual nodes
- Load balancing and hotspot detection
- Dynamic rebalancing during node changes
- Weighted nodes for heterogeneous clusters
- Metrics and monitoring for hash distribution

Your Tasks:
1. Implement ConsistentHashRing with virtual nodes
2. Add weighted consistent hashing
3. Implement load balancing algorithms
4. Add hotspot detection and mitigation
5. Create comprehensive monitoring and metrics

Interview Focus:
- Explain virtual nodes benefits
- Discuss load balancing strategies
- Handle heterogeneous node capacities
- Optimize for real-world scenarios
"""

import hashlib
import bisect
import random
import time
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from abc import ABC, abstractmethod
import threading
import statistics
from enum import Enum


class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED_RANDOM = "weighted_random"
    CONSISTENT_HASH = "consistent_hash"
    POWER_OF_TWO = "power_of_two"


@dataclass
class NodeMetrics:
    node_id: str
    weight: float = 1.0
    current_load: float = 0.0
    request_count: int = 0
    avg_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_updated: float = field(default_factory=time.time)
    is_healthy: bool = True


@dataclass
class HashRingStats:
    total_nodes: int
    total_virtual_nodes: int
    load_distribution: Dict[str, float]
    hotspots: List[str]
    balance_score: float  # 0-1, 1 = perfectly balanced
    node_utilization: Dict[str, float]


@dataclass
class Node:
    node_id: str
    host: str
    port: int
    weight: float = 1.0
    virtual_node_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        return isinstance(other, Node) and self.node_id == other.node_id


class HashFunction(ABC):
    """Abstract base class for hash functions"""
    
    @abstractmethod
    def hash(self, key: str) -> int:
        pass


class MD5HashFunction(HashFunction):
    def hash(self, key: str) -> int:
        """MD5-based hash function"""
        pass  # TODO: Implement


class SHA1HashFunction(HashFunction):
    def hash(self, key: str) -> int:
        """SHA1-based hash function"""
        pass  # TODO: Implement


class MurmurHashFunction(HashFunction):
    def hash(self, key: str) -> int:
        """Murmur hash function (simplified implementation)"""
        pass  # TODO: Implement


class ConsistentHashRing:
    def __init__(self, 
                 virtual_nodes_per_node: int = 150,
                 hash_function: Optional[HashFunction] = None,
                 load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.CONSISTENT_HASH):
        """
        Initialize consistent hash ring.
        
        Args:
            virtual_nodes_per_node: Default virtual nodes per physical node
            hash_function: Hash function to use
            load_balancing_strategy: Strategy for load balancing
        """
        pass  # TODO: Implement
    
    def add_node(self, node: Node) -> None:
        """Add node to the ring."""
        pass  # TODO: Implement
    
    def remove_node(self, node_id: str) -> List[Tuple[str, str]]:
        """
        Remove node from ring.
        
        Returns:
            List of (old_node, new_node) mappings for affected keys
        """
        pass  # TODO: Implement
    
    def get_node(self, key: str) -> Optional[Node]:
        """Get primary node for key using consistent hashing."""
        pass  # TODO: Implement
    
    def get_nodes(self, key: str, count: int = 1, 
                  strategy: Optional[LoadBalancingStrategy] = None) -> List[Node]:
        """
        Get multiple nodes for key using specified strategy.
        
        Args:
            key: Key to lookup
            count: Number of nodes to return
            strategy: Load balancing strategy (None = use default)
        """
        pass  # TODO: Implement
    
    def get_all_nodes_for_key_range(self, start_key: str, end_key: str) -> Dict[str, List[str]]:
        """Get all nodes responsible for key range."""
        pass  # TODO: Implement
    
    def update_node_weight(self, node_id: str, new_weight: float) -> None:
        """Update node weight and rebalance virtual nodes."""
        pass  # TODO: Implement
    
    def update_node_metrics(self, node_id: str, metrics: NodeMetrics) -> None:
        """Update node performance metrics."""
        pass  # TODO: Implement
    
    def get_ring_stats(self) -> HashRingStats:
        """Get comprehensive ring statistics."""
        pass  # TODO: Implement
    
    def detect_hotspots(self, threshold: float = 2.0) -> List[str]:
        """Detect nodes with load above threshold times average."""
        pass  # TODO: Implement
    
    def rebalance(self) -> Dict[str, Any]:
        """Rebalance the ring to improve load distribution."""
        pass  # TODO: Implement
    
    def _create_virtual_nodes(self, node: Node) -> List[int]:
        """Create virtual node positions for a physical node."""
        pass  # TODO: Implement
    
    def _calculate_virtual_node_count(self, node: Node) -> int:
        """Calculate number of virtual nodes based on weight."""
        pass  # TODO: Implement
    
    def _get_node_by_position(self, position: int) -> Optional[Node]:
        """Get node at specific ring position."""
        pass  # TODO: Implement


class WeightedConsistentHashRing(ConsistentHashRing):
    """Consistent hash ring with weighted nodes for heterogeneous clusters"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # TODO: Additional initialization
    
    def add_weighted_node(self, node: Node, weight: float) -> None:
        """Add node with specific weight."""
        pass  # TODO: Implement
    
    def auto_weight_nodes(self, capacity_metrics: Dict[str, Dict[str, float]]) -> None:
        """Automatically weight nodes based on capacity metrics."""
        pass  # TODO: Implement
    
    def get_weight_distribution(self) -> Dict[str, float]:
        """Get current weight distribution across nodes."""
        pass  # TODO: Implement


class LoadBalancer:
    """Advanced load balancer with multiple strategies"""
    
    def __init__(self, hash_ring: ConsistentHashRing):
        pass  # TODO: Implement
    
    def select_node(self, key: str, strategy: LoadBalancingStrategy, 
                   exclude_nodes: Optional[Set[str]] = None) -> Optional[Node]:
        """Select node using specified strategy."""
        pass  # TODO: Implement
    
    def select_nodes(self, key: str, count: int, strategy: LoadBalancingStrategy) -> List[Node]:
        """Select multiple nodes using specified strategy."""
        pass  # TODO: Implement
    
    def _round_robin_selection(self, nodes: List[Node]) -> Node:
        """Round-robin node selection."""
        pass  # TODO: Implement
    
    def _least_loaded_selection(self, nodes: List[Node]) -> Node:
        """Select least loaded node."""
        pass  # TODO: Implement
    
    def _weighted_random_selection(self, nodes: List[Node]) -> Node:
        """Weighted random selection based on node capacity."""
        pass  # TODO: Implement
    
    def _power_of_two_selection(self, nodes: List[Node]) -> Node:
        """Power of two choices algorithm."""
        pass  # TODO: Implement


class HotspotDetector:
    """Detect and mitigate hotspots in the hash ring"""
    
    def __init__(self, 
                 detection_window: float = 60.0,
                 hotspot_threshold: float = 2.0):
        pass  # TODO: Implement
    
    def record_request(self, node_id: str, key: str, response_time: float) -> None:
        """Record request for hotspot detection."""
        pass  # TODO: Implement
    
    def detect_hotspots(self, hash_ring: ConsistentHashRing) -> List[Tuple[str, float]]:
        """
        Detect current hotspots.
        
        Returns:
            List of (node_id, load_ratio) for hotspot nodes
        """
        pass  # TODO: Implement
    
    def detect_key_hotspots(self) -> List[Tuple[str, int]]:
        """
        Detect hot keys.
        
        Returns:
            List of (key, request_count) for hot keys
        """
        pass  # TODO: Implement
    
    def suggest_mitigation(self, hotspots: List[Tuple[str, float]]) -> Dict[str, Any]:
        """Suggest mitigation strategies for detected hotspots."""
        pass  # TODO: Implement


class HashRingMonitor:
    """Monitor hash ring performance and health"""
    
    def __init__(self, hash_ring: ConsistentHashRing):
        pass  # TODO: Implement
    
    def start_monitoring(self, interval: float = 10.0) -> None:
        """Start background monitoring."""
        pass  # TODO: Implement
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        pass  # TODO: Implement
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        pass  # TODO: Implement
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        pass  # TODO: Implement
    
    def check_balance(self) -> Dict[str, Any]:
        """Check ring balance and suggest improvements."""
        pass  # TODO: Implement
    
    def _monitoring_loop(self, interval: float) -> None:
        """Background monitoring loop."""
        pass  # TODO: Implement


class RendezvousHashing:
    """Alternative: Rendezvous (Highest Random Weight) hashing"""
    
    def __init__(self, hash_function: Optional[HashFunction] = None):
        pass  # TODO: Implement
    
    def add_node(self, node: Node) -> None:
        """Add node to rendezvous hash."""
        pass  # TODO: Implement
    
    def remove_node(self, node_id: str) -> None:
        """Remove node from rendezvous hash."""
        pass  # TODO: Implement
    
    def get_node(self, key: str) -> Optional[Node]:
        """Get node using rendezvous hashing."""
        pass  # TODO: Implement
    
    def get_nodes(self, key: str, count: int) -> List[Node]:
        """Get multiple nodes using rendezvous hashing."""
        pass  # TODO: Implement
    
    def _calculate_weight(self, node: Node, key: str) -> float:
        """Calculate weight for node-key pair."""
        pass  # TODO: Implement


class JumpConsistentHash:
    """Google's Jump Consistent Hash algorithm"""
    
    @staticmethod
    def jump_consistent_hash(key: int, num_buckets: int) -> int:
        """
        Jump consistent hash implementation.
        
        Args:
            key: Key to hash (must be integer)
            num_buckets: Number of buckets
            
        Returns:
            Bucket number (0 to num_buckets-1)
        """
        pass  # TODO: Implement
    
    def __init__(self):
        pass  # TODO: Implement
    
    def add_node(self, node: Node) -> None:
        """Add node (changes bucket count)."""
        pass  # TODO: Implement
    
    def remove_node(self, node_id: str) -> None:
        """Remove node (changes bucket count)."""
        pass  # TODO: Implement
    
    def get_node(self, key: str) -> Optional[Node]:
        """Get node using jump consistent hash."""
        pass  # TODO: Implement


class HashRingComparator:
    """Compare different hashing strategies"""
    
    def __init__(self):
        pass  # TODO: Implement
    
    def compare_algorithms(self, 
                          algorithms: List[Any],
                          nodes: List[Node],
                          keys: List[str],
                          operations: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compare different consistent hashing algorithms.
        
        Args:
            algorithms: List of hashing algorithm instances
            nodes: List of nodes to test with
            keys: List of keys to test
            operations: List of operations (add_node, remove_node, etc.)
            
        Returns:
            Comparison results with metrics for each algorithm
        """
        pass  # TODO: Implement
    
    def measure_redistribution(self, algorithm: Any, nodes: List[Node], 
                              keys: List[str]) -> Dict[str, float]:
        """Measure key redistribution when nodes are added/removed."""
        pass  # TODO: Implement
    
    def measure_load_distribution(self, algorithm: Any, keys: List[str]) -> Dict[str, float]:
        """Measure load distribution across nodes."""
        pass  # TODO: Implement


# Utility functions and helpers
def generate_test_keys(count: int, prefix: str = "key") -> List[str]:
    """Generate test keys for benchmarking."""
    pass  # TODO: Implement


def simulate_heterogeneous_cluster(node_count: int) -> List[Node]:
    """Generate nodes with varied capacities for testing."""
    pass  # TODO: Implement


def benchmark_hash_functions(functions: List[HashFunction], 
                           keys: List[str]) -> Dict[str, Dict[str, float]]:
    """Benchmark different hash functions."""
    pass  # TODO: Implement


def visualize_hash_ring(hash_ring: ConsistentHashRing, output_file: str = None) -> None:
    """Create visualization of hash ring distribution."""
    pass  # TODO: Implement


# Example usage patterns
def example_basic_consistent_hashing():
    """Example of basic consistent hashing usage"""
    pass  # TODO: Implement


def example_weighted_nodes():
    """Example using weighted nodes for heterogeneous cluster"""
    pass  # TODO: Implement


def example_load_balancing_strategies():
    """Example showing different load balancing strategies"""
    pass  # TODO: Implement


def example_hotspot_detection():
    """Example of hotspot detection and mitigation"""
    pass  # TODO: Implement


def example_algorithm_comparison():
    """Example comparing different hashing algorithms"""
    pass  # TODO: Implement