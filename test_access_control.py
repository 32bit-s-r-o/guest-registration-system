#!/usr/bin/env python3
"""
Simple access control test to debug the issue
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def test_access_control():
    """Test access control for backup endpoints"""
    print("🔒 Testing Access Control")
    print("=" * 50)
    
    # Create a fresh session (no cookies)
    session = requests.Session()
    
    # Test system backup endpoint
    print(f"Testing: {BASE_URL}/admin/backup")
    try:
        response = session.get(f"{BASE_URL}/admin/backup", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 302:
            print(f"Redirect Location: {response.headers.get('Location')}")
        print()
    except Exception as e:
        print(f"Exception: {e}")
        print()
    
    # Test monthly backup endpoint
    print(f"Testing: {BASE_URL}/api/backup/guests?year=2024&month=1")
    try:
        response = session.get(f"{BASE_URL}/api/backup/guests?year=2024&month=1", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 302:
            print(f"Redirect Location: {response.headers.get('Location')}")
        print()
    except Exception as e:
        print(f"Exception: {e}")
        print()
    
    # Test a simple protected endpoint for comparison
    print(f"Testing: {BASE_URL}/admin/dashboard")
    try:
        response = session.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 302:
            print(f"Redirect Location: {response.headers.get('Location')}")
        print()
    except Exception as e:
        print(f"Exception: {e}")
        print()

if __name__ == "__main__":
    test_access_control() 