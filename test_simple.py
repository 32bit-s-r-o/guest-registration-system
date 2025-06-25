#!/usr/bin/env python3
"""
Simple baseline test to verify test environment is working.
"""

import os
import sys
from datetime import datetime, date

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

def test_basic_functionality():
    """Test basic functionality to ensure environment is working."""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)
    
    # Test 1: Environment variables
    print("1. Testing environment variables...")
    db_url = os.environ.get('DATABASE_URL')
    table_prefix = os.environ.get('TABLE_PREFIX')
    print(f"   DATABASE_URL: {db_url}")
    print(f"   TABLE_PREFIX: {table_prefix}")
    assert db_url is not None, "DATABASE_URL should be set"
    assert table_prefix is not None, "TABLE_PREFIX should be set"
    print("   ✅ Environment variables are set correctly")
    
    # Test 2: Date formatting
    print("\n2. Testing date formatting...")
    test_date = date(2025, 3, 26)
    formats = {
        '%d.%m.%Y': '26.03.2025',
        '%Y-%m-%d': '2025-03-26',
        '%d/%m/%Y': '26/03/2025',
        '%m/%d/%Y': '03/26/2025'
    }
    
    for format_str, expected in formats.items():
        result = test_date.strftime(format_str)
        print(f"   {format_str}: {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    print("   ✅ Date formatting works correctly")
    
    # Test 3: Python path and imports
    print("\n3. Testing Python imports...")
    try:
        import sqlite3
        print("   ✅ sqlite3 imported successfully")
        
        from flask import Flask
        print("   ✅ Flask imported successfully")
        
        # Test database file exists if using SQLite
        if db_url and db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            if os.path.exists(db_path):
                print(f"   ✅ SQLite database file exists: {db_path}")
                
                # Check if we can connect
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
                tables = cur.fetchall()
                conn.close()
                print(f"   ✅ Database contains {len(tables)} table(s)")
            else:
                print(f"   ⚠️ SQLite database file not found: {db_path}")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    print("\n🎉 All basic functionality tests passed!")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1) 