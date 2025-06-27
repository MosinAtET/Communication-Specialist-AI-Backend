#!/usr/bin/env python3
"""
Database Setup Script for AI Communication Specialist

This script helps set up the SQL Server database with the required tables.
"""

import os
import sys
from dotenv import load_dotenv
import pyodbc

load_dotenv()

def create_tables():
    """Create the required database tables"""
    
    # Get database connection details from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    # Parse connection string (simple parsing for mssql+pyodbc://)
    if database_url.startswith("mssql+pyodbc://"):
        # Remove the mssql+pyodbc:// prefix and driver parameter
        connection_string = database_url.replace("mssql+pyodbc://", "")
        # Extract the main connection part
        if "?driver=" in connection_string:
            connection_string = connection_string.split("?driver=")[0]
        
        # Parse username:password@server/database
        if "@" in connection_string:
            auth_part, server_part = connection_string.split("@", 1)
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
            else:
                username = auth_part
                password = ""
            
            if "/" in server_part:
                server, database = server_part.split("/", 1)
            else:
                server = server_part
                database = "master"
        else:
            print("Error: Invalid DATABASE_URL format")
            sys.exit(1)
    else:
        print("Error: DATABASE_URL must start with mssql+pyodbc://")
        sys.exit(1)
    
    # Create connection string for pyodbc
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    
    try:
        # Connect to database
        print(f"Connecting to SQL Server at {server}...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Connected successfully!")
        
        # Create tables
        tables = [
            """
            CREATE TABLE EventDetails (
                EventID VARCHAR(10) PRIMARY KEY,
                Title NVARCHAR(255) NOT NULL,
                Date DATE NOT NULL,
                Time TIME NOT NULL,
                Description NVARCHAR(MAX),
                RegistrationLink NVARCHAR(500),
                IsRecorded NVARCHAR(10) CHECK (IsRecorded IN ('Yes', 'No'))
            )
            """,
            """
            CREATE TABLE SocialMediaPosts (
                PostID VARCHAR(10) PRIMARY KEY,
                Platform NVARCHAR(100) NOT NULL,
                PostDate DATE NOT NULL,
                PostTime TIME NOT NULL,
                ContentPreview NVARCHAR(MAX),
                CampaignTag NVARCHAR(100),
                Status NVARCHAR(50) DEFAULT 'Scheduled',
                EventID VARCHAR(10),
                FOREIGN KEY (EventID) REFERENCES EventDetails(EventID)
            )
            """,
            """
            CREATE TABLE SocialMediaComments (
                CommentID VARCHAR(10) PRIMARY KEY,
                PostID VARCHAR(10),
                UserName NVARCHAR(100),
                CommentText NVARCHAR(MAX),
                Timestamp DATETIME2 DEFAULT GETDATE(),
                ResponseStatus NVARCHAR(50) DEFAULT 'Pending',
                Classification NVARCHAR(100),
                FOREIGN KEY (PostID) REFERENCES SocialMediaPosts(PostID)
            )
            """,
            """
            CREATE TABLE AIResponses (
                ResponseID VARCHAR(10) PRIMARY KEY,
                TriggerType NVARCHAR(100),
                KeywordMatch NVARCHAR(100),
                ResponseText NVARCHAR(MAX)
            )
            """,
            """
            CREATE TABLE CommentResponses (
                ResponseID VARCHAR(10) PRIMARY KEY,
                CommentID VARCHAR(10),
                AIResponseID VARCHAR(10),
                ResponseText NVARCHAR(MAX),
                PlatformResponseID NVARCHAR(100),
                SentAt DATETIME2 DEFAULT GETDATE(),
                Status NVARCHAR(50) DEFAULT 'sent',
                FOREIGN KEY (CommentID) REFERENCES SocialMediaComments(CommentID),
                FOREIGN KEY (AIResponseID) REFERENCES AIResponses(ResponseID)
            )
            """,
            """
            CREATE TABLE AuditLog (
                LogID VARCHAR(10) PRIMARY KEY,
                Action NVARCHAR(100) NOT NULL,
                EntityType NVARCHAR(50) NOT NULL,
                EntityID VARCHAR(10),
                Details NVARCHAR(MAX),
                UserID NVARCHAR(100),
                Timestamp DATETIME2 DEFAULT GETDATE(),
                Status NVARCHAR(50) DEFAULT 'success'
            )
            """
        ]
        
        # Execute table creation
        for i, table_sql in enumerate(tables, 1):
            try:
                print(f"Creating table {i}/6...")
                cursor.execute(table_sql)
                conn.commit()
                print(f"✓ Table {i} created successfully")
            except pyodbc.Error as e:
                if "There is already an object named" in str(e):
                    print(f"⚠ Table {i} already exists, skipping...")
                else:
                    print(f"✗ Error creating table {i}: {e}")
                    conn.rollback()
        
        # Insert sample data
        print("\nInserting sample data...")
        
        # Sample AI responses
        sample_responses = [
            ("RESP001", "event-related", "webinar", "Thank you for your interest! You can register for our upcoming webinar at {registration_link}. We'd love to see you there!"),
            ("RESP002", "accessibility", "accessibility", "We're committed to making our content accessible to everyone. Please let us know if you need any accommodations, and we'll be happy to help!"),
            ("RESP003", "off-topic", "", "Thanks for your comment! While this is a bit off-topic for this post, we appreciate your engagement. Feel free to reach out to us directly for any specific questions.")
        ]
        
        for response_id, trigger_type, keyword_match, response_text in sample_responses:
            try:
                cursor.execute("""
                    INSERT INTO AIResponses (ResponseID, TriggerType, KeywordMatch, ResponseText)
                    VALUES (?, ?, ?, ?)
                """, (response_id, trigger_type, keyword_match, response_text))
                print(f"✓ Added AI response: {trigger_type}")
            except pyodbc.Error as e:
                if "Violation of PRIMARY KEY constraint" in str(e):
                    print(f"⚠ AI response {response_id} already exists, skipping...")
                else:
                    print(f"✗ Error adding AI response: {e}")
        
        # Sample event
        try:
            cursor.execute("""
                INSERT INTO EventDetails (EventID, Title, Date, Time, Description, RegistrationLink, IsRecorded)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("EVT001", "AI in Social Media Marketing Webinar", "2024-02-15", "14:00:00", 
                  "Join us for an insightful webinar on leveraging AI for social media marketing strategies.", 
                  "https://example.com/register", "Yes"))
            print("✓ Added sample event")
        except pyodbc.Error as e:
            if "Violation of PRIMARY KEY constraint" in str(e):
                print("⚠ Sample event already exists, skipping...")
            else:
                print(f"✗ Error adding sample event: {e}")
        
        conn.commit()
        print("\n✅ Database setup completed successfully!")
        
    except pyodbc.Error as e:
        print(f"❌ Database connection error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure SQL Server is running")
        print("2. Verify the DATABASE_URL in your .env file")
        print("3. Check that ODBC Driver 17 for SQL Server is installed")
        print("4. Verify network connectivity to the SQL Server")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("AI Communication Specialist - Database Setup")
    print("=" * 50)
    create_tables() 