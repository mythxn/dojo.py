import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Transaction:
    id: str
    amount: float
    currency: str
    status: str  # 'pending', 'completed', 'failed'
    created_at: datetime
    metadata: Dict[str, Any]


class Node:
    def __init__(self, txn: Transaction, expiry: datetime):
        self.txn = txn
        self.expiry = expiry
        self.prev = None
        self.next = None


class TransactionCache:
    def __init__(self, max_size: int, ttl_seconds: int):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.map: Dict[str, Node] = {}
        self.head = None  # Most recently used
        self.tail = None  # Least recently used
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def put(self, txn: Transaction):
        with self.lock:
            now = datetime.now()
            expiry = now + timedelta(seconds=self.ttl_seconds)

            if txn.id in self.map:
                node = self.map[txn.id]
                node.txn = txn
                node.expiry = expiry
                self._move_to_front(node)
            else:
                if len(self.map) >= self.max_size:
                    self._evict_lru()

                node = Node(txn, expiry)
                self._add_to_front(node)
                self.map[txn.id] = node

    def get(self, txn_id: str) -> Optional[Transaction]:
        with self.lock:
            node = self.map.get(txn_id)
            now = datetime.now()

            if not node:
                self.misses += 1
                return None

            if node.expiry < now:
                self._remove_node(node)
                del self.map[txn_id]
                self.misses += 1
                return None

            self._move_to_front(node)
            self.hits += 1
            return node.txn

    def update_status(self, txn_id: str, new_status: str) -> bool:
        with self.lock:
            node = self.map.get(txn_id)
            now = datetime.now()

            if not node or node.expiry < now:
                if node:
                    self._remove_node(node)
                    del self.map[txn_id]
                return False

            node.txn.status = new_status
            self._move_to_front(node)
            return True

    def get_cache_stats(self) -> Dict[str, int]:
        with self.lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "current_size": len(self.map),
                "max_size": self.max_size
            }

    def _evict_lru(self):
        if self.tail:
            lru_id = self.tail.txn.id
            self._remove_node(self.tail)
            del self.map[lru_id]

    def _add_to_front(self, node: Node):
        node.prev = None
        node.next = self.head
        if self.head:
            self.head.prev = node
        self.head = node
        if not self.tail:
            self.tail = node

    def _remove_node(self, node: Node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = node.next = None

    def _move_to_front(self, node: Node):
        self._remove_node(node)
        self._add_to_front(node)

if __name__ == "__main__":
    import time

    cache = TransactionCache(max_size=2, ttl_seconds=2)  # 2 items max, 2s TTL

    txn1 = Transaction("txn1", 100.0, "USD", "pending", datetime.now(), {"user": "u1"})
    txn2 = Transaction("txn2", 200.0, "USD", "pending", datetime.now(), {"user": "u2"})
    txn3 = Transaction("txn3", 300.0, "USD", "pending", datetime.now(), {"user": "u3"})

    print("\n[1] Put txn1 and txn2")
    cache.put(txn1)
    cache.put(txn2)

    print("[2] Get txn1 → should be hit")
    print("txn1:", cache.get("txn1"))

    print("[3] Put txn3 → should evict txn2 (LRU)")
    cache.put(txn3)

    print("[4] Get txn2 → should be miss (evicted)")
    print("txn2:", cache.get("txn2"))

    print("[5] Get txn3 → should be hit")
    print("txn3:", cache.get("txn3"))

    print("[6] Try to get missing txnX → should be miss")
    print("txnX:", cache.get("txnX"))

    print("[7] Wait for TTL to expire...")
    time.sleep(2.1)

    print("[8] Get txn1 → should be expired")
    print("txn1:", cache.get("txn1"))

    print("[9] Final cache stats:")
    print(cache.get_cache_stats())