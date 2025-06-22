#!/usr/bin/env python3
"""
Migration script to add registration_id column to the invoice table.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import text

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def migrate_invoice_registration():
    """Add registration_id column to invoice table."""
    with app.app_context():
        print("Adding registration_id column to invoice table...")
        
        try:
            # Add the column using raw SQL
            db.session.execute(text("""
                ALTER TABLE guest_reg_invoice 
                ADD COLUMN registration_id INTEGER REFERENCES guest_reg_registration(id)
            """))
            db.session.commit()
            
            print("✅ registration_id column added successfully!")
            
            # Verify the column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'guest_reg_invoice' 
                AND column_name = 'registration_id'
            """))
            
            if result.fetchone():
                print("✅ Column verified in database")
                return True
            else:
                print("❌ Column not found in database")
                return False
                
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Starting invoice registration migration...")
    print("=" * 50)
    
    success = migrate_invoice_registration()
    
    print("=" * 50)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1) 