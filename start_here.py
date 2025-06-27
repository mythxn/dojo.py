#!/usr/bin/env python3
"""
Senior Backend Engineer Interview Prep - Start Here
=================================================

This is your 3-day intensive Python backend interview preparation track.
Real-world problems, no leetcode - just like your actual interview!
"""

import os
import sys
from datetime import datetime, timedelta
import json
from pathlib import Path

class InterviewPrepTrack:
    def __init__(self):
        self.progress_file = "progress.json"
        self.challenges_dir = Path("challenges")
        self.challenges_dir.mkdir(exist_ok=True)
        self.load_progress()
        
    def load_progress(self):
        """Load existing progress or create new"""
        try:
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        except FileNotFoundError:
            self.progress = {
                "start_date": datetime.now().isoformat(),
                "current_day": 1,
                "completed_challenges": [],
                "skill_assessment": {},
                "interview_date": (datetime.now() + timedelta(days=3)).isoformat()
            }
            self.save_progress()
    
    def save_progress(self):
        """Save current progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def show_welcome(self):
        interview_date = datetime.fromisoformat(self.progress["interview_date"])
        days_left = (interview_date - datetime.now()).days
        
        print("🚀 SENIOR BACKEND ENGINEER INTERVIEW PREP")
        print("=" * 50)
        print(f"📅 Interview in: {days_left} days")
        print(f"📊 Current Day: {self.progress['current_day']}/3")
        print(f"✅ Completed: {len(self.progress['completed_challenges'])} challenges")
        print()
        
    def show_track_overview(self):
        print("📋 3-DAY TRACK OVERVIEW:")
        print()
        print("DAY 1: Python Fundamentals + System Design Basics")
        print("  • Python refresh (async, decorators, context managers)")
        print("  • API design and REST principles")
        print("  • Basic system architecture")
        print("  • Error handling and logging")
        print()
        print("DAY 2: Backend Patterns + Database Interactions")  
        print("  • Design patterns (Factory, Observer, Strategy)")
        print("  • Database operations and ORMs")
        print("  • Caching strategies")
        print("  • Message queues and async processing")
        print()
        print("DAY 3: Performance, Scaling & Integration")
        print("  • Performance optimization")
        print("  • Load balancing and scaling")
        print("  • Third-party integrations")
        print("  • Debugging production issues")
        print()
    
    def get_current_day_activities(self):
        current_day = self.progress["current_day"]
        
        activities = {
            1: [
                ("Python Fundamentals Assessment", "day1_python_fundamentals.py"),
                ("Build a REST API", "day1_rest_api.py"),
                ("System Design Discussion", "day1_system_design.py"),
                ("Error Handling Practice", "day1_error_handling.py")
            ],
            2: [
                ("Design Patterns Implementation", "day2_design_patterns.py"),
                ("Database Query Optimization", "day2_database.py"),
                ("Caching Layer Design", "day2_caching.py"),
                ("Async Task Processing", "day2_async.py")
            ],
            3: [
                ("Performance Profiling", "day3_performance.py"),
                ("Scaling Strategies", "day3_scaling.py"),
                ("Integration Testing", "day3_integration.py"),
                ("Mock Interview", "day3_mock_interview.py")
            ]
        }
        
        return activities.get(current_day, [])
    
    def show_daily_plan(self):
        print(f"📅 DAY {self.progress['current_day']} ACTIVITIES:")
        print("-" * 30)
        
        activities = self.get_current_day_activities()
        for i, (title, filename) in enumerate(activities, 1):
            status = "✅" if f"day{self.progress['current_day']}_activity{i}" in self.progress["completed_challenges"] else "⏳"
            file_path = self.challenges_dir / filename
            file_status = "📝" if file_path.exists() else "📄"
            print(f"{status} {i}. {title}")
            print(f"   File: {file_status} challenges/{filename}")
            print()
    
    def create_challenge_file(self, filename, challenge_content):
        """Create a challenge file with instructions and starter code"""
        file_path = self.challenges_dir / filename
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(challenge_content)
            print(f"📄 Created: challenges/{filename}")
        else:
            print(f"📝 File exists: challenges/{filename}")
        return file_path

    def start_activity(self):
        print("🎯 READY TO START?")
        print()
        print("Choose an option:")
        print("1. Create current day's challenge files")
        print("2. Create all challenge files")
        print("3. Jump to specific activity")
        print("4. View my progress")
        print("5. Validate my solutions")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            self.create_daily_challenges()
        elif choice == "2":
            self.create_all_challenges()
        elif choice == "3":
            self.jump_to_activity()
        elif choice == "4":
            self.show_detailed_progress()
        elif choice == "5":
            self.validate_solutions()
        else:
            print("Invalid choice. Run 'python start_here.py' again.")
    
    def get_challenge_templates(self):
        """Get all challenge templates organized by day"""
        return {
            1: {
                "day1_python_fundamentals.py": '''"""
