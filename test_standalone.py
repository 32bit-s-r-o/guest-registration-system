#!/usr/bin/env python3
"""
Standalone Test Runner for Guest Registration System
Runs tests that don't require HTTP connections
"""

import os
import sys
import subprocess
from pathlib import Path

db_url = os.environ.get('DATABASE_URL', 'sqlite:///guest_registration_test.db')

def run_test(script_name):
    """Run a test script and return success status"""
    try:
        script_path = Path(script_name)
        if not script_path.exists():
            print(f"❌ Script not found: {script_name}")
            return False
        
        print(f"🧪 Running: {script_name}")
        
        # Set up test environment variables for the subprocess
        env = os.environ.copy()
        db_path = os.path.abspath('guest_registration_test.db')
        env['DATABASE_URL'] = f'sqlite:///{db_path}'
        env['TABLE_PREFIX'] = 'test_guest_reg_'
        env['FLASK_ENV'] = 'testing'
        env['TESTING'] = 'true'
        env['BASE_URL'] = 'http://localhost:5001'
        
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=60,
                              env=env)
        
        if result.returncode == 0:
            print(f"✅ {script_name}: PASS")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"❌ {script_name}: FAIL")
            if result.stderr.strip():
                print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {script_name}: ERROR - {e}")
        return False

def main():
    """Run standalone tests"""
    print("🧪 Running Standalone Tests")
    print("=" * 50)

    # Set up test environment variables with absolute path
    db_path = os.path.abspath('guest_registration_test.db')
    test_db_url = f'sqlite:///{db_path}'
    test_table_prefix = 'test_guest_reg_'
    
    # Set environment variables for this process
    os.environ['DATABASE_URL'] = test_db_url
    os.environ['TABLE_PREFIX'] = test_table_prefix
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    os.environ['BASE_URL'] = 'http://localhost:5001'

    # Run migrations to ensure tables exist
    print("🔄 Running migrations to set up test database...")
    print(f"Database URL: {test_db_url}")
    print(f"Table prefix: {test_table_prefix}")
    
    # Run migrations with the correct environment
    env = os.environ.copy()
    env['DATABASE_URL'] = test_db_url
    env['TABLE_PREFIX'] = test_table_prefix
    
    result = subprocess.run([sys.executable, 'migrations.py', 'migrate'], 
                          env=env, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Migrations completed successfully")
        if result.stdout.strip():
            print(result.stdout)
    else:
        print("❌ Migrations failed")
        if result.stderr.strip():
            print(f"STDERR: {result.stderr}")
        if result.stdout.strip():
            print(f"STDOUT: {result.stdout}")

    # Tests that don't require HTTP connections
    standalone_tests = [
        'test_db_connection.py',
        'test_language_picker.py', 
        'test_migration_system.py',
        'test_backup_functionality.py',
        'test_format_date.py',
        'test_date_format_settings.py',
        'test_airbnb_parsing.py',
        'test_airbnb_filtering.py',
        'test_slovak_language.py'
    ]
    
    test_results = {}
    passed_tests = 0
    total_tests = len(standalone_tests)
    
    for test_script in standalone_tests:
        if run_test(test_script):
            test_results[test_script] = "PASS"
            passed_tests += 1
        else:
            test_results[test_script] = "FAIL"
        print("-" * 50)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Standalone Test Results Summary")
    print("=" * 50)
    for test, result in test_results.items():
        status_emoji = "✅" if result == "PASS" else "❌"
        print(f"{status_emoji} {test}: {result}")
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All standalone tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 