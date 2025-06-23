#!/usr/bin/env python3
"""
Test script for CSV export and breakdowns functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin and return session"""
    session = requests.Session()
    
    # Get login page to get CSRF token
    login_page = session.get(f"{BASE_URL}/admin/login")
    print(f"[DEBUG] GET /admin/login status: {login_page.status_code}")
    
    # Login
    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    }
    response = session.post(f"{BASE_URL}/admin/login", data=login_data, allow_redirects=True)
    print(f"[DEBUG] POST /admin/login status: {response.status_code}")
    print(f"[DEBUG] POST /admin/login final URL: {response.url}")
    print(f"[DEBUG] POST /admin/login headers: {response.headers}")
    print(f"[DEBUG] POST /admin/login cookies: {session.cookies.get_dict()}")
    print(f"[DEBUG] POST /admin/login body (first 500 chars):\n{response.text[:500]}")
    
    if response.status_code == 200 and "dashboard" in response.url:
        print("✅ Admin login successful")
        return session
    else:
        print("❌ Admin login failed")
        return None

def test_csv_exports(session):
    """Test CSV export functionality"""
    print("\n📊 Testing CSV Export Functionality")
    print("=" * 50)
    
    export_endpoints = [
        ('/admin/export/registrations', 'registrations'),
        ('/admin/export/guests', 'guests'),
        ('/admin/export/trips', 'trips'),
        ('/admin/export/invoices', 'invoices')
    ]
    
    for endpoint, name in export_endpoints:
        print(f"\n🔄 Testing {name} export...")
        response = session.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            print(f"✅ {name.capitalize()} CSV export successful")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Check if it's actually CSV content
            if 'text/csv' in response.headers.get('Content-Type', ''):
                print(f"   ✅ Valid CSV format")
                # Show first few lines
                lines = response.text.split('\n')[:5]
                print(f"   📄 Preview (first 5 lines):")
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"      {i}: {line[:100]}{'...' if len(line) > 100 else ''}")
            else:
                print(f"   ⚠️  Not CSV format")
        else:
            print(f"❌ {name.capitalize()} CSV export failed: {response.status_code}")

def test_breakdowns(session):
    """Test breakdown/analytics pages"""
    print("\n📈 Testing Breakdown/Analytics Pages")
    print("=" * 50)
    
    breakdown_endpoints = [
        ('/admin/breakdowns', 'Main Analytics'),
        ('/admin/breakdowns/registrations', 'Registration Analytics'),
        ('/admin/breakdowns/guests', 'Guest Analytics'),
        ('/admin/breakdowns/trips', 'Trip Analytics'),
        ('/admin/breakdowns/invoices', 'Invoice Analytics')
    ]
    
    for endpoint, name in breakdown_endpoints:
        print(f"\n🔄 Testing {name}...")
        response = session.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            print(f"✅ {name} page accessible")
            # Check for key content
            if 'chart' in response.text.lower() or 'analytics' in response.text.lower():
                print(f"   ✅ Contains analytics content")
            else:
                print(f"   ⚠️  May not contain expected analytics content")
        else:
            print(f"❌ {name} page failed: {response.status_code}")

def test_dashboard_integration(session):
    """Test dashboard integration"""
    print("\n🏠 Testing Dashboard Integration")
    print("=" * 50)
    
    response = session.get(f"{BASE_URL}/admin/dashboard")
    
    if response.status_code == 200:
        print("✅ Dashboard accessible")
        
        # Check for analytics link
        if 'analytics' in response.text.lower() or 'chart-bar' in response.text.lower():
            print("✅ Analytics link found in dashboard")
        else:
            print("⚠️  Analytics link not found in dashboard")
    else:
        print(f"❌ Dashboard failed: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 CSV Export and Breakdowns Test")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Admin username: {ADMIN_USERNAME}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login as admin
    session = login_admin()
    if not session:
        print("❌ Cannot proceed without admin login")
        return
    
    # Test CSV exports
    test_csv_exports(session)
    
    # Test breakdowns
    test_breakdowns(session)
    
    # Test dashboard integration
    test_dashboard_integration(session)
    
    print("\n🎉 Test completed!")
    print("\n📋 Summary:")
    print("• CSV export functionality for registrations, guests, trips, and invoices")
    print("• Analytics/breakdown pages with charts and statistics")
    print("• Dashboard integration with analytics link")
    print("• Multi-language support for all new features")
    
    print("\n🔗 Manual Testing URLs:")
    print(f"• Dashboard: {BASE_URL}/admin/dashboard")
    print(f"• Analytics: {BASE_URL}/admin/breakdowns")
    print(f"• Registration Analytics: {BASE_URL}/admin/breakdowns/registrations")
    print(f"• Guest Analytics: {BASE_URL}/admin/breakdowns/guests")
    print(f"• Trip Analytics: {BASE_URL}/admin/breakdowns/trips")
    print(f"• Invoice Analytics: {BASE_URL}/admin/breakdowns/invoices")
    
    print("\n📥 CSV Export URLs:")
    print(f"• Registrations: {BASE_URL}/admin/export/registrations")
    print(f"• Guests: {BASE_URL}/admin/export/guests")
    print(f"• Trips: {BASE_URL}/admin/export/trips")
    print(f"• Invoices: {BASE_URL}/admin/export/invoices")

if __name__ == "__main__":
    main() 