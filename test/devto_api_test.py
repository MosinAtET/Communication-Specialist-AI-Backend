import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.config import settings
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevToAPITester:
    """Test class for Dev.to API operations"""
    
    def __init__(self):
        self.api_key = settings.DEVTO_API_KEY
        self.username = settings.DEVTO_USERNAME
        self.base_url = "https://dev.to/api"
        
        if not self.api_key:
            logger.error("Dev.to API key not configured")
            raise ValueError("Dev.to API key is required")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Dev.to API requests"""
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test if the API key is valid by getting user profile"""
        try:
            logger.info("Testing Dev.to authentication...")
            
            # Get user profile information
            url = f"{self.base_url}/users/me"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                logger.info("✅ Dev.to authentication successful!")
                logger.info(f"Username: {profile_data.get('username', '')}")
                logger.info(f"Name: {profile_data.get('name', '')}")
                return {
                    "success": True,
                    "message": "Authentication successful",
                    "profile": profile_data
                }
            else:
                logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication test error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get detailed user profile information"""
        try:
            logger.info("Getting user profile...")
            
            url = f"{self.base_url}/users/me"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                logger.info("✅ User profile retrieved successfully")
                return {
                    "success": True,
                    "profile": profile
                }
            else:
                logger.error(f"❌ Failed to get profile: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_articles(self, count: int = 10) -> Dict[str, Any]:
        """Get user's articles"""
        try:
            logger.info(f"Getting user's articles (limit: {count})...")
            
            url = f"{self.base_url}/articles/me"
            headers = self._get_headers()
            params = {
                "per_page": count
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                articles_data = response.json()
                logger.info(f"✅ Retrieved {len(articles_data)} articles successfully")
                
                # Process articles
                processed_articles = []
                for article in articles_data:
                    processed_article = {
                        "article_id": str(article.get("id", "")),
                        "title": article.get("title", ""),
                        "published_at": article.get("published_at", ""),
                        "tags": article.get("tag_list", []),
                        "reactions_count": article.get("public_reactions_count", 0),
                        "comments_count": article.get("comments_count", 0),
                        "views_count": article.get("page_views_count", 0)
                    }
                    processed_articles.append(processed_article)
                
                return {
                    "success": True,
                    "articles": processed_articles,
                    "total_count": len(processed_articles)
                }
            else:
                logger.error(f"❌ Failed to get articles: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting user articles: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_article_details(self, article_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific article"""
        try:
            logger.info(f"Getting details for article: {article_id}")
            
            url = f"{self.base_url}/articles/{article_id}"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                article_data = response.json()
                logger.info("✅ Article details retrieved successfully")
                
                return {
                    "success": True,
                    "article": article_data
                }
            else:
                logger.error(f"❌ Failed to get article details: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting article details: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_article_comments(self, article_id: str, count: int = 20) -> Dict[str, Any]:
        """Get comments for a specific article"""
        try:
            logger.info(f"Getting comments for article: {article_id}")
            
            url = f"{self.base_url}/comments"
            headers = self._get_headers()
            params = {
                "a_id": article_id
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                comments_data = response.json()
                logger.info(f"✅ Retrieved {len(comments_data)} comments successfully")
                
                # Process comments
                processed_comments = []
                for comment in comments_data:
                    processed_comment = {
                        "comment_id": str(comment.get("id", "")),
                        "user_name": comment.get("user", {}).get("username", ""),
                        "text": comment.get("body_html", ""),
                        "created_at": comment.get("created_at", ""),
                        "reactions_count": comment.get("public_reactions_count", 0)
                    }
                    processed_comments.append(processed_comment)
                
                return {
                    "success": True,
                    "comments": processed_comments,
                    "total_count": len(processed_comments)
                }
            else:
                logger.error(f"❌ Failed to get comments: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting article comments: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_test_article(self) -> Dict[str, Any]:
        """Create a test article to verify posting functionality"""
        try:
            logger.info("Creating test article...")
            
            url = f"{self.base_url}/articles"
            headers = self._get_headers()
            
            # Create a simple test article
            data = {
                "article": {
                    "title": "Test Article - AI Communication Specialist",
                    "body_markdown": """
# Test Article

This is a test article created by the AI Communication Specialist system.

## Features Tested

- Article creation via API
- Markdown formatting
- Tag support

## Next Steps

This article will be used to test comment monitoring and response functionality.

---
*Created automatically for testing purposes*
                    """.strip(),
                    "published": False,  # Create as draft for safety
                    "tags": ["test", "ai", "automation"]
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                article_data = response.json()
                article_id = str(article_data.get("id", ""))
                logger.info(f"✅ Test article created successfully: {article_id}")
                return {
                    "success": True,
                    "article_id": article_id,
                    "article": article_data
                }
            else:
                logger.error(f"❌ Failed to create test article: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating test article: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Dev.to API tests"""
        logger.info("🚀 Starting Dev.to API tests...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Authentication
        logger.info("\n" + "="*50)
        logger.info("TEST 1: Authentication")
        logger.info("="*50)
        auth_result = self.test_authentication()
        results["tests"]["authentication"] = auth_result
        
        if not auth_result["success"]:
            logger.error("❌ Authentication failed. Stopping tests.")
            return results
        
        # Test 2: User Profile
        logger.info("\n" + "="*50)
        logger.info("TEST 2: User Profile")
        logger.info("="*50)
        profile_result = self.get_user_profile()
        results["tests"]["user_profile"] = profile_result
        
        # Test 3: User Articles
        logger.info("\n" + "="*50)
        logger.info("TEST 3: User Articles")
        logger.info("="*50)
        articles_result = self.get_user_articles(count=5)
        results["tests"]["user_articles"] = articles_result
        
        # Test 4: Create Test Article
        logger.info("\n" + "="*50)
        logger.info("TEST 4: Create Test Article")
        logger.info("="*50)
        create_result = self.create_test_article()
        results["tests"]["create_article"] = create_result
        
        # Test 5: Article Comments (if we have an article)
        if articles_result["success"] and articles_result["articles"]:
            logger.info("\n" + "="*50)
            logger.info("TEST 5: Article Comments")
            logger.info("="*50)
            first_article_id = articles_result["articles"][0]["article_id"]
            comments_result = self.get_article_comments(first_article_id, count=5)
            results["tests"]["article_comments"] = comments_result
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("TEST SUMMARY")
        logger.info("="*50)
        
        successful_tests = 0
        total_tests = len(results["tests"])
        
        for test_name, test_result in results["tests"].items():
            status = "✅ PASS" if test_result["success"] else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
            if test_result["success"]:
                successful_tests += 1
        
        logger.info(f"\nOverall: {successful_tests}/{total_tests} tests passed")
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": successful_tests,
            "failed_tests": total_tests - successful_tests
        }
        
        return results

def main():
    """Main function to run Dev.to API tests"""
    try:
        # Check if required environment variables are set
        if not settings.DEVTO_API_KEY:
            logger.error("❌ DEVTO_API_KEY not found in environment variables")
            logger.info("Please set the following environment variables:")
            logger.info("- DEVTO_API_KEY")
            logger.info("- DEVTO_USERNAME (optional)")
            return
        
        # Create tester instance
        tester = DevToAPITester()
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"devto_api_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n📄 Test results saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Error running Dev.to API tests: {e}")

if __name__ == "__main__":
    main() 