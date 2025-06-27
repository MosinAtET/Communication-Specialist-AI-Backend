#!/usr/bin/env python3
"""
Database Test Script for AI Communication Specialist

This script tests the SQL Server database connection and verifies table structure.
"""

import os
import sys
from dotenv import load_dotenv
import pyodbc

load_dotenv()

def test_database_connection():
    """Test the database connection and verify tables exist"""
    
    # Get database connection details from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        return False
    
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
            return False
    else:
        print("Error: DATABASE_URL must start with mssql+pyodbc://")
        return False
    
    # Create connection string for pyodbc
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    
    try:
        # Connect to database
        print(f"Testing connection to SQL Server at {server}...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Test basic query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"SQL Server Version: {version.split()[0]} {version.split()[1]}")
        
        # Check if required tables exist
        required_tables = [
            "EventDetails",
            "SocialMediaPosts", 
            "SocialMediaComments",
            "AIResponses",
            "CommentResponses",
            "AuditLog"
        ]
        
        print("\nChecking required tables...")
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                existing_tables.append(table)
                print(f"✅ {table}: {count} rows")
            except pyodbc.Error:
                missing_tables.append(table)
                print(f"❌ {table}: Not found")
        
        if missing_tables:
            print(f"\n⚠ Missing tables: {', '.join(missing_tables)}")
            print("Run setup_database.py to create the missing tables")
        else:
            print("\n✅ All required tables exist!")
        
        # Test sample queries
        print("\nTesting sample queries...")
        
        # Test EventDetails
        try:
            cursor.execute("SELECT TOP 1 EventID, Title FROM EventDetails")
            event = cursor.fetchone()
            if event:
                print(f"✅ Sample event found: {event[1]}")
            else:
                print("⚠ No events found in EventDetails table")
        except Exception as e:
            print(f"❌ Error querying EventDetails: {e}")
        
        # Test AIResponses
        try:
            cursor.execute("SELECT COUNT(*) FROM AIResponses")
            count = cursor.fetchone()[0]
            print(f"✅ AIResponses table has {count} responses")
        except Exception as e:
            print(f"❌ Error querying AIResponses: {e}")
        
        # Test SocialMediaPosts
        try:
            cursor.execute("SELECT COUNT(*) FROM SocialMediaPosts")
            count = cursor.fetchone()[0]
            print(f"✅ SocialMediaPosts table has {count} posts")
        except Exception as e:
            print(f"❌ Error querying SocialMediaPosts: {e}")
        
        conn.close()
        return True
        
    except pyodbc.Error as e:
        print(f"❌ Database connection error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure SQL Server is running")
        print("2. Verify the DATABASE_URL in your .env file")
        print("3. Check that ODBC Driver 17 for SQL Server is installed")
        print("4. Verify network connectivity to the SQL Server")
        print("5. Check username/password credentials")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection using the application's database module"""
    try:
        print("\nTesting SQLAlchemy connection...")
        from app.database import engine, get_db
        
        # Test engine connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ SQLAlchemy engine connection successful")
        
        # Test session
        db = next(get_db())
        try:
            result = db.execute("SELECT 1")
            print("✅ SQLAlchemy session connection successful")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection error: {e}")
        return False

if __name__ == "__main__":
    print("AI Communication Specialist - Database Test")
    print("=" * 50)
    
    # Test direct pyodbc connection
    pyodbc_success = test_database_connection()
    
    # Test SQLAlchemy connection
    sqlalchemy_success = test_sqlalchemy_connection()
    
    print("\n" + "=" * 50)
    if pyodbc_success and sqlalchemy_success:
        print("🎉 All database tests passed!")
        print("Your database is ready for the AI Communication Specialist application.")
    else:
        print("❌ Some database tests failed.")
        print("Please check your configuration and try again.")
        sys.exit(1) 