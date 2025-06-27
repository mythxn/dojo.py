#!/usr/bin/env python3
"""
Interview Simulator - Mock Interview Practice
===========================================

Simulates real senior backend engineer interviews with:
- Technical discussions
- System design questions  
- Code review scenarios
- Behavioral questions
- Performance under pressure
"""

import sys
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any

class InterviewSimulator:
    def __init__(self):
        self.load_user_profile()
        self.interview_types = {
            "technical": self.technical_interview,
            "system_design": self.system_design_interview,
            "code_review": self.code_review_interview,
            "behavioral": self.behavioral_interview,
            "mock": self.full_mock_interview
        }
        
    def load_user_profile(self):
        """Load user's skill assessment and progress"""
        try:
            with open("progress.json", "r") as f:
                self.progress = json.load(f)
                self.skill_level = self.progress.get("current_level", "intermediate")
        except FileNotFoundError:
            self.progress = {}
            self.skill_level = "intermediate"
            
    def full_mock_interview(self):
        """Complete mock interview simulation"""
        print("🎭 FULL MOCK INTERVIEW SIMULATION")
        print("=" * 50)
        print("Duration: 60 minutes")
        print("Format: Senior Backend Engineer Interview")
        print()
        
        # Interview structure
        sections = [
            ("Introduction & Background", 5, self.introduction_section),
            ("Technical Deep Dive", 20, self.technical_deep_dive),
            ("System Design", 25, self.system_design_section),
            ("Code Review", 8, self.code_review_section),
            ("Questions & Wrap-up", 2, self.questions_section)
        ]
        
        total_score = 0
        max_score = 0
        
        for section_name, duration, section_func in sections:
            print(f"\n🎯 {section_name.upper()} ({duration} minutes)")
            print("-" * 40)
            
            start_time = time.time()
            score, max_section_score = section_func(duration)
            elapsed = time.time() - start_time
            
            total_score += score
            max_score += max_section_score
            
            print(f"⏱️  Section completed in {elapsed/60:.1f} minutes")
            print(f"📊 Score: {score}/{max_section_score}")
            
            if elapsed > duration * 60:
                print("⚠️  Time exceeded - practice time management!")
                
        # Final evaluation
        self.provide_interview_feedback(total_score, max_score)
        self.save_interview_results(total_score, max_score)
        
    def introduction_section(self, duration: int) -> tuple:
        """Introduction and background discussion"""
        print("👋 Let's start with introductions.")
        print("Tell me about your background and recent projects.")
        print()
        
        response = input("Your response: ")
        
        # Evaluate response
        score = 0
        if len(response) > 50:
            score += 1
        if any(word in response.lower() for word in ['python', 'backend', 'api', 'database']):
            score += 1
        if any(word in response.lower() for word in ['scale', 'performance', 'system']):
            score += 1
            
        print(f"\n💭 Good introduction! Let's dive into technical topics.")
        return score, 3
        
    def technical_deep_dive(self, duration: int) -> tuple:
        """Technical deep dive questions"""
        print("🔧 Let's discuss some technical concepts.")
        print()
        
        questions = [
            {
                "question": "Explain how you would handle database connection pooling in a high-traffic Python application.",
                "keywords": ["pool", "connection", "concurrent", "sqlalchemy", "psycopg2"],
                "points": 3
            },
            {
                "question": "How would you implement rate limiting for an API? What are the different strategies?",
                "keywords": ["token bucket", "sliding window", "redis", "distributed", "rate limit"],
                "points": 3
            },
            {
                "question": "Describe your approach to handling async operations in Python. When would you use asyncio vs threading?",
                "keywords": ["asyncio", "await", "threading", "GIL", "concurrent", "io bound"],
                "points": 4
            }
        ]
        
        total_score = 0
        max_score = sum(q["points"] for q in questions)
        
        for i, q in enumerate(questions, 1):
            print(f"Question {i}: {q['question']}")
            response = input("Your answer: ")
            
            score = self.evaluate_technical_response(response, q["keywords"])
            total_score += min(score, q["points"])
            
            print(f"✅ Good answer! ({score}/{q['points']} points)")
            print()
            
        return total_score, max_score
        
    def system_design_section(self, duration: int) -> tuple:
        """System design interview section"""
        print("🏗️  SYSTEM DESIGN CHALLENGE")
        print()
        
        scenarios = [
            {
                "title": "Design a URL Shortener (like bit.ly)",
                "requirements": [
                    "Handle 100M URLs per day",
                    "Low latency for redirects",
                    "Analytics tracking",
                    "Custom aliases support"
                ],
                "discussion_points": [
                    "Database schema design",
                    "Caching strategy", 
                    "Load balancing",
                    "Analytics pipeline"
                ]
            },
            {
                "title": "Design a Chat System",
                "requirements": [
                    "Real-time messaging",
                    "Group chats",
                    "Message history",
                    "Online status"
                ],
                "discussion_points": [
                    "WebSocket vs polling",
                    "Message storage",
                    "Presence system",
                    "Scalability considerations"
                ]
            }
        ]
        
        scenario = random.choice(scenarios)
        
        print(f"📋 Scenario: {scenario['title']}")
        print("\nRequirements:")
        for req in scenario["requirements"]:
            print(f"  • {req}")
            
        print(f"\n🎯 You have {duration} minutes to design this system.")
        print("Walk me through your high-level architecture.")
        print()
        
        # High-level architecture
        print("1. High-level Architecture:")
        arch_response = input("Describe your overall architecture: ")
        arch_score = self.evaluate_architecture_response(arch_response)
        
        # Deep dive into specific components
        print(f"\n2. Let's dive deeper into specific components:")
        component_scores = []
        
        for point in scenario["discussion_points"]:
            print(f"\nDiscuss: {point}")
            response = input("Your approach: ")
            score = self.evaluate_system_design_response(response, point)
            component_scores.append(score)
            
        total_score = arch_score + sum(component_scores)
        max_score = 3 + len(component_scores) * 2  # 3 for architecture, 2 per component
        
        return min(total_score, max_score), max_score
        
    def code_review_section(self, duration: int) -> tuple:
        """Code review simulation"""
        print("🔍 CODE REVIEW EXERCISE")
        print()
        print("Review this Python code and identify issues:")
        print()
        
        # Problematic code sample
        code_sample = '''
def get_user_posts(user_id):
    posts = []
    for post in Post.objects.all():
        if post.user_id == user_id:
            posts.append(post)
    return posts

def send_notification(user_id, message):
    user = User.objects.get(id=user_id)
    email = user.email
    send_email(email, message)
    
class APIHandler:
    def handle_request(self, request):
        data = json.loads(request.body)
        user_id = data['user_id']
        result = get_user_posts(user_id)
        return json.dumps(result)
'''
        
        print(code_sample)
        print()
        print("What issues do you see and how would you fix them?")
        
        review_response = input("Your code review: ")
        
        # Expected issues: N+1 query, no error handling, inefficient filtering, 
        # no input validation, direct JSON access without error handling
        issues_found = self.evaluate_code_review(review_response)
        
        print(f"\n📊 Issues identified: {issues_found}/5")
        print("Key issues: N+1 queries, no error handling, inefficient filtering, no input validation")
        
        return issues_found, 5
        
    def questions_section(self, duration: int) -> tuple:
        """Questions for the interviewer"""
        print("❓ Do you have any questions about the role or company?")
        print("(This is important - always ask thoughtful questions!)")
        print()
        
        questions = input("Your questions: ")
        
        score = 1 if len(questions) > 10 else 0
        if any(word in questions.lower() for word in ['team', 'tech', 'challenge', 'growth']):
            score += 1
            
        return score, 2
        
    def evaluate_technical_response(self, response: str, keywords: List[str]) -> int:
        """Evaluate technical response based on keywords"""
        response_lower = response.lower()
        matches = sum(1 for keyword in keywords if keyword in response_lower)
        return min(matches, 3)  # Max 3 points per question
        
    def evaluate_architecture_response(self, response: str) -> int:
        """Evaluate system architecture response"""
        score = 0
        response_lower = response.lower()
        
        # Check for key architectural concepts
        if any(term in response_lower for term in ['load balancer', 'database', 'cache']):
            score += 1
        if any(term in response_lower for term in ['microservice', 'service', 'api']):
            score += 1  
        if any(term in response_lower for term in ['scale', 'scalability', 'performance']):
            score += 1
            
        return score
        
    def evaluate_system_design_response(self, response: str, topic: str) -> int:
        """Evaluate system design component response"""
        score = 0
        response_lower = response.lower()
        
        # Topic-specific evaluations
        if "database" in topic.lower():
            if any(term in response_lower for term in ['sql', 'nosql', 'index', 'schema']):
                score += 1
        elif "caching" in topic.lower():
            if any(term in response_lower for term in ['redis', 'memcached', 'ttl', 'cache']):
                score += 1
        elif "load balancing" in topic.lower():
            if any(term in response_lower for term in ['nginx', 'haproxy', 'round robin', 'health check']):
                score += 1
                
        # General good practices
        if len(response) > 30:  # Detailed response
            score += 1
            
        return min(score, 2)
        
    def evaluate_code_review(self, review: str) -> int:
        """Evaluate code review quality"""
        issues_found = 0
        review_lower = review.lower()
        
        # Check for common issues identification
        if any(term in review_lower for term in ['n+1', 'query', 'inefficient']):
            issues_found += 1
        if any(term in review_lower for term in ['error', 'exception', 'try', 'catch']):
            issues_found += 1
        if any(term in review_lower for term in ['validation', 'input', 'sanitize']):
            issues_found += 1
        if any(term in review_lower for term in ['json', 'parse', 'loads']):
            issues_found += 1
        if any(term in review_lower for term in ['filter', 'objects.filter', 'queryset']):
            issues_found += 1
            
        return issues_found
        
    def provide_interview_feedback(self, score: int, max_score: int):
        """Provide comprehensive interview feedback"""
        percentage = (score / max_score) * 100
        
        print(f"\n🎯 INTERVIEW RESULTS")
        print("=" * 40)
        print(f"Overall Score: {score}/{max_score} ({percentage:.1f}%)")
        
        if percentage >= 80:
            print("🎉 EXCELLENT! You're ready for senior-level interviews.")
            print("Strengths:")
            print("• Strong technical knowledge")
            print("• Good system design thinking")
            print("• Thoughtful code review skills")
        elif percentage >= 65:
            print("👍 GOOD! You're on track with some areas to improve.")
            print("Focus on:")
            print("• Deeper system design discussions")
            print("• More comprehensive technical explanations")
        else:
            print("📚 NEEDS IMPROVEMENT. More practice recommended.")
            print("Priority areas:")
            print("• Review core backend concepts")
            print("• Practice system design fundamentals")
            print("• Improve code review skills")
            
        print(f"\n💡 NEXT STEPS:")
        if percentage < 65:
            print("• Complete more challenges in pattern_practice.py")
            print("• Review backend_systems.py modules")
            print("• Practice explaining technical concepts clearly")
        else:
            print("• Continue with advanced challenges")
            print("• Focus on system design practice")
            print("• Review real-world production issues")
            
    def save_interview_results(self, score: int, max_score: int):
        """Save interview results to progress file"""
        self.progress["last_interview"] = {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "date": datetime.now().isoformat(),
            "type": "full_mock"
        }
        
        if "interview_history" not in self.progress:
            self.progress["interview_history"] = []
            
        self.progress["interview_history"].append(self.progress["last_interview"])
        
        with open("progress.json", "w") as f:
            json.dump(self.progress, f, indent=2)
            
        print("✅ Interview results saved to progress.json")
        
    def technical_interview(self):
        """Technical-only interview"""
        print("🔧 Technical Interview Focus")
        print("This will focus purely on technical knowledge and problem-solving.")
        score, max_score = self.technical_deep_dive(30)
        print(f"Technical Score: {score}/{max_score}")
        
    def system_design_interview(self):
        """System design focused interview"""
        print("🏗️  System Design Interview Focus")
        print("We'll dive deep into system architecture and design.")
        score, max_score = self.system_design_section(45)
        print(f"System Design Score: {score}/{max_score}")
        
    def code_review_interview(self):
        """Code review focused interview"""
        print("🔍 Code Review Interview Focus")
        print("We'll review code and discuss improvements.")
        score, max_score = self.code_review_section(20)
        print(f"Code Review Score: {score}/{max_score}")

def main():
    simulator = InterviewSimulator()
    
    if len(sys.argv) < 2:
        print("Available interview types:")
        print("  --mock          Full mock interview (60 min)")
        print("  --technical     Technical questions only")
        print("  --system        System design focus")
        print("  --review        Code review practice")
        return
        
    interview_type = sys.argv[1].replace("--", "")
    
    if interview_type in simulator.interview_types:
        print(f"🎭 Starting {interview_type} interview simulation...")
        print("Take your time and explain your thought process.\n")
        
        simulator.interview_types[interview_type]()
    else:
        print(f"Unknown interview type: {interview_type}")

if __name__ == "__main__":
    main()