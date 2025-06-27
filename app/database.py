from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# SQL Server connection string
# Format: mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://sa:YourPassword@localhost/SocialMediaAI?driver=ODBC+Driver+17+for+SQL+Server"
)

# Create engine with SQL Server specific settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with sample data"""
    db = SessionLocal()
    try:
        # Check if tables exist and have data
        from .models import EventDetails, AIResponses
        
        # Check if EventDetails table has data
        event_count = db.query(EventDetails).count()
        if event_count == 0:
            # Add sample event
            sample_event = EventDetails(
                EventID="EVT001",
                Title="AI in Social Media Marketing Webinar",
                Date="2024-02-15",
                Time="14:00:00",
                Description="Join us for an insightful webinar on leveraging AI for social media marketing strategies.",
                RegistrationLink="https://example.com/register",
                IsRecorded="Yes"
            )
            db.add(sample_event)
        
        # Check if AIResponses table has data
        response_count = db.query(AIResponses).count()
        if response_count == 0:
            # Add sample AI responses
            sample_responses = [
                AIResponses(
                    ResponseID="RESP001",
                    TriggerType="event-related",
                    KeywordMatch="webinar",
                    ResponseText="Thank you for your interest! You can register for our upcoming webinar at {registration_link}. We'd love to see you there!"
                ),
                AIResponses(
                    ResponseID="RESP002",
                    TriggerType="event-related",
                    KeywordMatch="conference",
                    ResponseText="Great question! Our conference '{event_title}' is coming up. You can register at {registration_link}. Looking forward to seeing you!"
                ),
                AIResponses(
                    ResponseID="RESP003",
                    TriggerType="event-related",
                    KeywordMatch="meeting",
                    ResponseText="Thanks for asking! Our meeting '{event_title}' is scheduled. Registration is available at {registration_link}. Hope to see you there!"
                ),
                AIResponses(
                    ResponseID="RESP004",
                    TriggerType="event-related",
                    KeywordMatch="registration",
                    ResponseText="You can register for '{event_title}' at {registration_link}. Let us know if you need any help with the registration process!"
                ),
                AIResponses(
                    ResponseID="RESP005",
                    TriggerType="event-related",
                    KeywordMatch="recording",
                    ResponseText="Great question! This event will {is_recorded}. We'll share the recording with all registered participants after the event."
                ),
                AIResponses(
                    ResponseID="RESP006",
                    TriggerType="accessibility",
                    KeywordMatch="accessibility",
                    ResponseText="We're committed to making our content accessible to everyone. Please let us know if you need any accommodations, and we'll be happy to help!"
                ),
                AIResponses(
                    ResponseID="RESP007",
                    TriggerType="accessibility",
                    KeywordMatch="accommodation",
                    ResponseText="We want to ensure everyone can participate fully. Please contact us directly for any accessibility accommodations you might need."
                ),
                AIResponses(
                    ResponseID="RESP008",
                    TriggerType="off-topic",
                    KeywordMatch="",
                    ResponseText="Thanks for your comment! While this is a bit off-topic for this post, we appreciate your engagement. Feel free to reach out to us directly for any specific questions."
                ),
                AIResponses(
                    ResponseID="RESP009",
                    TriggerType="negative",
                    KeywordMatch="",
                    ResponseText="We appreciate your feedback and take all comments seriously. Please reach out to us directly so we can address your concerns properly."
                ),
                AIResponses(
                    ResponseID="RESP010",
                    TriggerType="spam",
                    KeywordMatch="",
                    ResponseText="Thank you for your comment. We aim to keep our discussions focused and relevant to the topic at hand."
                ),
                AIResponses(
                    ResponseID="RESP011",
                    TriggerType="event-related",
                    KeywordMatch="",
                    ResponseText="Thanks for your interest in '{event_title}'! You can find more details and register at {registration_link}. We'd love to have you join us!"
                )
            ]
            db.add_all(sample_responses)
        
        db.commit()
        print("Database initialized with sample data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close() 