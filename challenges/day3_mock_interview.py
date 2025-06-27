"""
Day 3 Challenge: 1-Hour Mock Interview Simulation
===============================================

This simulates the actual 1-hour interview format.
Complete as much as possible within 60 minutes.

TIMER: Start your timer for 60 minutes when you begin!

Interview Structure:
- 5 min: Problem understanding and clarification
- 40 min: Implementation and testing
- 10 min: Code review and optimization discussion
- 5 min: Questions and wrap-up

Problem: Build a URL Shortener Service Backend
============================================

You need to implement a URL shortener service (like bit.ly) with the following requirements:

REQUIREMENTS:
1. Shorten long URLs to unique short codes
2. Redirect short codes back to original URLs
3. Track click analytics for each short URL
4. Handle custom aliases (if available)
5. Implement basic rate limiting
6. Add URL validation and expiration

CONSTRAINTS:
- Short codes should be 6-8 characters
- Service should handle 1000+ URLs
- Include proper error handling
- Add basic analytics (click count, last accessed)

BONUS POINTS:
- Custom alias support
- Rate limiting by IP
- URL expiration dates
- Analytics dashboard data structure
"""

import time
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from urllib.parse import urlparse

class URLShortener:
    """
    URL Shortener Service - Complete this implementation
    
    This is your main challenge - implement all methods below
    """
    
    def __init__(self):
        # TODO: Initialize your data structures
        # Hint: You'll need to store URL mappings, analytics, etc.
        pass
    
    def shorten_url(self, long_url: str, custom_alias: Optional[str] = None, 
                   expires_in_days: Optional[int] = None) -> Dict:
        """
        Shorten a long URL
        
        Returns: {
            "short_code": "abc123",
            "short_url": "https://short.ly/abc123", 
            "original_url": "https://example.com/very/long/url",
            "expires_at": "2024-01-01T00:00:00Z" or None
        }
        """
        # TODO: Implement URL shortening logic
        # Steps:
        # 1. Validate the URL
        # 2. Check if custom alias is available
        # 3. Generate short code if no custom alias
        # 4. Store mapping with expiration
        # 5. Return response
        pass
    
    def expand_url(self, short_code: str) -> Dict:
        """
        Get original URL from short code and record analytics
        
        Returns: {
            "original_url": "https://example.com/very/long/url",
            "status": "success" | "not_found" | "expired",
            "clicks": 42
        }
        """
        # TODO: Implement URL expansion logic
        # Steps:
        # 1. Check if short code exists
        # 2. Check if URL has expired
        # 3. Update analytics (click count, last accessed)
        # 4. Return original URL or error
        pass
    
    def get_analytics(self, short_code: str) -> Dict:
        """
        Get analytics for a short URL
        
        Returns: {
            "short_code": "abc123",
            "original_url": "https://example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "clicks": 42,
            "last_accessed": "2024-01-01T12:00:00Z",
            "expires_at": "2024-01-01T00:00:00Z" or None
        }
        """
        # TODO: Implement analytics retrieval
        pass
    
    def list_urls(self, limit: int = 10) -> List[Dict]:
        """
        List recent URLs with basic analytics
        """
        # TODO: Implement URL listing
        pass
    
    def delete_url(self, short_code: str) -> Dict:
        """
        Delete a short URL
        """
        # TODO: Implement URL deletion
        pass

class RateLimiter:
    """
    Simple rate limiter for the URL shortener
    """
    
    def __init__(self, max_requests: int = 10, window_minutes: int = 1):
        # TODO: Initialize rate limiter
        pass
    
    def is_allowed(self, ip_address: str) -> bool:
        """
        Check if request is allowed based on rate limiting
        """
        # TODO: Implement rate limiting logic
        pass

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted
    """
    # TODO: Implement URL validation
    pass

def generate_short_code(length: int = 6) -> str:
    """
    Generate a random short code
    """
    # TODO: Implement short code generation
    pass

# Test your implementation
if __name__ == "__main__":
    print("🎯 STARTING 1-HOUR MOCK INTERVIEW")
    print("=" * 50)
    print("⏰ Start your 60-minute timer NOW!")
    print()
    
    # Initialize the service
    shortener = URLShortener()
    rate_limiter = RateLimiter()
    
    # Test cases to verify your implementation
    test_urls = [
        "https://www.example.com/very/long/url/with/many/parameters?foo=bar&baz=qux",
        "https://github.com/user/repository/blob/main/very/long/file/path.py",
        "https://stackoverflow.com/questions/123456/how-to-implement-url-shortener"
    ]
    
    print("📝 Test 1: Basic URL Shortening")
    for i, url in enumerate(test_urls, 1):
        result = shortener.shorten_url(url)
        print(f"   {i}. {url[:50]}... -> {result}")
    
    print("\n📝 Test 2: URL Expansion")
    # Test expanding the first shortened URL
    # result = shortener.expand_url("abc123")  # Use actual short code
    # print(f"   Expanded: {result}")
    
    print("\n📝 Test 3: Custom Alias")
    custom_result = shortener.shorten_url(test_urls[0], custom_alias="my-link")
    print(f"   Custom alias: {custom_result}")
    
    print("\n📝 Test 4: Analytics")
    # analytics = shortener.get_analytics("abc123")  # Use actual short code
    # print(f"   Analytics: {analytics}")
    
    print("\n📝 Test 5: Rate Limiting")
    test_ip = "192.168.1.1"
    for i in range(12):  # Test rate limiting
        allowed = rate_limiter.is_allowed(test_ip)
        print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Rate limited'}")
    
    print("\n⏰ INTERVIEW COMPLETE!")
    print("🎉 Great job! In a real interview, now you would:")
    print("   1. Explain your design decisions")
    print("   2. Discuss scalability improvements")
    print("   3. Review error handling")
    print("   4. Answer questions about your implementation")
