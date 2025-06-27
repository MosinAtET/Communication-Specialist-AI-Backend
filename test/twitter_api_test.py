import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tweepy
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterAPITester:
    """Test class for Twitter API operations using Tweepy v2 Client"""
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )

    def test_authentication(self):
        try:
            logger.info("Testing Twitter v2 authentication...")
            
            try:
                me = self.client.get_me()
                logger.info(f"✅ Twitter v2 authentication successful! Username: {me.data.username}")
                return {"success": True, "username": me.data.username, "api_version": "v2"}
            except Exception as v2_error:
                if "429" in str(v2_error):
                    logger.error(f"❌ Rate limited: {v2_error}")
                    return {"success": False, "error": "Rate limited - try again later"}
                else:
                    logger.error(f"❌ Authentication failed: {v2_error}")
                    return {"success": False, "error": str(v2_error)}
                        
        except Exception as e:
            logger.error(f"❌ Twitter authentication failed: {e}")
            return {"success": False, "error": str(e)}

    def post_tweet(self, text: str):
        try:
            logger.info(f"Posting tweet: {text}")
            response = self.client.create_tweet(text=text)
            tweet_id = response.data.get("id") if response.data else None
            logger.info(f"✅ Tweet posted! Tweet ID: {tweet_id}")
            return {"success": True, "tweet_id": tweet_id}
        except Exception as e:
            logger.error(f"❌ Failed to post tweet: {e}")
            return {"success": False, "error": str(e)}

    def get_tweet_replies(self, tweet_id: str):
        try:
            logger.info(f"Getting replies for tweet ID: {tweet_id}")
            tweet = self.client.get_tweet(tweet_id, tweet_fields=["conversation_id"])
            if not tweet or not tweet.data:
                logger.error("Original tweet not found")
                return {"success": False, "error": "Original tweet not found"}
            conversation_id = tweet.data["conversation_id"]
            me = self.client.get_me()
            query = f"conversation_id:{conversation_id} to:{me.data.username}"
            response = self.client.search_recent_tweets(
                query=query,
                tweet_fields=["author_id", "created_at", "in_reply_to_user_id", "in_reply_to_status_id"],
                max_results=100
            )
            replies = []
            if response.data:
                for t in response.data:
                    if hasattr(t, "in_reply_to_status_id") and str(t.in_reply_to_status_id) == str(tweet_id):
                        user = self.client.get_user(id=t.author_id)
                        replies.append({
                            "comment_id": t.id,
                            "user_name": user.data.username if user and user.data else "",
                            "text": t.text,
                            "timestamp": t.created_at.isoformat() if hasattr(t, "created_at") else ""
                        })
            logger.info(f"✅ Found {len(replies)} replies.")
            return {"success": True, "replies": replies}
        except Exception as e:
            logger.error(f"❌ Error getting tweet replies: {e}")
            return {"success": False, "error": str(e)}

def main():
    tester = TwitterAPITester()
    print("\n--- Twitter API Authentication Test ---")
    print(tester.test_authentication())
    # Uncomment to test posting a tweet
    print("\n--- Post Tweet Test ---")
    print(tester.post_tweet("Hello from TwitterAPITester!"))
    # Uncomment and set a tweet_id to test getting replies
    # tweet_id = "YOUR_TWEET_ID_HERE"
    # print("\n--- Get Tweet Replies Test ---")
    # print(tester.get_tweet_replies(tweet_id))

if __name__ == "__main__":
    main() 