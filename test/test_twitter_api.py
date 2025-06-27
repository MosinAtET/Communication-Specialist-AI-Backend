import sys
import os
from datetime import datetime

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.social_media_platforms import SocialMediaManager
from dotenv import load_dotenv
load_dotenv()

# Test content for posting
test_content = "[TEST] This is a test tweet to verify Twitter API integration. Please ignore."

# Initialize the social media manager
manager = SocialMediaManager()

twitter = manager.get_platform("twitter")

print("=== Twitter API Posting Test ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

print("\n--- Testing Twitter Post ---")
if twitter and twitter.authenticated:
    result = twitter.schedule_post(test_content, datetime.now())
    print("Twitter Result:", result)
else:
    print("Twitter authentication failed or not configured.")

print("\n--- Twitter Platform Status ---")
status = "✅ Authenticated" if twitter and twitter.authenticated else "❌ Not Authenticated"
print(f"Twitter: {status}")

print("\n=== Testing Complete ===") 