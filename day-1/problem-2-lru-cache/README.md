# LRU Cache with TTL Implementation

## 🎯 Problem Overview

An LRU (Least Recently Used) cache with TTL (Time To Live) combines efficient caching with automatic expiration. It's one of the most common interview questions because it tests your understanding of data structures, algorithms, and real-world system design.

## 🎨 Visual Architecture

### LRU Cache Data Structure
```mermaid
graph TB
    subgraph "HashMap for O(1) Access"
    A[Key: 'user_1'] --> B[Node*]
    C[Key: 'user_2'] --> D[Node*]
    E[Key: 'user_3'] --> F[Node*]
    end
    
    subgraph "Doubly Linked List for O(1) Ordering"
    G[HEAD] <--> H[user_3<br/>Most Recent] 
    H <--> I[user_1<br/>Middle]
    I <--> J[user_2<br/>Least Recent]
    J <--> K[TAIL]
    end
    
    B -.-> I
    D -.-> J
    F -.-> H
```

### TTL Expiration Flow
```mermaid
sequenceDiagram
    participant Client
    participant Cache
    participant CleanupThread
    participant Storage
    
    Client->>Cache: get(key)
    Cache->>Cache: Check if expired
    alt Not Expired
        Cache->>Storage: Move to head (mark as recent)
        Cache-->>Client: Return value
    else Expired
        Cache->>Storage: Remove from cache
        Cache-->>Client: Return null
    end
    
    Note over CleanupThread: Background Process
    CleanupThread->>Cache: cleanup_expired()
    Cache->>Storage: Remove all expired entries
```

## 🔑 Key Concepts

### 1. LRU Eviction Policy
```mermaid
graph LR
    A[New Item Added] --> B{Cache Full?}
    B -->|No| C[Add to Head]
    B -->|Yes| D[Remove Tail Item]
    D --> E[Add New Item to Head]
    C --> F[Update HashMap]
    E --> F
    
    subgraph "Access Pattern"
    G[Item Accessed] --> H[Move to Head]
    H --> I[Update Access Time]
    end
```

### 2. TTL Implementation Strategies
```mermaid
graph TD
    A[TTL Strategies] --> B[Lazy Expiration]
    A --> C[Proactive Expiration]
    A --> D[Hybrid Approach]
    
    B --> B1[Check on access]
    B --> B2[Simple implementation]
    B --> B3[May waste memory]
    
    C --> C1[Background cleanup]
    C --> C2[Timer-based removal]
    C --> C3[Consistent memory usage]
    
    D --> D1[Lazy + Background]
    D --> D2[Best performance]
    D --> D3[Production ready]
```

## 🏗️ Implementation Deep Dive

### Data Structure Choice
```mermaid
classDiagram
    class LRUCache {
        -capacity: int
        -cache: HashMap~String, Node~
        -head: Node
        -tail: Node
        -lock: ReentrantLock
        +get(key): Value
        +put(key, value): void
        +evict_lru(): void
    }
    
    class Node {
        +key: String
        +value: Any
        +expiry_time: float
        +prev: Node
        +next: Node
    }
    
    class CacheStats {
        +hits: int
        +misses: int
        +evictions: int
        +expired_entries: int
    }
    
    LRUCache --> Node
    LRUCache --> CacheStats
```

### Thread Safety Considerations
```mermaid
graph TB
    A[Thread Safety Challenges] --> B[Race Conditions]
    A --> C[Data Consistency]
    A --> D[Performance Impact]
    
    B --> B1[Multiple threads accessing same key]
    B --> B2[Eviction during access]
    B --> B3[Cleanup vs access conflicts]
    
    C --> C1[HashMap corruption]
    C --> C2[Linked list integrity]
    C --> C3[Statistics accuracy]
    
    D --> D1[Lock contention]
    D --> D2[Read vs write locks]
    D --> D3[Lock-free alternatives]
```

## 🧪 Test Strategy

### Test Categories
```mermaid
mindmap
  root((LRU Cache Tests))
    Basic Operations
      Get/Put functionality
      Capacity enforcement
      LRU eviction order
    TTL Features
      Expiration behavior
      Custom TTL override
      Cleanup efficiency
    Thread Safety
      Concurrent access
      Race condition prevention
      Data consistency
    Performance
      O(1) operation verification
      Memory usage patterns
      High throughput scenarios
    Edge Cases
      Empty cache
      Single item cache
      Clock adjustments
```

