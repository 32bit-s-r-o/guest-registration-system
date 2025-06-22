#!/usr/bin/env python3
"""
Setup script for Guest Registration System
This script helps initialize the application and create the first admin user.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db, Admin

def create_admin_user():
    """Create the first admin user interactively."""
    print("\n=== Creating Admin User ===")
    print("Please provide the following information for the admin account:")
    
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return False
    
    email = input("Email: ").strip()
    if not email or '@' not in email:
        print("Please provide a valid email address!")
        return False
    
    password = input("Password: ").strip()
    if len(password) < 6:
        print("Password must be at least 6 characters long!")
        return False
    
    confirm_password = input("Confirm Password: ").strip()
    if password != confirm_password:
        print("Passwords do not match!")
        return False
    
    try:
        with app.app_context():
            # Check if admin already exists
            existing_admin = Admin.query.filter_by(username=username).first()
            if existing_admin:
                print(f"Admin user '{username}' already exists!")
                return False
            
            # Create new admin
            admin = Admin(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(admin)
            db.session.commit()
            
            print(f"\n✅ Admin user '{username}' created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def check_database_connection():
    """Check if the database connection is working."""
    print("\n=== Checking Database Connection ===")
    
    try:
        with app.app_context():
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease check your DATABASE_URL in the .env file.")
        return False

def create_tables():
    """Create database tables."""
    print("\n=== Creating Database Tables ===")
    
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def check_environment():
    """Check if environment variables are set."""
    print("\n=== Checking Environment Configuration ===")
    
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return False
    else:
        print("✅ Environment variables configured!")
        return True

def main():
    """Main setup function."""
    print("🚀 Guest Registration System Setup")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        print("\n❌ Setup failed. Please configure your environment variables first.")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("\n❌ Setup failed. Please check your database configuration.")
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        print("\n❌ Setup failed. Could not create database tables.")
        sys.exit(1)
    
    # Create admin user
    if not create_admin_user():
        print("\n❌ Setup failed. Could not create admin user.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nYou can now run the application with:")
    print("python app.py")
    print("\nAccess the admin panel at: http://localhost:5000/admin/login")

if __name__ == "__main__":
    main() 