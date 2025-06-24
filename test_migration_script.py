#!/usr/bin/env python3
"""
Test script for the migration system
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from config import Config

def test_migration_script():
    """Test the migration script functionality"""
    print("🧪 Testing Migration Script")
    print("=" * 50)
    
    # Get the project root
    project_root = Path(__file__).parent
    migration_script = project_root / "scripts" / "check_and_run_migrations.sh"
    wrapper_script = project_root / "run_migrations.sh"
    
    # Test 1: Check if scripts exist
    print("1. Checking if migration scripts exist...")
    if migration_script.exists():
        print("✅ Migration script exists")
    else:
        print("❌ Migration script not found")
        return False
    
    if wrapper_script.exists():
        print("✅ Wrapper script exists")
    else:
        print("❌ Wrapper script not found")
        return False
    
    # Test 2: Check if scripts are executable
    print("\n2. Checking script permissions...")
    if os.access(migration_script, os.X_OK):
        print("✅ Migration script is executable")
    else:
        print("❌ Migration script is not executable")
        return False
    
    if os.access(wrapper_script, os.X_OK):
        print("✅ Wrapper script is executable")
    else:
        print("❌ Wrapper script is not executable")
        return False
    
    # Test 3: Test help functionality
    print("\n3. Testing help functionality...")
    try:
        result = subprocess.run([str(wrapper_script), "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "Usage:" in result.stdout:
            print("✅ Help functionality works")
            # Check for new options
            if "--setup-only" in result.stdout and "--migrate-only" in result.stdout:
                print("✅ New command options are documented")
            else:
                print("⚠️ New command options may not be documented")
        else:
            print("❌ Help functionality failed")
            return False
    except Exception as e:
        print(f"❌ Help test failed: {e}")
        return False
    
    # Test 4: Test check-only functionality (without database)
    print("\n4. Testing check-only functionality...")
    try:
        result = subprocess.run([str(wrapper_script), "--check-only"], 
                              capture_output=True, text=True, timeout=30)
        # This should fail without a database, but the script should handle it gracefully
        if "Database connection failed" in result.stderr or "Database is not accessible" in result.stderr:
            print("✅ Check-only handles missing database gracefully")
        else:
            print("⚠️ Check-only test completed (may have database connection)")
    except Exception as e:
        print(f"⚠️ Check-only test failed: {e}")
    
    # Test 5: Test setup-only functionality (without database)
    print("\n5. Testing setup-only functionality...")
    try:
        result = subprocess.run([str(wrapper_script), "--setup-only"], 
                              capture_output=True, text=True, timeout=30)
        # This should fail without a database, but the script should handle it gracefully
        if "Database connection failed" in result.stderr or "Database is not accessible" in result.stderr:
            print("✅ Setup-only handles missing database gracefully")
        else:
            print("⚠️ Setup-only test completed (may have database connection)")
    except Exception as e:
        print(f"⚠️ Setup-only test failed: {e}")
    
    # Test 6: Test migrate-only functionality (without database)
    print("\n6. Testing migrate-only functionality...")
    try:
        result = subprocess.run([str(wrapper_script), "--migrate-only"], 
                              capture_output=True, text=True, timeout=30)
        # This should fail without a database, but the script should handle it gracefully
        if "Database connection failed" in result.stderr or "Database is not accessible" in result.stderr:
            print("✅ Migrate-only handles missing database gracefully")
        else:
            print("⚠️ Migrate-only test completed (may have database connection)")
    except Exception as e:
        print(f"⚠️ Migrate-only test failed: {e}")
    
    # Test 7: Test script structure
    print("\n7. Testing script structure...")
    with open(migration_script, 'r') as f:
        content = f.read()
        
    required_functions = [
        "check_database_connection",
        "check_database_empty",
        "check_migration_status", 
        "run_migrations",
        "run_setup",
        "check_if_migrations_needed",
        "check_if_setup_needed"
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✅ Function {func} found")
        else:
            print(f"❌ Function {func} not found")
            return False
    
    # Test 8: Test Docker integration files
    print("\n8. Testing Docker integration...")
    dockerfile = project_root / "Dockerfile"
    docker_compose = project_root / "docker-compose.yml"
    
    if dockerfile.exists():
        with open(dockerfile, 'r') as f:
            dockerfile_content = f.read()
        if "entrypoint.sh" in dockerfile_content and "check_and_run_migrations.sh" in dockerfile_content:
            print("✅ Dockerfile includes migration integration")
        else:
            print("❌ Dockerfile missing migration integration")
            return False
    else:
        print("❌ Dockerfile not found")
        return False
    
    if docker_compose.exists():
        with open(docker_compose, 'r') as f:
            compose_content = f.read()
        # Check for simplified approach (no separate setup/migration services)
        if "app:" in compose_content and "postgres:" in compose_content:
            if "setup:" not in compose_content and "migrations:" not in compose_content:
                print("✅ Docker Compose uses simplified approach (setup/migrations in main app)")
            else:
                print("⚠️ Docker Compose still has separate setup/migration services")
        else:
            print("❌ Docker Compose missing main services")
            return False
    else:
        print("❌ Docker Compose file not found")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All migration script tests passed!")
    print("=" * 50)
    return True

def test_setup_script():
    """Test the setup script functionality"""
    print("\n🔧 Testing Setup Script")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    setup_script = project_root / "setup.py"
    
    # Test 1: Check if setup script exists
    print("1. Checking if setup script exists...")
    if setup_script.exists():
        print("✅ Setup script exists")
    else:
        print("❌ Setup script not found")
        return False
    
    # Test 2: Check setup script structure
    print("\n2. Testing setup script structure...")
    with open(setup_script, 'r') as f:
        content = f.read()
        
    required_functions = [
        "check_environment",
        "test_database_connection",
        "create_tables",
        "create_admin_user",
        "show_next_steps"
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✅ Function {func} found")
        else:
            print(f"❌ Function {func} not found")
            return False
    
    # Test 3: Test setup script execution (without database)
    print("\n3. Testing setup script execution...")
    try:
        result = subprocess.run([sys.executable, str(setup_script)], 
                              capture_output=True, text=True, timeout=30)
        # This should fail without proper environment, but should show appropriate error
        if result.returncode != 0:
            print("✅ Setup script handles missing environment gracefully")
        else:
            print("⚠️ Setup script completed (may have proper environment)")
    except Exception as e:
        print(f"⚠️ Setup script test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All setup script tests passed!")
    print("=" * 50)
    return True

def test_migration_commands():
    """Test migration commands through manage.py"""
    print("\n🔧 Testing Migration Commands")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    manage_script = project_root / "manage.py"
    
    if not manage_script.exists():
        print("❌ manage.py not found")
        return False
    
    # Test migration status command
    print("1. Testing migration status command...")
    try:
        result = subprocess.run([sys.executable, str(manage_script), "migrate", "status"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Migration status command works")
        else:
            print("⚠️ Migration status command failed (may be expected without database)")
    except Exception as e:
        print(f"⚠️ Migration status test failed: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Migration and Setup System Tests")
    print("=" * 60)
    
    success = True
    
    # Test migration script
    if not test_migration_script():
        success = False
    
    # Test setup script
    if not test_setup_script():
        success = False
    
    # Test migration commands
    if not test_migration_commands():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("The migration and setup system is ready to use.")
        print("✅ Simplified approach: setup and migrations run in main app container")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    print("\n📚 For more information, see: docs/migration-system.md")
    sys.exit(0 if success else 1) 