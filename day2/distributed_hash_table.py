"""
Distributed Hash Table Implementation
====================================

Implement a distributed hash table with consistent hashing, replication, and failure handling.

Requirements:
- Consistent hashing for data distribution
- Node join/leave handling
- Data replication for fault tolerance
- Key-value operations (get, put, delete)
- Virtual nodes for better load distribution
- Failure detection and recovery

Your Tasks:
1. Implement consistent hashing ring
2. Create DHT node with key-value storage
3. Add replication and consistency protocols
4. Implement failure detection
5. Add data migration during topology changes

Interview Focus:
- Explain consistent hashing benefits
- Discuss CAP theorem trade-offs
- Handle network partitions and split-brain scenarios
"""

import hashlib
import time
import threading
import socket
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from collections import defaultdict
import bisect


class NodeStatus(Enum):
    ALIVE = "alive"
    SUSPECTED = "suspected"
    DEAD = "dead"
    JOINING = "joining"
    LEAVING = "leaving"


class ConsistencyLevel(Enum):
    ONE = 1        # One replica must respond
    QUORUM = 2     # Majority of replicas must respond
    ALL = 3        # All replicas must respond


@dataclass
class NodeInfo:
    node_id: str
    host: str
    port: int
    status: NodeStatus = NodeStatus.ALIVE
    last_seen: float = field(default_factory=time.time)
    virtual_nodes: List[int] = field(default_factory=list)
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        return isinstance(other, NodeInfo) and self.node_id == other.node_id


@dataclass
class DHTEntry:
    key: str
    value: Any
    version: int = 0
    timestamp: float = field(default_factory=time.time)
    replicas: Set[str] = field(default_factory=set)


@dataclass 
class OperationResult:
    success: bool
    value: Any = None
    version: int = 0
    error: Optional[str] = None
    coordinator: Optional[str] = None
    replicas_contacted: int = 0


