"""
PROBLEM: Money/Decimal Handler (15-20 minutes)

BUSINESS CONTEXT:
Payment systems must handle money with perfect precision. Floating point 
arithmetic causes rounding errors that can lose or create money.

REQUIREMENTS:
1. Create a Money class that handles decimal arithmetic precisely
2. Support different currencies (USD, EUR, etc.)
3. Implement basic operations (add, subtract, multiply, divide)
4. Handle currency conversion with exchange rates
5. Proper rounding rules for different currencies

FOLLOW-UP QUESTIONS:
- How do you handle currency conversion precision?
- What happens when you divide money that doesn't split evenly?
- How do you prevent money from being lost due to rounding?
- How would you handle different currency decimal places (JPY has 0, USD has 2)?
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Union
from dataclasses import dataclass


class Currency:
    """Currency definitions with decimal places."""
    USD = ("USD", 2)
    EUR = ("EUR", 2) 
    GBP = ("GBP", 2)
    JPY = ("JPY", 0)  # No decimal places
    BTC = ("BTC", 8)  # 8 decimal places


@dataclass
class Money:
    """Precise money representation using Decimal."""
    
    def __init__(self, amount: Union[str, int, float, Decimal], currency: str = "USD"):
        """
        Initialize Money with precise decimal amount.
        
        Args:
            amount: Money amount (avoid float when possible)
            currency: Currency code (USD, EUR, etc.)
        """
        # TODO: Initialize money with proper decimal precision
        pass
    
    def __add__(self, other: 'Money') -> 'Money':
        """Add two money amounts (same currency only)."""
        # TODO: Implement addition with currency validation
        pass
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money amounts (same currency only)."""
        # TODO: Implement subtraction with currency validation
        pass
    
    def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
        """Multiply money by a number."""
        # TODO: Implement multiplication with proper rounding
        pass
    
    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Divide money by a number."""
        # TODO: Implement division with proper rounding
        pass
    
    def __eq__(self, other: 'Money') -> bool:
        """Check if two money amounts are equal."""
        # TODO: Implement equality comparison
        pass
    
    def __lt__(self, other: 'Money') -> bool:
        """Check if this money is less than other."""
        # TODO: Implement less than comparison
        pass
    
    def __str__(self) -> str:
        """String representation of money."""
        # TODO: Format money properly (e.g., "$10.50", "¥1000")
        pass
    
    def convert_to(self, target_currency: str, exchange_rate: Decimal) -> 'Money':
        """Convert money to different currency."""
        # TODO: Implement currency conversion with proper rounding
        pass
    
    def split(self, parts: int) -> list['Money']:
        """Split money into equal parts, handling remainder properly."""
        # TODO: Split money and distribute remainder to avoid losing cents
        pass
    
    def round_to_currency(self) -> 'Money':
        """Round money to appropriate decimal places for currency."""
        # TODO: Round based on currency decimal places
        pass


class MoneyCalculator:
    """Helper class for complex money calculations."""
    
    def __init__(self, exchange_rates: Dict[tuple, Decimal] = None):
        """
        Initialize calculator with exchange rates.
        
        Args:
            exchange_rates: Dict of (from_currency, to_currency) -> rate
        """
        # TODO: Initialize with exchange rates
        pass
    
    def calculate_fee(self, amount: Money, fee_percentage: Decimal) -> Money:
        """Calculate fee as percentage of amount."""
        # TODO: Calculate fee with proper rounding
        pass
    
    def calculate_total_with_tax(self, amount: Money, tax_rate: Decimal) -> Money:
        """Calculate total amount including tax."""
        # TODO: Add tax to amount
        pass
    
    def distribute_amount(self, total: Money, recipients: int) -> list[Money]:
        """Distribute amount among recipients, handling remainder."""
        # TODO: Distribute money evenly, handle remainder
        pass
    
    def convert_currency(self, money: Money, target_currency: str) -> Money:
        """Convert money using stored exchange rates."""
        # TODO: Look up exchange rate and convert
        pass


# Example usage and test cases
if __name__ == "__main__":
    # Test basic money operations
    price = Money("10.50", "USD")
    tax = Money("0.84", "USD") 
    total = price + tax
    print(f"Price: {price}, Tax: {tax}, Total: {total}")
    
    # Test multiplication and rounding
    unit_price = Money("3.33", "USD")
    quantity = 3
    subtotal = unit_price * quantity
    print(f"Unit price: {unit_price} x {quantity} = {subtotal}")
    
    # Test division and splitting
    bill = Money("100.00", "USD")
    split_3_ways = bill.split(3)
    print(f"Bill {bill} split 3 ways: {split_3_ways}")
    
    # Test currency conversion
    usd_amount = Money("100.00", "USD")
    eur_amount = usd_amount.convert_to("EUR", Decimal("0.85"))
    print(f"{usd_amount} = {eur_amount}")
    
    # Test fee calculation
    calculator = MoneyCalculator()
    payment = Money("1000.00", "USD")
    processing_fee = calculator.calculate_fee(payment, Decimal("0.029"))  # 2.9%
    print(f"Payment: {payment}, Fee: {processing_fee}")