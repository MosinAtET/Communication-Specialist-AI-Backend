import os
from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://sa:YourPassword@localhost/SocialMediaAI?driver=ODBC+Driver+17+for+SQL+Server"
    )
    
    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Social Media API Keys
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_PERSON_URN: str = os.getenv("LINKEDIN_PERSON_URN", "")
    
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # Dev.to API Configuration
    DEVTO_API_KEY: str = os.getenv("DEVTO_API_KEY", "")
    DEVTO_USERNAME: str = os.getenv("DEVTO_USERNAME", "")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Platform configurations
    PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
        "linkedin": {
            "tone": "professional",
            "max_length": 500,
            "hashtag_limit": 5
        },
        "twitter": {
            "tone": "conversational",
            "max_length": 280,
            "hashtag_limit": 3
        },
        "devto": {
            "tone": "technical",
            "max_length": 500,
            "hashtag_limit": 4,
            "supports_markdown": True
        }
    }
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings() 