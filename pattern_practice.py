#!/usr/bin/env python3
"""
Backend Pattern Practice - Real-World Coding Challenges
=====================================================

This module contains hands-on coding challenges that simulate real backend scenarios.
Problems are adapted based on your skill level and interview requirements.
"""

import sys
import json
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class ChallengeLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    SENIOR = "senior"

@dataclass
class Challenge:
    id: str
    title: str
    description: str
    level: ChallengeLevel
    time_limit: int  # minutes
    test_cases: List[Dict]
    solution_template: str

class PatternPractice:
    def __init__(self):
        self.load_user_level()
        self.challenges = self.initialize_challenges()
        
    def load_user_level(self):
        """Load user's skill level from assessment"""
        try:
            with open("progress.json", "r") as f:
                progress = json.load(f)
                level_str = progress.get("current_level", "intermediate")
                self.user_level = ChallengeLevel(level_str)
        except:
            self.user_level = ChallengeLevel.INTERMEDIATE
            
    def initialize_challenges(self):
        """Initialize all coding challenges"""
        return {
            # API Design Challenges
            "api_design": Challenge(
                id="api_design",
                title="Design a Rate-Limited API Gateway",
                description="""
Design and implement an API Gateway that:
1. Routes requests to different backend services
2. Implements rate limiting per user/IP
3. Handles authentication and authorization
4. Logs all requests for monitoring
5. Implements circuit breaker pattern for resilience

Real-world context: You're building the main entry point for a microservices architecture.
Your solution should handle 10,000+ requests per second with proper error handling.
""",
                level=ChallengeLevel.SENIOR,
                time_limit=45,
                test_cases=[
                    {"input": "GET /api/users/123", "expected": "User data"},
                    {"input": "POST /api/orders", "expected": "Order created"},
                    {"input": "Rate limit exceeded", "expected": "429 Too Many Requests"}
                ],
                solution_template="""
class APIGateway:
    def __init__(self):
        # Initialize your gateway
        pass
        
    def route_request(self, request):
        # Implement request routing
        pass
        
    def apply_rate_limit(self, user_id, ip):
        # Implement rate limiting
        pass
        
    def authenticate(self, token):
        # Implement authentication
        pass
"""
            ),
            
            # Database Optimization Challenge
            "database_optimization": Challenge(
                id="database_optimization",
                title="Optimize Slow Database Queries",
                description="""
You inherit a system with these performance issues:
1. User feed query takes 15+ seconds with 1M+ posts
2. Search functionality times out frequently  
3. Analytics queries block normal operations
4. Database connections are exhausted during peak hours

Implement solutions for:
- Query optimization and indexing strategy
- Connection pooling and management
- Read replicas and query distribution
- Caching layer with cache invalidation
""",
                level=ChallengeLevel.INTERMEDIATE,
                time_limit=40,
                test_cases=[
                    {"query": "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", "expected": "< 100ms"},
                    {"query": "SEARCH posts content", "expected": "< 500ms"},
                    {"scenario": "1000 concurrent connections", "expected": "No connection errors"}
                ],
                solution_template="""
class DatabaseOptimizer:
    def __init__(self):
        # Initialize your optimizer
        pass
        
    def optimize_feed_query(self, user_id):
        # Optimize the slow feed query
        pass
        
    def implement_search(self, query):
        # Implement fast search
        pass
        
    def setup_connection_pool(self):
        # Configure connection pooling
        pass
"""
            ),
            
            # Async Processing Challenge  
            "async_processing": Challenge(
                id="async_processing",
                title="Build Async Task Processing System",
                description="""
Build a robust async task processing system for:
1. Email notifications (low priority, high volume)
2. Image processing (CPU intensive)
3. Payment processing (high priority, requires reliability)
4. Data ETL jobs (scheduled, long-running)

Requirements:
- Priority queues with different processing strategies
- Retry mechanism with exponential backoff
- Dead letter queue for failed tasks
- Health monitoring and alerting
- Graceful shutdown handling
""",
                level=ChallengeLevel.INTERMEDIATE,
                time_limit=50,
                test_cases=[
                    {"task": "send_email", "priority": "low", "expected": "Queued successfully"},
                    {"task": "process_payment", "priority": "high", "expected": "Processed immediately"},
                    {"scenario": "Worker failure", "expected": "Task retried with backoff"}
                ],
                solution_template="""
import asyncio
from asyncio import Queue
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class TaskProcessor:
    def __init__(self):
        # Initialize your task processor
        pass
        
    async def submit_task(self, task, priority=Priority.MEDIUM):
        # Submit task to appropriate queue
        pass
        
    async def process_tasks(self):
        # Main processing loop
        pass
        
    async def retry_failed_task(self, task, attempt):
        # Implement retry logic
        pass
"""
            ),
            
            # System Design Challenge
            "system_design": Challenge(
                id="system_design",
                title="Design a Distributed Cache System",
                description="""
Design a distributed caching system similar to Redis Cluster:
1. Consistent hashing for data distribution
2. Replication for fault tolerance
3. Automatic failover and recovery
4. Memory management and eviction policies
5. Client-side sharding and load balancing

Handle edge cases:
- Node failures and network partitions
- Cache warming strategies
- Data consistency vs availability tradeoffs
""",
                level=ChallengeLevel.SENIOR,
                time_limit=60,
                test_cases=[
                    {"operation": "SET key1 value1", "expected": "OK"},
                    {"operation": "GET key1", "expected": "value1"},
                    {"scenario": "Node failure", "expected": "Automatic failover"},
                    {"scenario": "Memory full", "expected": "LRU eviction"}
                ],
                solution_template="""
import hashlib
from typing import Dict, List, Optional

class CacheNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data = {}
        self.is_healthy = True
        
class DistributedCache:
    def __init__(self, nodes: List[str]):
        # Initialize your cache cluster
        pass
        
    def get_node_for_key(self, key: str) -> CacheNode:
        # Implement consistent hashing
        pass
        
    def set(self, key: str, value: str) -> bool:
        # Implement distributed set
        pass
        
    def get(self, key: str) -> Optional[str]:
        # Implement distributed get
        pass
"""
            )
        }
        
    def show_available_challenges(self):
        """Show challenges appropriate for user's level"""
        print(f"🎯 CHALLENGES FOR {self.user_level.value.upper()} LEVEL")
        print("=" * 50)
        
        suitable_challenges = [
            c for c in self.challenges.values() 
            if c.level.value == self.user_level.value or 
               (self.user_level == ChallengeLevel.SENIOR and c.level == ChallengeLevel.INTERMEDIATE)
        ]
        
        for i, challenge in enumerate(suitable_challenges, 1):
            difficulty = "🔥" if challenge.level == ChallengeLevel.SENIOR else "⚡" if challenge.level == ChallengeLevel.INTERMEDIATE else "⭐"
            print(f"{i}. {difficulty} {challenge.title}")
            print(f"   Time Limit: {challenge.time_limit} minutes")
            print(f"   Level: {challenge.level.value.title()}")
            print()
            
        return suitable_challenges
        
    def start_challenge(self, challenge_id: str):
        """Start a specific challenge"""
        if challenge_id not in self.challenges:
            print(f"❌ Challenge {challenge_id} not found!")
            return
            
        challenge = self.challenges[challenge_id]
        
        print(f"🚀 STARTING: {challenge.title}")
        print("=" * 60)
        print(challenge.description)
        print(f"\n⏱️  Time Limit: {challenge.time_limit} minutes")
        print(f"📊 Difficulty: {challenge.level.value.title()}")
        
        # Show solution template
        print("\n📝 SOLUTION TEMPLATE:")
        print("-" * 30)
        print(challenge.solution_template)
        
        # Show test cases
        print("\n🧪 TEST CASES:")
        print("-" * 30)
        for i, test_case in enumerate(challenge.test_cases, 1):
            print(f"Test {i}: {test_case}")
            
        print(f"\n🎯 Ready to code? You have {challenge.time_limit} minutes!")
        
        # Start timing
        start_time = time.time()
        
        print("\nEnter your solution (type 'SUBMIT' on a new line to finish):")
        solution_lines = []
        while True:
            line = input()
            if line.strip() == 'SUBMIT':
                break
            solution_lines.append(line)
            
        solution = '\n'.join(solution_lines)
        elapsed_time = (time.time() - start_time) / 60  # minutes
        
        # Evaluate solution
        self.evaluate_solution(challenge, solution, elapsed_time)
        
    def evaluate_solution(self, challenge: Challenge, solution: str, elapsed_time: float):
        """Evaluate the submitted solution"""
        print(f"\n📊 EVALUATION RESULTS")
        print("=" * 30)
        
        score = 0
        max_score = 10
        
        # Time evaluation
        if elapsed_time <= challenge.time_limit:
            time_score = max(0, 3 - (elapsed_time / challenge.time_limit))
            score += time_score
            print(f"⏱️  Time: {elapsed_time:.1f}/{challenge.time_limit} min ({time_score:.1f}/3 points)")
        else:
            print(f"⏱️  Time: {elapsed_time:.1f}/{challenge.time_limit} min (0/3 points - overtime)")
            
        # Code quality evaluation
        quality_score = self.evaluate_code_quality(solution)
        score += quality_score
        print(f"📝 Code Quality: {quality_score:.1f}/4 points")
        
        # Architecture evaluation
        arch_score = self.evaluate_architecture(challenge, solution)
        score += arch_score
        print(f"🏗️  Architecture: {arch_score:.1f}/3 points")
        
        print(f"\n🎯 Total Score: {score:.1f}/{max_score}")
        
        # Provide feedback
        self.provide_feedback(challenge, solution, score)
        
        # Save progress
        self.save_challenge_progress(challenge.id, score, elapsed_time)
        
    def evaluate_code_quality(self, solution: str) -> float:
        """Evaluate code quality aspects"""
        score = 0
        
        # Check for proper class structure
        if 'class ' in solution:
            score += 1
            
        # Check for error handling
        if 'try:' in solution or 'except' in solution:
            score += 1
            
        # Check for type hints
        if ':' in solution and '->' in solution:
            score += 1
            
        # Check for proper methods
        if 'def ' in solution:
            score += 1
            
        return score
        
    def evaluate_architecture(self, challenge: Challenge, solution: str) -> float:
        """Evaluate architectural considerations"""
        score = 0
        
        # Challenge-specific evaluations
        if challenge.id == "api_design":
            if 'rate_limit' in solution.lower():
                score += 1
            if 'auth' in solution.lower():
                score += 1
            if 'circuit' in solution.lower() or 'breaker' in solution.lower():
                score += 1
                
        elif challenge.id == "database_optimization":
            if 'index' in solution.lower():
                score += 1
            if 'pool' in solution.lower():
                score += 1
            if 'cache' in solution.lower():
                score += 1
                
        elif challenge.id == "async_processing":
            if 'asyncio' in solution:
                score += 1
            if 'Queue' in solution:
                score += 1
            if 'retry' in solution.lower():
                score += 1
                
        return score
        
    def provide_feedback(self, challenge: Challenge, solution: str, score: float):
        """Provide detailed feedback on the solution"""
        print(f"\n💡 FEEDBACK & IMPROVEMENT SUGGESTIONS")
        print("-" * 40)
        
        if score >= 8:
            print("🎉 Excellent work! Your solution demonstrates senior-level thinking.")
            print("Consider these advanced optimizations:")
        elif score >= 6:
            print("👍 Good solution! You're on the right track.")
            print("Areas for improvement:")
        else:
            print("📚 Keep practicing! Here are key areas to focus on:")
            
        # Challenge-specific feedback
        if challenge.id == "api_design":
            self.provide_api_design_feedback(solution)
        elif challenge.id == "database_optimization":
            self.provide_database_feedback(solution)
        elif challenge.id == "async_processing":
            self.provide_async_feedback(solution)
            
    def provide_api_design_feedback(self, solution: str):
        """Provide API design specific feedback"""
        if 'rate_limit' not in solution.lower():
            print("• Add rate limiting to prevent abuse")
        if 'auth' not in solution.lower():
            print("• Implement proper authentication/authorization")
        if 'log' not in solution.lower():
            print("• Add comprehensive logging for monitoring")
        if 'circuit' not in solution.lower():
            print("• Consider circuit breaker pattern for resilience")
            
    def provide_database_feedback(self, solution: str):
        """Provide database optimization feedback"""
        if 'index' not in solution.lower():
            print("• Consider database indexing strategies")
        if 'pool' not in solution.lower():
            print("• Implement connection pooling")
        if 'cache' not in solution.lower():
            print("• Add caching layer for frequently accessed data")
            
    def provide_async_feedback(self, solution: str):
        """Provide async processing feedback"""
        if 'asyncio' not in solution:
            print("• Use asyncio for better concurrency")
        if 'retry' not in solution.lower():
            print("• Implement retry mechanism with exponential backoff")
        if 'queue' not in solution.lower():
            print("• Use priority queues for task management")
            
    def save_challenge_progress(self, challenge_id: str, score: float, time_taken: float):
        """Save challenge progress to file"""
        try:
            with open("progress.json", "r") as f:
                progress = json.load(f)
        except FileNotFoundError:
            progress = {"completed_challenges": []}
            
        if "completed_challenges" not in progress:
            progress["completed_challenges"] = []
            
        challenge_result = {
            "challenge_id": challenge_id,
            "score": score,
            "time_taken": time_taken,
            "completed_at": datetime.now().isoformat()
        }
        
        progress["completed_challenges"].append(challenge_result)
        
        with open("progress.json", "w") as f:
            json.dump(progress, f, indent=2)
            
        print(f"✅ Progress saved! Challenge '{challenge_id}' completed with score {score:.1f}/10")

def main():
    practice = PatternPractice()
    
    if len(sys.argv) < 2:
        print("Available commands:")
        print("  --challenge <challenge_id>  Start specific challenge")
        print("  --list                      List available challenges") 
        print("  --level <level>             Set difficulty level")
        return
        
    command = sys.argv[1]
    
    if command == "--list":
        practice.show_available_challenges()
    elif command == "--challenge" and len(sys.argv) > 2:
        challenge_id = sys.argv[2]
        practice.start_challenge(challenge_id)
    elif command == "--level" and len(sys.argv) > 2:
        level = sys.argv[2]
        print(f"Setting level to: {level}")
        # Update user level logic here
    else:
        suitable_challenges = practice.show_available_challenges()
        print("Enter the number of the challenge you want to attempt:")
        try:
            choice = int(input()) - 1
            if 0 <= choice < len(suitable_challenges):
                challenge = suitable_challenges[choice]
                practice.start_challenge(challenge.id)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")

if __name__ == "__main__":
    main()