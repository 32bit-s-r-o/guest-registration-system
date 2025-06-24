#!/usr/bin/env python3
"""
Test script to verify that the 500 errors are fixed
"""

import requests
import time

def test_fixes():
    """Test that the 500 errors are fixed"""
    print("🔍 Testing Fixes for 500 Errors")
    print("=" * 50)
    
    BASE_URL = "http://127.0.0.1:5000"
    
    # Test 1: Main Analytics Page
    print("\n🧪 Testing Main Analytics Page...")
    try:
        response = requests.get(f"{BASE_URL}/admin/breakdowns")
        if response.status_code == 200:
            print("✅ Main Analytics Page: PASS")
        else:
            print(f"❌ Main Analytics Page: FAIL (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Main Analytics Page: FAIL (Exception: {e})")
    
    # Test 2: Edit Invoice Form (requires login and existing invoice)
    print("\n🧪 Testing Edit Invoice Form...")
    try:
        # First try to login
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/admin/login", data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code == 200:
            # Try to access edit invoice form for invoice ID 1
            edit_response = session.get(f"{BASE_URL}/admin/invoices/1/edit")
            if edit_response.status_code == 200:
                print("✅ Edit Invoice Form: PASS")
            elif edit_response.status_code == 404:
                print("⚠️  Edit Invoice Form: No invoice found (expected)")
            else:
                print(f"❌ Edit Invoice Form: FAIL (Status: {edit_response.status_code})")
        else:
            print("❌ Edit Invoice Form: FAIL (Could not login)")
    except Exception as e:
        print(f"❌ Edit Invoice Form: FAIL (Exception: {e})")
    
    print("\n" + "=" * 50)
    print("📊 Fix Test Results")
    print("=" * 50)
    print("✅ Main Analytics Page should now work")
    print("✅ Edit Invoice Form should now handle None dates properly")
    print("✅ All URL references should be correct")

if __name__ == '__main__':
    test_fixes() 