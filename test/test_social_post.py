import sys
import os
from datetime import datetime

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.social_media_platforms import SocialMediaManager
from dotenv import load_dotenv
load_dotenv()

# Test content for posting
test_content = "[TEST] This is a test post to verify API integration. Please ignore."

# Test content for Dev.to (technical blog post format)
test_devto_content = """# Test Article - API Integration Verification

## Introduction

This is a test article to verify the Dev.to API integration with our AI Communication Specialist system.

## Purpose

- Verify API connectivity
- Test content publishing
- Validate authentication
- Check response handling

## Technical Details

The integration supports:
- **Markdown formatting**
- **Tag extraction**
- **Comment monitoring**
- **AI-generated content**

## Conclusion

This test article will be used to verify the complete Dev.to integration workflow.

---
*This is an automated test post - please ignore*

#test #api #integration #automation"""

# Initialize the social media manager
manager = SocialMediaManager()

# Get platform instances
# linkedin = manager.get_platform("linkedin")
twitter = manager.get_platform("twitter")
# devto = manager.get_platform("devto")

print("=== Social Media Platform Testing ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

# print("\n--- Testing LinkedIn Post ---")
# if linkedin and linkedin.authenticated:
#     result = linkedin.schedule_post(test_content, datetime.now())
#     print("LinkedIn Result:", result)
# else:
#     print("LinkedIn authentication failed or not configured.")

print("\n--- Testing Twitter Post ---")
if twitter and twitter.authenticated:
    result = twitter.schedule_post(test_content, datetime.now())
    print("Twitter Result:", result)
else:
    print("Twitter authentication failed or not configured.")

# print("\n--- Testing Dev.to Article ---")
# if devto and devto.authenticated:
#     result = devto.schedule_post(test_devto_content, datetime.now())
#     print("Dev.to Result:", result)
# else:
#     print("Dev.to authentication failed or not configured.")

print("\n--- Platform Status Summary ---")
# platforms = ["linkedin", "twitter", "devto"]
platforms = ["twitter"]
for platform_name in platforms:
    platform = manager.get_platform(platform_name)
    status = "✅ Authenticated" if platform and platform.authenticated else "❌ Not Authenticated"
    print(f"{platform_name.capitalize()}: {status}")

print("\n=== Testing Complete ===") 