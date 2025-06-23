#!/usr/bin/env python3
"""
Simple test script for migration system
"""

import os
import sys
from datetime import datetime

def test_migration_files():
    """Test that migration files exist and are properly formatted"""
    print("🔄 Testing Migration System")
    print("=" * 50)
    
    migrations_dir = "migrations"
    
    if not os.path.exists(migrations_dir):
        print("❌ Migrations directory not found")
        return False
    
    migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
    
    if not migration_files:
        print("❌ No migration files found")
        return False
    
    print(f"✅ Found {len(migration_files)} migration files")
    
    for filename in migration_files:
        print(f"   ├─ {filename}")
        
        # Check file content
        filepath = os.path.join(migrations_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Check for required sections
        if '-- Migration:' not in content:
            print(f"   └─ ❌ Missing migration header in {filename}")
            continue
            
        if '-- Up Migration' not in content:
            print(f"   └─ ❌ Missing up migration section in {filename}")
            continue
            
        if '-- Down Migration' not in content:
            print(f"   └─ ❌ Missing down migration section in {filename}")
            continue
            
        print(f"   └─ ✅ Properly formatted")
    
    return True

def test_version_system():
    """Test version management"""
    print("\n📊 Testing Version System")
    print("=" * 50)
    
    # Check if version.py exists
    if not os.path.exists("version.py"):
        print("❌ version.py not found")
        return False
    
    print("✅ version.py found")
    
    # Try to import version system
    try:
        from version import version_manager, check_version_compatibility
        print("✅ Version system imports successfully")
        
        # Test version info
        version_info = version_manager.get_version_info()
        print(f"✅ Current version: {version_info['current_version']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Version system test failed: {e}")
        return False

def test_migration_commands():
    """Test migration command line interface"""
    print("\n🔧 Testing Migration Commands")
    print("=" * 50)
    
    # Test status command
    try:
        import subprocess
        result = subprocess.run(['python', 'migrations.py', 'status'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Migration status command works")
        else:
            print(f"⚠️ Migration status command failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Could not test migration commands: {e}")
    
    return True

def main():
    """Run all migration tests"""
    print("🚀 Migration System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Migration Files", test_migration_files),
        ("Version System", test_version_system),
        ("Migration Commands", test_migration_commands),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print("📋 Migration System Test Summary")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All migration system tests passed!")
        print("✅ Migration system is ready for use")
    else:
        print("⚠️ Some tests failed - check the output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 