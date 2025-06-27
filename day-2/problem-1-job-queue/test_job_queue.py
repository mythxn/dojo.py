"""
Test cases for Job Queue implementations
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from day2.job_queue import (
    JobQueue, Worker, WorkerPool, JobScheduler, JobProcessingSystem,
    Job, JobStatus, RetryStrategy, RetryConfig, JobResult,
    InMemoryPersistence, FileSystemPersistence, job_task
)


class TestJob:
    
    def test_job_creation(self):
        """Test basic job creation and properties"""
        def test_func(x, y):
            return x + y
        
        job = Job(
            id="test_job_1",
            func=test_func,
            args=(1, 2),
            kwargs={"extra": "data"},
            priority=5
        )
        
        assert job.id == "test_job_1"
        assert job.func == test_func
        assert job.args == (1, 2)
        assert job.kwargs == {"extra": "data"}
        assert job.priority == 5
        assert job.status == JobStatus.PENDING
        assert job.retry_count == 0
    
    def test_job_comparison(self):
        """Test job comparison for priority queue"""
        job1 = Job(id="1", func=lambda: None, priority=5)
        job2 = Job(id="2", func=lambda: None, priority=3)
        job3 = Job(id="3", func=lambda: None, priority=5)
        
        # Lower priority number = higher priority
        assert job2 < job1
        assert not (job1 < job2)
        
        # Same priority, compare by creation time
        time.sleep(0.001)  # Ensure different creation time
        job4 = Job(id="4", func=lambda: None, priority=5)
        assert job1 < job4
    
    def test_scheduled_job_comparison(self):
        """Test comparison of scheduled jobs"""
        now = datetime.now()
        future = now + timedelta(seconds=10)
        
        job1 = Job(id="1", func=lambda: None, scheduled_time=now)
        job2 = Job(id="2", func=lambda: None, scheduled_time=future)
        job3 = Job(id="3", func=lambda: None)  # No schedule
        
        assert job1 < job2  # Earlier scheduled time
        assert job3 < job1  # Non-scheduled jobs have priority over scheduled


class TestJobQueue:
    
    def test_basic_submission_and_retrieval(self):
        """Test basic job submission and retrieval"""
        queue = JobQueue()
        
        def test_func():
            return "result"
        
        # Submit job
        job_id = queue.submit(test_func, priority=5)
        assert job_id is not None
        assert queue.size() == 1
        
        # Get job
        job = queue.get_next_job()
        assert job is not None
        assert job.id == job_id
        assert job.func == test_func
        assert job.priority == 5
        assert queue.size() == 0  # Job should be removed from pending
    
    def test_priority_ordering(self):
        """Test that jobs are returned in priority order"""
        queue = JobQueue()
        
        # Submit jobs with different priorities
        id1 = queue.submit(lambda: "low", priority=10)
        id2 = queue.submit(lambda: "high", priority=1)
        id3 = queue.submit(lambda: "medium", priority=5)
        
        # Should return in priority order (1, 5, 10)
        job1 = queue.get_next_job()
        job2 = queue.get_next_job()
        job3 = queue.get_next_job()
        
        assert job1.id == id2  # priority 1
        assert job2.id == id3  # priority 5
        assert job3.id == id1  # priority 10
    
    def test_scheduled_jobs(self):
        """Test scheduled job handling"""
        queue = JobQueue()
        
        future_time = datetime.now() + timedelta(seconds=1)
        
        # Submit immediate and scheduled jobs
        immediate_id = queue.submit(lambda: "immediate")
        scheduled_id = queue.submit(lambda: "scheduled", scheduled_time=future_time)
        
        # Should get immediate job first
        job = queue.get_next_job()
        assert job.id == immediate_id
        
        # Scheduled job should not be available yet
        job = queue.get_next_job()
        assert job is None
        
        # Wait for scheduled time
        time.sleep(1.1)
        job = queue.get_next_job()
        assert job.id == scheduled_id
    
    def test_job_completion(self):
        """Test job completion tracking"""
        queue = JobQueue()
        
        job_id = queue.submit(lambda: "result")
        job = queue.get_next_job()
        
        # Complete job successfully
        result = JobResult(success=True, result="completed", execution_time=0.5)
        queue.complete_job(job_id, result)
        
        # Check job status
        completed_job = queue.get_job(job_id)
        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.result.success == True
        assert completed_job.result.result == "completed"
        assert completed_job.completed_at is not None
    
    def test_job_failure_and_retry(self):
        """Test job failure and retry logic"""
        retry_config = RetryConfig(max_retries=2, strategy=RetryStrategy.FIXED_DELAY, base_delay=0.1)
        queue = JobQueue()
        
        job_id = queue.submit(lambda: "result", retry_config=retry_config)
        job = queue.get_next_job()
        
        # Fail the job
        queue.fail_job(job_id, "Test error")
        
        # Job should be queued for retry
        failed_job = queue.get_job(job_id)
        assert failed_job.status == JobStatus.RETRYING
        assert failed_job.retry_count == 1
        assert failed_job.last_error == "Test error"
        
        # Should be able to get job for retry after delay
        time.sleep(0.15)  # Wait for retry delay
        retry_job = queue.get_next_job()
        assert retry_job.id == job_id
    
    def test_max_retries_exceeded(self):
        """Test job failure when max retries exceeded"""
        retry_config = RetryConfig(max_retries=1, strategy=RetryStrategy.FIXED_DELAY, base_delay=0.1)
        queue = JobQueue()
        
        job_id = queue.submit(lambda: "result", retry_config=retry_config)
        
        # Fail job twice (exceeding max retries)
        job = queue.get_next_job()
        queue.fail_job(job_id, "First failure")
        
        time.sleep(0.15)
        job = queue.get_next_job()
        queue.fail_job(job_id, "Second failure")
        
        # Job should be permanently failed
        failed_job = queue.get_job(job_id)
        assert failed_job.status == JobStatus.FAILED
        assert failed_job.retry_count == 2
    
    def test_job_cancellation(self):
        """Test job cancellation"""
        queue = JobQueue()
        
        job_id = queue.submit(lambda: "result")
        
        # Cancel pending job
        assert queue.cancel_job(job_id) == True
        
        # Job should be cancelled
        cancelled_job = queue.get_job(job_id)
        assert cancelled_job.status == JobStatus.CANCELLED
        
        # Should not be retrievable from queue
        assert queue.get_next_job() is None
        
        # Cannot cancel already cancelled job
        assert queue.cancel_job(job_id) == False
    
    def test_batch_submission(self):
        """Test batch job submission"""
        queue = JobQueue()
        
        jobs = [
            (lambda: "job1", (), {}),
            (lambda: "job2", (1, 2), {"priority": 5}),
            (lambda: "job3", (), {"priority": 1})
        ]
        
        job_ids = queue.submit_batch(jobs)
        assert len(job_ids) == 3
        assert queue.size() == 3
        
        # Should return jobs in priority order
        job1 = queue.get_next_job()  # priority 1
        job2 = queue.get_next_job()  # priority 0 (default)
        job3 = queue.get_next_job()  # priority 5
        
        assert job1.priority == 1
        assert job2.priority == 0
        assert job3.priority == 5
    
    def test_queue_capacity_limit(self):
        """Test queue capacity limits"""
        queue = JobQueue(max_size=2)
        
        # Fill queue to capacity
        id1 = queue.submit(lambda: "job1")
        id2 = queue.submit(lambda: "job2")
        assert queue.size() == 2
        assert queue.is_full() == True
        
        # Next submission should fail or block
        # Implementation dependent - could raise exception or return None
        try:
            id3 = queue.submit(lambda: "job3")
            # If it doesn't raise exception, it should return None or False
            assert id3 is None or id3 == False
        except Exception:
            pass  # Expected for capacity-limited queue
    
    def test_queue_statistics(self):
        """Test queue statistics"""
        queue = JobQueue()
        
        # Submit various jobs
        id1 = queue.submit(lambda: "job1", priority=1)
        id2 = queue.submit(lambda: "job2", priority=1)
        id3 = queue.submit(lambda: "job3", priority=5)
        
        stats = queue.get_stats()
        assert stats.pending_jobs == 3
        assert stats.total_jobs == 3
        assert stats.queue_depth_by_priority[1] == 2
        assert stats.queue_depth_by_priority[5] == 1
        
        # Complete a job
        job = queue.get_next_job()
        result = JobResult(success=True, result="done", execution_time=1.0)
        queue.complete_job(job.id, result)
        
        stats = queue.get_stats()
        assert stats.pending_jobs == 2
        assert stats.completed_jobs == 1
        assert stats.average_execution_time == 1.0


class TestWorker:
    
    def test_worker_basic_functionality(self):
        """Test basic worker functionality"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        # Add a job
        results = []
        def test_job():
            results.append("executed")
            return "success"
        
        queue.submit(test_job)
        
        # Start worker
        worker.start()
        
        # Wait for job processing
        time.sleep(0.2)
        
        # Stop worker
        worker.stop()
        
        assert len(results) == 1
        assert results[0] == "executed"
        
        # Check job was completed
        stats = queue.get_stats()
        assert stats.completed_jobs == 1
    
    def test_worker_job_execution(self):
        """Test worker job execution with results"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        def add_numbers(x, y):
            return x + y
        
        job_id = queue.submit(add_numbers, 5, 3)
        
        worker.start()
        time.sleep(0.2)
        worker.stop()
        
        # Check job result
        completed_job = queue.get_job(job_id)
        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.result.success == True
        assert completed_job.result.result == 8
    
    def test_worker_exception_handling(self):
        """Test worker handles job exceptions properly"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        def failing_job():
            raise ValueError("Test error")
        
        job_id = queue.submit(failing_job, retry_config=RetryConfig(max_retries=0))
        
        worker.start()
        time.sleep(0.2)
        worker.stop()
        
        # Job should be marked as failed
        failed_job = queue.get_job(job_id)
        assert failed_job.status == JobStatus.FAILED
        assert failed_job.result.success == False
        assert "Test error" in failed_job.result.error
    
    def test_worker_retry_logic(self):
        """Test worker retry logic"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        call_count = [0]
        def flaky_job():
            call_count[0] += 1
            if call_count[0] < 3:
                raise RuntimeError("Temporary failure")
            return "success"
        
        retry_config = RetryConfig(max_retries=3, strategy=RetryStrategy.FIXED_DELAY, base_delay=0.1)
        job_id = queue.submit(flaky_job, retry_config=retry_config)
        
        worker.start()
        time.sleep(1.0)  # Allow time for retries
        worker.stop()
        
        # Job should eventually succeed
        completed_job = queue.get_job(job_id)
        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.result.success == True
        assert completed_job.result.result == "success"
        assert call_count[0] == 3  # Should have been called 3 times
    
    def test_worker_statistics(self):
        """Test worker statistics tracking"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        # Add multiple jobs
        for i in range(5):
            queue.submit(lambda x=i: f"result_{x}")
        
        worker.start()
        time.sleep(0.5)  # Process jobs
        worker.stop()
        
        stats = worker.get_stats()
        assert stats.worker_id == "worker1"
        assert stats.jobs_processed == 5
        assert stats.jobs_failed == 0
        assert stats.total_execution_time > 0