## 💡 Interview Discussion Points

### Common Questions & Answers

**Q: "Why use HashMap + Doubly Linked List?"**
```mermaid
graph LR
    A[HashMap Only] --> A1[❌ No ordering info]
    B[Array Only] --> B1[❌ O(n) search]
    C[Linked List Only] --> C1[❌ O(n) access]
    D[HashMap + DLL] --> D1[✅ O(1) access + ordering]
```

**Q: "How do you handle TTL efficiently?"**
- **Lazy Expiration**: Check on access (simple, may waste memory)
- **Active Expiration**: Background cleanup (complex, memory efficient)
- **Hybrid**: Both approaches (production ready)

**Q: "What about thread safety?"**
```python
# Read-Write Lock Strategy
class ThreadSafeLRUCache:
    def __init__(self):
        self.read_lock = threading.RLock()
        self.write_lock = threading.RLock()
    
    def get(self, key):
        with self.read_lock:
            # Check expiration, update position
    
    def put(self, key, value):
        with self.write_lock:
            # Add/update entry, handle eviction
```

### Time & Space Complexity
| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| **get()** | O(1) | - | HashMap lookup + DLL move |
| **put()** | O(1) | - | HashMap insert + DLL operations |
| **cleanup()** | O(n) | - | Scan all entries for expiration |
| **Overall** | - | O(capacity) | HashMap + DLL storage |

## 🎯 Real-World Applications

### Web Application Cache
```mermaid
sequenceDiagram
    participant Browser
    participant WebServer
    participant LRUCache
    participant Database
    
    Browser->>WebServer: Request user profile
    WebServer->>LRUCache: get(user_id)
    alt Cache Hit
        LRUCache-->>WebServer: User data
        WebServer-->>Browser: Profile page
    else Cache Miss
        LRUCache-->>WebServer: null
        WebServer->>Database: SELECT user data
        Database-->>WebServer: User data
        WebServer->>LRUCache: put(user_id, data, ttl=300)
        WebServer-->>Browser: Profile page
    end
```

### Multi-Level Caching
```mermaid
graph TD
    A[Client Request] --> B[L1: Memory Cache<br/>Fast, Small]
    B -->|Miss| C[L2: Redis Cache<br/>Network, Medium]
    C -->|Miss| D[L3: Database<br/>Slow, Large]
    
    D --> E[Store in L2]
    E --> F[Store in L1]
    F --> G[Return to Client]
    
    B -->|Hit| G
    C -->|Hit| F
```

## 🔧 Advanced Features

### Cache Warming
```mermaid
graph LR
    A[Application Start] --> B[Cache Warmer]
    B --> C[Load Popular Keys]
    C --> D[Predict Access Patterns]
    D --> E[Pre-populate Cache]
    E --> F[Monitor Hit Rates]
    F --> G[Adjust Strategy]
```

### Cache Statistics
```mermaid
graph TB
    A[Cache Metrics] --> B[Hit Rate]
    A --> C[Miss Rate]
    A --> D[Eviction Rate]
    A --> E[Memory Usage]
    
    B --> F[Monitor Performance]
    C --> G[Identify Problems]
    D --> H[Tune Capacity]
    E --> I[Resource Planning]
```

## 🚀 Implementation Guide

### Step-by-Step Approach
1. **Basic LRU** - HashMap + Doubly Linked List
2. **Add TTL** - Expiration timestamps
3. **Thread Safety** - Locks and synchronization
4. **Optimization** - Background cleanup, statistics
5. **Advanced** - Cache warming, multi-level

### Testing Your Implementation
```bash
# Run basic functionality tests
pytest test_lru_cache.py::TestLRUCache::test_basic_operations -v

# Test TTL features
pytest test_lru_cache.py::TestTTLFunctionality -v

# Verify thread safety
pytest test_lru_cache.py::TestThreadSafety -v

# Performance benchmarks
pytest test_lru_cache.py::TestPerformance -v
```

## 🏆 Success Criteria

After completing this challenge:
- ✅ Understand why HashMap + DLL is the optimal choice
- ✅ Implement O(1) get/put operations correctly
- ✅ Handle TTL with multiple strategies
- ✅ Make cache thread-safe without sacrificing performance
- ✅ Add comprehensive monitoring and statistics
- ✅ Explain trade-offs between different caching strategies