class ConsistentHashRing:
    def __init__(self, virtual_nodes_per_node: int = 150):
        """
        Initialize consistent hash ring.
        
        Args:
            virtual_nodes_per_node: Number of virtual nodes per physical node
        """
        pass  # TODO: Implement
    
    def add_node(self, node: NodeInfo) -> None:
        """Add node to the ring."""
        pass  # TODO: Implement
    
    def remove_node(self, node_id: str) -> List[Tuple[int, str]]:
        """
        Remove node from ring.
        
        Returns:
            List of (hash_position, affected_key_range) that need rebalancing
        """
        pass  # TODO: Implement
    
    def get_node(self, key: str) -> Optional[NodeInfo]:
        """Get primary node responsible for key."""
        pass  # TODO: Implement
    
    def get_successor_nodes(self, key: str, count: int = 3) -> List[NodeInfo]:
        """Get N successor nodes for key (for replication)."""
        pass  # TODO: Implement
    
    def get_predecessor_nodes(self, key: str, count: int = 3) -> List[NodeInfo]:
        """Get N predecessor nodes for key."""
        pass  # TODO: Implement
    
    def get_nodes_in_range(self, start_hash: int, end_hash: int) -> List[NodeInfo]:
        """Get all nodes responsible for hash range."""
        pass  # TODO: Implement
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing."""
        pass  # TODO: Implement
    
    def get_ring_state(self) -> Dict[int, str]:
        """Get current ring state for debugging."""
        pass  # TODO: Implement


class FailureDetector:
    def __init__(self, failure_timeout: float = 30.0, suspect_timeout: float = 10.0):
        """
        Initialize failure detector.
        
        Args:
            failure_timeout: Time before marking node as dead
            suspect_timeout: Time before marking node as suspected
        """
        pass  # TODO: Implement
    
    def heartbeat(self, node_id: str) -> None:
        """Record heartbeat from node."""
        pass  # TODO: Implement
    
    def check_failures(self) -> Tuple[List[str], List[str]]:
        """
        Check for failed nodes.
        
        Returns:
            Tuple of (suspected_nodes, dead_nodes)
        """
        pass  # TODO: Implement
    
    def mark_alive(self, node_id: str) -> None:
        """Mark node as alive."""
        pass  # TODO: Implement
    
    def get_node_status(self, node_id: str) -> NodeStatus:
        """Get current status of node."""
        pass  # TODO: Implement


class ReplicationManager:
    def __init__(self, replication_factor: int = 3):
        """
        Initialize replication manager.
        
        Args:
            replication_factor: Number of replicas to maintain
        """
        pass  # TODO: Implement
    
    def get_replica_nodes(self, key: str, hash_ring: ConsistentHashRing) -> List[NodeInfo]:
        """Get nodes that should store replicas of key."""
        pass  # TODO: Implement
    
    def replicate_data(self, key: str, value: Any, version: int, 
                      replica_nodes: List[NodeInfo]) -> int:
        """
        Replicate data to replica nodes.
        
        Returns:
            Number of successful replications
        """
        pass  # TODO: Implement
    
    def read_repair(self, key: str, replicas: List[Tuple[NodeInfo, DHTEntry]]) -> bool:
        """Perform read repair to fix inconsistencies."""
        pass  # TODO: Implement
    
    def anti_entropy_repair(self, node1: NodeInfo, node2: NodeInfo) -> int:
        """Perform anti-entropy repair between two nodes."""
        pass  # TODO: Implement


class DHTNode:
    def __init__(self, node_id: str, host: str, port: int, 
                 replication_factor: int = 3, virtual_nodes: int = 150):
        """
        Initialize DHT node.
        
        Args:
            node_id: Unique node identifier
            host: Node host address
            port: Node port
            replication_factor: Number of replicas
            virtual_nodes: Number of virtual nodes
        """
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start the DHT node."""
        pass  # TODO: Implement
    
    def stop(self) -> None:
        """Stop the DHT node."""
        pass  # TODO: Implement
    
    def join(self, bootstrap_nodes: List[Tuple[str, int]]) -> bool:
        """Join existing DHT cluster."""
        pass  # TODO: Implement
    
    def leave(self) -> bool:
        """Leave DHT cluster gracefully."""
        pass  # TODO: Implement
    
    def put(self, key: str, value: Any, consistency: ConsistencyLevel = ConsistencyLevel.QUORUM) -> OperationResult:
        """Store key-value pair."""
        pass  # TODO: Implement
    
    def get(self, key: str, consistency: ConsistencyLevel = ConsistencyLevel.QUORUM) -> OperationResult:
        """Retrieve value by key."""
        pass  # TODO: Implement
    
    def delete(self, key: str, consistency: ConsistencyLevel = ConsistencyLevel.QUORUM) -> OperationResult:
        """Delete key-value pair."""
        pass  # TODO: Implement
    
    def _coordinate_read(self, key: str, consistency: ConsistencyLevel) -> OperationResult:
        """Coordinate read operation across replicas."""
        pass  # TODO: Implement
    
    def _coordinate_write(self, key: str, value: Any, consistency: ConsistencyLevel) -> OperationResult:
        """Coordinate write operation across replicas."""
        pass  # TODO: Implement
    
    def _local_get(self, key: str) -> Optional[DHTEntry]:
        """Get value from local storage."""
        pass  # TODO: Implement
    
    def _local_put(self, key: str, value: Any, version: int) -> bool:
        """Store value in local storage."""
        pass  # TODO: Implement
    
    def _local_delete(self, key: str) -> bool:
        """Delete value from local storage."""
        pass  # TODO: Implement
    
    def _handle_node_join(self, new_node: NodeInfo) -> None:
        """Handle new node joining the cluster."""
        pass  # TODO: Implement
    
    def _handle_node_leave(self, leaving_node: NodeInfo) -> None:
        """Handle node leaving the cluster."""
        pass  # TODO: Implement
    
    def _migrate_data(self, target_node: NodeInfo, key_range: Tuple[int, int]) -> int:
        """Migrate data to target node for given key range."""
        pass  # TODO: Implement
    
    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        pass  # TODO: Implement
    
    def _gossip_loop(self) -> None:
        """Background gossip protocol for failure detection."""
        pass  # TODO: Implement
    
    def _anti_entropy_loop(self) -> None:
        """Background anti-entropy repair."""
        pass  # TODO: Implement
    
    def get_cluster_state(self) -> Dict[str, Any]:
        """Get current cluster state."""
        pass  # TODO: Implement
    
    def get_local_stats(self) -> Dict[str, Any]:
        """Get local node statistics."""
        pass  # TODO: Implement


