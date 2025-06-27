import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging

# Configure logging to show DEBUG and INFO messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from app.scheduler import CommunicationScheduler

# === EDIT THESE VALUES ===
post_id = "P5F3CD641"  # Your internal post ID
platform = "twitter"   # Platform name
platform_post_id = "1938073648717348914"  # The actual tweet ID (from Twitter API response)

if __name__ == "__main__":
    scheduler = CommunicationScheduler()
    print(f"Running manual comment monitor for post_id={post_id}, platform={platform}, platform_post_id={platform_post_id}")
    scheduler._monitor_comments(post_id, platform, platform_post_id)
    print("Done.") 