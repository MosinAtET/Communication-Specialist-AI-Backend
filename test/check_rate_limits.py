import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tweepy
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_rate_limits():
    """Check Twitter API rate limits"""
    try:
        client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # Try to get rate limit info (this might also be rate limited)
        try:
            # Get user info to check authentication and rate limits
            me = client.get_me()
            print("✅ Authentication successful!")
            print(f"Username: {me.data.username}")
            print("Rate limits should reset in 15 minutes from now.")
        except Exception as e:
            if "429" in str(e):
                print("❌ Rate limited! You need to wait for limits to reset.")
                print("Twitter rate limits typically reset every 15 minutes.")
            else:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    print("Checking Twitter API rate limits...")
    check_rate_limits() 