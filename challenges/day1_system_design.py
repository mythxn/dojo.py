"""
Day 1 Challenge 3: System Design Discussion
==========================================

Design a scalable backend system for a social media platform.
Focus on architectural thinking and component design.

Problem: Design Twitter-like Social Media Backend
===============================================

You need to design the backend architecture for a Twitter-like social media platform.

REQUIREMENTS:
1. Users can post tweets (280 characters max)
2. Users can follow other users
3. Users see a timeline of tweets from people they follow
4. Support for likes and retweets
5. Handle 100M+ users, 500M+ tweets per day
6. Global availability with low latency

YOUR TASK:
Design the system architecture and implement key components.
Focus on: Database design, API structure, and scalability considerations.

Think about:
- Data models and relationships
- Database choice and schema design
- API endpoints and request/response formats
- Caching strategies
- How to handle high traffic loads
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum

class TweetType(Enum):
    ORIGINAL = "original"
    RETWEET = "retweet"
    REPLY = "reply"

# === DATA MODELS ===

class User:
    """User model for social media platform"""
    
    def __init__(self, user_id: str, username: str, email: str):
        # TODO: Design user data structure
        # Consider: profile info, timestamps, verification status
        pass
    
    def to_dict(self) -> Dict:
        # TODO: Implement user serialization
        pass

class Tweet:
    """Tweet model with support for different types"""
    
    def __init__(self, tweet_id: str, user_id: str, content: str, 
                 tweet_type: TweetType = TweetType.ORIGINAL):
        # TODO: Design tweet data structure
        # Consider: timestamps, media, hashtags, mentions
        pass
    
    def to_dict(self) -> Dict:
        # TODO: Implement tweet serialization
        pass

class Timeline:
    """User timeline management"""
    
    def __init__(self, user_id: str):
        # TODO: Design timeline data structure
        pass
    
    def add_tweet(self, tweet: Tweet) -> None:
        # TODO: Add tweet to timeline
        pass
    
    def get_tweets(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        # TODO: Get paginated tweets for timeline
        pass

# === CORE SERVICES ===

class UserService:
    """Handle user-related operations"""
    
    def __init__(self):
        # TODO: Initialize user storage
        pass
    
    def create_user(self, username: str, email: str) -> Dict:
        # TODO: Create new user with validation
        pass
    
    def follow_user(self, follower_id: str, following_id: str) -> Dict:
        # TODO: Implement follow relationship
        pass
    
    def unfollow_user(self, follower_id: str, following_id: str) -> Dict:
        # TODO: Implement unfollow
        pass
    
    def get_followers(self, user_id: str) -> List[str]:
        # TODO: Get user's followers
        pass
    
    def get_following(self, user_id: str) -> List[str]:
        # TODO: Get users that this user follows
        pass

class TweetService:
    """Handle tweet-related operations"""
    
    def __init__(self):
        # TODO: Initialize tweet storage
        pass
    
    def create_tweet(self, user_id: str, content: str) -> Dict:
        # TODO: Create new tweet with validation
        pass
    
    def like_tweet(self, user_id: str, tweet_id: str) -> Dict:
        # TODO: Like a tweet
        pass
    
    def retweet(self, user_id: str, tweet_id: str) -> Dict:
        # TODO: Retweet functionality
        pass
    
    def get_tweet(self, tweet_id: str) -> Dict:
        # TODO: Get specific tweet
        pass

class TimelineService:
    """Handle timeline generation and caching"""
    
    def __init__(self, user_service: UserService, tweet_service: TweetService):
        # TODO: Initialize timeline service
        pass
    
    def get_home_timeline(self, user_id: str, limit: int = 20) -> List[Dict]:
        # TODO: Generate home timeline (tweets from followed users)
        # This is the most complex part - consider caching strategies
        pass
    
    def get_user_timeline(self, user_id: str, limit: int = 20) -> List[Dict]:
        # TODO: Get specific user's tweets
        pass

# === SYSTEM DESIGN QUESTIONS ===

class SystemDesignDiscussion:
    """
    Answer these system design questions in comments or implement solutions
    """
    
    def database_design(self):
        """
        TODO: Design your database schema
        
        Questions to consider:
        1. SQL vs NoSQL - what would you choose and why?
        2. How would you structure the users table?
        3. How would you structure the tweets table?
        4. How would you handle the follow relationships?
        5. How would you handle likes and retweets?
        
        Draw/describe your schema here:
        """
        pass
    
    def api_design(self):
        """
        TODO: Design your REST API endpoints
        
        List the main endpoints you would need:
        - User management endpoints
        - Tweet management endpoints  
        - Timeline endpoints
        - Social interaction endpoints
        
        Example:
        POST /api/v1/users - Create user
        GET /api/v1/users/{id}/timeline - Get user timeline
        """
        pass
    
    def scalability_considerations(self):
        """
        TODO: How would you scale this system?
        
        Consider:
        1. Database scaling (sharding, read replicas)
        2. Caching strategies (Redis, CDN)
        3. Load balancing
        4. Timeline generation at scale
        5. Geographic distribution
        """
        pass
    
    def technology_choices(self):
        """
        TODO: What technologies would you use?
        
        Consider:
        - Programming language and framework
        - Database choice
        - Caching layer
        - Message queues
        - Load balancers
        - Monitoring and logging
        """
        pass

# Test your system design
if __name__ == "__main__":
    print("🏗️  SYSTEM DESIGN: Social Media Platform")
    print("=" * 50)
    
    # Initialize services
    user_service = UserService()
    tweet_service = TweetService()
    timeline_service = TimelineService(user_service, tweet_service)
    
    print("\n📝 Testing Basic Operations:")
    
    # Test 1: Create users
    print("\n1. Creating users:")
    user1 = user_service.create_user("alice", "alice@example.com")
    user2 = user_service.create_user("bob", "bob@example.com")
    print(f"Created users: {user1}, {user2}")
    
    # Test 2: Follow relationship
    print("\n2. Testing follow:")
    follow_result = user_service.follow_user("alice", "bob")
    print(f"Follow result: {follow_result}")
    
    # Test 3: Create tweets
    print("\n3. Creating tweets:")
    tweet1 = tweet_service.create_tweet("bob", "Hello, Twitter!")
    tweet2 = tweet_service.create_tweet("bob", "System design is fun!")
    print(f"Created tweets: {tweet1}, {tweet2}")
    
    # Test 4: Timeline generation
    print("\n4. Generating timeline:")
    alice_timeline = timeline_service.get_home_timeline("alice")
    print(f"Alice's timeline: {alice_timeline}")
    
    print("\n🎯 DISCUSSION POINTS:")
    print("1. How would you optimize timeline generation for millions of users?")
    print("2. How would you handle celebrity users with millions of followers?")
    print("3. How would you ensure data consistency across multiple data centers?")
    print("4. How would you handle trending topics and hashtags?")
    print("5. How would you implement real-time notifications?")
    
    print("\n✅ System design exercise completed!")
    print("💡 In a real interview, you would discuss these design decisions!")