Day 1 Challenge 1: Python Fundamentals Assessment
================================================

Test your Python skills with these core concepts.
Complete each function and run the file to test your solutions.

Topics: Functions, decorators, context managers, generators
"""

# Challenge 1: Decorator Implementation
def timing_decorator(func):
    """Create a decorator that measures and prints execution time"""
    # TODO: Implement timing decorator
    pass

@timing_decorator
def slow_function():
    import time
    time.sleep(0.1)
    return "completed"

# Challenge 2: Context Manager
class DatabaseConnection:
    """Implement a context manager for database connections"""
    
    def __init__(self, db_name):
        self.db_name = db_name
        # TODO: Implement __init__
    
    def __enter__(self):
        # TODO: Implement context manager entry
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Implement context manager exit
        pass

# Challenge 3: Generator Function
def fibonacci_generator(n):
    """Generate fibonacci sequence up to n numbers"""
    # TODO: Implement fibonacci generator
    pass

# Challenge 4: List Comprehension with Filtering
def process_data(data_list):
    """
    Filter and transform data:
    - Keep only positive numbers
    - Square each number
    - Return as list
    """
    # TODO: Implement using list comprehension
    pass

# Test your implementations
if __name__ == "__main__":
    print("Testing Python Fundamentals...")
    
    # Test 1: Decorator
    print("\\n1. Testing timing decorator:")
    result = slow_function()
    
    # Test 2: Context Manager
    print("\\n2. Testing context manager:")
    with DatabaseConnection("test_db") as db:
        print(f"Connected to {db.db_name if hasattr(db, 'db_name') else 'database'}")
    
    # Test 3: Generator
    print("\\n3. Testing fibonacci generator:")
    fib_gen = fibonacci_generator(8)
    fib_list = list(fib_gen)
    print(f"Fibonacci sequence: {fib_list}")
    
    # Test 4: List comprehension
    print("\\n4. Testing data processing:")
    test_data = [-2, -1, 0, 1, 2, 3, 4, 5]
    processed = process_data(test_data)
    print(f"Processed data: {processed}")
    
    print("\\n✅ All tests completed! Check your implementations.")
''',
                "day1_rest_api.py": '''"""
Day 1 Challenge 2: Build a REST API
==================================

Design and implement a basic REST API for a task management system.
Focus on proper HTTP methods, status codes, and data validation.

Requirements:
- CRUD operations for tasks
- Proper error handling
- Input validation
- RESTful routing
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

