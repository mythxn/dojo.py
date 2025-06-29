"""
PROBLEM: Duplicate Transaction Detection (20-25 minutes)

BUSINESS CONTEXT:
Users sometimes double-click payment buttons or network issues cause duplicate requests.
You need to detect and prevent duplicate transactions in real-time, beyond simple idempotency.

REQUIREMENTS:
1. Detect duplicate transactions using fuzzy matching
2. Handle exact duplicates (same request ID) and similar duplicates
3. Time-window based detection (duplicates within 5 minutes)
4. Match on: amount, merchant, payment method, user
5. Store transaction fingerprints efficiently
6. Handle high throughput with minimal latency

FOLLOW-UP QUESTIONS:
- How do you handle legitimate duplicate amounts (same user, same merchant)?
- What if the user intentionally makes the same purchase twice?
- How do you clean up old fingerprints to save memory?
- How would you scale this across multiple servers?
- How do you handle partial matches (similar but not identical)?
"""

import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import threading


class MatchStrength(Enum):
    EXACT = "exact"           # Identical transaction
    STRONG = "strong"         # Very likely duplicate  
    WEAK = "weak"             # Possibly duplicate
    NO_MATCH = "no_match"     # Not a duplicate


@dataclass
class Transaction:
    """Transaction data for duplicate detection."""
    id: str
    user_id: str
    merchant_id: str
    amount_cents: int
    currency: str
    payment_method_id: str
    description: Optional[str]
    timestamp: datetime
    metadata: Dict[str, str] = None


@dataclass
class TransactionFingerprint:
    """Compact representation of transaction for matching."""
    exact_hash: str           # Hash of exact transaction details
    fuzzy_hash: str          # Hash for fuzzy matching
    amount_cents: int
    user_id: str
    merchant_id: str
    payment_method_id: str
    timestamp: datetime
    original_transaction_id: str


@dataclass
class DuplicateMatch:
    """Result of duplicate detection."""
    is_duplicate: bool
    match_strength: MatchStrength
    matched_transaction_id: Optional[str]
    confidence_score: float   # 0.0 to 1.0
    reason: str


class DuplicateDetector:
    """Real-time duplicate transaction detection system."""
    
    def __init__(self, time_window_minutes: int = 5, max_fingerprints: int = 100000):
        """
        Initialize duplicate detector.
        
        Args:
            time_window_minutes: How long to keep fingerprints for matching
            max_fingerprints: Maximum fingerprints to keep in memory
        """
        # TODO: Initialize storage and configuration
        pass
    
    def check_duplicate(self, transaction: Transaction) -> DuplicateMatch:
        """
        Check if transaction is a duplicate.
        
        Args:
            transaction: Transaction to check
            
        Returns:
            DuplicateMatch with detection results
        """
        # TODO: Implement duplicate detection logic
        pass
    
    def add_transaction(self, transaction: Transaction):
        """Add transaction fingerprint to detection system."""
        # TODO: Create and store fingerprint
        pass
    
    def _create_fingerprint(self, transaction: Transaction) -> TransactionFingerprint:
        """Create transaction fingerprint for matching."""
        # TODO: Generate exact and fuzzy hashes
        pass
    
    def _generate_exact_hash(self, transaction: Transaction) -> str:
        """Generate hash for exact duplicate detection."""
        # TODO: Hash all transaction fields for exact matching
        pass
    
    def _generate_fuzzy_hash(self, transaction: Transaction) -> str:
        """Generate hash for fuzzy duplicate detection."""
        # TODO: Hash key fields only (ignore description, timestamps)
        pass
    
    def _find_exact_matches(self, fingerprint: TransactionFingerprint) -> List[str]:
        """Find transactions with identical fingerprints."""
        # TODO: Look up exact hash matches
        pass
    
    def _find_fuzzy_matches(self, fingerprint: TransactionFingerprint) -> List[Tuple[str, float]]:
        """Find similar transactions with confidence scores."""
        # TODO: Look up fuzzy matches and calculate similarity
        pass
    
    def _calculate_similarity(self, fp1: TransactionFingerprint, fp2: TransactionFingerprint) -> float:
        """Calculate similarity score between two transactions."""
        # TODO: Compare transaction attributes and return 0.0-1.0 score
        pass
    
    def _is_within_time_window(self, timestamp1: datetime, timestamp2: datetime) -> bool:
        """Check if two timestamps are within detection window."""
        # TODO: Compare timestamps against time window
        pass
    
    def _cleanup_old_fingerprints(self):
        """Remove expired fingerprints to save memory."""
        # TODO: Remove fingerprints older than time window
        pass
    
    def _determine_match_strength(self, confidence_score: float) -> MatchStrength:
        """Convert confidence score to match strength."""
        # TODO: Map confidence score to match strength enum
        pass
    
    def get_statistics(self) -> Dict[str, int]:
        """Get detector statistics for monitoring."""
        # TODO: Return counts, hit rates, memory usage
        pass


