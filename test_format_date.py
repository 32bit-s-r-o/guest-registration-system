#!/usr/bin/env python3
"""
Test script to verify the format_date filter works correctly.
"""

import os
import sqlite3

print(f"[DEBUG] DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"[DEBUG] TABLE_PREFIX: {os.environ.get('TABLE_PREFIX')}")

db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('sqlite:///'):
    db_path = db_url.replace('sqlite:///', '')
    if os.path.exists(db_path):
        print(f"[DEBUG] SQLite DB file exists: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_guest_reg_user';")
            row = cur.fetchone()
            if row:
                print("[DEBUG] Table test_guest_reg_user exists in SQLite DB.")
            else:
                print("[DEBUG] Table test_guest_reg_user DOES NOT exist in SQLite DB!")
            conn.close()
        except Exception as e:
            print(f"[DEBUG] Error checking table existence: {e}")
    else:
        print(f"[DEBUG] SQLite DB file does NOT exist: {db_path}")
else:
    print("[DEBUG] Not using SQLite DB.")

# Set up test environment before importing app
def setup_test_environment():
    """Set up test environment variables"""
    # Database configuration with absolute path
    if 'DATABASE_URL' not in os.environ:
        db_path = os.path.abspath('guest_registration_test.db')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    if 'TABLE_PREFIX' not in os.environ:
        os.environ['TABLE_PREFIX'] = 'test_guest_reg_'
    
    # Flask configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'

# Set up test environment
setup_test_environment()

from app import app, db, User
from datetime import date
from flask import render_template_string
from config import Config

def test_format_date_in_template():
    """Test the format_date filter in a template context."""
    with app.app_context():
        try:
            # Create or get test user with default format
            default_user = User.query.filter_by(username='test_format_user').first()
            if not default_user:
                from werkzeug.security import generate_password_hash
                default_user = User(
                    username='test_format_user',
                    email='test_format@example.com',
                    password_hash=generate_password_hash('test123'),
                    role='admin',
                    date_format='d.m.Y'  # Default format
                )
                db.session.add(default_user)
                db.session.commit()
                print("✅ Created test user with default date format")
            
            # Reset to default format for first test
            default_user.date_format = 'd.m.Y'
            db.session.commit()
            
            print(f"Testing with user: {default_user.username} (format: {default_user.date_format})")
            
            # Test direct strftime first
            test_date = date(2025, 3, 26)
            print(f"  Test date type: {type(test_date)}, value: {test_date}")
            # Convert PHP format to Python format for direct test
            py_format = default_user.date_format.replace('d', '%d').replace('m', '%m').replace('Y', '%Y')
            direct_result = test_date.strftime(py_format)
            print(f"  Direct strftime (converted): {test_date} -> {direct_result}")
            
            # Test in template context
            template_string = "{{ test_date|format_date }}"
            
            with app.test_request_context():
                from flask_login import login_user
                login_user(default_user)
                result = render_template_string(template_string, test_date=test_date)
                print(f"  Template result: {test_date} -> {result}")
                
                # Verify template result matches expected format
                expected = '26.03.2025'
                if result == expected:
                    print(f"  ✅ Template formatting correct: {result}")
                else:
                    print(f"  ❌ Template formatting incorrect: expected {expected}, got {result}")
                
            # Test with custom format
            print("\nTesting custom date format...")
            default_user.date_format = 'Y-m-d'
            db.session.commit()
            
            print(f"Testing with user: {default_user.username} (format: {default_user.date_format})")
            # Convert PHP format to Python format for direct test
            py_format = default_user.date_format.replace('Y', '%Y').replace('m', '%m').replace('d', '%d')
            direct_result = test_date.strftime(py_format)
            print(f"  Direct strftime (converted): {test_date} -> {direct_result}")
            
            with app.test_request_context():
                login_user(default_user)
                result = render_template_string(template_string, test_date=test_date)
                print(f"  Template result: {test_date} -> {result}")
                
                # Verify template result matches expected format
                expected = '2025-03-26'
                if result == expected:
                    print(f"  ✅ Template formatting correct: {result}")
                else:
                    print(f"  ❌ Template formatting incorrect: expected {expected}, got {result}")
            
            print("✅ Date formatting tests completed successfully!")
        
        except Exception as e:
            print(f"❌ Error in date format test: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_format_date_in_template() 