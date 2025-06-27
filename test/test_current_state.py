#!/usr/bin/env python3
"""
Test Current State Script

This script checks the current state of platforms and scheduled posts.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_platform_availability():
    """Test which platforms are available"""
    print("🔍 Testing platform availability")
    print("=" * 40)
    
    try:
        from app.social_media_platforms import SocialMediaManager
        
        manager = SocialMediaManager()
        available_platforms = manager.get_available_platforms()
        
        print(f"✅ Available platforms: {available_platforms}")
        
        # Test each platform
        test_platforms = ["linkedin", "twitter", "devto"]
        for platform in test_platforms:
            platform_instance = manager.get_platform(platform)
            if platform == "devto":
                if platform_instance:
                    print(f"✅ {platform.upper()}: Available (correct)")
                else:
                    print(f"❌ {platform.upper()}: Not available (incorrect)")
            else:
                if platform_instance:
                    print(f"❌ {platform.upper()}: Available (incorrect - should be disabled)")
                else:
                    print(f"✅ {platform.upper()}: Not available (correct - disabled)")
                    
    except Exception as e:
        print(f"❌ Error testing platforms: {e}")

def test_scheduler_filter():
    """Test if scheduler properly filters platforms"""
    print(f"\n⏰ Testing scheduler platform filtering")
    print("=" * 45)
    
    try:
        from app.scheduler import CommunicationScheduler
        
        scheduler = CommunicationScheduler()
        
        # Test with all platforms
        test_platforms = ["linkedin", "twitter", "devto"]
        print(f"Testing platforms: {test_platforms}")
        
        # This should only process devto
        result = scheduler.schedule_post("Test post", test_platforms)
        
        if result["success"]:
            scheduled_posts = result.get("scheduled_posts", {})
            print(f"✅ Scheduler result: {list(scheduled_posts.keys())}")
            
            if "devto" in scheduled_posts and "linkedin" not in scheduled_posts and "twitter" not in scheduled_posts:
                print("✅ Scheduler correctly filtered platforms!")
            else:
                print("❌ Scheduler did not filter platforms correctly")
        else:
            print(f"❌ Scheduler failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")

if __name__ == "__main__":
    test_platform_availability()
    test_scheduler_filter()
    print(f"\n🎉 Testing completed!") 