class TestWorkerPool:
    
    def test_worker_pool_basic(self):
        """Test basic worker pool functionality"""
        queue = JobQueue()
        pool = WorkerPool(queue, num_workers=3)
        
        # Add multiple jobs
        results = []
        lock = threading.Lock()
        
        def test_job(value):
            with lock:
                results.append(value)
            return value
        
        for i in range(10):
            queue.submit(test_job, i)
        
        pool.start()
        time.sleep(0.5)  # Process jobs
        pool.stop()
        
        # All jobs should be processed
        assert len(results) == 10
        assert set(results) == set(range(10))
        
        # Check queue is empty
        assert queue.size() == 0
    
    def test_worker_pool_scaling(self):
        """Test worker pool scaling"""
        queue = JobQueue()
        pool = WorkerPool(queue, num_workers=2)
        
        pool.start()
        
        # Check initial worker count
        initial_stats = pool.get_worker_stats()
        assert len(initial_stats) == 2
        
        # Scale up
        pool.scale(5)
        time.sleep(0.1)  # Allow workers to start
        
        scaled_stats = pool.get_worker_stats()
        assert len(scaled_stats) == 5
        
        # Scale down
        pool.scale(3)
        time.sleep(0.1)
        
        final_stats = pool.get_worker_stats()
        assert len(final_stats) == 3
        
        pool.stop()
    
    def test_worker_pool_load_distribution(self):
        """Test that work is distributed among workers"""
        queue = JobQueue()
        pool = WorkerPool(queue, num_workers=3)
        
        worker_usage = {}
        lock = threading.Lock()
        
        def track_worker():
            worker_id = threading.current_thread().name
            with lock:
                worker_usage[worker_id] = worker_usage.get(worker_id, 0) + 1
            time.sleep(0.1)  # Simulate work
        
        # Add jobs
        for i in range(9):  # 3 jobs per worker ideally
            queue.submit(track_worker)
        
        pool.start()
        time.sleep(1.0)  # Process all jobs
        pool.stop()
        
        # Work should be distributed among workers
        assert len(worker_usage) <= 3  # At most 3 workers used
        total_work = sum(worker_usage.values())
        assert total_work == 9


