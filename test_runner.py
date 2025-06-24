#!/usr/bin/env python3
"""
Simple Test Runner - Updates existing tests to use test configuration
"""

import os
import sys
from test_config import TestConfig

def update_test_scripts():
    """Update test scripts to use test configuration"""
    print("🔧 Updating Test Scripts for Test Environment")
    print("=" * 60)
    
    # Set up test environment
    TestConfig.setup_test_environment()
    
    # List of test scripts that need BASE_URL updates
    test_scripts = [
        'test_backup_api.py',
        'test_backup_functionality.py', 
        'system_test.py',
        'test_email_functionality.py',
        'test_csv_export.py'
    ]
    
    for script in test_scripts:
        if os.path.exists(script):
            print(f"📝 Updating {script}...")
            update_script_base_url(script)
        else:
            print(f"⚠️ {script} not found")
    
    print("✅ Test scripts updated!")

def update_script_base_url(script_path):
    """Update BASE_URL in a test script"""
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Replace BASE_URL with test server URL
        old_base_url = "http://127.0.0.1:5000"
        new_base_url = TestConfig.TEST_SERVER_URL
        
        if old_base_url in content:
            content = content.replace(old_base_url, new_base_url)
            
            with open(script_path, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Updated BASE_URL: {old_base_url} → {new_base_url}")
        else:
            print(f"   ⚠️ No BASE_URL found to update")
            
    except Exception as e:
        print(f"   ❌ Error updating {script_path}: {e}")

def run_single_test(test_script):
    """Run a single test script with test configuration"""
    print(f"🧪 Running Single Test: {test_script}")
    print("=" * 60)
    
    # Set up test environment
    TestConfig.setup_test_environment()
    
    # Update the specific test script
    if os.path.exists(test_script):
        update_script_base_url(test_script)
    
    # Run the test
    import subprocess
    try:
        result = subprocess.run(['python', test_script], 
                              capture_output=True, text=True, timeout=300)
        
        print(f"Output:\n{result.stdout}")
        
        if result.returncode == 0:
            print(f"✅ {test_script}: PASS")
            return True
        else:
            print(f"❌ {test_script}: FAIL")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {test_script}: {e}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_runner.py update    # Update all test scripts")
        print("  python test_runner.py <script>  # Run single test script")
        return
    
    command = sys.argv[1]
    
    if command == 'update':
        update_test_scripts()
    else:
        # Assume it's a test script name
        test_script = command
        if os.path.exists(test_script):
            success = run_single_test(test_script)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Test script not found: {test_script}")

if __name__ == '__main__':
    main() 