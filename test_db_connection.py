#!/usr/bin/env python3
"""
Test database connection script
"""

import os
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()

def get_database_url():
    """Construct database URL from environment variables or use default."""
    # Check if DATABASE_URL is explicitly set
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # If it contains Docker-style variable substitution, handle it
        if '${POSTGRES_PASSWORD:-postgres}' in database_url:
            postgres_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
            database_url = database_url.replace('${POSTGRES_PASSWORD:-postgres}', postgres_password)
        return database_url
    
    # Default to SQLite for test suite
    return 'sqlite:///guest_registration_test.db'

def test_connection():
    """Test database connection."""
    try:
        from sqlalchemy import create_engine, text
        
        # Get the database URL
        db_url = get_database_url()
        print(f"Database URL: {db_url}")
        
        # Create engine and test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing database connection...")
    print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD', 'postgres')}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print()
    
    success = test_connection()
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify the connection details in your .env file")
        print("3. Make sure the database exists")
        print("4. Check firewall settings if connecting to remote database")
        print("5. Verify the POSTGRES_PASSWORD environment variable is set") 