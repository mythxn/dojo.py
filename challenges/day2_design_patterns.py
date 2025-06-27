"""
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
        return "Connecting to MySQL..."

    
    def execute_query(self, query: str) -> str:
        return "Executing query: " + query + "on a MySQL database..."

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection implementation"""
    
    def connect(self) -> str:
        return "Connecting to PostgreSQL..."
    
    def execute_query(self, query: str) -> str:
        return "Executing query: " + query + "on a PostgreSQL database..."

class MongoDBConnection(DatabaseConnection):
    """MongoDB database connection implementation"""
    
    def connect(self) -> str:
        return "Connecting to MongoDB..."
    
    def execute_query(self, query: str) -> str:
        return "Executing query: " + query + "on a MongoDB database..."

class DatabaseFactory:
    """Factory for creating database connections"""
    
    @staticmethod
    def create_connection(db_type: DatabaseType) -> DatabaseConnection:
        """Create database connection based on type"""
        if db_type == DatabaseType.MYSQL:
            return MySQLConnection()
        elif db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLConnection()
        elif db_type == DatabaseType.MONGODB:
            return MongoDBConnection()
        else:
            raise ValueError("Invalid database type")


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
        self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.update(event_type, data)

class UserManager(Subject):
    def __init__(self):
        super().__init__()
        self.users = {}

    def register_user(self, user_id: str, email: str) -> None:
        self.users[user_id] = email
        print(f"✅ User {user_id} registered.")
        self.notify("user_registered", {"user_id": user_id, "email": email})

    def login_user(self, user_id: str) -> None:
        if user_id in self.users:
            print(f"🔓 User {user_id} logged in.")
            self.notify("user_logged_in", {"user_id": user_id})


class EmailNotifier(Observer):
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "user_registered":
            print(f"📧 Sending welcome email to {data['email']}")

class AnalyticsTracker(Observer):
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        print(f"📊 Tracking event: {event_type} for user {data['user_id']}")

# === STRATEGY PATTERN ===
class PaymentStrategy(ABC):
    """Abstract payment strategy"""
    
    @abstractmethod
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        pass

class CreditCardPayment(PaymentStrategy):
    """Credit card payment strategy"""
    
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        card = kwargs.get("card_number", "N/A")
        print(f"💳 Charging {amount} to credit card {card}")
        return {"status": "success", "method": "credit_card"}

class PayPalPayment(PaymentStrategy):
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        email = kwargs.get("email", "unknown")
        print(f"🅿️ Processing PayPal payment of {amount} for {email}")
        return {"status": "success", "method": "paypal"}

class BankTransferPayment(PaymentStrategy):
    """Bank transfer payment strategy"""

    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        acc = kwargs.get("account", "0000")
        print(f"🏦 Initiating bank transfer of {amount} from account {acc}")
        return {"status": "success", "method": "bank_transfer"}

class PaymentProcessor:
    """Payment processor using strategy pattern"""
    
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy) -> None:
        self.strategy = strategy
    
    def process_payment(self, amount: float, **kwargs) -> Dict[str, Any]:
        return self.strategy.process_payment(amount, **kwargs)

# Test your implementations
if __name__ == "__main__":
    print("Testing Design Patterns...")
    
    # Test Factory Pattern
    print("\n=== Factory Pattern Test ===")
    mysql_conn = DatabaseFactory.create_connection(DatabaseType.MYSQL)
    print(f"MySQL: {mysql_conn.connect()}")
    
    # Test Observer Pattern
    print("\n=== Observer Pattern Test ===")
    user_manager = UserManager()
    email_notifier = EmailNotifier()
    analytics = AnalyticsTracker()
    
    user_manager.attach(email_notifier)
    user_manager.attach(analytics)
    
    user_manager.register_user("user1", "user1@example.com")
    user_manager.login_user("user1")
    
    # Test Strategy Pattern
    print("\n=== Strategy Pattern Test ===")
    processor = PaymentProcessor(CreditCardPayment())
    result1 = processor.process_payment(100.0, card_number="1234-5678-9012-3456")
    print(f"Credit card payment: {result1}")
    
    processor.set_strategy(PayPalPayment())
    result2 = processor.process_payment(50.0, email="user@example.com")
    print(f"PayPal payment: {result2}")
    
    print("\n✅ Design patterns tests completed!")
