#!/usr/bin/env python3
"""
Migration script to add airbnb_confirm_code column to existing database.
Run this script to update your existing database with the new confirmation code functionality.
"""

import sys
from app import app, db
from sqlalchemy import text

def migrate_confirm_code():
    """Add airbnb_confirm_code column to the trip table if it does not exist."""
    print("🔄 Migrating database to add confirmation code support...")
    try:
        with app.app_context():
            prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
            table_name = f"{prefix}trip"
            # Check if column already exists
            result = db.session.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = 'airbnb_confirm_code'
            """), {"table_name": table_name})
            if result.fetchone():
                print("✅ airbnb_confirm_code column already exists!")
                return True
            # Add the new column
            print(f"📝 Adding airbnb_confirm_code column to {table_name} table...")
            db.session.execute(text(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN airbnb_confirm_code VARCHAR(50) UNIQUE
            """))
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   - Added airbnb_confirm_code column to trip table")
            print("   - Column is VARCHAR(50) with UNIQUE constraint")
            return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            with app.app_context():
                db.session.rollback()
        except Exception:
            pass
        return False

def main():
    print("🔄 Guest Registration System - Database Migration")
    print("=" * 50)
    if not migrate_confirm_code():
        print("\n❌ Migration failed. Please check the error message above.")
        sys.exit(1)
    print("\n🎉 Migration completed successfully!")
    print("You can now:")
    print("1. Run the application: python app.py")
    print("2. Use confirmation code functionality")
    print("3. Sync Airbnb reservations with confirmation codes")

if __name__ == "__main__":
    main() 