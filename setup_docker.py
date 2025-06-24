#!/usr/bin/env python3
"""
Docker Setup script for Guest Registration System
This script initializes the database and creates the first admin user non-interactively.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db, User

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check required environment variables
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check table prefix
    table_prefix = os.getenv('TABLE_PREFIX', 'guest_reg_')
    print(f"✅ Table prefix configured: {table_prefix}")
    
    print("✅ Environment configuration looks good!")
    return True

def test_database_connection():
    """Test database connection."""
    print("\n🔍 Testing database connection...")
    
    try:
        with app.app_context():
            # Test connection by executing a simple query
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
                result.fetchone()
            print("✅ Database connection successful!")
            
            # Show database info
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   Database: {db_url}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create database tables."""
    print("\n🔨 Creating database tables...")
    
    try:
        with app.app_context():
            # Get table prefix for display
            table_prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
            
            # Create all tables
            db.create_all()
            
            # Get table names
            tables = [
                f"{table_prefix}user",
                f"{table_prefix}amenity", 
                f"{table_prefix}amenity_housekeeper",
                f"{table_prefix}calendar",
                f"{table_prefix}trip",
                f"{table_prefix}registration",
                f"{table_prefix}guest",
                f"{table_prefix}invoice",
                f"{table_prefix}invoice_item",
                f"{table_prefix}housekeeping",
                f"{table_prefix}housekeeping_photo"
            ]
            
            print("✅ Database tables created successfully!")
            print(f"   Tables created: {', '.join(tables)}")
            
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create the first admin user non-interactively."""
    print("\n👤 Creating admin user...")
    
    try:
        with app.app_context():
            # Check if admin already exists (not deleted)
            existing_admin = User.query.filter_by(is_deleted=False).first()
            if existing_admin:
                print(f"✅ Admin user already exists: {existing_admin.username}")
                return True
            
            # Create default admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                # Add some default company information
                company_name='Guest Registration System',
                company_ico='12345678',
                company_vat='CZ12345678',
                contact_name='System Administrator',
                contact_phone='+420 123 456 789',
                contact_address='System Address\nCity 12345\nCountry',
                contact_website='https://example.com',
                contact_description='Default system administrator',
                custom_line_1='Welcome to Guest Registration System',
                custom_line_2='Professional guest management',
                custom_line_3='Secure and reliable'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print(f"   Username: admin")
            print(f"   Email: admin@example.com")
            print(f"   Password: admin123")
            print(f"   Role: admin")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_next_steps():
    """Show next steps after setup."""
    print("\n🎉 Docker setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Access the admin panel:")
    print("   http://localhost:8000/admin/login")
    print("\n2. Login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n3. Create your first amenity and trip!")
    print("\n📚 Additional commands:")
    print("   python manage.py seed     # Add sample data")

def main():
    """Main setup function."""
    print("🚀 Guest Registration System - Docker Setup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    # Create admin user
    if not create_admin_user():
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main() 