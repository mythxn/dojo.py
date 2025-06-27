from typing import Dict, Optional


class Task:
    """Task model"""

    def __init__(self, title: str, description: str = "", priority: str = "medium"):
        self.title = title
        self.description = description
        self.priority = priority

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=data.get("priority", "medium")
        )


class TaskAPI:
    """Simple in-memory task API"""

    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1

    def create_task(self, data: Dict) -> Dict:
        error = validate_task_data(data)
        if error:
            return {"error": error, "status": 400}

        task = Task.from_dict(data)
        self.tasks[self.next_id] = task
        response = {"task": task.to_dict(), "status": 201}
        self.next_id += 1
        return response

    def get_task(self, task_id: int) -> Dict:
        task = self.tasks.get(task_id)
        if task:
            return {"task": task.to_dict(), "status": 200}
        return {"error": f"Task id {task_id} not found", "status": 404}

    def get_all_tasks(self, priority_filter: Optional[str] = None) -> Dict:
        if priority_filter:
            filtered = [
                task.to_dict()
                for task in self.tasks.values()
                if task.priority == priority_filter
            ]
        else:
            filtered = [task.to_dict() for task in self.tasks.values()]
        return {"tasks": filtered, "status": 200}

    def update_task(self, task_id: int, data: Dict) -> Dict:
        if task_id not in self.tasks:
            return {"error": f"Task id {task_id} not found", "status": 404}

        error = validate_task_data(data)
        if error:
            return {"error": error, "status": 400}

        self.tasks[task_id] = Task.from_dict(data)
        return {"task": self.tasks[task_id].to_dict(), "status": 200}

    def delete_task(self, task_id: int) -> Dict:
        if task_id in self.tasks:
            self.tasks.pop(task_id)
            return {"message": f"Task id {task_id} deleted", "status": 200}
        return {"error": f"Task id {task_id} not found", "status": 404}


def validate_task_data(data: Dict) -> Optional[str]:
    required_fields = ["title", "description", "priority"]
    if set(data.keys()) != set(required_fields):
        return f"Missing or extra fields: expected {required_fields}"
    if data["priority"] not in ["high", "medium", "low"]:
        return f"Invalid priority: '{data['priority']}'"
    return None


if __name__ == "__main__":
    print("Testing Task API...")

    api = TaskAPI()

    # Test 1: Create tasks
    print("\n1. Creating tasks:")
    result1 = api.create_task({
        "title": "Learn Python",
        "description": "Basics + decorators",
        "priority": "high"
    })
    print(f"Create result: {result1}")

    result2 = api.create_task({
        "title": "Build API",
        "description": "REST API practice",
        "priority": "medium"
    })
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
    update_result = api.update_task(1, {
        "title": "Master Python",
        "description": "Generators, Context Managers, and Decorators",
        "priority": "high"
    })
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