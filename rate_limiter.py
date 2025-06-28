import threading
import time
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict


@dataclass
class RateLimitResult:
    allowed: bool
    remaining_requests: int
    reset_time: float  # when the full quota will be available again
    retry_after: float  # when the next request will be allowed


class PaymentRateLimiter:
    """Thread-safe sliding window rate limiter per user."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.lock = threading.Lock()
        self.user_timestamps: Dict[str, deque] = defaultdict(deque)

    def is_payment_allowed(self, user_id: str) -> RateLimitResult:
        """Returns whether the user can make a payment right now."""
        now = time.time()

        with self.lock:
            timestamps = self.user_timestamps[user_id]

            self._evict_old_requests(timestamps, now)

            if len(timestamps) >= self.max_requests:
                oldest = timestamps[0]
                retry_after = oldest + self.window_seconds - now
                reset_time = oldest + self.window_seconds

                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=reset_time,
                    retry_after=retry_after
                )

            # Accept the payment
            timestamps.append(now)
            remaining = self.max_requests - len(timestamps)
            reset_time = timestamps[0] + self.window_seconds

            return RateLimitResult(
                allowed=True,
                remaining_requests=remaining,
                reset_time=reset_time,
                retry_after=0
            )

    def _evict_old_requests(self, timestamps: deque, now: float):
        """Remove timestamps that are outside the time window."""
        threshold = now - self.window_seconds
        while timestamps and timestamps[0] <= threshold:
            timestamps.popleft()

    def reset_user_limits(self, user_id: str):
        """Manually clear usage history for a user (e.g., by admin)."""
        with self.lock:
            self.user_timestamps[user_id].clear()


# === Example Usage ===
if __name__ == "__main__":
    limiter = PaymentRateLimiter(max_requests=3, window_seconds=60)

    for i in range(5):
        result = limiter.is_payment_allowed("user123")
        print(f"Payment {i+1}: Allowed={result.allowed}, Remaining={result.remaining_requests}, Retry after={round(result.retry_after, 2)}s")
        time.sleep(1)

    result = limiter.is_payment_allowed("user456")
    print(f"Different user: {result}")