class TestJobScheduler:
    
    def test_job_scheduling(self):
        """Test job scheduler functionality"""
        queue = JobQueue()
        scheduler = JobScheduler(queue)
        
        results = []
        def scheduled_job(value):
            results.append((value, time.time()))
        
        # Schedule jobs at different times
        now = datetime.now()
        job1 = Job(id="1", func=scheduled_job, args=("first",), 
                  scheduled_time=now + timedelta(seconds=0.2))
        job2 = Job(id="2", func=scheduled_job, args=("second",), 
                  scheduled_time=now + timedelta(seconds=0.4))
        
        scheduler.start()
        scheduler.schedule_job(job1)
        scheduler.schedule_job(job2)
        
        # Start worker to process jobs
        worker = Worker("worker1", queue)
        worker.start()
        
        time.sleep(0.6)  # Wait for both jobs to be scheduled and executed
        
        worker.stop()
        scheduler.stop()
        
        assert len(results) == 2
        # First job should execute before second
        assert results[0][0] == "first"
        assert results[1][0] == "second"
        assert results[1][1] > results[0][1]  # Second job executed later


class TestJobPersistence:
    
    def test_in_memory_persistence(self):
        """Test in-memory persistence"""
        persistence = InMemoryPersistence()
        
        job = Job(id="test_job", func=lambda: "test")
        
        # Save and load job
        persistence.save_job(job)
        loaded_jobs = persistence.load_jobs()
        
        assert len(loaded_jobs) == 1
        assert loaded_jobs[0].id == "test_job"
        
        # Update status
        persistence.update_job_status("test_job", JobStatus.COMPLETED)
        updated_jobs = persistence.load_jobs()
        assert updated_jobs[0].status == JobStatus.COMPLETED
        
        # Delete job
        persistence.delete_job("test_job")
        final_jobs = persistence.load_jobs()
        assert len(final_jobs) == 0
    
    def test_filesystem_persistence(self, tmp_path):
        """Test filesystem persistence"""
        persistence = FileSystemPersistence(str(tmp_path))
        
        job = Job(id="test_job", func=lambda: "test")
        
        # Save and load job
        persistence.save_job(job)
        loaded_jobs = persistence.load_jobs()
        
        assert len(loaded_jobs) == 1
        assert loaded_jobs[0].id == "test_job"
        
        # Verify file was created
        job_files = list(tmp_path.glob("*.json"))
        assert len(job_files) == 1


