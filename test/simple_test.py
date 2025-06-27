#!/usr/bin/env python3
"""
Simple test to check current state
"""

def test_basic():
    print("🔍 Testing basic functionality")
    print("=" * 30)
    
    try:
        # Test 1: Check if we can import the manager
        print("1. Testing import...")
        import sys
        import os
        sys.path.append('app')
        
        from social_media_platforms import SocialMediaManager
        print("✅ Import successful")
        
        # Test 2: Check available platforms
        print("2. Testing available platforms...")
        manager = SocialMediaManager()
        available = manager.get_available_platforms()
        print(f"✅ Available platforms: {available}")
        
        # Test 3: Check specific platforms
        print("3. Testing specific platforms...")
        linkedin = manager.get_platform("linkedin")
        twitter = manager.get_platform("twitter")
        devto = manager.get_platform("devto")
        
        print(f"   LinkedIn: {'❌ Available' if linkedin else '✅ Not available'}")
        print(f"   Twitter:  {'❌ Available' if twitter else '✅ Not available'}")
        print(f"   Dev.to:   {'✅ Available' if devto else '❌ Not available'}")
        
        # Test 4: Test scheduler filtering
        print("4. Testing scheduler filtering...")
        from scheduler import CommunicationScheduler
        scheduler = CommunicationScheduler()
        
        # Test with all platforms
        result = scheduler.schedule_post("Test post", ["linkedin", "twitter", "devto"])
        
        if result["success"]:
            scheduled_posts = result.get("scheduled_posts", {})
            platforms_scheduled = list(scheduled_posts.keys())
            print(f"✅ Scheduler result: {platforms_scheduled}")
            
            if "devto" in platforms_scheduled and "linkedin" not in platforms_scheduled and "twitter" not in platforms_scheduled:
                print("✅ Scheduler correctly filtered platforms!")
            else:
                print("❌ Scheduler did not filter platforms correctly")
        else:
            print(f"❌ Scheduler failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic() 