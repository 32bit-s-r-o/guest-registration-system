#!/usr/bin/env python3
"""
Migration script to:
1. Rename Admin table to User
2. Add role field to User table
3. Create Housekeeping table
4. Update all foreign key references
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

load_dotenv()

def migrate_to_user_role_system():
    """Migrate from Admin to User role system."""
    
    with app.app_context():
        print("🔄 Starting migration to User role system...")
        
        # Get table prefix
        table_prefix = app.config['TABLE_PREFIX']
        
        try:
            # 1. Create new User table with role field
            print("📋 Creating new User table...")
            db.session.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {table_prefix}user (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(120) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    airbnb_listing_id VARCHAR(100),
                    airbnb_calendar_url TEXT,
                    airbnb_sync_enabled BOOLEAN DEFAULT FALSE,
                    airbnb_last_sync TIMESTAMP,
                    company_name VARCHAR(200),
                    company_ico VARCHAR(50),
                    company_vat VARCHAR(50),
                    contact_name VARCHAR(200),
                    contact_phone VARCHAR(50),
                    contact_address TEXT,
                    contact_website VARCHAR(200),
                    contact_description TEXT,
                    photo_required_adults BOOLEAN DEFAULT TRUE,
                    photo_required_children BOOLEAN DEFAULT TRUE,
                    custom_line_1 VARCHAR(200),
                    custom_line_2 VARCHAR(200),
                    custom_line_3 VARCHAR(200)
                )
            """))
            
            # 2. Copy data from Admin to User table
            print("📋 Copying data from Admin to User table...")
            db.session.execute(text(f"""
                INSERT INTO {table_prefix}user (
                    id, username, email, password_hash, role, created_at,
                    airbnb_listing_id, airbnb_calendar_url, airbnb_sync_enabled, airbnb_last_sync,
                    company_name, company_ico, company_vat, contact_name, contact_phone,
                    contact_address, contact_website, contact_description,
                    photo_required_adults, photo_required_children,
                    custom_line_1, custom_line_2, custom_line_3
                )
                SELECT 
                    id, username, email, password_hash, 'admin' as role, created_at,
                    airbnb_listing_id, airbnb_calendar_url, airbnb_sync_enabled, airbnb_last_sync,
                    company_name, company_ico, company_vat, contact_name, contact_phone,
                    contact_address, contact_website, contact_description,
                    photo_required_adults, photo_required_children,
                    custom_line_1, custom_line_2, custom_line_3
                FROM {table_prefix}admin
                ON CONFLICT (id) DO NOTHING
            """))
            
            # 3. Create Housekeeping table
            print("📋 Creating Housekeeping table...")
            db.session.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {table_prefix}housekeeping (
                    id SERIAL PRIMARY KEY,
                    trip_id INTEGER NOT NULL REFERENCES {table_prefix}trip(id) ON DELETE CASCADE,
                    housekeeper_id INTEGER NOT NULL REFERENCES {table_prefix}user(id) ON DELETE CASCADE,
                    date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    pay_amount DECIMAL(10,2) DEFAULT 0,
                    paid BOOLEAN DEFAULT FALSE,
                    paid_date TIMESTAMP,
                    amenity_photo_path VARCHAR(255),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 4. Update foreign key references in Trip table
            print("📋 Updating Trip table foreign key...")
            db.session.execute(text(f"""
                ALTER TABLE {table_prefix}trip 
                DROP CONSTRAINT IF EXISTS {table_prefix}trip_admin_id_fkey
            """))
            db.session.execute(text(f"""
                ALTER TABLE {table_prefix}trip 
                ADD CONSTRAINT {table_prefix}trip_admin_id_fkey 
                FOREIGN KEY (admin_id) REFERENCES {table_prefix}user(id) ON DELETE CASCADE
            """))
            
            # 5. Update foreign key references in Invoice table
            print("📋 Updating Invoice table foreign key...")
            db.session.execute(text(f"""
                ALTER TABLE {table_prefix}invoice 
                DROP CONSTRAINT IF EXISTS {table_prefix}invoice_admin_id_fkey
            """))
            db.session.execute(text(f"""
                ALTER TABLE {table_prefix}invoice 
                ADD CONSTRAINT {table_prefix}invoice_admin_id_fkey 
                FOREIGN KEY (admin_id) REFERENCES {table_prefix}user(id) ON DELETE CASCADE
            """))
            
            # 6. Create indexes for better performance
            print("📋 Creating indexes...")
            db.session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_prefix}housekeeping_trip_id 
                ON {table_prefix}housekeeping(trip_id)
            """))
            db.session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_prefix}housekeeping_housekeeper_id 
                ON {table_prefix}housekeeping(housekeeper_id)
            """))
            db.session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_prefix}housekeeping_date 
                ON {table_prefix}housekeeping(date)
            """))
            db.session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_prefix}user_role 
                ON {table_prefix}user(role)
            """))
            
            # Commit all changes
            db.session.commit()
            
            print("✅ Migration completed successfully!")
            print("\n📋 Summary of changes:")
            print("   - Created new User table with role field")
            print("   - Copied all data from Admin to User table")
            print("   - Created Housekeeping table for housekeeper management")
            print("   - Updated foreign key references")
            print("   - Created performance indexes")
            print("\n⚠️  Next steps:")
            print("   1. Update your app.py to use User model instead of Admin")
            print("   2. Add role-based access control to your routes")
            print("   3. Create housekeeper-specific routes and templates")
            print("   4. Test the new system thoroughly")
            print("\n💡 You can now safely drop the old Admin table if everything works correctly")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            print("Rolling back changes...")
            
            # Rollback: Drop new tables if they exist
            try:
                db.session.execute(text(f"DROP TABLE IF EXISTS {table_prefix}housekeeping"))
                db.session.execute(text(f"DROP TABLE IF EXISTS {table_prefix}user"))
                db.session.commit()
                print("✅ Rollback completed")
            except Exception as rollback_error:
                print(f"⚠️  Rollback warning: {str(rollback_error)}")
            
            raise

if __name__ == '__main__':
    migrate_to_user_role_system() 