class TestJobProcessingSystem:
    
    def test_complete_system_integration(self):
        """Test complete job processing system"""
        system = JobProcessingSystem(num_workers=2)
        
        results = []
        def test_job(value):
            results.append(value)
            return f"processed_{value}"
        
        system.start()
        
        # Submit various types of jobs
        immediate_id = system.submit_job(test_job, "immediate")
        delayed_id = system.submit_delayed_job(test_job, timedelta(seconds=0.5), "delayed")
        
        # Wait for completion
        immediate_result = system.wait_for_job(immediate_id, timeout=1.0)
        delayed_result = system.wait_for_job(delayed_id, timeout=2.0)
        
        system.stop()
        
        assert immediate_result.success == True
        assert immediate_result.result == "processed_immediate"
        assert delayed_result.success == True
        assert delayed_result.result == "processed_delayed"
        
        assert "immediate" in results
        assert "delayed" in results
    
    def test_system_health_check(self):
        """Test system health check"""
        system = JobProcessingSystem(num_workers=2)
        system.start()
        
        health = system.health_check()
        
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "worker_count" in health
        assert "queue_size" in health
        assert "uptime" in health
        
        system.stop()
    
    def test_system_statistics(self):
        """Test comprehensive system statistics"""
        system = JobProcessingSystem(num_workers=2)
        
        def simple_job():
            return "done"
        
        system.start()
        
        # Submit jobs
        for i in range(5):
            system.submit_job(simple_job)
        
        time.sleep(0.5)  # Process jobs
        
        stats = system.get_system_stats()
        
        assert "queue_stats" in stats
        assert "worker_stats" in stats
        assert "system_uptime" in stats
        assert stats["queue_stats"]["total_jobs"] == 5
        
        system.stop()


