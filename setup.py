#!/usr/bin/env python3
"""
AI Communication Specialist - Setup Script

This script helps set up the AI Communication Specialist project
by installing dependencies and creating initial configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n🔧 Creating environment configuration...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation")
            return True
    
    if os.path.exists("env.example"):
        shutil.copy("env.example", ".env")
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys and database credentials")
        return True
    else:
        print("❌ env.example file not found")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["logs", "templates", "static"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def check_database_connection():
    """Check database connection (if configured)"""
    print("\n🗄️  Checking database connection...")
    
    try:
        from app.config import settings
        from app.database import create_tables
        
        if "username:password" in settings.DATABASE_URL:
            print("⚠️  Database URL not configured")
            print("📝 Please update DATABASE_URL in .env file")
            return False
        
        create_tables()
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("📝 Please check your DATABASE_URL configuration")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API keys...")
    
    try:
        from app.config import settings
        
        missing_keys = []
        
        if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_google_api_key_here":
            missing_keys.append("GOOGLE_API_KEY")
        
        if not settings.LINKEDIN_ACCESS_TOKEN or settings.LINKEDIN_ACCESS_TOKEN == "your_linkedin_access_token":
            missing_keys.append("LINKEDIN_ACCESS_TOKEN")
        
        if not settings.TWITTER_ACCESS_TOKEN or settings.TWITTER_ACCESS_TOKEN == "your_twitter_access_token":
            missing_keys.append("TWITTER_ACCESS_TOKEN")
        
        if missing_keys:
            print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
            print("📝 Please configure these in your .env file")
            return False
        else:
            print("✅ All API keys configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking API keys: {e}")
        return False

def run_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test AI agent initialization
        from app.ai_agent import AICommunicationAgent
        ai_agent = AICommunicationAgent()
        print("✅ AI Agent initialized")
        
        # Test scheduler initialization
        from app.scheduler import CommunicationScheduler
        scheduler = CommunicationScheduler()
        print("✅ Scheduler initialized")
        
        # Test social media manager
        from app.social_media_platforms import SocialMediaManager
        manager = SocialMediaManager()
        print("✅ Social Media Manager initialized")
        
        print("✅ All components initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Communication Specialist - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Check database connection
    check_database_connection()
    
    # Check API keys
    check_api_keys()
    
    # Run tests
    run_tests()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your API keys and database credentials")
    print("2. Run 'python test_demo.py' to test functionality")
    print("3. Run 'python run.py' to start the application")
    print("4. Visit http://localhost:8000 for the web dashboard")
    print("5. Visit http://localhost:8000/docs for API documentation")
    
    print("\n📚 Documentation:")
    print("- README.md: Complete project documentation")
    print("- env.example: Configuration template")
    print("- test_demo.py: Functionality demonstration")

if __name__ == "__main__":
    main() 