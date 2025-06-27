#!/usr/bin/env python3
"""
Demo script for AI Communication Specialist

This script demonstrates the core functionality of the AI Communication Specialist
without requiring actual API credentials. Configure your .env file for full operation.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ai_agent import AICommunicationAgent
from app.social_media_platforms import SocialMediaManager

def demo_ai_agent():
    """Demonstrate AI agent functionality"""
    print(f"\n🤖 AI Agent Demo")
    print("=" * 50)
    
    try:
        ai_agent = AICommunicationAgent()
        
        # Test date parsing
        test_prompts = [
            "Schedule a post about our July Webinar next Monday at 10 AM",
            "Post about the library conference tomorrow at 2 PM",
            "Create a post for Friday 3 PM about the workshop"
        ]
        
        for prompt in test_prompts:
            print(f"\n📝 Parsing: '{prompt}'")
            result = ai_agent.parse_schedule_request(prompt)
            if result["success"]:
                print(f"✅ Parsed datetime: {result['datetime']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        # Test content generation
        print(f"\n📝 Content Generation Demo")
        print(f"\n📱 Generating content for LINKEDIN:")
        content_result = ai_agent.generate_platform_content("linkedin", {
            "title": "The Future of Public Libraries",
            "description": "Join us for an insightful discussion on the evolving role of libraries in the digital age.",
            "date": "July 5, 2024 at 3:00 PM ET",
            "registration_link": "https://example.com/register"
        })
        
        if content_result["success"]:
            print(f"✅ Content: {content_result['content'][:100]}...")
        else:
            print(f"❌ Error: {content_result['error']}")
        
        # Test comment classification
        print(f"\n💬 Comment Classification Demo")
        test_comments = [
            "Will the webinar be recorded?",
            "Where do I register?",
            "What's for lunch?",
            "This is spam content",
            "The event was terrible"
        ]
        
        for comment in test_comments:
            print(f"\n💭 Classifying: '{comment}'")
            result = ai_agent.classify_comment(comment)
            if result["success"]:
                print(f"✅ Classification: {result['classification']} (confidence: {result.get('confidence', 'N/A')}%)")
            else:
                print(f"❌ Error: {result['error']}")
                
    except Exception as e:
        print(f"❌ Error initializing AI agent: {e}")

def demo_social_media_platforms():
    """Demonstrate social media platform functionality"""
    print(f"\n📱 Social Media Platforms Demo")
    print("=" * 50)
    
    try:
        manager = SocialMediaManager()
        
        # Test platform availability
        # platforms = ["linkedin", "twitter", "devto"]
        platforms = ["devto"]
        for platform in platforms:
            platform_instance = manager.get_platform(platform)
            if platform_instance:
                print(f"✅ {platform.upper()}: Authenticated")
            else:
                print(f"❌ {platform.upper()}: Not configured")
        
        print(f"\nℹ️  Configure API credentials in .env file to enable platform posting")
        
    except Exception as e:
        print(f"❌ Error with social media platforms: {e}")

def main():
    """Main demo function"""
    print("🚀 AI Communication Specialist - Demo")
    print("=" * 60)
    print("This demo shows the core functionality without requiring")
    print("actual API credentials. Configure .env file for full operation.")
    
    # Demo AI Agent
    demo_ai_agent()
    
    # Demo Social Media Platforms
    demo_social_media_platforms()
    
    # Complete Workflow Demo
    print(f"\n🔄 Complete Workflow Demo")
    print("=" * 50)
    print(f"📋 Example Workflow:")
    print(f"1. User prompt: 'Schedule a post about our July Webinar across Social Media Platform next Monday at 10 AM'")
    print(f"2. AI Agent parses date: 'next Monday' → June 23, 2025")
    print(f"3. AI generates platform-specific content")
    print(f"4. Posts scheduled for 10:00 AM")
    print(f"5. Comment monitoring activated (15-min intervals)")
    
    print(f"\n📊 Expected Results:")
    print(f"- Post Scheduling Accuracy: 100%")
    print(f"- Comment Classification Accuracy: ≥90%")
    print(f"- Average Response Time: <2 minutes")
    print(f"- Post Engagement Rate Increase: +20% from baseline")
    
    print(f"\n🎉 Demo completed successfully!")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Copy env.example to .env")
    print(f"2. Configure your API keys and database connection")
    print(f"3. Run 'python run.py' to start the full application")
    print(f"4. Visit http://localhost:8000 for the web dashboard")

if __name__ == "__main__":
    main() 