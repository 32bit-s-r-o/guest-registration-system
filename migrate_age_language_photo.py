#!/usr/bin/env python3
"""
Migration script to add age category, language, and photo upload configuration.
This script adds the new fields to existing tables.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the migration to add new fields."""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
    table_prefix = os.getenv('TABLE_PREFIX', 'guest_reg_')
    
    print(f"Connecting to database: {database_url}")
    print(f"Using table prefix: {table_prefix}")
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_prefix}guest' 
                AND column_name = 'age_category'
            """))
            
            if result.fetchone():
                print("✓ age_category column already exists in guest table")
            else:
                print("Adding age_category column to guest table...")
                conn.execute(text(f"""
                    ALTER TABLE {table_prefix}guest 
                    ADD COLUMN age_category VARCHAR(20) NOT NULL DEFAULT 'adult'
                """))
                print("✓ Added age_category column to guest table")
            
            # Check if language column exists in registration table
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_prefix}registration' 
                AND column_name = 'language'
            """))
            
            if result.fetchone():
                print("✓ language column already exists in registration table")
            else:
                print("Adding language column to registration table...")
                conn.execute(text(f"""
                    ALTER TABLE {table_prefix}registration 
                    ADD COLUMN language VARCHAR(10) NOT NULL DEFAULT 'en'
                """))
                print("✓ Added language column to registration table")
            
            # Check if photo upload configuration columns exist in admin table
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_prefix}admin' 
                AND column_name = 'photo_required_adults'
            """))
            
            if result.fetchone():
                print("✓ photo_required_adults column already exists in admin table")
            else:
                print("Adding photo upload configuration columns to admin table...")
                conn.execute(text(f"""
                    ALTER TABLE {table_prefix}admin 
                    ADD COLUMN photo_required_adults BOOLEAN NOT NULL DEFAULT TRUE
                """))
                conn.execute(text(f"""
                    ALTER TABLE {table_prefix}admin 
                    ADD COLUMN photo_required_children BOOLEAN NOT NULL DEFAULT TRUE
                """))
                print("✓ Added photo upload configuration columns to admin table")
            
            # Commit the changes
            conn.commit()
            
            print("\n🎉 Migration completed successfully!")
            print("\nNew features added:")
            print("- Age category selection (adult/child) for guests")
            print("- Language storage for registrations")
            print("- Configurable photo upload requirements based on age")
            print("\nNext steps:")
            print("1. Restart your Flask application")
            print("2. Configure photo upload settings in Admin Settings")
            print("3. Test the new registration form with age categories")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_migration() 