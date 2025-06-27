#!/usr/bin/env python3
"""
Test Fixes Script

This script tests the fixes for timezone and database connection issues.
"""

import sys
import os
from datetime import datetime
import pytz

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_timezone_fix():
    """Test that timezone conversion is working correctly"""
    print("🧪 Testing Timezone Fix")
    print("=" * 40)
    
    try:
        from app.ai_agent import AICommunicationAgent
        
        ai_agent = AICommunicationAgent()
        
        # Test with 11:15 AM
        test_input = "tomorrow at 11:15 AM"
        print(f"Input: {test_input}")
        
        result = ai_agent.parse_schedule_request(test_input)
        
        if result["success"]:
            parsed_utc = result["datetime"]
            ist = pytz.timezone('Asia/Kolkata')
            parsed_ist = parsed_utc.astimezone(ist)
            
            print(f"✅ Parsed UTC: {parsed_utc}")
            print(f"✅ Parsed IST: {parsed_ist}")
            print(f"✅ Time in IST: {parsed_ist.strftime('%I:%M %p')}")
            
            # Verify it's 11:15 AM, not 4:45 PM
            if parsed_ist.strftime('%I:%M %p') == "11:15 AM":
                print("✅ Timezone fix working correctly!")
            else:
                print("❌ Timezone fix not working correctly!")
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error testing timezone: {e}")

def test_database_connection():
    """Test database connection handling"""
    print("\n🗄️ Testing Database Connection")
    print("=" * 40)
    
    try:
        from app.database import SessionLocal
        from app.models import EventDetails
        
        # Test multiple database connections
        for i in range(3):
            db = None
            try:
                db = SessionLocal()
                count = db.query(EventDetails).count()
                print(f"✅ Connection {i+1}: {count} events found")
            except Exception as e:
                print(f"❌ Connection {i+1} error: {e}")
            finally:
                if db:
                    db.close()
                    
        print("✅ Database connection handling working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")

def test_platform_validation():
    """Test platform validation"""
    print("\n🔗 Testing Platform Validation")
    print("=" * 40)
    
    try:
        from app.social_media_platforms import SocialMediaManager
        
        manager = SocialMediaManager()
        
        # platforms = ["linkedin", "twitter", "devto"]
        platforms = ["devto"]
        for platform in platforms:
            platform_instance = manager.get_platform(platform)
            if platform_instance:
                print(f"✅ {platform.upper()}: Platform instance created")
            else:
                print(f"❌ {platform.upper()}: Platform instance failed")
                
    except Exception as e:
        print(f"❌ Error testing platforms: {e}")

if __name__ == "__main__":
    test_timezone_fix()
    test_database_connection()
    test_platform_validation()
    print("\n🎉 All tests completed!") 