class DHTClient:
    """Client for interacting with DHT cluster"""
    
    def __init__(self, known_nodes: List[Tuple[str, int]]):
        pass  # TODO: Implement
    
    def put(self, key: str, value: Any, consistency: ConsistencyLevel = ConsistencyLevel.QUORUM) -> OperationResult:
        """Store key-value pair."""
        pass  # TODO: Implement
    
    def get(self, key: str, consistency: ConsistencyLevel = ConsistencyLevel.QUORUM) -> OperationResult:
        """Retrieve value by key."""
        pass  # TODO: Implement
    
    def delete(self, key: str, consistency: ConsistencyLevel = ConsistencyLevel.QUORUM) -> OperationResult:
        """Delete key-value pair."""
        pass  # TODO: Implement
    
    def _find_coordinator(self, key: str) -> Optional[Tuple[str, int]]:
        """Find coordinator node for key."""
        pass  # TODO: Implement
    
    def _update_cluster_view(self) -> None:
        """Update view of cluster topology."""
        pass  # TODO: Implement


class VectorClock:
    """Vector clock for causality tracking"""
    
    def __init__(self, node_id: str):
        pass  # TODO: Implement
    
    def increment(self) -> None:
        """Increment local clock."""
        pass  # TODO: Implement
    
    def update(self, other_clock: 'VectorClock') -> None:
        """Update clock with another vector clock."""
        pass  # TODO: Implement
    
    def compare(self, other: 'VectorClock') -> str:
        """
        Compare with another vector clock.
        
        Returns:
            'before', 'after', 'concurrent', or 'equal'
        """
        pass  # TODO: Implement
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary representation."""
        pass  # TODO: Implement
    
    @classmethod
    def from_dict(cls, data: Dict[str, int], node_id: str) -> 'VectorClock':
        """Create from dictionary representation."""
        pass  # TODO: Implement


class ConflictResolver:
    """Resolve conflicts during read repair"""
    
    @staticmethod
    def last_write_wins(entries: List[DHTEntry]) -> DHTEntry:
        """Resolve conflict using last-write-wins strategy."""
        pass  # TODO: Implement
    
    @staticmethod
    def version_vector_reconcile(entries: List[DHTEntry]) -> List[DHTEntry]:
        """Resolve conflicts using vector clocks."""
        pass  # TODO: Implement


class PartitionDetector:
    """Detect and handle network partitions"""
    
    def __init__(self, min_cluster_size: int = 3):
        pass  # TODO: Implement
    
    def detect_partition(self, known_nodes: Set[str], alive_nodes: Set[str]) -> bool:
        """Detect if node is in minority partition."""
        pass  # TODO: Implement
    
    def handle_partition(self, is_minority: bool) -> None:
        """Handle partition by either continuing or becoming read-only."""
        pass  # TODO: Implement


# Example usage and testing utilities
def create_test_cluster(num_nodes: int = 5) -> List[DHTNode]:
    """Create a test cluster for development."""
    pass  # TODO: Implement


def simulate_node_failure(cluster: List[DHTNode], node_index: int) -> None:
    """Simulate node failure for testing."""
    pass  # TODO: Implement


def verify_data_consistency(cluster: List[DHTNode], key: str) -> bool:
    """Verify data is consistently replicated across cluster."""
    pass  # TODO: Implement


def benchmark_operations(cluster: List[DHTNode], num_operations: int = 1000) -> Dict[str, float]:
    """Benchmark DHT operations."""
    pass  # TODO: Implement