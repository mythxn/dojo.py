"""
Background Job Processing System
===============================

Implement a comprehensive job queue system with priority, retry, and scheduling.

Requirements:
- Priority-based job scheduling
- Retry mechanisms with exponential backoff
- Delayed job execution
- Worker pool management
- Job status tracking and monitoring
- Persistence for job recovery

Your Tasks:
1. Implement Job and JobQueue classes
2. Create WorkerPool with configurable workers
3. Add retry logic with different strategies
4. Implement job scheduling and delays
5. Add comprehensive monitoring and metrics

Interview Focus:
- Discuss job persistence and recovery
- Explain different retry strategies
- Handle worker failures and job distribution
"""

import time
import threading
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Dict, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import heapq
import json
from concurrent.futures import ThreadPoolExecutor, Future
import logging


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class RetryStrategy(Enum):
    NONE = "none"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass
class JobResult:
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class RetryConfig:
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0
    max_delay: float = 300.0
    jitter: bool = True


@dataclass
class Job:
    id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0  # Lower number = higher priority
    scheduled_time: Optional[datetime] = None
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    last_error: Optional[str] = None
    result: Optional[JobResult] = None
    
    def __lt__(self, other):
        # For priority queue: scheduled jobs first, then by priority, then by creation time
        if self.scheduled_time and other.scheduled_time:
            return self.scheduled_time < other.scheduled_time
        elif self.scheduled_time:
            return False  # Scheduled jobs have lower priority in ready queue
        elif other.scheduled_time:
            return True
        else:
            return (self.priority, self.created_at) < (other.priority, other.created_at)


@dataclass
class WorkerStats:
    worker_id: str
    jobs_processed: int = 0
    jobs_failed: int = 0
    total_execution_time: float = 0.0
    current_job: Optional[str] = None
    last_activity: Optional[datetime] = None


@dataclass
class QueueStats:
    pending_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_jobs: int = 0
    average_execution_time: float = 0.0
    queue_depth_by_priority: Dict[int, int] = field(default_factory=dict)


class JobQueue:
    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize job queue.
        
        Args:
            max_size: Maximum queue size (None = unlimited)
        """
        pass  # TODO: Implement
    
    def submit(self, func: Callable, *args, priority: int = 0, 
               scheduled_time: Optional[datetime] = None,
               retry_config: Optional[RetryConfig] = None, **kwargs) -> str:
        """
        Submit a job to the queue.
        
        Args:
            func: Function to execute
            *args: Function arguments
            priority: Job priority (lower = higher priority)
            scheduled_time: When to execute (None = immediate)
            retry_config: Retry configuration
            **kwargs: Function keyword arguments
            
        Returns:
            Job ID
        """
        pass  # TODO: Implement
    
    def submit_batch(self, jobs: List[tuple]) -> List[str]:
        """Submit multiple jobs in a batch."""
        pass  # TODO: Implement
    
    def get_next_job(self) -> Optional[Job]:
        """Get next job to execute (considering schedule and priority)."""
        pass  # TODO: Implement
    
    def complete_job(self, job_id: str, result: JobResult) -> None:
        """Mark job as completed with result."""
        pass  # TODO: Implement
    
    def fail_job(self, job_id: str, error: str) -> None:
        """Mark job as failed and handle retry logic."""
        pass  # TODO: Implement
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        pass  # TODO: Implement
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        pass  # TODO: Implement
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with given status."""
        pass  # TODO: Implement
    
    def get_stats(self) -> QueueStats:
        """Get queue statistics."""
        pass  # TODO: Implement
    
    def size(self) -> int:
        """Get current queue size."""
        pass  # TODO: Implement
    
    def is_full(self) -> bool:
        """Check if queue is at capacity."""
        pass  # TODO: Implement
    
    def cleanup_completed_jobs(self, older_than: timedelta) -> int:
        """Remove completed jobs older than specified time."""
        pass  # TODO: Implement


class Worker:
    def __init__(self, worker_id: str, job_queue: JobQueue):
        """
        Initialize worker.
        
        Args:
            worker_id: Unique worker identifier
            job_queue: Job queue to process
        """
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start worker thread."""
        pass  # TODO: Implement
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop worker gracefully."""
        pass  # TODO: Implement
    
    def is_running(self) -> bool:
        """Check if worker is running."""
        pass  # TODO: Implement
    
    def get_stats(self) -> WorkerStats:
        """Get worker statistics."""
        pass  # TODO: Implement
    
    def _run(self) -> None:
        """Main worker loop."""
        pass  # TODO: Implement
    
    def _execute_job(self, job: Job) -> JobResult:
        """Execute a single job."""
        pass  # TODO: Implement
    
    def _calculate_retry_delay(self, job: Job) -> float:
        """Calculate delay before retry based on strategy."""
        pass  # TODO: Implement


