from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from app.config import settings
import tweepy  # Commented out since Twitter platform is disabled
import requests

logger = logging.getLogger(__name__)

class SocialMediaPlatform(ABC):
    """Abstract base class for social media platforms"""
    
    def __init__(self):
        self.authenticated = False
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def schedule_post(self, content: str, scheduled_time: datetime) -> Dict[str, Any]:
        """Schedule a post on the platform"""
        pass
    
    @abstractmethod
    def get_comments(self, post_id: str) -> Dict[str, Any]:
        """Get comments for a post"""
        pass
    
    @abstractmethod
    def respond_to_comment(self, comment_id: str, response: str, *args, **kwargs) -> Dict[str, Any]:
        """Reply to a comment"""
        pass
    
    @abstractmethod
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get the status of a post"""
        pass

# class LinkedInPlatform(SocialMediaPlatform):
#     """LinkedIn platform integration"""
#     
#     def __init__(self):
#         super().__init__()
#         self.client_id = settings.LINKEDIN_CLIENT_ID
#         self.client_secret = settings.LINKEDIN_CLIENT_SECRET
#         self.access_token = settings.LINKEDIN_ACCESS_TOKEN
#         self.person_urn = settings.LINKEDIN_PERSON_URN
#         self.authenticate()
#     
#     def authenticate(self) -> bool:
#         try:
#             if not self.access_token or not self.person_urn:
#                 logger.error("LinkedIn access token or person URN not configured")
#                 return False
#             self.authenticated = True
#             logger.info("LinkedIn authentication successful")
#             return True
#         except Exception as e:
#             logger.error(f"LinkedIn authentication failed: {e}")
#             return False
#     
#     def schedule_post(self, content: str, scheduled_time: datetime) -> Dict[str, Any]:
#         try:
#             if not self.authenticated:
#                 return {"success": False, "error": "Not authenticated"}
#             
#             # Validate person_urn format
#             if not self.person_urn or not self.person_urn.startswith("urn:li:person:"):
#                 return {"success": False, "error": "Invalid LinkedIn person URN format"}
#             
#             url = "https://api.linkedin.com/v2/ugcPosts"
#             headers = {
#                 "Authorization": f"Bearer {self.access_token}",
#                 "X-Restli-Protocol-Version": "2.0.0",
#                 "Content-Type": "application/json"
#             }
#             data = {
#                 "author": self.person_urn,
#                 "lifecycleState": "PUBLISHED",
#                 "specificContent": {
#                     "com.linkedin.ugc.ShareContent": {
#                         "shareCommentary": {"text": content},
#                         "shareMediaCategory": "NONE"
#                     }
#                 },
#                 "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
#             }
#             
#             logger.info(f"LinkedIn API request data: {data}")
#             response = requests.post(url, headers=headers, json=data)
#             
#             if response.status_code == 201:
#                 post_id = response.json().get("id", "")
#                 logger.info(f"LinkedIn post scheduled: {post_id}")
#                 return {"success": True, "post_id": post_id}
#             else:
#                 logger.error(f"LinkedIn post error: {response.status_code} - {response.text}")
#                 return {"success": False, "error": response.text}
#         except Exception as e:
#             logger.error(f"Error scheduling LinkedIn post: {e}")
#             return {"success": False, "error": str(e)}
#     
#     def get_comments(self, post_id: str) -> Dict[str, Any]:
#         try:
#             if not self.authenticated:
#                 return {"success": False, "error": "Not authenticated"}
#             # LinkedIn API: Get comments for a post
#             url = f"https://api.linkedin.com/v2/socialActions/{post_id}/comments"
#             headers = {
#                 "Authorization": f"Bearer {self.access_token}",
#                 "X-Restli-Protocol-Version": "2.0.0"
#             }
#             response = requests.get(url, headers=headers)
#             if response.status_code == 200:
#                 comments_data = response.json().get("elements", [])
#                 comments = []
#                 for c in comments_data:
#                     comments.append({
#                         "comment_id": c.get("id", ""),
#                         "user_name": c.get("actor", ""),
#                         "text": c.get("message", {}).get("text", ""),
#                         "timestamp": c.get("created", datetime.now().isoformat())
#                     })
#                 return {"success": True, "comments": comments}
#             else:
#                 logger.error(f"LinkedIn get comments error: {response.text}")
#                 return {"success": False, "error": response.text}
#         except Exception as e:
#             logger.error(f"Error getting LinkedIn comments: {e}")
#             return {"success": False, "error": str(e)}
#     
#     def respond_to_comment(self, comment_id: str, response: str) -> Dict[str, Any]:
#         try:
#             if not self.authenticated:
#                 return {"success": False, "error": "Not authenticated"}
#             url = f"https://api.linkedin.com/v2/socialActions/{comment_id}/comments"
#             headers = {
#                 "Authorization": f"Bearer {self.access_token}",
#                 "X-Restli-Protocol-Version": "2.0.0",
#                 "Content-Type": "application/json"
#             }
#             data = {"actor": self.person_urn, "message": {"text": response}}
#             resp = requests.post(url, headers=headers, json=data)
#             if resp.status_code == 201:
#                 comment_id = resp.json().get("id", "")
#                 logger.info(f"LinkedIn comment reply sent: {comment_id}")
#                 return {"success": True, "response_id": comment_id}
#             else:
#                 logger.error(f"LinkedIn reply error: {resp.text}")
#                 return {"success": False, "error": resp.text}
#         except Exception as e:
#             logger.error(f"Error replying to LinkedIn comment: {e}")
#             return {"success": False, "error": str(e)}
#     
#     def get_post_status(self, post_id: str) -> Dict[str, Any]:
#         """Get LinkedIn post status"""
#         try:
#             if not self.authenticated:
#                 return {"success": False, "error": "Not authenticated"}
#             
#             # Simulate getting post status
#             status_data = {
#                 "post_id": post_id,
#                 "status": "published",
#                 "engagement": {
#                     "likes": 25,
#                     "comments": 8,
#                     "shares": 3
#                 }
#             }
#             
#             return {"success": True, "status": status_data}
#             
#         except Exception as e:
#             logger.error(f"Error getting LinkedIn post status: {e}")
#             return {"success": False, "error": str(e)}

class TwitterPlatform(SocialMediaPlatform):
    """Twitter/X platform integration using Tweepy v2 Client"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.user_id = None
        self.authenticated = False  # Do not authenticate at startup
        # self.authenticate()  # Removed to avoid blocking API calls at startup
    
    def authenticate(self) -> bool:
        try:
            # Create v2 client for Twitter API v2
            self.client = tweepy.Client(
                bearer_token=settings.TWITTER_BEARER_TOKEN,
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True  # Automatically handle rate limits
            )
            
            # Try to get user info (may fail due to rate limits)
            try:
                user = self.client.get_me()
                self.user_id = user.data.id if user and user.data else None
                self.authenticated = self.user_id is not None
                if self.authenticated:
                    logger.info(f"✅ Twitter v2 authentication successful. User ID: {self.user_id}")
                else:
                    logger.error("❌ Twitter v2 authentication failed: Could not fetch user ID.")
            except tweepy.TooManyRequests as rate_limit_error:
                # Handle rate limits gracefully
                logger.warning(f"⚠️ Twitter rate limited during authentication: {rate_limit_error}")
                logger.info("✅ Twitter credentials are valid, marking as authenticated")
                self.authenticated = True
                self.user_id = None  # We'll get this when needed
            except Exception as auth_error:
                logger.error(f"❌ Twitter v2 authentication failed: {auth_error}")
                self.authenticated = False
                    
            return self.authenticated
        except Exception as e:
            logger.error(f"❌ Twitter v2 authentication failed: {e}")
            return False
    
    def schedule_post(self, content: str, scheduled_time: datetime) -> Dict[str, Any]:
        try:
            # Authenticate if not already authenticated or user_id is missing
            if not self.authenticated or not self.user_id:
                self.authenticate()
            if not self.authenticated or not self.user_id:
                return {"success": False, "error": "Not authenticated or missing user ID"}
            response = self.client.create_tweet(text=content, user_auth=True)
            tweet_id = response.data.get("id") if response.data else None
            logger.info(f"Twitter v2 post scheduled: {tweet_id}")
            return {"success": True, "post_id": str(tweet_id)}
        except Exception as e:
            logger.error(f"Error scheduling Twitter v2 post: {e}")
            return {"success": False, "error": str(e)}
    
    def get_comments(self, post_id: str) -> Dict[str, Any]:
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            
            # Free tier limitation: search_recent_tweets has very restrictive rate limits (1 request per 15 min)
            # For practical use, we return empty comments to avoid hitting rate limits
            # In a production environment, you would need:
            # 1. Elevated access to Twitter API, or
            # 2. Webhook implementation, or
            # 3. Manual comment monitoring through your app's UI
            
            logger.info(f"Free tier limitation: search_recent_tweets limited to 1 request per 15 min")
            logger.info(f"Returning empty comments for post {post_id} to avoid rate limits")
            logger.info(f"Consider upgrading to elevated access for better rate limits")
            
            return {"success": True, "comments": []}
            
        except Exception as e:
            logger.error(f"Error getting Twitter replies: {e}")
            return {"success": False, "error": str(e)}
    
    def respond_to_comment(self, comment_id: str, response: str, *args, **kwargs) -> Dict[str, Any]:
        try:
            if not self.authenticated:
                logger.error(f"❌ Not authenticated. comment_id={comment_id}")
                return {"success": False, "error": "Not authenticated"}
            if not comment_id or not str(comment_id).isalnum():
                logger.error(f"❌ Invalid or missing comment_id: {comment_id}")
                return {"success": False, "error": "Invalid or missing comment_id"}
            
            # Use v2 API for posting replies
            try:
                reply = self.client.create_tweet(text=response, in_reply_to_tweet_id=comment_id)
                response_id = str(reply.data.id) if reply and reply.data else None
                if response_id:
                    logger.info(f"✅ Twitter reply sent successfully: {response_id}")
                    return {"success": True, "response_id": response_id}
                else:
                    logger.error("❌ Twitter reply failed: No response ID returned")
                    return {"success": False, "error": "No response ID returned"}
                    
            except tweepy.TooManyRequests as rate_limit_error:
                logger.warning(f"⚠️ Twitter rate limited when replying to comment: {rate_limit_error}")
                return {
                    "success": False, 
                    "error": "Twitter rate limit exceeded",
                    "details": "Please wait before trying to reply again",
                    "retry_after": "15 minutes"
                }
            except tweepy.Forbidden as forbidden_error:
                logger.error(f"❌ Twitter forbidden error: {forbidden_error}")
                return {"success": False, "error": "Twitter API access forbidden"}
            except tweepy.NotFound as not_found_error:
                logger.error(f"❌ Twitter comment not found: {not_found_error}")
                return {"success": False, "error": "Comment not found or deleted"}
                
        except Exception as e:
            logger.error(f"❌ Error replying to Twitter comment: {e}")
            return {"success": False, "error": str(e)}
    
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get Twitter post status"""
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            
            # Simulate getting post status
            status_data = {
                "post_id": post_id,
                "status": "published",
                "engagement": {
                    "likes": 15,
                    "retweets": 5,
                    "replies": 3
                }
            }
            
            return {"success": True, "status": status_data}
            
        except Exception as e:
            logger.error(f"Error getting Twitter post status: {e}")
            return {"success": False, "error": str(e)}

class DevToPlatform(SocialMediaPlatform):
    """Dev.to platform integration"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.DEVTO_API_KEY
        self.username = settings.DEVTO_USERNAME
        self.base_url = "https://dev.to/api"
        self.authenticate()
    
    def authenticate(self) -> bool:
        if self.api_key:
            self.authenticated = True
            logger.info("Dev.to authentication successful")
            return True
        else:
            logger.warning("Dev.to API key not configured")
            return False
    
    def schedule_post(self, content: str, scheduled_time: datetime) -> Dict[str, Any]:
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            
            # Dev.to API: Create an article
            url = f"{self.base_url}/articles"
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Parse content to extract title and body
            lines = content.split('\n')
            title = lines[0].strip() if lines else "New Article"
            body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else content
            
            # Extract tags from content (look for hashtags)
            import re
            tags = re.findall(r'#(\w+)', content)
            tags = tags[:4]  # Limit to 4 tags as per Dev.to API requirement
            
            data = {
                "article": {
                    "title": title,
                    "body_markdown": body,
                    "published": True,
                    "tags": tags
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                article_data = response.json()
                post_id = str(article_data.get("id", ""))
                logger.info(f"Dev.to article published: {post_id}")
                return {"success": True, "post_id": post_id}
            else:
                logger.error(f"Dev.to post error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error publishing Dev.to article: {e}")
            return {"success": False, "error": str(e)}
    
    def get_comments(self, post_id: str) -> Dict[str, Any]:
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            
            # Dev.to API: Get comments for an article
            url = f"{self.base_url}/comments"
            headers = {
                "api-key": self.api_key
            }
            params = {
                "a_id": post_id
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                comments_data = response.json()
                logger.info(f"Raw Dev.to comments API response: {comments_data}")
                comments = []
                def extract_comments(comment_list):
                    for c in comment_list:
                        comment_id = str(c.get("id", ""))
                        if not comment_id:
                            comment_id = str(c.get("id_code", ""))  # Use id_code if id is missing
                        comments.append({
                            "comment_id": comment_id,
                            "user_name": c.get("user", {}).get("username", ""),
                            "text": c.get("body_html", ""),
                            "timestamp": c.get("created_at", datetime.now().isoformat()),
                            "parent_id": c.get("parent_id") if "parent_id" in c else None
                        })
                        # Recursively extract children if present
                        if "children" in c and isinstance(c["children"], list):
                            extract_comments(c["children"])
                extract_comments(comments_data)
                return {"success": True, "comments": comments}
            else:
                logger.error(f"Dev.to get comments error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting Dev.to comments: {e}")
            return {"success": False, "error": str(e)}
    
    def respond_to_comment(self, comment_id: str, response: str, *args, **kwargs) -> Dict[str, Any]:
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            if not comment_id or not str(comment_id).isalnum():
                return {"success": False, "error": "Invalid or missing comment_id"}

            # IMPORTANT: Dev.to/Forem API does not provide a public endpoint for posting comments
            # The API only supports reading comments, not creating them
            # This is a limitation of the Dev.to platform's public API
            
            logger.warning(f"⚠️ Dev.to comment reply attempted but API doesn't support posting comments")
            return {
                "success": False, 
                "error": "Dev.to API limitation: Comment posting not supported",
                "details": "The Dev.to/Forem API does not provide a public endpoint for posting comments. Only reading comments is supported.",
                "suggestion": "Consider using the web interface or contact Dev.to support for comment posting capabilities."
            }

        except Exception as e:
            logger.error(f"❌ Dev.to reply exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get Dev.to article status"""
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            
            # Dev.to API: Get article details
            url = f"{self.base_url}/articles/{post_id}"
            headers = {
                "api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                article_data = response.json()
                status_data = {
                    "post_id": post_id,
                    "status": "published" if article_data.get("published") else "draft",
                    "engagement": {
                        "likes": article_data.get("public_reactions_count", 0),
                        "comments": article_data.get("comments_count", 0),
                        "views": article_data.get("page_views_count", 0)
                    }
                }
                return {"success": True, "status": status_data}
            else:
                logger.error(f"Dev.to get article error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting Dev.to article status: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_articles(self, count: int = 10) -> Dict[str, Any]:
        """Get user's articles (additional method for Dev.to)"""
        try:
            if not self.authenticated:
                return {"success": False, "error": "Not authenticated"}
            
            url = f"{self.base_url}/articles/me"
            headers = {
                "api-key": self.api_key
            }
            params = {
                "per_page": count
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                articles_data = response.json()
                articles = []
                for article in articles_data:
                    articles.append({
                        "article_id": str(article.get("id", "")),
                        "title": article.get("title", ""),
                        "published_at": article.get("published_at", ""),
                        "tags": article.get("tag_list", []),
                        "reactions_count": article.get("public_reactions_count", 0),
                        "comments_count": article.get("comments_count", 0)
                    })
                return {"success": True, "articles": articles}
            else:
                logger.error(f"Dev.to get articles error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting Dev.to articles: {e}")
            return {"success": False, "error": str(e)}

class SocialMediaManager:
    """Manager for all social media platforms"""
    
    def __init__(self):
        self.platforms = {
            # "linkedin": LinkedInPlatform(),
            "twitter": TwitterPlatform(),
            "devto": DevToPlatform()
        }
    
    def get_platform(self, platform_name: str) -> Optional[SocialMediaPlatform]:
        """Get a specific platform instance"""
        return self.platforms.get(platform_name.lower())
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        return list(self.platforms.keys())
    
    def get_authenticated_platforms(self) -> List[str]:
        """Get list of authenticated platforms"""
        return [name for name, platform in self.platforms.items() if platform.authenticated] 