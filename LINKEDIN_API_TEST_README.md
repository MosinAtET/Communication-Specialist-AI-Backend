# LinkedIn API Read Test

This module provides comprehensive testing functionality for LinkedIn API read operations. It allows you to verify if your LinkedIn API credentials are working correctly and test various read operations.

## Features

- ✅ **Authentication Testing** - Verify your access token is valid
- ✅ **User Profile Retrieval** - Get your LinkedIn profile information
- ✅ **User Posts Reading** - Retrieve your recent posts
- ✅ **Post Comments Reading** - Get comments for specific posts
- ✅ **Post Details** - Get detailed information about specific posts
- ✅ **Comprehensive Logging** - Detailed logs for debugging
- ✅ **JSON Results Export** - Save test results to JSON files

## Prerequisites

1. **LinkedIn Developer Account**: You need a LinkedIn Developer account
2. **LinkedIn App**: Create a LinkedIn app in the developer console
3. **Access Token**: Generate an access token with appropriate permissions
4. **Person URN**: Your LinkedIn Person URN (optional, but recommended)

## Setup

### 1. Environment Variables

Set the following environment variables in your `.env` file:

```bash
# Required
LINKEDIN_ACCESS_TOKEN=your_access_token_here

# Optional but recommended
LINKEDIN_PERSON_URN=urn:li:person:your_person_id
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

### 2. LinkedIn App Permissions

Make sure your LinkedIn app has the following permissions:
- `r_liteprofile` - Read basic profile
- `r_emailaddress` - Read email address
- `r_basicprofile` - Read basic profile
- `w_member_social` - Write posts and comments
- `r_organization_social` - Read organization posts

## Usage

### Method 1: Run Complete Test Suite

```bash
# Run all tests
python test_linkedin_api.py
```

This will run all available tests and save results to a JSON file.

### Method 2: Use Programmatically

```python
from app.linkedin_api_test import LinkedInAPITester

# Create tester instance
tester = LinkedInAPITester()

# Test authentication
auth_result = tester.test_authentication()
if auth_result["success"]:
    print("✅ Authentication successful!")
    
    # Get user profile
    profile_result = tester.get_user_profile()
    
    # Get user posts
    posts_result = tester.get_user_posts(count=5)
    
    # Get comments for a specific post
    if posts_result["success"] and posts_result["posts"]:
        post_id = posts_result["posts"][0]["post_id"]
        comments_result = tester.get_post_comments(post_id, count=10)
```

### Method 3: Run Example Usage

```bash
python app/linkedin_api_example.py
```

## Test Results

The test suite will provide detailed results including:

- **Authentication Status**: Whether your access token is valid
- **Profile Information**: Your LinkedIn profile details
- **Posts Retrieved**: Number and content of posts found
- **Comments Retrieved**: Number and content of comments found
- **Error Details**: Specific error messages if any tests fail

Results are saved to a JSON file with timestamp: `linkedin_api_test_results_YYYYMMDD_HHMMSS.json`

## API Endpoints Tested

1. **GET /v2/me** - Get user profile
2. **GET /v2/ugcPosts** - Get user posts
3. **GET /v2/ugcPosts/{post_id}** - Get specific post details
4. **GET /v2/socialActions/{post_id}/comments** - Get post comments

## Troubleshooting

### Common Issues

1. **"Access token not configured"**
   - Make sure `LINKEDIN_ACCESS_TOKEN` is set in your environment variables

2. **"Authentication failed: 401 Unauthorized"**
   - Your access token may be expired or invalid
   - Generate a new access token from LinkedIn Developer Console

3. **"Failed to get posts: 403 Forbidden"**
   - Your app may not have the required permissions
   - Check your LinkedIn app permissions in the developer console

4. **"No posts found"**
   - You may not have any posts, or the Person URN may be incorrect
   - Verify your `LINKEDIN_PERSON_URN` is correct

### Getting Your Person URN

1. Go to your LinkedIn profile
2. View page source
3. Search for `"publicIdentifier"`
4. Your Person URN format: `urn:li:person:your_public_identifier`

### Getting Access Token

1. Go to [LinkedIn Developer Console](https://www.linkedin.com/developers/)
2. Create or select your app
3. Go to "Auth" tab
4. Generate access token with required permissions
5. Copy the token to your environment variables

## File Structure

```
app/
├── linkedin_api_test.py      # Main test class
├── linkedin_api_example.py   # Example usage
└── config.py                 # Configuration settings

test_linkedin_api.py          # Simple test runner
LINKEDIN_API_TEST_README.md   # This file
```

## Example Output

```
🚀 Starting LinkedIn API read tests...

==================================================
TEST 1: Authentication
==================================================
Testing LinkedIn authentication...
✅ LinkedIn authentication successful!
Profile: John Doe

==================================================
TEST 2: User Profile
==================================================
Getting user profile...
✅ User profile retrieved successfully

==================================================
TEST 3: User Posts
==================================================
Getting user's recent posts (limit: 5)...
✅ Retrieved 3 posts successfully

==================================================
TEST 4: Post Comments
==================================================
Getting comments for post: urn:li:activity:1234567890
✅ Retrieved 2 comments successfully

==================================================
TEST SUMMARY
==================================================
authentication: ✅ PASS
user_profile: ✅ PASS
user_posts: ✅ PASS
post_comments: ✅ PASS

Overall: 4/4 tests passed

📄 Test results saved to: linkedin_api_test_results_20241201_143022.json
```

## Security Notes

- Never commit your access tokens to version control
- Use environment variables for sensitive data
- Regularly rotate your access tokens
- Monitor your API usage to stay within rate limits

## Rate Limits

LinkedIn API has rate limits:
- 100 requests per day for basic profile
- 100 requests per day for posts
- 100 requests per day for comments

Monitor your usage in the LinkedIn Developer Console. 