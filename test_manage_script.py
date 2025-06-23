#!/usr/bin/env python3
"""
Test script for the universal management script
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def log_test(test_name, status, message=""):
    """Log test result"""
    emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"{emoji.get(status, '❓')} {test_name}: {status}")
    if message:
        print(f"   └─ {message}")

def test_script_exists():
    """Test that manage.py exists"""
    if os.path.exists("manage.py"):
        return True, "manage.py found"
    else:
        return False, "manage.py not found"

def test_help_command():
    """Test help command"""
    try:
        result = subprocess.run([sys.executable, "manage.py", "--help"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and "Universal Management Script" in result.stdout:
            return True, "Help command works"
        else:
            return False, f"Help command failed: {result.stderr}"
    except Exception as e:
        return False, f"Help command exception: {e}"

def test_status_command():
    """Test status command"""
    try:
        result = subprocess.run([sys.executable, "manage.py", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and "System Status" in result.stdout:
            return True, "Status command works"
        else:
            return False, f"Status command failed: {result.stderr}"
    except Exception as e:
        return False, f"Status command exception: {e}"

def test_migration_status():
    """Test migration status command"""
    try:
        result = subprocess.run([sys.executable, "manage.py", "migrate", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and "Migration Status" in result.stdout:
            return True, "Migration status works"
        else:
            return False, f"Migration status failed: {result.stderr}"
    except Exception as e:
        return False, f"Migration status exception: {e}"

def test_cleanup_command():
    """Test cleanup command"""
    try:
        # Create a temporary file to clean up
        with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as f:
            temp_file = f.name
        
        result = subprocess.run([sys.executable, "manage.py", "clean"], 
                              capture_output=True, text=True, timeout=30)
        
        # Check if temp file was cleaned up
        file_cleaned = not os.path.exists(temp_file)
        
        if result.returncode == 0 and "Cleanup completed" in result.stdout:
            return True, f"Cleanup works (file cleaned: {file_cleaned})"
        else:
            return False, f"Cleanup failed: {result.stderr}"
    except Exception as e:
        return False, f"Cleanup exception: {e}"

def test_invalid_command():
    """Test invalid command handling"""
    try:
        result = subprocess.run([sys.executable, "manage.py", "invalid_command"], 
                              capture_output=True, text=True, timeout=30)
        # Check that the command failed (non-zero return code)
        if result.returncode != 0:
            return True, "Invalid command properly rejected"
        else:
            return False, "Invalid command not properly handled"
    except Exception as e:
        return False, f"Invalid command test exception: {e}"

def test_script_import():
    """Test that manage.py can be imported"""
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Import the SystemManager class
        from manage import SystemManager
        
        # Create instance
        manager = SystemManager()
        
        return True, "Script imports successfully"
    except Exception as e:
        return False, f"Script import failed: {e}"

def test_available_commands():
    """Test that all expected commands are available"""
    try:
        from manage import SystemManager
        manager = SystemManager()
        
        expected_commands = ['test', 'migrate', 'seed', 'backup', 'utility', 'status', 'clean', 'setup', 'all']
        
        for cmd in expected_commands:
            if cmd not in manager.available_commands:
                return False, f"Missing command: {cmd}"
        
        return True, f"All {len(expected_commands)} commands available"
    except Exception as e:
        return False, f"Command availability test failed: {e}"

def test_script_categories():
    """Test that script categories are properly defined"""
    try:
        from manage import SystemManager
        manager = SystemManager()
        
        expected_categories = ['tests', 'migrations', 'seeds', 'backups', 'utilities']
        
        for category in expected_categories:
            if category not in manager.scripts:
                return False, f"Missing category: {category}"
        
        return True, f"All {len(expected_categories)} categories defined"
    except Exception as e:
        return False, f"Script categories test failed: {e}"

def main():
    """Run all management script tests"""
    print("🧪 Testing Universal Management Script")
    print("=" * 60)
    
    tests = [
        ("Script Exists", test_script_exists),
        ("Script Import", test_script_import),
        ("Available Commands", test_available_commands),
        ("Script Categories", test_script_categories),
        ("Help Command", test_help_command),
        ("Status Command", test_status_command),
        ("Migration Status", test_migration_status),
        ("Cleanup Command", test_cleanup_command),
        ("Invalid Command", test_invalid_command),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            log_test(test_name, "PASS" if success else "FAIL", message)
            if success:
                passed += 1
        except Exception as e:
            log_test(test_name, "FAIL", f"Exception: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Management Script Test Summary")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All management script tests passed!")
        print("✅ Universal management script is ready for use")
        
        print("\n🚀 Available Commands:")
        print("  python manage.py test                    # Run all tests")
        print("  python manage.py migrate status          # Check migration status")
        print("  python manage.py migrate migrate         # Run pending migrations")
        print("  python manage.py seed                    # Run seed operations")
        print("  python manage.py backup                  # Run backup operations")
        print("  python manage.py utility                 # List available utilities")
        print("  python manage.py status                  # Show system status")
        print("  python manage.py clean                   # Clean up temporary files")
        print("  python manage.py setup                   # Setup system from scratch")
        print("  python manage.py all                     # Run all operations")
    else:
        print("⚠️ Some tests failed - check the output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 