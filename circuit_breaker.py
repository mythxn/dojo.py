import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Any, Optional


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3
    timeout_seconds: int = 5
    success_threshold: int = 2
    response_timeout: int = 500


@dataclass
class CallResult:
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = datetime.now()


class CircuitBreakerOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = threading.Lock()
        self.history: list[CallResult] = []

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if not self._can_execute():
            raise CircuitBreakerOpenError(f"Circuit {self.name} is OPEN")

        start = datetime.now()
        try:
            result = func(*args, **kwargs)
            duration_ms = (datetime.now() - start).total_seconds() * 1000
            self._record_success(duration_ms)
            return result
        except Exception as e:
            duration_ms = (datetime.now() - start).total_seconds() * 1000
            self._record_failure(str(e), duration_ms)
            raise

    def _can_execute(self) -> bool:
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            if self.state == CircuitState.HALF_OPEN:
                return True
            if self.state == CircuitState.OPEN and self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                return True
            return False

    def _should_attempt_reset(self) -> bool:
        if not self.last_failure_time:
            return False
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds

    def _record_success(self, duration_ms: float) -> None:
        with self.lock:
            self.history.append(CallResult(True, duration_ms))
            self.success_count += 1
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN and self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def _record_failure(self, error: str, duration_ms: float) -> None:
        with self.lock:
            self.history.append(CallResult(False, duration_ms, error))
            self.failure_count += 1
            self.success_count = 0

            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = datetime.now()

    def get_state(self) -> CircuitState:
        with self.lock:
            if self.state == CircuitState.OPEN and self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            return self.state

    def get_stats(self) -> dict:
        with self.lock:
            return {
                "state": self.state.value,
                "failures": self.failure_count,
                "successes": self.success_count,
                "total_calls": len(self.history),
            }

    def reset(self):
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.history.clear()


# --- Mock External Services ---

def unreliable_service(success_rate: float = 0.7):
    """Simulate service that fails randomly."""
    time.sleep(0.05)  # simulate latency
    if random.random() > success_rate:
        raise ConnectionError("Simulated failure")
    return "OK"


# --- Unit-Test Style Simulation ---

if __name__ == "__main__":
    cb = CircuitBreaker("payments", CircuitBreakerConfig())

    print("\n[1] Healthy calls:")
    for i in range(3):
        try:
            print(cb.call(unreliable_service, 1.0))
        except Exception as e:
            print(f"Fail: {e}")
        print(cb.get_state(), cb.get_stats())

    print("\n[2] Trigger failures:")
    for i in range(4):
        try:
            print(cb.call(unreliable_service, 0.0))
        except Exception as e:
            print(f"Fail: {e}")
        print(cb.get_state(), cb.get_stats())

    print("\n[3] Wait for timeout to attempt HALF_OPEN:")
    time.sleep(cb.config.timeout_seconds)

    try:
        print(cb.call(unreliable_service, 1.0))
    except Exception as e:
        print(f"Fail: {e}")
    print(cb.get_state(), cb.get_stats())

    print("\n[4] Successful retries to CLOSE:")
    try:
        print(cb.call(unreliable_service, 1.0))
        print(cb.call(unreliable_service, 1.0))
    except Exception as e:
        print(f"Fail: {e}")

    print(cb.get_state(), cb.get_stats())