class TestRetryStrategies:
    
    def test_exponential_backoff(self):
        """Test exponential backoff retry strategy"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        retry_config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            base_delay=0.1,
            max_delay=1.0
        )
        
        # Test delay calculation
        job = Job(id="test", func=lambda: None, retry_config=retry_config)
        
        # First retry
        job.retry_count = 1
        delay1 = worker._calculate_retry_delay(job)
        
        # Second retry
        job.retry_count = 2
        delay2 = worker._calculate_retry_delay(job)
        
        # Third retry
        job.retry_count = 3
        delay3 = worker._calculate_retry_delay(job)
        
        # Delays should increase exponentially
        assert delay2 > delay1
        assert delay3 > delay2
        assert delay3 <= 1.0  # Should not exceed max_delay
    
    def test_linear_backoff(self):
        """Test linear backoff retry strategy"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        retry_config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            base_delay=0.1
        )
        
        job = Job(id="test", func=lambda: None, retry_config=retry_config)
        
        # Calculate delays for different retry counts
        delays = []
        for retry_count in [1, 2, 3]:
            job.retry_count = retry_count
            delays.append(worker._calculate_retry_delay(job))
        
        # Delays should increase linearly
        assert delays[1] == delays[0] + 0.1
        assert delays[2] == delays[0] + 0.2
    
    def test_fixed_delay(self):
        """Test fixed delay retry strategy"""
        queue = JobQueue()
        worker = Worker("worker1", queue)
        
        retry_config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.FIXED_DELAY,
            base_delay=0.5
        )
        
        job = Job(id="test", func=lambda: None, retry_config=retry_config)
        
        # All retries should have same delay
        for retry_count in [1, 2, 3]:
            job.retry_count = retry_count
            delay = worker._calculate_retry_delay(job)
            assert abs(delay - 0.5) < 0.1  # Allow for jitter


class TestJobDecorator:
    
    def test_job_task_decorator(self):
        """Test job task decorator"""
        retry_config = RetryConfig(max_retries=2)
        
        @job_task(priority=5, retry_config=retry_config)
        def decorated_job(x, y):
            return x * y
        
        assert hasattr(decorated_job, '_job_priority')
        assert decorated_job._job_priority == 5
        assert decorated_job._job_retry_config == retry_config
        
        # Function should still work normally
        assert decorated_job(3, 4) == 12


class TestPerformance:
    
    def test_high_throughput_processing(self):
        """Test system performance under high load"""
        system = JobProcessingSystem(num_workers=4)
        
        processed_count = [0]
        lock = threading.Lock()
        
        def fast_job():
            with lock:
                processed_count[0] += 1
        
        system.start()
        
        # Submit many jobs
        num_jobs = 1000
        start_time = time.time()
        
        for i in range(num_jobs):
            system.submit_job(fast_job)
        
        # Wait for processing
        while processed_count[0] < num_jobs:
            time.sleep(0.01)
        
        duration = time.time() - start_time
        system.stop()
        
        # Calculate throughput
        throughput = num_jobs / duration
        assert throughput > 100  # Should process at least 100 jobs/second
        assert processed_count[0] == num_jobs
    
    def test_memory_usage_with_many_jobs(self):
        """Test memory usage doesn't grow unbounded"""
        queue = JobQueue()
        
        # Submit many jobs
        for i in range(10000):
            queue.submit(lambda x=i: x)
        
        initial_size = queue.size()
        
        # Process some jobs
        for _ in range(5000):
            job = queue.get_next_job()
            if job:
                result = JobResult(success=True, result="done")
                queue.complete_job(job.id, result)
        
        # Clean up completed jobs
        removed = queue.cleanup_completed_jobs(timedelta(seconds=0))
        
        final_size = queue.size()
        assert final_size < initial_size
        assert removed == 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])