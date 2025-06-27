"""
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
    print("\n1. Creating tasks:")
    result1 = api.create_task({"title": "Learn Python", "priority": "high"})
    print(f"Create result: {result1}")
    
    result2 = api.create_task({"title": "Build API", "description": "REST API practice"})
    print(f"Create result: {result2}")
    
    # Test 2: Get all tasks
    print("\n2. Getting all tasks:")
    all_tasks = api.get_all_tasks()
    print(f"All tasks: {all_tasks}")
    
    # Test 3: Get specific task
    print("\n3. Getting specific task:")
    task = api.get_task(1)
    print(f"Task 1: {task}")
    
    # Test 4: Update task
    print("\n4. Updating task:")
    update_result = api.update_task(1, {"title": "Master Python", "completed": True})
    print(f"Update result: {update_result}")
    
    # Test 5: Filter tasks
    print("\n5. Filtering by priority:")
    high_priority = api.get_all_tasks(priority_filter="high")
    print(f"High priority tasks: {high_priority}")
    
    # Test 6: Delete task
    print("\n6. Deleting task:")
    delete_result = api.delete_task(2)
    print(f"Delete result: {delete_result}")
    
    print("\n✅ API tests completed!")