class AdvancedDuplicateDetector(DuplicateDetector):
    """Enhanced detector with advanced features."""
    
    def __init__(self, time_window_minutes: int = 5, max_fingerprints: int = 100000):
        super().__init__(time_window_minutes, max_fingerprints)
        # TODO: Initialize advanced features
        pass
    
    def check_duplicate_with_rules(self, transaction: Transaction, rules: Dict[str, any]) -> DuplicateMatch:
        """Check duplicates with custom business rules."""
        # TODO: Apply business-specific duplicate detection rules
        pass
    
    def whitelist_duplicate(self, transaction_id1: str, transaction_id2: str):
        """Mark two transactions as legitimate duplicates."""
        # TODO: Add to whitelist to prevent future duplicate detection
        pass
    
    def blacklist_pattern(self, pattern: Dict[str, str]):
        """Mark a pattern as always duplicate."""
        # TODO: Add pattern to always-duplicate list
        pass
    
    def detect_fraud_patterns(self, user_id: str, time_range_minutes: int = 60) -> List[Dict]:
        """Detect suspicious transaction patterns for fraud prevention."""
        # TODO: Look for rapid-fire transactions, amount patterns, etc.
        pass
    
    def _apply_merchant_rules(self, transaction: Transaction) -> Dict[str, any]:
        """Apply merchant-specific duplicate detection rules."""
        # TODO: Different rules for different merchant types
        pass
    
    def _check_user_behavior(self, user_id: str, transaction: Transaction) -> float:
        """Analyze user's typical behavior to adjust duplicate detection."""
        # TODO: Consider user's normal transaction patterns
        pass


class DuplicateDetectorCluster:
    """Distributed duplicate detection across multiple servers."""
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        """
        Initialize cluster node.
        
        Args:
            node_id: This node's identifier
            cluster_nodes: List of all nodes in cluster
        """
        # TODO: Initialize distributed detection
        pass
    
    def check_duplicate_distributed(self, transaction: Transaction) -> DuplicateMatch:
        """Check for duplicates across all cluster nodes."""
        # TODO: Coordinate duplicate checking across cluster
        pass
    
    def _hash_to_node(self, transaction_hash: str) -> str:
        """Determine which node should handle this transaction."""
        # TODO: Consistent hashing to distribute load
        pass
    
    def _sync_with_cluster(self, fingerprint: TransactionFingerprint):
        """Synchronize fingerprint with other cluster nodes."""
        # TODO: Replicate fingerprint to other nodes
        pass


# Example usage and test cases
if __name__ == "__main__":
    detector = DuplicateDetector(time_window_minutes=5, max_fingerprints=10000)
    
    # Test transaction
    transaction1 = Transaction(
        id="txn_123",
        user_id="user_456", 
        merchant_id="merchant_789",
        amount_cents=1500,  # $15.00
        currency="USD",
        payment_method_id="card_abc",
        description="Coffee shop purchase",
        timestamp=datetime.now()
    )
    
    # Check for duplicates (should be no match)
    result1 = detector.check_duplicate(transaction1)
    print(f"First transaction duplicate check: {result1.is_duplicate}")
    
    # Add transaction to detector
    detector.add_transaction(transaction1)
    
    # Test exact duplicate
    transaction2 = Transaction(
        id="txn_124",  # Different ID
        user_id="user_456",
        merchant_id="merchant_789", 
        amount_cents=1500,  # Same amount
        currency="USD",
        payment_method_id="card_abc",  # Same card
        description="Coffee shop purchase",  # Same description
        timestamp=datetime.now()  # Within time window
    )
    
    result2 = detector.check_duplicate(transaction2)
    print(f"Potential duplicate: {result2.is_duplicate}, strength: {result2.match_strength}")
    print(f"Confidence: {result2.confidence_score:.2f}, reason: {result2.reason}")
    
    # Test statistics
    stats = detector.get_statistics()
    print(f"Detector stats: {stats}")
    
    # Test advanced detector
    advanced_detector = AdvancedDuplicateDetector()
    fraud_patterns = advanced_detector.detect_fraud_patterns("user_456", 60)
    print(f"Fraud patterns detected: {len(fraud_patterns)}")