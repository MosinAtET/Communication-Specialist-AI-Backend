#!/usr/bin/env python3
"""
Simple Timezone Test
"""

from datetime import datetime
import pytz

def test_timezone():
    print("🧪 Simple Timezone Test")
    print("=" * 30)
    
    # Test 11:15 AM conversion
    ist = pytz.timezone('Asia/Kolkata')
    utc = pytz.utc
    
    # Create 11:15 AM in IST
    today = datetime.now().date()
    dt_ist = ist.localize(datetime.combine(today, datetime.min.time().replace(hour=11, minute=15)))
    dt_utc = dt_ist.astimezone(utc)
    
    print(f"Input time: 11:15 AM IST")
    print(f"IST datetime: {dt_ist}")
    print(f"UTC datetime: {dt_utc}")
    print(f"UTC time: {dt_utc.strftime('%I:%M %p')}")
    
    # Test the reverse conversion
    dt_utc_parsed = utc.localize(datetime.combine(today, datetime.min.time().replace(hour=11, minute=15)))
    dt_ist_converted = dt_utc_parsed.astimezone(ist)
    
    print(f"\nIf AI returns 11:15 AM as UTC:")
    print(f"UTC datetime: {dt_utc_parsed}")
    print(f"IST converted: {dt_ist_converted}")
    print(f"IST time: {dt_ist_converted.strftime('%I:%M %p')}")

if __name__ == "__main__":
    test_timezone() 