class Task:
    """Task model"""
    
    def __init__(self, title: str, description: str = "", priority: str = "medium"):
        # TODO: Implement task initialization
        pass
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        # TODO: Implement serialization
        pass
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary"""
        # TODO: Implement deserialization
        pass

class TaskAPI:
    """Simple in-memory task API"""
    
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1
    
    def create_task(self, data: Dict) -> Dict:
        """
        POST /tasks
        Create a new task
        Returns: {"task": task_dict, "status": 201} or {"error": str, "status": 400}
        """
        # TODO: Implement task creation with validation
        pass
    
    def get_task(self, task_id: int) -> Dict:
        """
        GET /tasks/{id}
        Get a specific task
        Returns: {"task": task_dict, "status": 200} or {"error": str, "status": 404}
        """
        # TODO: Implement task retrieval
        pass
    
    def get_all_tasks(self, priority_filter: Optional[str] = None) -> Dict:
        """
        GET /tasks?priority=high
        Get all tasks with optional filtering
        Returns: {"tasks": [task_dict], "status": 200}
        """
        # TODO: Implement task listing with filtering
        pass
    
    def update_task(self, task_id: int, data: Dict) -> Dict:
        """
        PUT /tasks/{id}
        Update an existing task
        Returns: {"task": task_dict, "status": 200} or {"error": str, "status": 404/400}
        """
        # TODO: Implement task update
        pass
    
    def delete_task(self, task_id: int) -> Dict:
        """
        DELETE /tasks/{id}
        Delete a task
        Returns: {"message": str, "status": 200} or {"error": str, "status": 404}
        """
        # TODO: Implement task deletion
        pass

def validate_task_data(data: Dict) -> Optional[str]:
    """Validate task data and return error message if invalid"""
    # TODO: Implement validation
    # Check required fields, data types, valid priority values
    pass

# Test your API implementation
if __name__ == "__main__":
    print("Testing Task API...")
    
    api = TaskAPI()
    
    # Test 1: Create tasks
    print("\\n1. Creating tasks:")
    result1 = api.create_task({"title": "Learn Python", "priority": "high"})
    print(f"Create result: {result1}")
    
    result2 = api.create_task({"title": "Build API", "description": "REST API practice"})
    print(f"Create result: {result2}")
    
    # Test 2: Get all tasks
    print("\\n2. Getting all tasks:")
    all_tasks = api.get_all_tasks()
    print(f"All tasks: {all_tasks}")
    
    # Test 3: Get specific task
    print("\\n3. Getting specific task:")
    task = api.get_task(1)
    print(f"Task 1: {task}")
    
    # Test 4: Update task
    print("\\n4. Updating task:")
    update_result = api.update_task(1, {"title": "Master Python", "completed": True})
    print(f"Update result: {update_result}")
    
    # Test 5: Filter tasks
    print("\\n5. Filtering by priority:")
    high_priority = api.get_all_tasks(priority_filter="high")
    print(f"High priority tasks: {high_priority}")
    
    # Test 6: Delete task
    print("\\n6. Deleting task:")
    delete_result = api.delete_task(2)
    print(f"Delete result: {delete_result}")
    
    print("\\n✅ API tests completed!")
'''
            },
            2: {
                "day2_design_patterns.py": '''"""
Day 2 Challenge 1: Design Patterns Implementation
================================================

Implement common design patterns used in backend development.
Focus on practical patterns that solve real-world problems.

Patterns to implement:
1. Factory Pattern - Create different types of database connections
2. Observer Pattern - Event system for user actions
3. Strategy Pattern - Different payment processing methods
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum

