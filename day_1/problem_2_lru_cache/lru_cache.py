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
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired_entries: int = 0


@dataclass
class CacheEntry:
    value: Any
    access_time: float
    expiry_time: Optional[float] = None


class LRUCache:
    def __init__(self, capacity: int, default_ttl: Optional[float] = None):
        """
        Initialize LRU Cache.
        
        Args:
            capacity: Maximum number of entries
            default_ttl: Default time-to-live in seconds (None = no expiration)
        """
        pass  # TODO: Implement
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key, updating access time.
        
        Args:
            key: Cache key
            
        Returns:
            Value if found and not expired, None otherwise
        """
        pass  # TODO: Implement
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Put key-value pair in cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (overrides default_ttl)
        """
        pass  # TODO: Implement
    
    def delete(self, key: str) -> bool:
        """
        Delete entry by key.
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed, False otherwise
        """
        pass  # TODO: Implement
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        pass  # TODO: Implement
    
    def size(self) -> int:
        """Get current number of entries."""
        pass  # TODO: Implement
    
    def is_expired(self, entry: CacheEntry, current_time: float) -> bool:
        """Check if entry is expired."""
        pass  # TODO: Implement
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        pass  # TODO: Implement
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass  # TODO: Implement
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        pass  # TODO: Implement
    
    def _move_to_end(self, key: str) -> None:
        """Move key to end (most recently used)."""
        pass  # TODO: Implement


class TTLCache:
    """Alternative implementation focusing on TTL efficiency"""
    
    def __init__(self, capacity: int, default_ttl: float):
        pass  # TODO: Implement
    
    def get(self, key: str) -> Optional[Any]:
        pass  # TODO: Implement
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        pass  # TODO: Implement
    
    def _background_cleanup(self) -> None:
        """Background thread for cleaning expired entries."""
        pass  # TODO: Implement


class CacheWarmer:
    """Utility for cache warming and bulk operations"""
    
    def __init__(self, cache: LRUCache):
        pass  # TODO: Implement
    
    def warm_cache(self, data_loader: callable, keys: list) -> None:
        """Warm cache with data from loader function."""
        pass  # TODO: Implement
    
    def bulk_get(self, keys: list) -> Dict[str, Any]:
        """Get multiple keys efficiently."""
        pass  # TODO: Implement
    
    def bulk_put(self, items: Dict[str, Any], ttl: Optional[float] = None) -> None:
        """Put multiple items efficiently."""
        pass  # TODO: Implement


class MultiLevelCache:
    """Multi-level cache implementation (L1: memory, L2: disk, etc.)"""
    
    def __init__(self, l1_cache: LRUCache, l2_cache: Optional[Any] = None):
        pass  # TODO: Implement
    
    def get(self, key: str) -> Optional[Any]:
        """Get from L1, fallback to L2."""
        pass  # TODO: Implement
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put to both L1 and L2."""
        pass  # TODO: Implement