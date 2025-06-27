import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.social_media_platforms import DevToPlatform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_devto_article():
    """Verify Dev.to article exists and get its details"""
    
    # Test parameters
    article_id = "424j"  # Your Dev.to article ID
    
    print(f"Verifying Dev.to article ID: {article_id}")
    
    # Create Dev.to platform instance
    devto = DevToPlatform()
    
    # Test authentication
    if not devto.authenticated:
        print("❌ Dev.to authentication failed")
        return
    
    print("✅ Dev.to authenticated successfully")
    
    # Get article status
    print(f"\nGetting article details for ID: {article_id}")
    status_result = devto.get_post_status(article_id)
    print(f"Article status result: {status_result}")
    
    if status_result["success"]:
        status_data = status_result["status"]
        print(f"\n📄 Article Details:")
        print(f"   Post ID: {status_data['post_id']}")
        print(f"   Status: {status_data['status']}")
        print(f"   Engagement:")
        print(f"     - Likes: {status_data['engagement']['likes']}")
        print(f"     - Comments: {status_data['engagement']['comments']}")
        print(f"     - Views: {status_data['engagement']['views']}")
        
        if status_data['engagement']['comments'] == 0:
            print(f"\n⚠️ This article has no comments yet.")
            print(f"   To test the reply functionality, you need to:")
            print(f"   1. Go to your Dev.to article")
            print(f"   2. Add a comment manually")
            print(f"   3. Then run the comment monitoring again")
        else:
            print(f"\n✅ Article has {status_data['engagement']['comments']} comments")
            print(f"   Running comment monitoring should work now")
    else:
        print(f"❌ Failed to get article details: {status_result['error']}")
        print(f"   The article ID '{article_id}' might be incorrect")
        print(f"   Check your Dev.to dashboard for the correct article ID")

if __name__ == "__main__":
    verify_devto_article() 