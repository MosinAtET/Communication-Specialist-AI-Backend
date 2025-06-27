#!/usr/bin/env python3
"""
AI Communication Specialist - Main Entry Point

This script starts the AI Communication Specialist application with both
the API server and the web dashboard.
"""

import uvicorn
import logging
from app.main import app
from app.database import create_tables, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the application"""
    try:
        logger.info("Starting AI Communication Specialist...")
        
        # Create database tables
        logger.info("Initializing database...")
        create_tables()
        init_db()
        
        # Start the FastAPI server
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Shutting down AI Communication Specialist...")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == "__main__":
    main() 