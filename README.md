# 1-Hour Pair Programming Interview Problems

## What Companies Actually Ask (Not LeetCode)

Based on real 1-hour coding interviews at fintech/payment companies like Ziina, Stripe, Square, etc.

## All Problems (Ordered Most → Least Likely)

### 🔥 Core Problems (Most Likely - 60%+ of interviews)

**Problem 1: Payment Rate Limiter** - `rate_limiter.py`
- Prevent payment fraud/abuse - 15-20 minutes

**Problem 2: Transaction Cache** - `transaction_cache.py` 
- Cache recent transactions with expiry - 15-20 minutes

**Problem 3: Circuit Breaker** - `circuit_breaker.py`
- Protect against external service failures - 15-20 minutes

**Problem 4: Payment Queue** - `payment_queue.py`
- Process payments with priorities - 20-25 minutes

### ⚡ Intermediate Problems (Common - 40%+ of interviews)

**Problem 5: Webhook Delivery System** - `webhook_delivery.py`
- Reliable delivery with retries - 20-25 minutes

**Problem 6: Connection Pool** - `connection_pool.py`
- Manage database connections - 15-20 minutes

**Problem 7: Idempotency Handler** - `idempotency_handler.py`
- Prevent duplicate payment processing - 15-20 minutes

### 🎯 Advanced Problems (Less Common - 20%+ of interviews)

**Problem 8: Balance Tracker** - `balance_tracker.py`
- Real-time account balance management - 20-25 minutes

**Problem 9: Event Processor** - `event_processor.py`
- Reliable event delivery system - 20-25 minutes

## Interview Format (60 minutes)

- **5 min:** Problem clarification
- **35 min:** Core implementation (pair programming)
- **15 min:** Edge cases & optimization
- **5 min:** Discussion & questions

## What They're Looking For

1. **Clean code** while thinking out loud
2. **Edge case handling** (timeouts, failures)
3. **Simple solutions** that work
4. **Good collaboration** during pairing
5. **Testing mindset** (how would you test this?)

Each problem includes:
- ✅ Real-world business context
- ✅ Starter code structure
- ✅ Test cases to guide you
- ✅ Common follow-up questions
- ✅ Expected time to complete