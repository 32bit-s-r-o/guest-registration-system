#!/usr/bin/env python3
"""
Simple test script for backup API endpoints
"""

import requests
import sys
import os
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def log_test(test_name, status, message=""):
    """Log test result"""
    emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"{emoji.get(status, '❓')} {test_name}: {status}")
    if message:
        print(f"   └─ {message}")

def login_admin():
    """Login as admin"""
    session = requests.Session()
    
    # Get login page
    response = session.get(f"{BASE_URL}/admin/login")
    if response.status_code != 200:
        return None, "Login page not accessible"
    
    # Submit login form
    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    }
    response = session.post(f"{BASE_URL}/admin/login", data=login_data)
    
    if response.status_code == 200 and 'dashboard' in response.url:
        return session, "Successfully logged in"
    else:
        return None, f"Login failed - Status: {response.status_code}"

def test_monthly_guest_backup():
    """Test monthly guest backup API"""
    print("\n📊 Testing Monthly Guest Backup API")
    print("=" * 50)
    
    session, message = login_admin()
    if not session:
        log_test("Admin Login", "FAIL", message)
        return
    
    log_test("Admin Login", "PASS", message)
    
    # Test current month
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Test CSV format
    try:
        response = session.get(f"{BASE_URL}/api/backup/guests?year={current_year}&month={current_month}")
        
        if response.status_code == 200:
            if response.headers.get('content-type', '').startswith('text/csv'):
                log_test("Monthly Guest Backup CSV", "PASS", f"CSV export successful for {current_month}/{current_year}")
                
                # Check content
                csv_content = response.text
                if 'first_name,last_name' in csv_content:
                    log_test("CSV Content", "PASS", "Contains expected headers")
                else:
                    log_test("CSV Content", "WARN", "Headers not as expected")
            else:
                log_test("Monthly Guest Backup CSV", "FAIL", f"Wrong content type: {response.headers.get('content-type')}")
        else:
            log_test("Monthly Guest Backup CSV", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Monthly Guest Backup CSV", "FAIL", f"Exception: {str(e)}")
    
    # Test JSON format
    try:
        response = session.get(f"{BASE_URL}/api/backup/guests?year={current_year}&month={current_month}&format=json")
        
        if response.status_code == 200:
            if response.headers.get('content-type', '').startswith('application/json'):
                log_test("Monthly Guest Backup JSON", "PASS", f"JSON export successful for {current_month}/{current_year}")
                
                # Check JSON content
                try:
                    json_data = response.json()
                    if isinstance(json_data, list):
                        log_test("JSON Content", "PASS", f"Contains {len(json_data)} guest records")
                    else:
                        log_test("JSON Content", "WARN", "JSON structure not as expected")
                except:
                    log_test("JSON Content", "FAIL", "Invalid JSON response")
            else:
                log_test("Monthly Guest Backup JSON", "FAIL", f"Wrong content type: {response.headers.get('content-type')}")
        else:
            log_test("Monthly Guest Backup JSON", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Monthly Guest Backup JSON", "FAIL", f"Exception: {str(e)}")
    
    # Test error handling
    try:
        response = session.get(f"{BASE_URL}/api/backup/guests")
        
        if response.status_code == 400:
            log_test("Error Handling", "PASS", "Correctly handles missing parameters")
        else:
            log_test("Error Handling", "FAIL", f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Error Handling", "FAIL", f"Exception: {str(e)}")

def test_system_backup():
    """Test system backup endpoint"""
    print("\n💾 Testing System Backup")
    print("=" * 50)
    
    session, message = login_admin()
    if not session:
        log_test("Admin Login", "FAIL", message)
        return
    
    log_test("Admin Login", "PASS", message)
    
    try:
        response = session.get(f"{BASE_URL}/admin/backup")
        
        if response.status_code == 200:
            if response.headers.get('content-type', '').startswith('application/zip'):
                log_test("System Backup Download", "PASS", "ZIP backup downloaded successfully")
                
                # Check file size
                file_size = len(response.content)
                if file_size > 0:
                    log_test("Backup File Size", "PASS", f"Backup file size: {file_size} bytes")
                else:
                    log_test("Backup File Size", "FAIL", "Backup file is empty")
                    
            else:
                log_test("System Backup Download", "FAIL", f"Wrong content type: {response.headers.get('content-type')}")
        else:
            log_test("System Backup Download", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("System Backup Download", "FAIL", f"Exception: {str(e)}")

def test_access_control():
    """Test that backup endpoints are properly protected"""
    print("\n🔒 Testing Access Control")
    print("=" * 50)
    
    # Create unauthenticated session
    session = requests.Session()
    
    # Test system backup without authentication
    try:
        response = session.get(f"{BASE_URL}/admin/backup", allow_redirects=False)
        if response.status_code == 302:  # Redirect to login
            log_test("System Backup Access Control", "PASS", "Properly redirects to login")
        else:
            log_test("System Backup Access Control", "FAIL", f"Expected redirect, got {response.status_code}")
    except Exception as e:
        log_test("System Backup Access Control", "FAIL", f"Exception: {str(e)}")
    
    # Test monthly guest backup without authentication
    try:
        response = session.get(f"{BASE_URL}/api/backup/guests?year=2024&month=1", allow_redirects=False)
        if response.status_code == 302:  # Redirect to login
            log_test("Monthly Backup Access Control", "PASS", "Properly redirects to login")
        else:
            log_test("Monthly Backup Access Control", "FAIL", f"Expected redirect, got {response.status_code}")
    except Exception as e:
        log_test("Monthly Backup Access Control", "FAIL", f"Exception: {str(e)}")

def main():
    """Run all backup tests"""
    print("🚀 Backup API Test Suite")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Admin credentials: {ADMIN_USERNAME}/{ADMIN_PASSWORD}")
    
    test_access_control()
    test_monthly_guest_backup()
    test_system_backup()
    
    print("\n" + "=" * 60)
    print("📋 Backup Features Tested:")
    print("• Access control (admin-only)")
    print("• Monthly guest backup API (CSV/JSON)")
    print("• System backup (ZIP download)")
    print("• Error handling")
    print("=" * 60)

if __name__ == "__main__":
    main() 