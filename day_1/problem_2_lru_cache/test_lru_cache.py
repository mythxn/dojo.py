"""
Test cases for LRU Cache implementations
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from day_1.problem_2_lru_cache.lru_cache import LRUCache


class TestLRUCache:
    
    def test_basic_operations(self):
        """Test basic get/put operations"""
        cache = LRUCache(capacity=3)
        
        # Test put and get
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.size() == 3
    
    def test_capacity_limit(self):
        """Test that cache respects capacity limit"""
        cache = LRUCache(capacity=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.size() == 2
    
    def test_lru_eviction_order(self):
        """Test that least recently used items are evicted first"""
        cache = LRUCache(capacity=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add key4, should evict key2 (least recently used)
        cache.put("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None     # Evicted
        assert cache.get("key3") == "value3"  # Still there
        assert cache.get("key4") == "value4"  # Newly added
    
    def test_update_existing_key(self):
        """Test updating existing key doesn't change capacity"""
        cache = LRUCache(capacity=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Update existing key
        cache.put("key1", "new_value1")
        
        assert cache.size() == 2
        assert cache.get("key1") == "new_value1"
        assert cache.get("key2") == "value2"
    
    def test_delete_operation(self):
        """Test delete operation"""
        cache = LRUCache(capacity=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        assert cache.delete("key1") == True
        assert cache.delete("key1") == False  # Already deleted
        assert cache.get("key1") is None
        assert cache.size() == 1
    
    def test_clear_operation(self):
        """Test clear operation"""
        cache = LRUCache(capacity=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        cache.clear()
        
        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

class TestPerformance:
    
    def test_large_cache_performance(self):
        """Test performance with large number of operations"""
        cache = LRUCache(capacity=10000)
        
        # Test write performance
        start_time = time.time()
        for i in range(10000):
            cache.put(f"key_{i}", f"value_{i}")
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        for i in range(10000):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time
        
        # Should be reasonably fast (adjust thresholds as needed)
        assert write_time < 2.0
        assert read_time < 1.0
    
    def test_memory_usage(self):
        """Test that cache properly manages memory"""
        cache = LRUCache(capacity=1000)
        
        # Fill cache to capacity
        for i in range(1000):
            cache.put(f"key_{i}", "x" * 1000)  # 1KB values
        
        # Add more entries (should evict old ones)
        for i in range(1000, 2000):
            cache.put(f"key_{i}", "x" * 1000)
        
        # Should maintain size limit
        assert cache.size() == 1000
        
        # Earlier entries should be evicted
        assert cache.get("key_0") is None
        assert cache.get("key_999") is None
        assert cache.get("key_1000") == "x" * 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])