# Advanced Consistent Hashing

## 🎯 Problem Overview

Consistent hashing is crucial for building scalable distributed systems. This advanced implementation covers virtual nodes, weighted hashing, load balancing, and hotspot detection - essential skills for designing systems like CDNs, databases, and load balancers.

## 🎨 Visual Architecture

### Consistent Hashing with Virtual Nodes
```mermaid
graph TB
    subgraph "Hash Ring (0 to 2^32-1)"
    A[VNode A1<br/>Hash: 100M]
    B[VNode B1<br/>Hash: 300M]
    C[VNode A2<br/>Hash: 500M]
    D[VNode C1<br/>Hash: 700M]
    E[VNode B2<br/>Hash: 900M]
    F[VNode A3<br/>Hash: 1.1B]
    G[VNode C2<br/>Hash: 1.3B]
    H[VNode B3<br/>Hash: 1.5B]
    end
    
    A --> B --> C --> D --> E --> F --> G --> H --> A
    
    I[Physical Node A<br/>3 Virtual Nodes] -.-> A
    I -.-> C
    I -.-> F
    
    J[Physical Node B<br/>3 Virtual Nodes] -.-> B
    J -.-> E
    J -.-> H
    
    K[Physical Node C<br/>2 Virtual Nodes] -.-> D
    K -.-> G
```

### Load Balancing Strategies
```mermaid
graph TD
    A[Load Balancing Request] --> B{Strategy?}
    
    B --> C[Consistent Hash<br/>Deterministic placement]
    B --> D[Least Loaded<br/>Real-time metrics]
    B --> E[Round Robin<br/>Sequential assignment]
    B --> F[Power of Two<br/>Random sampling]
    
    C --> G[Hash(key) → Node]
    D --> H[Monitor node load → Choose lightest]
    E --> I[Counter % num_nodes]
    F --> J[Sample 2 nodes → Choose better]
    
    K[Request Routing] --> L[Primary Node]
    L --> M{Node Healthy?}
    M -->|Yes| N[Route Request]
    M -->|No| O[Find Next Available Node]
```

## 🔑 Key Concepts

### Virtual Nodes Benefits
```mermaid
graph LR
    A[Virtual Nodes Advantages] --> B[Better Load Distribution]
    A --> C[Flexible Weighting]
    A --> D[Faster Rebalancing]
    A --> E[Heterogeneous Hardware]
    
    B --> B1[Reduces variance in load]
    C --> C1[More VNodes = Higher capacity]
    D --> D1[Redistribute load gradually]
    E --> E1[Assign VNodes by server capacity]
    
    F[Without Virtual Nodes] --> G[Uneven Distribution]
    F --> H[Hot Spots]
    F --> I[Poor Utilization]
    
    J[With Virtual Nodes] --> K[Smooth Distribution]
    J --> L[Load Balancing]
    J --> M[Optimal Resource Usage]
```

### Weighted Consistent Hashing
```mermaid
graph TB
    subgraph "Heterogeneous Cluster"
    A[Small Server<br/>4 CPU, 8GB RAM<br/>Weight: 1]
    B[Medium Server<br/>8 CPU, 16GB RAM<br/>Weight: 2]
    C[Large Server<br/>16 CPU, 32GB RAM<br/>Weight: 4]
    end
    
    D[Virtual Node Assignment] --> E[Server A: 50 VNodes]
    D --> F[Server B: 100 VNodes]
    D --> G[Server C: 200 VNodes]
    
    H[Load Distribution] --> I[Server A: ~14% traffic]
    H --> J[Server B: ~29% traffic]
    H --> K[Server C: ~57% traffic]
    
    L[Proportional to Capacity] --> M[Optimal Resource Utilization]
```

## 🏗️ Advanced Features

### Hotspot Detection and Mitigation
```mermaid
sequenceDiagram
    participant Monitor
    participant HashRing
    participant LoadBalancer
    participant Nodes
    
    Monitor->>Nodes: Collect metrics (CPU, requests/sec, latency)
    Nodes-->>Monitor: Node statistics
    
    Monitor->>Monitor: Analyze load distribution
    Monitor->>Monitor: Detect hotspots (load > 2x average)
    
    alt Hotspot Detected
        Monitor->>HashRing: Get hotspot node info
        HashRing-->>Monitor: Node details and key ranges
        
        Monitor->>LoadBalancer: Suggest mitigation
        LoadBalancer->>LoadBalancer: Apply load shedding
        LoadBalancer->>HashRing: Redistribute virtual nodes
        
        Note over HashRing: Increase VNodes for overloaded ranges
    end
    
    Monitor->>Monitor: Continue monitoring
```

