"""
LRU Cache with TTL Implementation
================================

Implement a Least Recently Used (LRU) cache with Time-To-Live (TTL) functionality.

Requirements:
- O(1) get and put operations
- Thread-safe implementation
- Automatic expiration of entries based on TTL
- Configurable maximum size
- Proper cleanup of expired entries

Your Tasks:
1. Implement LRUCache with O(1) operations
2. Add TTL functionality with automatic cleanup
3. Make it thread-safe
4. Implement cache statistics (hits, misses, evictions)
5. Add cache warming and bulk operations

Interview Focus:
- Explain data structure choices (HashMap + Doubly Linked List)
- Discuss memory management and cleanup strategies
- Handle concurrent access patterns
"""

import time
import threading
from typing import Any, Optional, Dict, Tuple
from dataclasses import dataclass
from collections import OrderedDict


@dataclass
class CacheEntry:
    value: Any
    access_time: float
    expiry_time: Optional[float] = None

class Node:
    def __init__(self, key: str, value, ttl=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
        self.expiry = time.time() + ttl if ttl else None

    def is_expired(self):
        return self.expiry is not None and time.time() > self.expiry

class LRUCache:
    def __init__(self, capacity: int, default_ttl: Optional[float] = None):
        """
        Initialize LRU Cache.
        
        Args:
            capacity: Maximum number of entries
            default_ttl: Default time-to-live in seconds (None = no expiration)
        """
        self.capacity = capacity
        self.cache = {}
        self.head = Node("head", None)
        self.tail = Node("tail", None)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key, updating access time.
        
        Args:
            key: Cache key
            
        Returns:
            Value if found and not expired, None otherwise
        """
        if key in self.cache:
            node = self.cache[key]
            if node.is_expired():
                self._remove(node)
                del self.cache[key]
                return None
            else:
                self._remove(node)
                self._add_to_front(node)
                return node.value
        return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Put key-value pair in cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (overrides default_ttl)
        """
        if key in self.cache:
            self._remove(self.cache[key])

        node = Node(key, value, ttl)
        self.cache[key] = node
        self._add_to_front(node)

        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def delete(self, key: str) -> bool:
        """
        Delete entry by key.
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed, False otherwise
        """
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.cache = {}
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def size(self) -> int:
        """Get current number of entries."""
        return len(self.cache)

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        for key in list(self.cache.keys()):
            node = self.cache[key]
            if node.is_expired():
                removed += 1
                self._remove(node)
                del self.cache[key]
        return removed
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        lru = self.tail.prev
        if lru != self.head:
            self._remove(lru)
            del self.cache[lru.key]

    def _remove(self, node: Node) -> None:
        """Remove node from cache."""
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def _add_to_front(self, node: Node) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
