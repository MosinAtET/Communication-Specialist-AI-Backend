import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.social_media_platforms import DevToPlatform
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_devto_comments():
    """Test Dev.to comment fetching and replying"""
    
    # Test parameters - replace with your actual values
    article_id = "424j"  # Your Dev.to article ID
    
    print(f"Testing Dev.to comments for article ID: {article_id}")
    
    # Create Dev.to platform instance
    devto = DevToPlatform()
    
    # Test authentication
    print("\n1. Testing authentication...")
    if devto.authenticated:
        print("✅ Dev.to authenticated successfully")
    else:
        print("❌ Dev.to authentication failed")
        return
    
    # Test getting comments
    print(f"\n2. Testing get_comments for article {article_id}...")
    comments_result = devto.get_comments(article_id)
    print(f"Comments result: {comments_result}")
    
    if comments_result["success"]:
        comments = comments_result["comments"]
        print(f"Found {len(comments)} comments")
        
        if len(comments) > 0:
            # Test replying to the first comment
            first_comment = comments[0]
            print(f"\n3. Testing reply to comment {first_comment['comment_id']}...")
            
            test_response = "Thank you for your comment! This is an automated response from our AI system."
            reply_result = devto.respond_to_comment(first_comment["comment_id"], test_response)
            print(f"Reply result: {reply_result}")
            
            if reply_result["success"]:
                print("✅ Reply posted successfully!")
            else:
                print(f"❌ Reply failed: {reply_result['error']}")
        else:
            print("⚠️ No comments found to reply to")
            print("Make sure you have comments on your Dev.to article")
    else:
        print(f"❌ Failed to get comments: {comments_result['error']}")

if __name__ == "__main__":
    test_devto_comments() 