### Multi-Level Load Balancing
```mermaid
graph TD
    A[Client Request] --> B[L1: Geographic LB<br/>Route to closest region]
    B --> C[L2: Cluster LB<br/>Choose datacenter]
    C --> D[L3: Consistent Hash LB<br/>Select server group]
    D --> E[L4: Local LB<br/>Pick specific server]
    
    F[Consistent Hashing Layer] --> G[Primary Hash Ring<br/>Coarse-grained placement]
    G --> H[Secondary Hash Ring<br/>Fine-grained placement]
    H --> I[Server Selection<br/>Health-aware routing]
```

## 🧪 Test Strategy

### Hash Distribution Quality Testing
```mermaid
graph TD
    A[Distribution Testing] --> B[Statistical Analysis]
    A --> C[Load Simulation]
    A --> D[Rebalancing Impact]
    
    B --> B1[Chi-square test for uniformity]
    B --> B2[Standard deviation of loads]
    B --> B3[Kolmogorov-Smirnov test]
    
    C --> C1[Million key simulation]
    C --> C2[Real-world key patterns]
    C --> C3[Burst traffic scenarios]
    
    D --> D1[Node addition/removal impact]
    D --> D2[Key migration measurement]
    D --> D3[Minimal disruption verification]
```

### Performance Benchmarking
```mermaid
mindmap
  root((Performance Tests))
    Latency
      Hash computation time
      Node lookup speed
      Virtual node management
    Throughput
      Requests per second
      Concurrent hash operations
      Batch processing efficiency
    Memory
      Hash ring storage overhead
      Virtual node memory usage
      Statistics tracking cost
    Scalability
      Performance with 1000+ nodes
      Million+ virtual nodes
      Geographic distribution
```

## 💡 Interview Discussion Points

### Algorithm Comparison
```mermaid
graph LR
    A[Hashing Algorithms] --> B[Standard Consistent Hashing]
    A --> C[Rendezvous Hashing]
    A --> D[Jump Consistent Hash]
    A --> E[Maglev Hashing]
    
    B --> B1[Good: Simple, widely used<br/>Bad: Poor distribution without VNodes]
    C --> C1[Good: Perfect distribution<br/>Bad: O(N) lookup time]
    D --> D1[Good: Minimal memory, O(1)<br/>Bad: Limited flexibility]
    E --> E1[Good: Google-proven, fast<br/>Bad: Complex implementation]
```

### Common Questions

**Q: "How do you handle hash ring rebalancing?"**
```python
class RebalancingStrategy:
    def add_node(self, new_node):
        # 1. Calculate new virtual node positions
        # 2. Identify affected key ranges
        # 3. Migrate data gradually (avoid thundering herd)
        # 4. Update routing tables atomically
        # 5. Monitor for completion
        pass
    
    def remove_node(self, node_id):
        # 1. Mark node as leaving (no new requests)
        # 2. Redistribute virtual nodes
        # 3. Migrate data to new nodes
        # 4. Remove from ring atomically
        pass
```

**Q: "How do you optimize for cache locality?"**
```mermaid
graph TD
    A[Cache Locality Optimization] --> B[Consistent Placement]
    A --> C[Temporal Locality]
    A --> D[Spatial Locality]
    
    B --> B1[Same key always maps to same node]
    C --> C1[Recent keys likely to be accessed again]
    D --> D1[Similar keys likely accessed together]
    
    E[Implementation] --> F[Sticky Sessions]
    E --> G[Key Prefix Grouping]
    E --> H[LRU Cache per Node]
```

**Q: "How do you handle network partitions?"**
| Scenario | Strategy | Trade-off |
|----------|----------|-----------|
| **Majority Partition** | Continue operations | Risk inconsistency |
| **Minority Partition** | Read-only mode | Reduced availability |
| **Split Brain** | Quorum-based decisions | Complex coordination |
| **Healing** | Conflict resolution | Temporary inconsistency |

