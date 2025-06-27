# Social Media AI Communication Specialist

An intelligent agent to autonomously handle social media content creation, scheduling, and interaction management across LinkedIn and Twitter/X.

## Features

- **AI-Powered Content Generation**: Create engaging, platform-optimized content using Google's Gemini AI
- **Multi-Platform Support**: Automatically generate platform-optimized content for LinkedIn and Twitter/X
- **Smart Scheduling**: Natural language parsing for scheduling posts (e.g., "post tomorrow at 2 PM")
- **Comment Management**: AI-powered comment classification and automated responses
- **Database Integration**: SQL Server backend with comprehensive audit logging
- **Web Dashboard**: User-friendly interface for content management and monitoring
- **RESTful API**: Full API for integration with other systems

## Architecture

The system consists of several key components:

1. **AI Agent** (`app/ai_agent.py`): Handles content generation and natural language processing
2. **Social Media Platforms** (`app/social_media_platforms.py`): Platform-specific integrations
3. **Scheduler** (`app/scheduler.py`): Manages post scheduling and execution
4. **Database Models** (`app/models.py`): SQL Server schema definitions
5. **FastAPI Application** (`app/main.py`): REST API and web interface
6. **Dashboard** (`app/dashboard.py`): Web-based management interface

## Prerequisites

- Python 3.8+
- SQL Server (with ODBC Driver 17)
- Google AI API key
- Social media API credentials:
  1. **LinkedIn**: Set up a LinkedIn app with appropriate permissions
  2. **Twitter/X**: Configure Twitter API v2 credentials

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SocialMediaAI
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and database configuration
   ```

5. **Configure database**:
   ```bash
   python setup.py
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/SocialMediaAI?driver=ODBC+Driver+17+for+SQL+Server

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Twitter/X API Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### API Key Setup

1. **Google AI**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **LinkedIn**: Configure LinkedIn Graph API
3. **Twitter/X**: Configure Twitter API v2

## Usage

### Web Dashboard

Access the dashboard at `http://localhost:8000` to:
- Generate and schedule posts
- Monitor post performance
- Manage comments and responses
- View analytics

### API Endpoints

#### Generate Content
```bash
POST /api/generate-content
{
    "prompt": "Create a post about AI trends",
    "platforms": ["linkedin", "twitter"]
}
```

#### Schedule Post
```bash
POST /api/schedule-post
{
    "prompt": "Post about our new product launch tomorrow at 10 AM",
    "platforms": ["linkedin", "twitter"]
}
```

#### Get Post Status
```bash
GET /api/posts/{post_id}/status
```

#### Respond to Comments
```bash
POST /api/comments/{comment_id}/respond
{
    "response": "Thank you for your feedback!"
}
```

## Database Schema

The system uses SQL Server with the following tables:

- **EventDetails**: Calendar events and scheduling information
- **SocialMediaPosts**: Post content, scheduling, and status
- **SocialMediaComments**: Comment tracking and classification
- **AIResponses**: AI-generated responses and audit trail

## Content Generation

The AI agent generates platform-optimized content with:

- **Tone**: Professional (LinkedIn), Conversational (Twitter)
- **Length**: Optimized for each platform's character limits
- **Hashtags**: Platform-appropriate hashtag usage
- **Formatting**: Platform-specific formatting requirements

## Scheduling

Posts can be scheduled using natural language:
- "Post tomorrow at 2 PM"
- "Schedule for next Friday at 10 AM"
- "Post in 3 hours"

## Comment Management

The system automatically:
- Monitors comments on published posts
- Classifies comments by sentiment and intent
- Generates appropriate responses
- Tracks engagement metrics

## Development

### Running Tests
```bash
python test_demo.py
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 