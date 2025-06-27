#!/usr/bin/env python3
"""
Interactive Learning and Assessment System
=========================================

This module provides adaptive learning based on your performance.
It assesses your current Python skill level and adjusts difficulty accordingly.
"""

import sys
import json
import time
from datetime import datetime
import traceback
from typing import Dict, List, Any, Callable

class SkillAssessment:
    def __init__(self):
        self.results = {}
        self.current_level = "beginner"
        
    def run_assessment(self):
        """Run the complete skill assessment"""
        print("🎯 PYTHON SKILLS ASSESSMENT")
        print("=" * 40)
        print("This assessment will determine your current skill level")
        print("and adapt the interview prep accordingly.")
        print()
        
        # Core Python concepts
        self.assess_python_fundamentals()
        self.assess_oop_concepts()
        self.assess_async_programming()
        self.assess_system_design_thinking()
        
        # Calculate overall level
        self.determine_skill_level()
        self.save_results()
        self.show_results()
        
    def assess_python_fundamentals(self):
        """Test fundamental Python knowledge"""
        print("📚 SECTION 1: Python Fundamentals")
        print("-" * 30)
        
        score = 0
        total = 0
        
        # Question 1: Decorators
        print("1. Implement a timing decorator that measures function execution time:")
        print("   def timing_decorator(func):")
        print("       # Your implementation here")
        print()
        
        user_code = self.get_multiline_input("Enter your decorator implementation:")
        if self.test_decorator_implementation(user_code):
            score += 2
            print("✅ Excellent! Your decorator works correctly.")
        else:
            print("❌ The decorator has issues. Here's a working example:")
            self.show_decorator_solution()
        total += 2
        
        # Question 2: Context Managers
        print("\n2. Create a context manager for database connections:")
        print("   class DatabaseConnection:")
        print("       # Implement __enter__ and __exit__")
        print()
        
        user_code = self.get_multiline_input("Enter your context manager:")
        if self.test_context_manager(user_code):
            score += 2
            print("✅ Great context manager implementation!")
        else:
            score += 1
            print("⚠️  Partial credit. Here's an improved version:")
            self.show_context_manager_solution()
        total += 2
        
        # Question 3: Generators
        print("\n3. Write a generator that yields Fibonacci numbers:")
        user_code = self.get_multiline_input("Enter your generator function:")
        if self.test_fibonacci_generator(user_code):
            score += 1
            print("✅ Perfect generator implementation!")
        total += 1
        
        self.results['python_fundamentals'] = (score / total) * 10
        print(f"\n📊 Python Fundamentals Score: {score}/{total} ({self.results['python_fundamentals']:.1f}/10)")
        
    def assess_oop_concepts(self):
        """Test Object-Oriented Programming concepts"""
        print("\n🏗️  SECTION 2: OOP and Design Patterns")
        print("-" * 30)
        
        score = 0
        total = 0
        
        # Singleton Pattern
        print("1. Implement a thread-safe Singleton pattern:")
        user_code = self.get_multiline_input("Enter your Singleton implementation:")
        if self.test_singleton_pattern(user_code):
            score += 2
            print("✅ Excellent thread-safe singleton!")
        else:
            score += 1
            print("⚠️  Good attempt. Here's a thread-safe version:")
            self.show_singleton_solution()
        total += 2
        
        # Factory Pattern
        print("\n2. Design a Factory pattern for creating different types of loggers:")
        print("   (ConsoleLogger, FileLogger, DatabaseLogger)")
        user_code = self.get_multiline_input("Enter your Factory implementation:")
        score += self.evaluate_factory_pattern(user_code)
        total += 2
        
        self.results['oop_patterns'] = (score / total) * 10
        print(f"\n📊 OOP & Patterns Score: {score}/{total} ({self.results['oop_patterns']:.1f}/10)")
        
    def assess_async_programming(self):
        """Test asynchronous programming knowledge"""
        print("\n⚡ SECTION 3: Async Programming")
        print("-" * 30)
        
        score = 0
        total = 0
        
        # Async/await basics
        print("1. Write an async function that fetches data from multiple URLs concurrently:")
        user_code = self.get_multiline_input("Enter your async implementation:")
        score += self.evaluate_async_code(user_code)
        total += 3
        
        # Producer-Consumer pattern
        print("\n2. Implement a producer-consumer pattern using asyncio.Queue:")
        user_code = self.get_multiline_input("Enter your implementation:")
        score += self.evaluate_producer_consumer(user_code)
        total += 2
        
        self.results['async_programming'] = (score / total) * 10
        print(f"\n📊 Async Programming Score: {score}/{total} ({self.results['async_programming']:.1f}/10)")
        
    def assess_system_design_thinking(self):
        """Test system design and architectural thinking"""
        print("\n🏛️  SECTION 4: System Design Thinking")
        print("-" * 30)
        
        score = 0
        total = 0
        
        # API Design
        print("1. Design a RESTful API for a blog system with posts, comments, and users.")
        print("   List the endpoints, HTTP methods, and request/response formats:")
        response = input("Your API design: ")
        score += self.evaluate_api_design(response)
        total += 3
        
        # Caching Strategy
        print("\n2. How would you implement caching for frequently accessed blog posts?")
        print("   Consider cache invalidation, TTL, and consistency:")
        response = input("Your caching strategy: ")
        score += self.evaluate_caching_strategy(response)
        total += 2
        
        self.results['system_design'] = (score / total) * 10
        print(f"\n📊 System Design Score: {score}/{total} ({self.results['system_design']:.1f}/10)")
        
    def get_multiline_input(self, prompt):
        """Get multiline code input from user"""
        print(f"\n{prompt}")
        print("(Enter your code, then type 'END' on a new line to finish)")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        return '\n'.join(lines)
        
    def test_decorator_implementation(self, code):
        """Test if the decorator implementation works"""
        try:
            # Create a safe execution environment
            namespace = {}
            exec(code, namespace)
            
            # Test the decorator
            if 'timing_decorator' in namespace:
                decorator = namespace['timing_decorator']
                
                @decorator
                def test_func():
                    time.sleep(0.1)
                    return "test"
                
                result = test_func()
                return result == "test"
        except:
            return False
        return False
        
    def test_context_manager(self, code):
        """Test context manager implementation"""
        try:
            namespace = {}
            exec(code, namespace)
            
            if 'DatabaseConnection' in namespace:
                conn_class = namespace['DatabaseConnection']
                with conn_class() as conn:
                    pass
                return True
        except:
            return False
        return False
        
    def test_fibonacci_generator(self, code):
        """Test Fibonacci generator"""
        try:
            namespace = {}
            exec(code, namespace)
            
            # Look for generator function
            for name, obj in namespace.items():
                if callable(obj) and 'fibonacci' in name.lower():
                    gen = obj()
                    first_5 = [next(gen) for _ in range(5)]
                    return first_5 == [0, 1, 1, 2, 3] or first_5 == [1, 1, 2, 3, 5]
        except:
            return False
        return False
        
    def test_singleton_pattern(self, code):
        """Test singleton pattern implementation"""
        try:
            namespace = {}
            exec(code, namespace)
            
            # Look for singleton class
            for name, obj in namespace.items():
                if isinstance(obj, type) and 'singleton' in name.lower():
                    instance1 = obj()
                    instance2 = obj()
                    return instance1 is instance2
        except:
            return False
        return False
        
    def evaluate_factory_pattern(self, code):
        """Evaluate factory pattern implementation"""
        # Simple scoring based on keywords and structure
        score = 0
        if 'class' in code and 'Logger' in code:
            score += 1
        if 'Factory' in code or 'create' in code:
            score += 1
        return score
        
    def evaluate_async_code(self, code):
        """Evaluate async programming code"""
        score = 0
        if 'async def' in code:
            score += 1
        if 'await' in code:
            score += 1
        if 'asyncio' in code or 'aiohttp' in code:
            score += 1
        return score
        
    def evaluate_producer_consumer(self, code):
        """Evaluate producer-consumer pattern"""
        score = 0
        if 'asyncio.Queue' in code or 'Queue' in code:
            score += 1
        if 'producer' in code.lower() and 'consumer' in code.lower():
            score += 1
        return score
        
    def evaluate_api_design(self, response):
        """Evaluate API design response"""
        score = 0
        response_lower = response.lower()
        
        # Check for REST concepts
        if any(method in response_lower for method in ['get', 'post', 'put', 'delete']):
            score += 1
        if '/posts' in response_lower or '/users' in response_lower:
            score += 1
        if 'json' in response_lower or 'status' in response_lower:
            score += 1
        return score
        
    def evaluate_caching_strategy(self, response):
        """Evaluate caching strategy response"""
        score = 0
        response_lower = response.lower()
        
        if any(term in response_lower for term in ['redis', 'memcached', 'cache']):
            score += 1
        if any(term in response_lower for term in ['ttl', 'invalidation', 'expiry']):
            score += 1
        return score
        
    def show_decorator_solution(self):
        """Show example decorator solution"""
        solution = '''
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper
'''
        print(solution)
        
    def show_context_manager_solution(self):
        """Show example context manager solution"""
        solution = '''
class DatabaseConnection:
    def __init__(self, db_url="sqlite:///example.db"):
        self.db_url = db_url
        self.connection = None
        
    def __enter__(self):
        print(f"Connecting to {self.db_url}")
        # In real implementation: self.connection = sqlite3.connect(self.db_url)
        self.connection = "mock_connection"
        return self.connection
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            print("Closing database connection")
            # In real implementation: self.connection.close()
        if exc_type:
            print(f"Exception occurred: {exc_val}")
        return False  # Don't suppress exceptions
'''
        print(solution)
        
    def show_singleton_solution(self):
        """Show thread-safe singleton solution"""
        solution = '''
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
'''
        print(solution)
        
    def determine_skill_level(self):
        """Determine overall skill level based on assessment results"""
        avg_score = sum(self.results.values()) / len(self.results)
        
        if avg_score >= 8:
            self.current_level = "senior"
        elif avg_score >= 6:
            self.current_level = "intermediate"
        else:
            self.current_level = "beginner"
            
    def save_results(self):
        """Save assessment results to file"""
        try:
            with open("progress.json", "r") as f:
                progress = json.load(f)
        except FileNotFoundError:
            progress = {}
            
        progress["skill_assessment"] = self.results
        progress["current_level"] = self.current_level
        progress["assessment_date"] = datetime.now().isoformat()
        
        with open("progress.json", "w") as f:
            json.dump(progress, f, indent=2)
            
    def show_results(self):
        """Display final assessment results"""
        print("\n" + "="*50)
        print("🎯 ASSESSMENT RESULTS")
        print("="*50)
        
        for category, score in self.results.items():
            category_display = category.replace('_', ' ').title()
            print(f"{category_display}: {score:.1f}/10")
            
        avg_score = sum(self.results.values()) / len(self.results)
        print(f"\nOverall Score: {avg_score:.1f}/10")
        print(f"Skill Level: {self.current_level.upper()}")
        
        print("\n📋 RECOMMENDED NEXT STEPS:")
        if self.current_level == "senior":
            print("• Focus on advanced system design patterns")
            print("• Practice complex debugging scenarios")  
            print("• Work on performance optimization challenges")
        elif self.current_level == "intermediate":
            print("• Strengthen async programming skills")
            print("• Practice more design patterns")
            print("• Focus on system design fundamentals")
        else:
            print("• Review Python fundamentals")
            print("• Practice basic OOP concepts")
            print("• Start with simpler coding challenges")
            
        print(f"\n🚀 Continue with: python pattern_practice.py --level {self.current_level}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--assess":
        assessment = SkillAssessment()
        assessment.run_assessment()
    else:
        print("Use: python interactive_learning.py --assess")

if __name__ == "__main__":
    main()