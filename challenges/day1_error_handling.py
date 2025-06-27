"""
Day 1 Challenge 4: Error Handling Practice
=========================================

Practice robust error handling patterns for backend applications.
Focus on graceful degradation and proper error reporting.

Topics covered:
- Exception handling best practices
- Custom exception classes
- Logging and monitoring
- Input validation
- External service failures
- Resource management
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    AUTHENTICATION_ERROR = "auth_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    INTERNAL_ERROR = "internal_error"

# === CUSTOM EXCEPTIONS ===

class BaseAPIException(Exception):
    """Base exception for API errors"""
    
    def __init__(self, message: str, error_type: ErrorType, status_code: int = 500):
        # TODO: Initialize custom exception
        pass
    
    def to_dict(self) -> Dict:
        # TODO: Convert exception to API response format
        pass

class ValidationError(BaseAPIException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = None):
        # TODO: Initialize validation error
        pass

class ExternalServiceError(BaseAPIException):
    """Raised when external service calls fail"""
    
    def __init__(self, service_name: str, message: str, retry_after: int = None):
        # TODO: Initialize external service error
        pass

class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, reset_time: datetime):
        # TODO: Initialize rate limit error
        pass

# === RESILIENT SERVICES ===

class DatabaseService:
    """Simulates database operations with potential failures"""
    
    def __init__(self, failure_rate: float = 0.1):
        self.failure_rate = failure_rate
        self.data = {}
    
    def get_user(self, user_id: str) -> Dict:
        """Get user with error handling"""
        # TODO: Implement database get with error handling
        # Simulate random failures based on failure_rate
        pass
    
    def save_user(self, user_id: str, user_data: Dict) -> bool:
        """Save user with error handling"""
        # TODO: Implement database save with error handling
        pass
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user with error handling"""
        # TODO: Implement database delete with error handling
        pass

class ExternalAPIService:
    """Simulates external API calls with retries and circuit breaker"""
    
    def __init__(self, failure_rate: float = 0.2):
        self.failure_rate = failure_rate
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = None
    
    def call_external_api(self, endpoint: str, data: Dict) -> Dict:
        """Make external API call with circuit breaker pattern"""
        # TODO: Implement circuit breaker pattern
        # Consider: failure counting, circuit open/closed states, timeout
        pass
    
    def _make_api_call(self, endpoint: str, data: Dict) -> Dict:
        """Simulate actual API call"""
        # TODO: Simulate API call with random failures
        pass
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker after timeout"""
        # TODO: Implement circuit breaker reset logic
        pass

class NotificationService:
    """Email/SMS notification service with graceful degradation"""
    
    def __init__(self):
        self.email_service_available = True
        self.sms_service_available = True
    
    def send_notification(self, user_id: str, message: str, 
                         preferred_method: str = "email") -> Dict:
        """Send notification with fallback methods"""
        # TODO: Implement notification with fallback
        # Try preferred method first, then fallback options
        pass
    
    def send_email(self, user_id: str, message: str) -> bool:
        """Send email notification"""
        # TODO: Implement email sending with error handling
        pass
    
    def send_sms(self, user_id: str, message: str) -> bool:
        """Send SMS notification"""
        # TODO: Implement SMS sending with error handling
        pass

# === VALIDATION UTILITIES ===

def validate_user_input(data: Dict) -> None:
    """Validate user input and raise ValidationError if invalid"""
    # TODO: Implement comprehensive input validation
    # Check required fields, data types, formats, etc.
    pass

def validate_email(email: str) -> bool:
    """Validate email format"""
    # TODO: Implement email validation
    pass

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # TODO: Implement phone validation
    pass

# === RETRY DECORATOR ===

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """Decorator for retrying operations with exponential backoff"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # TODO: Implement retry logic with exponential backoff
            pass
        return wrapper
    return decorator

# === RESOURCE MANAGEMENT ===

@contextmanager
def managed_database_connection():
    """Context manager for database connections"""
    # TODO: Implement database connection management
    # Ensure proper cleanup even if exceptions occur
    pass

@contextmanager
def managed_file_operation(filename: str, mode: str = 'r'):
    """Context manager for file operations"""
    # TODO: Implement file operation management
    pass

# === MAIN APPLICATION WITH ERROR HANDLING ===

class UserManagementAPI:
    """User management API with comprehensive error handling"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.api_service = ExternalAPIService()
        self.notification_service = NotificationService()
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create user with full error handling"""
        try:
            # TODO: Implement user creation with error handling
            # Steps:
            # 1. Validate input
            # 2. Check if user exists
            # 3. Save to database
            # 4. Send welcome notification
            # 5. Log success/failure
            pass
        except ValidationError as e:
            # TODO: Handle validation errors
            pass
        except Exception as e:
            # TODO: Handle unexpected errors
            pass
    
    def get_user(self, user_id: str) -> Dict:
        """Get user with error handling"""
        try:
            # TODO: Implement user retrieval with error handling
            pass
        except Exception as e:
            # TODO: Handle errors gracefully
            pass
    
    def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Update user with error handling"""
        try:
            # TODO: Implement user update with error handling
            pass
        except Exception as e:
            # TODO: Handle errors gracefully
            pass
    
    def delete_user(self, user_id: str) -> Dict:
        """Delete user with error handling"""
        try:
            # TODO: Implement user deletion with error handling
            pass
        except Exception as e:
            # TODO: Handle errors gracefully
            pass

# Test error handling scenarios
if __name__ == "__main__":
    print("🛡️  ERROR HANDLING PRACTICE")
    print("=" * 40)
    
    api = UserManagementAPI()
    
    # Test 1: Invalid input validation
    print("\n1. Testing input validation:")
    invalid_user = {"username": "", "email": "invalid-email"}
    result = api.create_user(invalid_user)
    print(f"Invalid input result: {result}")
    
    # Test 2: Valid user creation
    print("\n2. Testing valid user creation:")
    valid_user = {
        "username": "testuser",
        "email": "test@example.com",
        "phone": "+1234567890"
    }
    result = api.create_user(valid_user)
    print(f"Valid user result: {result}")
    
    # Test 3: Database failure simulation
    print("\n3. Testing database failures:")
    api.db_service.failure_rate = 0.8  # High failure rate
    for i in range(5):
        result = api.get_user("user123")
        print(f"Attempt {i+1}: {result}")
    
    # Test 4: External service failures
    print("\n4. Testing external service circuit breaker:")
    api.api_service.failure_rate = 0.9  # Very high failure rate
    for i in range(8):
        try:
            result = api.api_service.call_external_api("/validate", {"user": "test"})
            print(f"API call {i+1}: Success")
        except Exception as e:
            print(f"API call {i+1}: Failed - {e}")
    
    print("\n🎯 ERROR HANDLING SCENARIOS TO CONSIDER:")
    print("1. What happens when the database is completely down?")
    print("2. How do you handle partial system failures?")
    print("3. How do you ensure data consistency during failures?")
    print("4. How do you monitor and alert on error rates?")
    print("5. How do you handle cascading failures?")
    
    print("\n✅ Error handling practice completed!")