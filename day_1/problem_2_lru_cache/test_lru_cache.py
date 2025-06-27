"""
Test cases for LRU Cache implementations
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from day_1.problem_2_lru_cache.lru_cache import LRUCache, TTLCache, CacheWarmer, CacheStats


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


class TestTTLFunctionality:
    
    def test_default_ttl(self):
        """Test cache with default TTL"""
        cache = LRUCache(capacity=10, default_ttl=1.0)  # 1 second TTL
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_custom_ttl_override(self):
        """Test custom TTL overriding default"""
        cache = LRUCache(capacity=10, default_ttl=1.0)
        
        cache.put("key1", "value1")  # Uses default TTL (1 second)
        cache.put("key2", "value2", ttl=2.0)  # Custom TTL (2 seconds)
        
        # After 1.1 seconds
        time.sleep(1.1)
        assert cache.get("key1") is None   # Expired
        assert cache.get("key2") == "value2"  # Still valid
        
        # After another 1 second (2.1 total)
        time.sleep(1.0)
        assert cache.get("key2") is None   # Now expired
    
    def test_no_ttl_entries(self):
        """Test entries without TTL don't expire"""
        cache = LRUCache(capacity=10, default_ttl=None)
        
        cache.put("key1", "value1")  # No TTL
        cache.put("key2", "value2", ttl=1.0)  # With TTL
        
        time.sleep(1.1)
        assert cache.get("key1") == "value1"  # Still valid
        assert cache.get("key2") is None      # Expired
    
    def test_cleanup_expired(self):
        """Test manual cleanup of expired entries"""
        cache = LRUCache(capacity=10, default_ttl=0.5)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        time.sleep(0.6)  # All should be expired
        
        # Before cleanup
        assert cache.size() == 3
        
        # After cleanup
        removed_count = cache.cleanup_expired()
        assert removed_count == 3
        assert cache.size() == 0
    
    def test_mixed_expired_valid_entries(self):
        """Test cleanup with mix of expired and valid entries"""
        cache = LRUCache(capacity=10, default_ttl=None)
        
        cache.put("key1", "value1", ttl=0.5)   # Will expire
        cache.put("key2", "value2")            # No expiration
        cache.put("key3", "value3", ttl=2.0)   # Long expiration
        
        time.sleep(0.6)
        
        removed_count = cache.cleanup_expired()
        assert removed_count == 1
        assert cache.size() == 2
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestCacheStats:
    
    def test_hit_miss_tracking(self):
        """Test cache hit/miss statistics"""
        cache = LRUCache(capacity=3)
        
        # Initial stats
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0
        
        # Add some data
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Test hits
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("key3")  # Miss
        
        stats = cache.get_stats()
        assert stats.hits == 2
        assert stats.misses == 1
    
    def test_eviction_tracking(self):
        """Test eviction statistics"""
        cache = LRUCache(capacity=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Causes eviction
        
        stats = cache.get_stats()
        assert stats.evictions == 1
    
    def test_expiration_tracking(self):
        """Test expired entry statistics"""
        cache = LRUCache(capacity=10, default_ttl=0.5)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        time.sleep(0.6)
        cache.cleanup_expired()
        
        stats = cache.get_stats()
        assert stats.expired_entries == 2


class TestThreadSafety:
    
    def test_concurrent_access(self):
        """Test thread safety with concurrent reads/writes"""
        cache = LRUCache(capacity=100)
        
        def worker(worker_id):
            for i in range(50):
                key = f"key_{worker_id}_{i}"
                value = f"value_{worker_id}_{i}"
                cache.put(key, value)
                assert cache.get(key) == value
        
        # Run 10 workers concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for future in futures:
                future.result()  # Wait for completion
        
        # Verify cache state
        assert cache.size() <= 100  # Shouldn't exceed capacity
    
    def test_concurrent_eviction(self):
        """Test thread safety during evictions"""
        cache = LRUCache(capacity=10)
        
        def fill_cache(start_id):
            for i in range(20):  # More than capacity
                cache.put(f"key_{start_id}_{i}", f"value_{start_id}_{i}")
        
        # Multiple threads causing evictions
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fill_cache, i) for i in range(5)]
            for future in futures:
                future.result()
        
        assert cache.size() == 10  # Should maintain capacity limit
    
    def test_concurrent_cleanup(self):
        """Test thread safety during cleanup operations"""
        cache = LRUCache(capacity=100, default_ttl=0.5)
        
        def add_entries():
            for i in range(50):
                cache.put(f"key_{i}", f"value_{i}")
        
        def cleanup_loop():
            for _ in range(10):
                cache.cleanup_expired()
                time.sleep(0.1)
        
        # Add entries and cleanup concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(add_entries)
            time.sleep(0.6)  # Let entries expire
            
            futures = [executor.submit(cleanup_loop) for _ in range(2)]
            for future in futures:
                future.result()


class TestTTLCache:
    
    def test_ttl_cache_basic(self):
        """Test TTL-focused cache implementation"""
        cache = TTLCache(capacity=10, default_ttl=1.0)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        time.sleep(1.1)
        assert cache.get("key1") is None


class TestCacheWarmer:
    
    def test_cache_warming(self):
        """Test cache warming functionality"""
        cache = LRUCache(capacity=10)
        warmer = CacheWarmer(cache)
        
        def data_loader(key):
            return f"loaded_value_for_{key}"
        
        keys = ["key1", "key2", "key3"]
        warmer.warm_cache(data_loader, keys)
        
        for key in keys:
            assert cache.get(key) == f"loaded_value_for_{key}"
    
    def test_bulk_operations(self):
        """Test bulk get/put operations"""
        cache = LRUCache(capacity=10)
        warmer = CacheWarmer(cache)
        
        # Bulk put
        items = {
            "key1": "value1",
            "key2": "value2", 
            "key3": "value3"
        }
        warmer.bulk_put(items)
        
        # Bulk get
        results = warmer.bulk_get(["key1", "key2", "key3", "key4"])
        
        assert results["key1"] == "value1"
        assert results["key2"] == "value2"
        assert results["key3"] == "value3"
        assert "key4" not in results  # Doesn't exist


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