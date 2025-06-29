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

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

CURRENCIES = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,  # No decimal places
    "BTC": 8,  # 8 decimal places
}


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
        if currency not in CURRENCIES:
            raise ValueError(f'Unsupported currency: {currency}')
        self.currency = currency
        decimal_places = CURRENCIES[currency]
        quantize_exp = Decimal('1') / (10 ** decimal_places)
        self.amount = Decimal(str(amount)).quantize(quantize_exp, rounding=ROUND_HALF_UP)


    def __add__(self, other: 'Money') -> 'Money':
        """Add two money amounts (same currency only)."""
        if self.currency != other.currency:
            raise ValueError(f'Cannot add {self.currency} and {other.currency}')

        result_amount = self.amount + other.amount
        return Money(result_amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money amounts (same currency only)."""
        if self.currency != other.currency:
            raise ValueError(f'Cannot subtract {self.currency} and {other.currency}')

        result_amount = self.amount - other.amount
        return Money(result_amount, self.currency)

    def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
        """Multiply money by a number."""
        result = self.amount * Decimal(str(multiplier))
        return Money(result, self.currency)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Divide money by a number."""
        if divisor == 0:
            raise ValueError('Cannot divide by zero.')
        result = self.amount / Decimal(str(divisor))
        return Money(result, self.currency)

    def __eq__(self, other: 'Money') -> bool:
        """Check if two money amounts are equal."""
        if not isinstance(other, Money):
            return False
        return self.currency == other.currency and self.amount == other.amount

    def __lt__(self, other: 'Money') -> bool:
        """Check if this money is less than other."""
        if self.currency != other.currency:
            raise ValueError(f'Cannot compare {self.currency} and {other.currency}')
        return self.amount < other.amount

    def __str__(self) -> str:
        decimal_places = CURRENCIES[self.currency]
        # Format with fixed decimal places
        formatted = f"{self.amount:.{decimal_places}f}"
        return f"{formatted} {self.currency}"
    
    def __repr__(self) -> str:
        return f"Money('{self.amount}', '{self.currency}')"

    def convert_to(self, target_currency: str, exchange_rate: Decimal) -> 'Money':
        """Convert money to different currency."""
        if target_currency not in CURRENCIES:
            raise ValueError(f'Unsupported target country: {target_currency}')

        target_amount = self.amount * Decimal(str(exchange_rate))
        decimal_places = CURRENCIES[target_currency]
        quantize_exp = Decimal('1') / (10 ** decimal_places)
        target_amount = target_amount.quantize(quantize_exp, rounding=ROUND_HALF_UP)

        return Money(target_amount, target_currency)

    def split(self, parts: int) -> list['Money']:
        """Split money into equal parts, handling remainder properly."""
        if parts <= 0:
            raise ValueError("Parts must be a positive integer")

        decimal_places = CURRENCIES[self.currency]
        quantize_exp = Decimal('1') / (10 ** decimal_places)

        # Base share
        share = (self.amount / parts).quantize(quantize_exp, rounding=ROUND_HALF_UP)

        # Total of shares might be off due to rounding, compute remainder
        total_distributed = share * parts
        remainder = self.amount - total_distributed

        # Create list with base share
        result = [Money(share, self.currency) for _ in range(parts)]

        # Distribute remainder (1 cent etc.) to first few recipients
        i = 0
        while remainder != Decimal('0.0'):
            result[i].amount += quantize_exp
            remainder -= quantize_exp
            i += 1

        return result



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

    # Test comparison operations
    small_amount = Money("5.00", "USD")
    large_amount = Money("10.00", "USD")
    same_amount = Money("5.00", "USD")
    print(f"{small_amount} < {large_amount}: {small_amount < large_amount}")
    print(f"{small_amount} == {same_amount}: {small_amount == same_amount}")
