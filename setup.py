#!/usr/bin/env python3
"""
Setup script for Guest Registration System
This script initializes the database and creates the first admin user.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db, Admin

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check required environment variables
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on config.env.example")
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
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful!")
            
            # Show database info
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   Database: {db_url}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL configuration")
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
                f"{table_prefix}admin",
                f"{table_prefix}trip", 
                f"{table_prefix}registration",
                f"{table_prefix}guest"
            ]
            
            print("✅ Database tables created successfully!")
            print(f"   Tables created: {', '.join(tables)}")
            
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_admin_user():
    """Create the first admin user interactively."""
    print("\n👤 Creating admin user...")
    
    try:
        with app.app_context():
            # Check if admin already exists
            existing_admin = Admin.query.first()
            if existing_admin:
                print(f"✅ Admin user already exists: {existing_admin.username}")
                return True
            
            # Get admin details interactively
            print("Please provide details for the first admin user:")
            
            username = input("Username (default: admin): ").strip() or "admin"
            email = input("Email: ").strip()
            
            if not email:
                print("❌ Email is required!")
                return False
            
            password = input("Password (default: admin123): ").strip() or "admin123"
            
            if len(password) < 6:
                print("❌ Password must be at least 6 characters long!")
                return False
            
            # Create admin user
            admin = Admin(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def show_next_steps():
    """Show next steps after setup."""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the application:")
    print("   python app.py")
    print("\n2. Access the admin panel:")
    print("   http://localhost:5000/admin/login")
    print("\n3. Login with your admin credentials")
    print("\n4. Create your first trip and start collecting registrations!")
    print("\n📚 Additional commands:")
    print("   python reset_data.py seed     # Add sample data")
    print("   python reset_data.py stats    # View database statistics")
    print("   python reset_data.py tables   # View table structure")

def main():
    """Main setup function."""
    print("🚀 Guest Registration System Setup")
    print("=" * 40)
    
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