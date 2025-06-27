#!/usr/bin/env python3
"""
Timezone Test Script

This script tests the timezone handling and date parsing logic.
"""

import sys
import os
from datetime import datetime
import pytz

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.ai_agent import AICommunicationAgent

def test_timezone_parsing():
    """Test timezone parsing with various inputs"""
    print("🧪 Testing Timezone Parsing")
    print("=" * 50)
    
    try:
        ai_agent = AICommunicationAgent()
        
        # Test cases
        test_cases = [
            "tomorrow at 11:15 AM",
            "next Monday at 2:30 PM", 
            "Friday 9:00 AM",
            "post at 3:45 PM"
        ]
        
        for test_input in test_cases:
            print(f"\n📝 Testing: '{test_input}'")
            result = ai_agent.parse_schedule_request(test_input)
            
            if result["success"]:
                parsed_utc = result["datetime"]
                ist = pytz.timezone('Asia/Kolkata')
                parsed_ist = parsed_utc.astimezone(ist)
                
                print(f"✅ Parsed UTC: {parsed_utc}")
                print(f"✅ Parsed IST: {parsed_ist}")
                print(f"✅ Time in IST: {parsed_ist.strftime('%I:%M %p')}")
            else:
                print(f"❌ Error: {result['error']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def test_timezone_conversion():
    """Test direct timezone conversions"""
    print("\n🔄 Testing Direct Timezone Conversions")
    print("=" * 50)
    
    ist = pytz.timezone('Asia/Kolkata')
    utc = pytz.utc
    
    # Test cases
    test_times = [
        ("11:15 AM", "11:15"),
        ("2:30 PM", "14:30"),
        ("9:00 AM", "09:00"),
        ("3:45 PM", "15:45")
    ]
    
    for time_str, expected_24h in test_times:
        print(f"\n⏰ Testing: {time_str}")
        
        # Parse 12-hour format to 24-hour
        if "PM" in time_str.upper() and not time_str.startswith("12"):
            hour = int(time_str.split(":")[0]) + 12
        else:
            hour = int(time_str.split(":")[0])
            if hour == 12 and "AM" in time_str.upper():
                hour = 0
        
        minute = int(time_str.split(":")[1].split()[0])
        
        # Create datetime in IST
        today = datetime.now().date()
        dt_ist = ist.localize(datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)))
        dt_utc = dt_ist.astimezone(utc)
        
        print(f"✅ IST: {dt_ist.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"✅ UTC: {dt_utc.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"✅ 24h: {dt_ist.strftime('%H:%M')}")

if __name__ == "__main__":
    test_timezone_parsing()
    test_timezone_conversion()
    print("\n🎉 Timezone testing completed!") 