# === FACTORY PATTERN ===
class DatabaseType(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"

class DatabaseConnection(ABC):
    """Abstract base class for database connections"""
    
    @abstractmethod
    def connect(self) -> str:
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> str:
        pass

class MySQLConnection(DatabaseConnection):
    """MySQL database connection implementation"""
    
    def connect(self) -> str:
        # TODO: Implement MySQL connection
        pass
    
    def execute_query(self, query: str) -> str:
        # TODO: Implement MySQL query execution
        pass

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection implementation"""
    
    def connect(self) -> str:
        # TODO: Implement PostgreSQL connection
        pass
    
    def execute_query(self, query: str) -> str:
        # TODO: Implement PostgreSQL query execution
        pass

class MongoDBConnection(DatabaseConnection):
    """MongoDB database connection implementation"""
    
    def connect(self) -> str:
        # TODO: Implement MongoDB connection
        pass
    
    def execute_query(self, query: str) -> str:
        # TODO: Implement MongoDB query execution
        pass

class DatabaseFactory:
    """Factory for creating database connections"""
    
    @staticmethod
    def create_connection(db_type: DatabaseType, **kwargs) -> DatabaseConnection:
        """Create database connection based on type"""
        # TODO: Implement factory method
        pass

# === OBSERVER PATTERN ===
class Observer(ABC):
    """Abstract observer interface"""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        pass

class Subject(ABC):
    """Abstract subject interface"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        # TODO: Implement observer attachment
        pass
    
    def detach(self, observer: Observer) -> None:
        # TODO: Implement observer detachment
        pass
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        # TODO: Implement observer notification
        pass

class UserManager(Subject):
    """User management system that notifies observers"""
    
    def __init__(self):
        super().__init__()
        self.users = {}
    
    def register_user(self, user_id: str, email: str) -> None:
        """Register a new user and notify observers"""
        # TODO: Implement user registration with notification
        pass
    
    def login_user(self, user_id: str) -> None:
        """User login and notify observers"""
        # TODO: Implement user login with notification
        pass

class EmailNotifier(Observer):
    """Email notification observer"""
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        # TODO: Implement email notification logic
        pass

class AnalyticsTracker(Observer):
    """Analytics tracking observer"""
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        # TODO: Implement analytics tracking logic
        pass

# === STRATEGY PATTERN ===
class PaymentStrategy(ABC):
    """Abstract payment strategy"""
    
    @abstractmethod
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        pass

class CreditCardPayment(PaymentStrategy):
    """Credit card payment strategy"""
    
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        # TODO: Implement credit card payment processing
        pass

class PayPalPayment(PaymentStrategy):
    """PayPal payment strategy"""
    
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        # TODO: Implement PayPal payment processing
        pass

class BankTransferPayment(PaymentStrategy):
    """Bank transfer payment strategy"""
    
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        # TODO: Implement bank transfer processing
        pass

class PaymentProcessor:
    """Payment processor using strategy pattern"""
    
    def __init__(self, strategy: PaymentStrategy):
        # TODO: Initialize with payment strategy
        pass
    
    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """Change payment strategy"""
        # TODO: Implement strategy switching
        pass
    
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        """Process payment using current strategy"""
        # TODO: Implement payment processing
        pass

# Test your implementations
if __name__ == "__main__":
    print("Testing Design Patterns...")
    
    # Test Factory Pattern
    print("\\n=== Factory Pattern Test ===")
    mysql_conn = DatabaseFactory.create_connection(DatabaseType.MYSQL, host="localhost")
    print(f"MySQL: {mysql_conn.connect()}")
    
    # Test Observer Pattern
    print("\\n=== Observer Pattern Test ===")
    user_manager = UserManager()
    email_notifier = EmailNotifier()
    analytics = AnalyticsTracker()
    
    user_manager.attach(email_notifier)
    user_manager.attach(analytics)
    
    user_manager.register_user("user1", "user1@example.com")
    user_manager.login_user("user1")
    
    # Test Strategy Pattern
    print("\\n=== Strategy Pattern Test ===")
    processor = PaymentProcessor(CreditCardPayment())
    result1 = processor.process_payment(100.0, card_number="1234-5678-9012-3456")
    print(f"Credit card payment: {result1}")
    
    processor.set_strategy(PayPalPayment())
    result2 = processor.process_payment(50.0, email="user@example.com")
    print(f"PayPal payment: {result2}")
    
    print("\\n✅ Design patterns tests completed!")
'''
            }
        }
    
    def create_daily_challenges(self):
        """Create challenge files for current day"""
        current_day = self.progress["current_day"]
        templates = self.get_challenge_templates()
        
        if current_day in templates:
            print(f"\\n🎯 Creating Day {current_day} challenge files...")
            day_templates = templates[current_day]
            
            for filename, content in day_templates.items():
                self.create_challenge_file(filename, content)
            
            print(f"\\n✅ Day {current_day} challenges ready!")
            print("📂 Open the 'challenges' folder in your IDE to start coding.")
        else:
            print(f"No templates available for day {current_day}")
    
    def create_all_challenges(self):
        """Create all challenge files for all days"""
        print("\\n🎯 Creating all challenge files...")
        templates = self.get_challenge_templates()
        
        for day, day_templates in templates.items():
            print(f"\\nDay {day}:")
            for filename, content in day_templates.items():
                self.create_challenge_file(filename, content)
        
        print("\\n✅ All challenges created!")
        print("📂 Open the 'challenges' folder in your IDE to start coding.")
    
    def validate_solutions(self):
        """Run validation tests on solution files"""
        print("\\n🔍 Validating your solutions...")
        activities = self.get_current_day_activities()
        validated_count = 0
        
        for i, (title, filename) in enumerate(activities, 1):
            file_path = self.challenges_dir / filename
            if file_path.exists():
                print(f"\\n📝 Checking {filename}...")
                try:
                    # Basic validation - check if file can be imported/executed
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    if "TODO" in content:
                        print(f"⚠️  {filename}: Still has TODO items to complete")
                    elif "pass" in content and content.count("pass") > 2:
                        print(f"⏳ {filename}: Contains placeholder 'pass' statements")
                    else:
                        print(f"✅ {filename}: Looks complete!")
                        validated_count += 1
                        
                        # Mark as completed if validation passes
                        activity_id = f"day{self.progress['current_day']}_activity{i}"
                        if activity_id not in self.progress["completed_challenges"]:
                            self.progress["completed_challenges"].append(activity_id)
                            
                except Exception as e:
                    print(f"❌ {filename}: Error reading file - {e}")
            else:
                print(f"📄 {filename}: File not found")
        
        if validated_count > 0:
            self.save_progress()
            print(f"\\n🎉 Validated {validated_count} solutions!")
        
        print("\\n💡 Tip: Run your Python files individually to test your implementations!")

    def continue_track(self):
        activities = self.get_current_day_activities()
        for i, (title, command) in enumerate(activities, 1):
            activity_id = f"day{self.progress['current_day']}_activity{i}"
            if activity_id not in self.progress["completed_challenges"]:
                print(f"🎯 Continuing with: {title}")
                print(f"Running: {command}")
                os.system(command)
                break
        else:
            print("✅ All activities for today completed!")
            if self.progress["current_day"] < 3:
                self.progress["current_day"] += 1
                self.save_progress()
                print(f"🎉 Moving to Day {self.progress['current_day']}!")
    
    def jump_to_activity(self):
        print("📋 Available Activities:")
        for day in range(1, 4):
            print(f"\nDay {day}:")
            activities = {
                1: ["Python Assessment", "REST API", "System Design", "Error Handling"],
                2: ["Design Patterns", "Database", "Caching", "Async Tasks"],
                3: ["Performance", "Scaling", "Integration", "Mock Interview"]
            }
            for i, activity in enumerate(activities[day], 1):
                print(f"  {day}.{i} {activity}")
        
        choice = input("\nEnter activity (e.g., 1.2 for Day 1, Activity 2): ").strip()
        # Implementation for jumping to specific activity
        print(f"Jumping to activity {choice}...")
    
    def show_detailed_progress(self):
        print("📊 DETAILED PROGRESS REPORT")
        print("=" * 40)
        print(f"Started: {self.progress['start_date'][:10]}")
        print(f"Current Day: {self.progress['current_day']}")
        print(f"Completed Challenges: {len(self.progress['completed_challenges'])}")
        
        if self.progress.get("skill_assessment"):
            print("\n🎯 Skill Assessment Results:")
            for skill, score in self.progress["skill_assessment"].items():
                print(f"  {skill}: {score}/10")
        
        print(f"\n📅 Interview Date: {self.progress['interview_date'][:10]}")
        days_left = (datetime.fromisoformat(self.progress["interview_date"]) - datetime.now()).days
        print(f"⏰ Days Remaining: {days_left}")

def main():
    track = InterviewPrepTrack()
    track.show_welcome()
    track.show_track_overview()
    track.show_daily_plan()
    track.start_activity()

if __name__ == "__main__":
    main()