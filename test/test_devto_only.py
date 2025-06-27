#!/usr/bin/env python3
"""
Dev.to Only Test Script

This script tests that only Dev.to is working and LinkedIn/Twitter are disabled.
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_devto_only():
    """Test that only Dev.to is available"""
    print("🧪 Testing Dev.to Only Configuration")
    print("=" * 50)
    
    try:
        from app.social_media_platforms import SocialMediaManager
        
        manager = SocialMediaManager()
        
        # Test available platforms
        available_platforms = manager.get_available_platforms()
        print(f"✅ Available platforms: {available_platforms}")
        
        # Test each platform
        test_platforms = ["linkedin", "twitter", "devto"]
        for platform in test_platforms:
            platform_instance = manager.get_platform(platform)
            if platform == "devto":
                if platform_instance:
                    print(f"✅ {platform.upper()}: Available (as expected)")
                else:
                    print(f"❌ {platform.upper()}: Not available (unexpected)")
            else:
                if platform_instance:
                    print(f"❌ {platform.upper()}: Available (unexpected - should be disabled)")
                else:
                    print(f"✅ {platform.upper()}: Not available (as expected - disabled)")
        
        # Test Dev.to authentication
        devto = manager.get_platform("devto")
        if devto:
            print(f"\n🔗 Testing Dev.to Authentication:")
            if devto.authenticated:
                print("✅ Dev.to: Authenticated successfully")
            else:
                print("⚠️  Dev.to: Not authenticated (check API key)")
        else:
            print("❌ Dev.to: Platform not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_scheduler_config():
    """Test scheduler configuration"""
    print("\n⏰ Testing Scheduler Configuration")
    print("=" * 50)
    
    try:
        from app.scheduler import CommunicationScheduler
        
        scheduler = CommunicationScheduler()
        print("✅ Scheduler initialized successfully")
        
        # Test default platforms
        test_prompt = "Post about AI tomorrow at 2 PM"
        result = scheduler.schedule_post(test_prompt)
        
        if result["success"]:
            print("✅ Post scheduling working")
            print(f"📝 Scheduled posts: {list(result['scheduled_posts'].keys())}")
        else:
            print(f"❌ Post scheduling failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_devto_only()
    test_scheduler_config()
    print("\n🎉 Dev.to only testing completed!") 