class WorkerPool:
    def __init__(self, job_queue: JobQueue, num_workers: int = 4, 
                 worker_timeout: float = 300.0):
        """
        Initialize worker pool.
        
        Args:
            job_queue: Job queue to process
            num_workers: Number of worker threads
            worker_timeout: Timeout for worker operations
        """
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start all workers."""
        pass  # TODO: Implement
    
    def stop(self, timeout: float = 10.0) -> None:
        """Stop all workers gracefully."""
        pass  # TODO: Implement
    
    def scale(self, new_size: int) -> None:
        """Scale worker pool to new size."""
        pass  # TODO: Implement
    
    def get_worker_stats(self) -> List[WorkerStats]:
        """Get statistics for all workers."""
        pass  # TODO: Implement
    
    def get_healthy_workers(self) -> int:
        """Get count of healthy/active workers."""
        pass  # TODO: Implement
    
    def restart_failed_workers(self) -> int:
        """Restart any failed workers."""
        pass  # TODO: Implement


class JobScheduler:
    """Handles scheduling of delayed jobs"""
    
    def __init__(self, job_queue: JobQueue):
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start scheduler thread."""
        pass  # TODO: Implement
    
    def stop(self) -> None:
        """Stop scheduler."""
        pass  # TODO: Implement
    
    def schedule_job(self, job: Job) -> None:
        """Add job to schedule."""
        pass  # TODO: Implement
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        pass  # TODO: Implement


class JobPersistence(ABC):
    """Abstract interface for job persistence"""
    
    @abstractmethod
    def save_job(self, job: Job) -> None:
        pass
    
    @abstractmethod
    def load_jobs(self) -> List[Job]:
        pass
    
    @abstractmethod
    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        pass
    
    @abstractmethod
    def delete_job(self, job_id: str) -> None:
        pass


class InMemoryPersistence(JobPersistence):
    """Simple in-memory persistence for testing"""
    
    def __init__(self):
        pass  # TODO: Implement
    
    def save_job(self, job: Job) -> None:
        pass  # TODO: Implement
    
    def load_jobs(self) -> List[Job]:
        pass  # TODO: Implement
    
    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        pass  # TODO: Implement
    
    def delete_job(self, job_id: str) -> None:
        pass  # TODO: Implement


class FileSystemPersistence(JobPersistence):
    """File-based persistence"""
    
    def __init__(self, storage_dir: str):
        pass  # TODO: Implement
    
    def save_job(self, job: Job) -> None:
        pass  # TODO: Implement
    
    def load_jobs(self) -> List[Job]:
        pass  # TODO: Implement
    
    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        pass  # TODO: Implement
    
    def delete_job(self, job_id: str) -> None:
        pass  # TODO: Implement


class JobProcessingSystem:
    """Complete job processing system"""
    
    def __init__(self, num_workers: int = 4, max_queue_size: Optional[int] = None,
                 persistence: Optional[JobPersistence] = None):
        """
        Initialize job processing system.
        
        Args:
            num_workers: Number of worker threads
            max_queue_size: Maximum queue size
            persistence: Job persistence layer
        """
        pass  # TODO: Implement
    
    def start(self) -> None:
        """Start the entire system."""
        pass  # TODO: Implement
    
    def stop(self, timeout: float = 30.0) -> None:
        """Stop the system gracefully."""
        pass  # TODO: Implement
    
    def submit_job(self, func: Callable, *args, **kwargs) -> str:
        """Submit a job (convenience method)."""
        pass  # TODO: Implement
    
    def submit_delayed_job(self, func: Callable, delay: timedelta, 
                          *args, **kwargs) -> str:
        """Submit a delayed job."""
        pass  # TODO: Implement
    
    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get status of a job."""
        pass  # TODO: Implement
    
    def wait_for_job(self, job_id: str, timeout: Optional[float] = None) -> JobResult:
        """Wait for job completion and return result."""
        pass  # TODO: Implement
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        pass  # TODO: Implement
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        pass  # TODO: Implement


# Utility functions and decorators
def job_task(priority: int = 0, retry_config: Optional[RetryConfig] = None):
    """Decorator to mark functions as job tasks"""
    def decorator(func):
        func._job_priority = priority
        func._job_retry_config = retry_config
        return func
    return decorator


def create_cron_job(func: Callable, cron_expression: str, *args, **kwargs):
    """Create a cron-style recurring job (bonus implementation)"""
    pass  # TODO: Implement


# Example usage patterns
def example_basic_job_processing():
    """Example of basic job processing"""
    pass  # TODO: Implement


def example_priority_jobs():
    """Example with priority jobs"""
    pass  # TODO: Implement


def example_retry_strategies():
    """Example showing different retry strategies"""
    pass  # TODO: Implement


def example_scheduled_jobs():
    """Example of job scheduling"""
    pass  # TODO: Implement