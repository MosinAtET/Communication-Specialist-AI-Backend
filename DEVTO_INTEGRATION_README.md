# Dev.to Integration

This document describes the integration of Dev.to as a social media platform in the AI Communication Specialist system.

## Overview

Dev.to is a community of software developers who share articles, discuss the latest in tech, and connect with peers. The integration allows you to:

- ✅ **Publish Articles** - Create and publish technical blog posts
- ✅ **Monitor Comments** - Track comments on your articles
- ✅ **Respond to Comments** - Automatically or manually respond to reader comments
- ✅ **Track Engagement** - Monitor likes, comments, and views
- ✅ **AI-Generated Content** - Generate technical blog posts using AI

## Features

### 1. Article Publishing
- Create technical blog posts with markdown support
- Automatic tag extraction from content
- Support for code blocks and technical formatting
- Draft and published article support

### 2. Comment Management
- Monitor comments on published articles
- AI-powered comment classification
- Automated response generation
- Manual response capabilities

### 3. Content Generation
- AI-generated technical blog posts
- Platform-specific content optimization
- Markdown formatting support
- Technical tone and style

## Setup

### 1. Dev.to API Key

1. Go to [Dev.to Settings](https://dev.to/settings/account)
2. Scroll down to "API Keys" section
3. Generate a new API key
4. Copy the API key to your environment variables

### 2. Environment Variables

Add the following to your `.env` file:

```bash
# Dev.to API Configuration
DEVTO_API_KEY=your_devto_api_key_here
DEVTO_USERNAME=your_devto_username
```

### 3. API Permissions

The Dev.to API key provides access to:
- Read user profile and articles
- Create and update articles
- Read and create comments
- Access article analytics

## Usage

### 1. Schedule a Dev.to Article

```python
from app.social_media_platforms import SocialMediaManager

# Create manager instance
manager = SocialMediaManager()

# Get Dev.to platform
devto = manager.get_platform("devto")

# Schedule an article
result = devto.schedule_post(
    content="# My Technical Article\n\nThis is a technical blog post...",
    scheduled_time=datetime.now()
)
```

### 2. Get User Articles

```python
# Get user's articles
articles_result = devto.get_user_articles(count=10)

if articles_result["success"]:
    for article in articles_result["articles"]:
        print(f"Title: {article['title']}")
        print(f"Views: {article['views_count']}")
        print(f"Comments: {article['comments_count']}")
```

### 3. Monitor Comments

```python
# Get comments for an article
comments_result = devto.get_comments(article_id)

if comments_result["success"]:
    for comment in comments_result["comments"]:
        print(f"User: {comment['user_name']}")
        print(f"Comment: {comment['text']}")
```

## API Endpoints

### Core Endpoints

1. **Authentication**: `GET /api/users/me`
2. **User Articles**: `GET /api/articles/me`
3. **Create Article**: `POST /api/articles`
4. **Get Article**: `GET /api/articles/{id}`
5. **Get Comments**: `GET /api/comments?a_id={article_id}`
6. **Create Comment**: `POST /api/comments`

### Article Structure

```json
{
  "article": {
    "title": "Article Title",
    "body_markdown": "# Markdown Content\n\nArticle body...",
    "published": true,
    "tags": ["tag1", "tag2", "tag3"]
  }
}
```

## Content Generation

### AI-Generated Technical Posts

The system generates Dev.to content with:
- **Technical tone** - Professional and informative
- **Markdown formatting** - Proper headings, code blocks, lists
- **Developer-focused** - Relevant to software developers
- **Engagement optimization** - Encourages comments and discussion

### Example Generated Content

```markdown
# Building Scalable APIs with FastAPI

## Introduction

FastAPI has become the go-to framework for building modern, high-performance APIs in Python. In this article, we'll explore best practices for creating scalable APIs that can handle production workloads.

## Key Features

- **Automatic API documentation**
- **Type hints and validation**
- **Async support out of the box**
- **High performance**

## Why Attend Our Workshop?

Join us for a hands-on workshop where you'll learn:

1. Setting up FastAPI projects
2. Database integration patterns
3. Authentication and authorization
4. Testing strategies
5. Deployment best practices

## Registration

📅 **Date**: January 25, 2025 at 2:00 PM IST
🔗 **Register**: [Event Registration Link]

Don't miss this opportunity to level up your API development skills!

#fastapi #python #api #webdevelopment #workshop
```

## Testing

### Run Dev.to API Tests

```bash
# Test Dev.to API functionality
python test_devto_api.py
```

### Test Results

The test suite will verify:
- ✅ Authentication
- ✅ User profile retrieval
- ✅ Article creation
- ✅ Comment monitoring
- ✅ API response handling

## Integration Points

### 1. Main Application

Dev.to is integrated into the main FastAPI application:
- **Platform selection** in scheduling requests
- **Content generation** with AI
- **Comment monitoring** and response
- **Dashboard integration**

### 2. Scheduler

The scheduler handles:
- **Article publishing** at scheduled times
- **Comment monitoring** for published articles
- **Response generation** and posting

### 3. AI Agent

The AI agent provides:
- **Technical content generation**
- **Comment classification**
- **Response generation**
- **Platform-specific optimization**

## Configuration

### Platform Settings

```python
PLATFORM_CONFIGS = {
    "devto": {
        "tone": "technical",
        "max_length": 5000,
        "hashtag_limit": 8,
        "supports_markdown": True
    }
}
```

### Content Guidelines

- **Length**: 500-1000 words for technical posts
- **Format**: Markdown with proper headings
- **Tone**: Technical and informative
- **Tags**: Up to 8 relevant technical hashtags
- **Structure**: Introduction, content, conclusion, CTA

## Best Practices

### 1. Content Creation

- Use clear, descriptive titles
- Include code examples when relevant
- Add proper markdown formatting
- Use relevant technical tags
- Include call-to-action

### 2. Comment Management

- Respond promptly to technical questions
- Provide helpful, detailed answers
- Use markdown in responses
- Engage with the community

### 3. Analytics

- Monitor article performance
- Track engagement metrics
- Analyze comment patterns
- Optimize content based on data

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify API key is correct
   - Check API key permissions
   - Ensure username is set

2. **Article Creation Failed**
   - Check markdown formatting
   - Verify content length
   - Ensure tags are valid

3. **Comment Retrieval Issues**
   - Verify article ID is correct
   - Check API rate limits
   - Ensure article is published

### Rate Limits

Dev.to API has rate limits:
- **Read requests**: 1000 requests per hour
- **Write requests**: 100 requests per hour
- **Authentication**: No specific limits

## Security

### API Key Management

- Store API keys in environment variables
- Never commit keys to version control
- Rotate keys regularly
- Use least privilege principle

### Data Privacy

- Only access your own content
- Respect user privacy in comments
- Follow Dev.to's terms of service
- Handle data securely

## Future Enhancements

### Planned Features

- **Series support** - Multi-part article series
- **Cross-posting** - Share content across platforms
- **Analytics dashboard** - Detailed performance metrics
- **Comment sentiment analysis** - Advanced comment classification
- **Automated publishing** - Smart scheduling based on engagement

### Integration Opportunities

- **GitHub integration** - Link to repositories
- **Code snippet sharing** - Enhanced code blocks
- **Community engagement** - Automated community interaction
- **Trend analysis** - Content optimization based on trends

## Support

For issues with Dev.to integration:

1. Check the [Dev.to API documentation](https://docs.forem.com/api/)
2. Review the test results and logs
3. Verify environment configuration
4. Test with the provided test scripts

## Contributing

To contribute to Dev.to integration:

1. Follow the existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Test with real Dev.to accounts
5. Follow security best practices 