## 🎯 Real-World Applications

### CDN Edge Server Selection
```mermaid
sequenceDiagram
    participant User
    participant DNS
    participant CDN_Controller
    participant EdgeServers
    
    User->>DNS: Resolve cdn.example.com
    DNS->>CDN_Controller: Get optimal edge server
    
    CDN_Controller->>CDN_Controller: User IP → Geographic hash
    CDN_Controller->>CDN_Controller: Content ID → Content hash
    CDN_Controller->>CDN_Controller: Combine hashes → Server selection
    
    CDN_Controller-->>DNS: Return edge server IP
    DNS-->>User: Edge server address
    
    User->>EdgeServers: Request content
    EdgeServers-->>User: Serve content
```

### Database Sharding
```mermaid
graph TD
    A[Application] --> B[Shard Router]
    B --> C[Consistent Hash Function]
    C --> D{Shard Selection}
    
    D --> E[Shard 1<br/>Hash range: 0-85M]
    D --> F[Shard 2<br/>Hash range: 85M-170M]
    D --> G[Shard 3<br/>Hash range: 170M-255M]
    
    H[Auto-Scaling] --> I{Load Threshold Exceeded?}
    I -->|Yes| J[Add New Shard]
    J --> K[Rebalance Hash Ring]
    K --> L[Migrate Data]
    
    M[Cross-Shard Queries] --> N[Query All Shards]
    N --> O[Merge Results]
```

## 🔧 Advanced Implementation Patterns

### Hierarchical Consistent Hashing
```mermaid
graph TB
    A[Global Hash Ring<br/>Route to Region] --> B[US-East Ring]
    A --> C[US-West Ring]
    A --> D[EU Ring]
    
    B --> B1[Datacenter 1]
    B --> B2[Datacenter 2]
    
    B1 --> B3[Rack 1]
    B1 --> B4[Rack 2]
    
    B3 --> B5[Server 1]
    B3 --> B6[Server 2]
```

### Dynamic Weight Adjustment
```mermaid
sequenceDiagram
    participant Monitor
    participant WeightController
    participant HashRing
    participant Servers
    
    loop Every 30 seconds
        Monitor->>Servers: Collect performance metrics
        Servers-->>Monitor: CPU, memory, request latency
        
        Monitor->>WeightController: Send aggregated metrics
        WeightController->>WeightController: Calculate optimal weights
        
        alt Weight Change Needed
            WeightController->>HashRing: Update node weights
            HashRing->>HashRing: Redistribute virtual nodes
            HashRing->>Servers: Rebalance load gradually
        end
    end
```

## 🚀 Implementation Guide

### Phase 1: Basic Consistent Hashing
```python
# 1. Hash ring with basic node placement
# 2. Key lookup algorithm
# 3. Node addition/removal
```

### Phase 2: Virtual Nodes
```python
# 1. Multiple virtual nodes per physical node
# 2. Weighted distribution
# 3. Load balancing improvements
```

### Phase 3: Advanced Load Balancing
```python
# 1. Multiple load balancing strategies
# 2. Health-aware routing
# 3. Performance monitoring
```

### Phase 4: Production Optimization
```python
# 1. Hotspot detection and mitigation
# 2. Dynamic rebalancing
# 3. Multi-level hash rings
```

## 🧪 Testing Your Implementation

```bash
# Test basic consistent hashing
pytest test_consistent_hashing.py::TestConsistentHashRing -v

# Test load balancing strategies
pytest test_consistent_hashing.py::TestLoadBalancer -v

# Test hotspot detection
pytest test_consistent_hashing.py::TestHotspotDetector -v

# Performance and distribution tests
pytest test_consistent_hashing.py::TestPerformance -v
pytest test_consistent_hashing.py::TestUtilityFunctions -v
```

## 🏆 Success Criteria

After completing this challenge:
- ✅ Master consistent hashing theory and practice
- ✅ Implement virtual nodes for better distribution
- ✅ Design weighted hashing for heterogeneous systems
- ✅ Build hotspot detection and mitigation
- ✅ Compare different hashing algorithms
- ✅ Optimize for real-world performance requirements
- ✅ Handle dynamic load balancing scenarios
- ✅ Apply consistent hashing to various system architectures