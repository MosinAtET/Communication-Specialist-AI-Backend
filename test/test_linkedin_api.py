import requests
import json
from datetime import datetime

class LinkedInPostsAPI:
    def __init__(self, access_token):
        """
        Initialize LinkedIn API client with access token
        
        Args:
            access_token (str): LinkedIn API access token
        """
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    def get_user_profile(self):
        """
        Get basic profile information using userinfo endpoint
        
        Returns:
            dict: API response containing profile data
        """
        try:
            # Use userinfo endpoint which works with profile and openid permissions
            profile_url = f"{self.base_url}/userinfo"
            response = requests.get(profile_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'API request failed with status {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_managed_organizations(self):
        """
        Get organizations that the user can manage
        
        Returns:
            dict: API response containing organization data
        """
        try:
            # Get organizations the user can manage
            orgs_url = f"{self.base_url}/organizationAcls"
            params = {
                'q': 'roleAssignee',
                'role': 'ADMINISTRATOR',
                'projection': '(elements*(organization~(id,name,localizedName)))'
            }
            
            response = requests.get(orgs_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'API request failed with status {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_user_posts(self, count=10):
        """
        Get posts for the authenticated user using UGC Posts API
        Note: This requires w_member_social permission
        
        Args:
            count (int): Number of posts to retrieve (max 50)
            
        Returns:
            dict: API response containing posts data
        """
        try:
            # Use UGC Posts API for user posts
            posts_url = f"{self.base_url}/ugcPosts"
            params = {
                'q': 'authors',
                'authors': 'urn:li:person:~',
                'count': min(count, 50),
                'sortBy': 'CREATED_TIME'
            }
            
            response = requests.get(posts_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'API request failed with status {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_organization_posts(self, organization_id, count=10):
        """
        Get posts for an organization using UGC Posts API
        Note: This requires r_organization_social permission
        
        Args:
            organization_id (str): LinkedIn organization ID (numeric)
            count (int): Number of posts to retrieve
            
        Returns:
            dict: API response containing posts data
        """
        try:
            posts_url = f"{self.base_url}/ugcPosts"
            params = {
                'q': 'authors',
                'authors': f'urn:li:organization:{organization_id}',
                'count': min(count, 50),
                'sortBy': 'CREATED_TIME'
            }
            
            response = requests.get(posts_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'API request failed with status {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def create_user_post(self, text_content, visibility="PUBLIC"):
        """
        Create a new post for the authenticated user using UGC Posts API
        Note: This requires w_member_social permission
        
        Args:
            text_content (str): The text content of the post
            visibility (str): Post visibility - "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: API response containing created post data
        """
        try:
            create_url = f"{self.base_url}/ugcPosts"
            
            # Prepare the post data for UGC Posts API
            post_data = {
                "author": "urn:li:company:~",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            response = requests.post(create_url, headers=self.headers, json=post_data)
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message': 'User post created successfully',
                    'data': response.json()
                }
            else:
                return {
                    'error': f'Failed to create user post. Status: {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def create_organization_post(self, organization_id, text_content, visibility="PUBLIC"):
        """
        Create a new post for an organization/company page using UGC Posts API
        Note: This requires w_organization_social permission
        
        Args:
            organization_id (str): LinkedIn organization ID (numeric)
            text_content (str): The text content of the post
            visibility (str): Post visibility - "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: API response containing created post data
        """
        try:
            create_url = f"{self.base_url}/ugcPosts"
            
            # Prepare the post data for organization
            post_data = {
                "author": f"urn:li:organization:{organization_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            response = requests.post(create_url, headers=self.headers, json=post_data)
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message': 'Organization post created successfully',
                    'data': response.json()
                }
            else:
                return {
                    'error': f'Failed to create organization post. Status: {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def create_organization_post_with_link(self, organization_id, text_content, link_url, 
                                         link_title=None, link_description=None, visibility="PUBLIC"):
        """
        Create a new organization post with a shared link using UGC Posts API
        
        Args:
            organization_id (str): LinkedIn organization ID (numeric)
            text_content (str): The text content of the post
            link_url (str): URL to share
            link_title (str): Title for the shared link (optional)
            link_description (str): Description for the shared link (optional)
            visibility (str): Post visibility - "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: API response containing created post data
        """
        try:
            create_url = f"{self.base_url}/ugcPosts"
            
            # Prepare the post data with link
            post_data = {
                "author": f"urn:li:organization:{organization_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text_content
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": link_description or ""
                                },
                                "originalUrl": link_url,
                                "title": {
                                    "text": link_title or link_url
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            response = requests.post(create_url, headers=self.headers, json=post_data)
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message': 'Organization post with link created successfully',
                    'data': response.json()
                }
            else:
                return {
                    'error': f'Failed to create organization post with link. Status: {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_post_by_id(self, post_id):
        """
        Get a specific post by its ID using ugcPosts endpoint
        
        Args:
            post_id (str): LinkedIn UGC post ID
            
        Returns:
            dict: API response containing post data
        """
        try:
            post_url = f"{self.base_url}/ugcPosts/{post_id}"
            response = requests.get(post_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'API request failed with status {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': 'Network error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'error': 'Unexpected error',
                'message': str(e)
            }

def test_linkedin_posts_api():
    """
    Test function to demonstrate LinkedIn Posts API usage
    """
    # LinkedIn API access token
    ACCESS_TOKEN = "AQX_MdktHomXq9zVPTSgnBQkyHTcQEaDKBsBSi2jCol8whDAMiZgwInV8ojKOmlXzPJU7R7Yo9rrTh6wbado77eYJx08rvLZmyCb9V_0wvHvw5nUCPXXzf5CsThDyAjZHXc4tyVGBlQgQaZaQt6Fz6ZuwpBqC_xH7igjjrni5pCUOUE-pfFY5In8juCgmi0gztf5XQm5T651Wdoho_11Rr1TYLdS_cbE5TLKfFRpgWwjke61uCJIwyBfb1XuEhrPE4bjIKF4wbZX1Wu90IHq_wecOZZB_P_Ka8Ui6psgjZXHNiiYv1YnKdDZp95NGyNoybferArK4hbYThdupsvR4VJi3-8IWw"
    
    # Initialize API client
    linkedin_api = LinkedInPostsAPI(ACCESS_TOKEN)
    
    print("=== LinkedIn Posts API Test (Updated) ===\n")
    
    # Test 0: Get user profile first
    print("0. Testing: Get user profile")
    print("-" * 40)
    profile = linkedin_api.get_user_profile()
    
    if 'error' in profile:
        print(f"Error: {profile['error']}")
        print(f"Message: {profile['message']}")
    else:
        print("Successfully retrieved user profile:")
        print(f"  Name: {profile.get('name', 'N/A')}")
        print(f"  Email: {profile.get('email', 'N/A')}")
        print(f"  Picture: {profile.get('picture', 'N/A')}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 1: Get managed organizations
    print("1. Testing: Get managed organizations")
    print("-" * 40)
    organizations = linkedin_api.get_managed_organizations()
    
    org_id = None
    if 'error' in organizations:
        print(f"Error: {organizations['error']}")
        print(f"Message: {organizations['message']}")
    else:
        print(f"Successfully retrieved {len(organizations.get('elements', []))} organizations")
        for i, org in enumerate(organizations.get('elements', [])[:3]):
            org_info = org.get('organization~', {})
            org_id = org_info.get('id')
            print(f"\nOrganization {i+1}:")
            print(f"  ID: {org_id}")
            print(f"  Name: {org_info.get('localizedName', org_info.get('name', 'N/A'))}")
            
            # Store the first organization ID for testing
            if i == 0 and org_id:
                test_org_id = org_id
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Get user posts
    print("2. Testing: Get current user's posts")
    print("-" * 40)
    user_posts = linkedin_api.get_user_posts(count=3)
    
    if 'error' in user_posts:
        print(f"Error: {user_posts['error']}")
        print(f"Message: {user_posts['message']}")
        print("Note: This requires w_member_social permission")
    else:
        print(f"Successfully retrieved {len(user_posts.get('elements', []))} posts")
        for i, post in enumerate(user_posts.get('elements', [])[:3]):
            print(f"\nPost {i+1}:")
            print(f"  ID: {post.get('id', 'N/A')}")
            print(f"  Created: {post.get('created', {}).get('time', 'N/A')}")
            
            # Extract text content
            content = ""
            if 'specificContent' in post:
                share_content = post.get('specificContent', {}).get('com.linkedin.ugc.ShareContent', {})
                share_commentary = share_content.get('shareCommentary', {})
                content = share_commentary.get('text', 'No text content')
            
            text_preview = content[:100] + "..." if len(content) > 100 else content
            print(f"  Content: {text_preview}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Get organization posts (if we have an org ID)
    print("3. Testing: Get organization posts")
    print("-" * 40)
    
    if 'test_org_id' in locals() and test_org_id:
        org_posts = linkedin_api.get_organization_posts(test_org_id, count=3)
        
        if 'error' in org_posts:
            print(f"Error: {org_posts['error']}")
            print(f"Message: {org_posts['message']}")
            print("Note: This requires r_organization_social permission")
        else:
            print(f"Successfully retrieved {len(org_posts.get('elements', []))} organization posts")
            for i, post in enumerate(org_posts.get('elements', [])):
                print(f"\nOrg Post {i+1}:")
                print(f"  ID: {post.get('id', 'N/A')}")
                print(f"  Created: {post.get('created', {}).get('time', 'N/A')}")
                
                # Extract text content
                content = ""
                if 'specificContent' in post:
                    share_content = post.get('specificContent', {}).get('com.linkedin.ugc.ShareContent', {})
                    share_commentary = share_content.get('shareCommentary', {})
                    content = share_commentary.get('text', 'No text content')
                
                text_preview = content[:100] + "..." if len(content) > 100 else content
                print(f"  Content: {text_preview}")
    else:
        print("Skipping organization posts test - no organization ID available")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Create a user post
    print("4. Testing: Create a user post")
    print("-" * 40)
    
    test_user_post_content = f"🚀 Testing LinkedIn API user post creation! This post was created programmatically using Python and the updated LinkedIn UGC Posts API. #LinkedInAPI #Python #Testing\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    user_create_result = linkedin_api.create_user_post(test_user_post_content, visibility="PUBLIC")
    
    if 'error' in user_create_result:
        print(f"Error creating user post: {user_create_result['error']}")
        print(f"Message: {user_create_result['message']}")
        print("Note: This requires w_member_social permission")
    else:
        print("✅ User post created successfully!")
        post_id = user_create_result.get('data', {}).get('id', 'N/A')
        print(f"New Post ID: {post_id}")
        print(f"Content: {test_user_post_content[:100]}...")
    
    print("\n" + "="*50 + "\n")
    
    # Test 5: Create an organization post (if we have an org ID)
    print("5. Testing: Create an organization post")
    print("-" * 40)
    
    if 'test_org_id' in locals() and test_org_id:
        test_org_post_content = f"🏢 Testing LinkedIn API organization post creation! This post was created programmatically for our company page using Python and the LinkedIn UGC Posts API. #LinkedInAPI #CompanyPage #Marketing\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        org_create_result = linkedin_api.create_organization_post(test_org_id, test_org_post_content, visibility="PUBLIC")
        
        if 'error' in org_create_result:
            print(f"Error creating organization post: {org_create_result['error']}")
            print(f"Message: {org_create_result['message']}")
            print("Note: This requires w_organization_social permission")
        else:
            print("✅ Organization post created successfully!")
            org_post_id = org_create_result.get('data', {}).get('id', 'N/A')
            print(f"New Organization Post ID: {org_post_id}")
            print(f"Content: {test_org_post_content[:100]}...")
    else:
        print("Skipping organization post creation - no organization ID available")
    
    print("\n" + "="*50 + "\n")
    
    # Test 6: Create an organization post with link (if we have an org ID)
    print("6. Testing: Create an organization post with link")
    print("-" * 40)
    
    if 'test_org_id' in locals() and test_org_id:
        link_post_content = "Check out this comprehensive guide to LinkedIn API development! 💻 Perfect for developers looking to integrate LinkedIn functionality into their applications. #LinkedInAPI #Development #SocialMedia"
        link_url = "https://docs.microsoft.com/en-us/linkedin/"
        link_title = "LinkedIn API Documentation - Microsoft Learn"
        link_description = "Official LinkedIn API documentation with comprehensive guides, tutorials, and best practices for developers."
        
        org_link_result = linkedin_api.create_organization_post_with_link(
            organization_id=test_org_id,
            text_content=link_post_content,
            link_url=link_url,
            link_title=link_title,
            link_description=link_description,
            visibility="PUBLIC"
        )
        
        if 'error' in org_link_result:
            print(f"Error creating organization post with link: {org_link_result['error']}")
            print(f"Message: {org_link_result['message']}")
            print("Note: This requires w_organization_social permission")
        else:
            print("✅ Organization post with link created successfully!")
            org_link_post_id = org_link_result.get('data', {}).get('id', 'N/A')
            print(f"New Organization Post ID: {org_link_post_id}")
            print(f"Content: {link_post_content}")
            print(f"Shared Link: {link_url}")
    else:
        print("Skipping organization post with link creation - no organization ID available")
    
    print("\n=== Test Complete ===")
    print("\n📝 Summary:")
    print("- ✅ Tested profile retrieval")
    print("- ✅ Tested organization management retrieval")  
    print("- ⚠️  Tested reading user posts (requires w_member_social)")
    print("- ⚠️  Tested reading organization posts (requires r_organization_social)")
    print("- ⚠️  Tested creating user posts (requires w_member_social)")
    print("- ⚠️  Tested creating organization posts (requires w_organization_social)")
    print("- ⚠️  Tested creating organization posts with links (requires w_organization_social)")
    
    print("\n🔑 Required Permissions:")
    print("- r_liteprofile: ✅ (Basic profile access)")
    print("- r_emailaddress: ✅ (Email access)")
    print("- w_member_social: ❌ (Create/read user posts)")
    print("- r_organization_social: ❌ (Read organization posts)")
    print("- w_organization_social: ❌ (Create organization posts)")
    
    print("\n⚠️  Note: The create post tests will actually post to LinkedIn!")
    print("Make sure you're okay with the test content being posted before running.")
    print("\n💡 To get additional permissions:")
    print("1. Go to your LinkedIn Developer App settings")
    print("2. Request additional permissions in the 'Products' section")
    print("3. You may need to apply for LinkedIn Marketing Developer Platform access")
    print("4. Some permissions require LinkedIn review and approval")

if __name__ == "__main__":
    test_linkedin_posts_api()