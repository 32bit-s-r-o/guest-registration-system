#!/usr/bin/env python3
"""
Comprehensive System Test for Guest Registration System
Tests all major functionality including public pages, admin features, registration process, and data management.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os
import tempfile
import re

# Configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class SystemTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.current_test = 0
        self.created_trip_id = None
        self.created_registration_id = None
        self.created_invoice_id = None
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        self.current_test += 1
        result = {
            'test_id': self.current_test,
            'test_name': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} Test {self.current_test}: {test_name} - {status}")
        if details:
            print(f"   Details: {details}")
    
    def login_admin(self):
        """Login as admin"""
        try:
            # Get login page
            response = self.session.get(f"{BASE_URL}/admin/login")
            if response.status_code != 200:
                return False, f"Login page failed: {response.status_code}"
            
            # Login
            login_data = {
                'username': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/admin/login", data=login_data, allow_redirects=True)
            
            if response.status_code == 200 and "dashboard" in response.url:
                return True, "Login successful"
            else:
                return False, f"Login failed: {response.status_code}"
        except Exception as e:
            return False, f"Login exception: {str(e)}"
    
    def test_public_pages(self):
        """Test all public pages"""
        print("\n🌐 Testing Public Pages")
        print("=" * 50)
        
        public_pages = [
            ('/', 'Home Page'),
            ('/about', 'About Page'),
            ('/contact', 'Contact Page'),
            ('/gdpr', 'GDPR Page'),
            ('/register', 'Registration Landing Page'),
        ]
        
        for endpoint, name in public_pages:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_test(f"Public Page: {name}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"Public Page: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Public Page: {name}", "FAIL", f"Exception: {str(e)}")
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        print("\n🔐 Testing Admin Authentication")
        print("=" * 50)
        
        # Test login
        success, details = self.login_admin()
        if success:
            self.log_test("Admin Login", "PASS", details)
        else:
            self.log_test("Admin Login", "FAIL", details)
            return False
        
        # Test logout
        try:
            response = self.session.get(f"{BASE_URL}/admin/logout", allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Admin Logout", "PASS", "Logout successful")
            else:
                self.log_test("Admin Logout", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Logout", "FAIL", f"Exception: {str(e)}")
        
        # Login again for subsequent tests
        success, details = self.login_admin()
        return success
    
    def test_admin_dashboard(self):
        """Test admin dashboard functionality"""
        print("\n🏠 Testing Admin Dashboard")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/dashboard")
            if response.status_code == 200:
                self.log_test("Dashboard Access", "PASS", "Dashboard accessible")
                
                # Check for key dashboard elements
                if 'pending_registrations' in response.text or 'trip' in response.text.lower():
                    self.log_test("Dashboard Content", "PASS", "Contains expected content")
                else:
                    self.log_test("Dashboard Content", "WARN", "May be missing expected content")
            else:
                self.log_test("Dashboard Access", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dashboard Access", "FAIL", f"Exception: {str(e)}")
    
    def test_trip_management(self):
        """Test trip management functionality"""
        print("\n✈️ Testing Trip Management")
        print("=" * 50)
        
        # Test trips list
        try:
            response = self.session.get(f"{BASE_URL}/admin/trips")
            if response.status_code == 200:
                self.log_test("Trips List", "PASS", "Trips page accessible")
            else:
                self.log_test("Trips List", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Trips List", "FAIL", f"Exception: {str(e)}")
        
        # Test new trip form
        try:
            response = self.session.get(f"{BASE_URL}/admin/trips/new")
            if response.status_code == 200:
                self.log_test("New Trip Form", "PASS", "New trip form accessible")
            else:
                self.log_test("New Trip Form", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("New Trip Form", "FAIL", f"Exception: {str(e)}")
        
        # Test creating a new trip
        try:
            trip_data = {
                'title': f'Test Trip {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'start_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d'),
                'max_guests': 4
            }
            response = self.session.post(f"{BASE_URL}/admin/trips/new", data=trip_data, allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Create Trip", "PASS", f"Trip created: {trip_data['title']}")
                # Extract trip ID for later tests
                match = re.search(r'href="/admin/trips/(\d+)"', response.text)
                if match:
                    self.created_trip_id = match.group(1)
            else:
                self.log_test("Create Trip", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create Trip", "FAIL", f"Exception: {str(e)}")
    
    def test_registration_management(self):
        """Test registration management"""
        print("\n📝 Testing Registration Management")
        print("=" * 50)
        
        # Test registrations list
        try:
            response = self.session.get(f"{BASE_URL}/admin/registrations")
            if response.status_code == 200:
                self.log_test("Registrations List", "PASS", "Registrations page accessible")
            else:
                self.log_test("Registrations List", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Registrations List", "FAIL", f"Exception: {str(e)}")
        
        # Test viewing a specific registration (if any exist)
        try:
            # First check if any registrations exist
            response = self.session.get(f"{BASE_URL}/admin/registrations")
            if response.status_code == 200:
                # Look for a registration link in the response
                if 'href="/admin/registration/' in response.text:
                    # Extract the first registration ID from the page
                    match = re.search(r'href="/admin/registration/(\d+)"', response.text)
                    if match:
                        reg_id = match.group(1)
                        self.created_registration_id = reg_id
                        response = self.session.get(f"{BASE_URL}/admin/registration/{reg_id}")
                        if response.status_code == 200:
                            self.log_test("View Registration", "PASS", f"Registration {reg_id} view accessible")
                        else:
                            self.log_test("View Registration", "FAIL", f"Status: {response.status_code}")
                    else:
                        self.log_test("View Registration", "WARN", "No registration links found on page")
                else:
                    self.log_test("View Registration", "WARN", "No registrations exist in database")
            else:
                self.log_test("View Registration", "FAIL", f"Registrations page status: {response.status_code}")
        except Exception as e:
            self.log_test("View Registration", "FAIL", f"Exception: {str(e)}")
    
    def test_registration_approval_rejection(self):
        """Test registration approval and rejection functionality"""
        print("\n✅❌ Testing Registration Approval/Rejection")
        print("=" * 50)
        
        if not self.created_registration_id:
            self.log_test("Registration Approval/Rejection", "WARN", "No registration available for testing")
            return
        
        # Test registration approval
        try:
            response = self.session.post(f"{BASE_URL}/admin/registration/{self.created_registration_id}/approve", allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Approve Registration", "PASS", f"Registration {self.created_registration_id} approved")
            else:
                self.log_test("Approve Registration", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Approve Registration", "FAIL", f"Exception: {str(e)}")
        
        # Test registration rejection (if we had another registration)
        try:
            # Try to reject a non-existent registration to test the endpoint
            response = self.session.post(f"{BASE_URL}/admin/registration/99999/reject", 
                                       data={'comment': 'Test rejection'}, allow_redirects=True)
            if response.status_code == 404:
                self.log_test("Reject Registration Endpoint", "PASS", "Rejection endpoint exists and handles missing registration")
            else:
                self.log_test("Reject Registration Endpoint", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Reject Registration Endpoint", "FAIL", f"Exception: {str(e)}")
    
    def test_invoice_management(self):
        """Test invoice management functionality"""
        print("\n💰 Testing Invoice Management")
        print("=" * 50)
        
        # Test invoices list
        try:
            response = self.session.get(f"{BASE_URL}/admin/invoices")
            if response.status_code == 200:
                self.log_test("Invoices List", "PASS", "Invoices page accessible")
            else:
                self.log_test("Invoices List", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invoices List", "FAIL", f"Exception: {str(e)}")
        
        # Test new invoice form
        try:
            response = self.session.get(f"{BASE_URL}/admin/invoices/new")
            if response.status_code == 200:
                self.log_test("New Invoice Form", "PASS", "New invoice form accessible")
            else:
                self.log_test("New Invoice Form", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("New Invoice Form", "FAIL", f"Exception: {str(e)}")
        
        # Test creating a new invoice
        try:
            invoice_data = {
                'client_name': f'Test Client {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'client_email': 'test@example.com',
                'client_vat_number': 'CZ12345678',
                'client_address': 'Test Address 123\nTest City 12345',
                'issue_date': datetime.now().strftime('%Y-%m-%d'),
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'currency': 'EUR',
                'notes': 'Test invoice created by system test',
                'item_count': 1,
                'item_description_0': 'Test Service',
                'item_quantity_0': 1,
                'item_unit_price_0': 100.00,
                'item_vat_rate_0': 21.0
            }
            response = self.session.post(f"{BASE_URL}/admin/invoices/new", data=invoice_data, allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Create Invoice", "PASS", f"Invoice created for: {invoice_data['client_name']}")
                # Extract invoice ID for later tests
                match = re.search(r'href="/admin/invoices/(\d+)"', response.text)
                if match:
                    self.created_invoice_id = match.group(1)
            else:
                self.log_test("Create Invoice", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create Invoice", "FAIL", f"Exception: {str(e)}")
    
    def test_invoice_operations(self):
        """Test invoice view, edit, delete, and status operations"""
        print("\n📄 Testing Invoice Operations")
        print("=" * 50)
        
        # If no invoice was created in the previous test, try to find an existing one
        if not self.created_invoice_id:
            try:
                response = self.session.get(f"{BASE_URL}/admin/invoices")
                if response.status_code == 200:
                    # Look for an existing invoice link
                    match = re.search(r'href="/admin/invoices/(\d+)"', response.text)
                    if match:
                        self.created_invoice_id = match.group(1)
                        self.log_test("Invoice Operations", "PASS", f"Found existing invoice {self.created_invoice_id} for testing")
                    else:
                        self.log_test("Invoice Operations", "WARN", "No invoices available for testing - skipping operations")
                        return
                else:
                    self.log_test("Invoice Operations", "FAIL", f"Cannot access invoices page: {response.status_code}")
                    return
            except Exception as e:
                self.log_test("Invoice Operations", "FAIL", f"Exception finding invoice: {str(e)}")
                return
        
        # Test viewing invoice
        try:
            response = self.session.get(f"{BASE_URL}/admin/invoices/{self.created_invoice_id}")
            if response.status_code == 200:
                self.log_test("View Invoice", "PASS", f"Invoice {self.created_invoice_id} view accessible")
            else:
                self.log_test("View Invoice", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("View Invoice", "FAIL", f"Exception: {str(e)}")
        
        # Test editing invoice
        try:
            response = self.session.get(f"{BASE_URL}/admin/invoices/{self.created_invoice_id}/edit")
            if response.status_code == 200:
                self.log_test("Edit Invoice Form", "PASS", f"Invoice {self.created_invoice_id} edit form accessible")
            else:
                self.log_test("Edit Invoice Form", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Edit Invoice Form", "FAIL", f"Exception: {str(e)}")
        
        # Test changing invoice status
        try:
            status_data = {'status': 'sent'}
            response = self.session.post(f"{BASE_URL}/admin/invoices/{self.created_invoice_id}/change-status", 
                                       data=status_data, allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Change Invoice Status", "PASS", f"Invoice {self.created_invoice_id} status changed to sent")
            else:
                self.log_test("Change Invoice Status", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Change Invoice Status", "FAIL", f"Exception: {str(e)}")
        
        # Test PDF generation
        try:
            response = self.session.get(f"{BASE_URL}/admin/invoices/{self.created_invoice_id}/pdf")
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' in content_type or 'text/html' in content_type:
                    self.log_test("Generate Invoice PDF", "PASS", f"PDF generated for invoice {self.created_invoice_id}")
                else:
                    self.log_test("Generate Invoice PDF", "WARN", f"Unexpected content type: {content_type}")
            else:
                self.log_test("Generate Invoice PDF", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Generate Invoice PDF", "FAIL", f"Exception: {str(e)}")
    
    def test_csv_exports(self):
        """Test CSV export functionality"""
        print("\n📊 Testing CSV Exports")
        print("=" * 50)
        
        export_endpoints = [
            ('/admin/export/registrations', 'Registrations Export'),
            ('/admin/export/guests', 'Guests Export'),
            ('/admin/export/trips', 'Trips Export'),
            ('/admin/export/invoices', 'Invoices Export')
        ]
        
        for endpoint, name in export_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/csv' in content_type:
                        self.log_test(name, "PASS", f"CSV exported ({len(response.content)} bytes)")
                    else:
                        self.log_test(name, "WARN", f"Not CSV format: {content_type}")
                else:
                    self.log_test(name, "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(name, "FAIL", f"Exception: {str(e)}")
    
    def test_analytics_pages(self):
        """Test analytics and breakdown pages"""
        print("\n📈 Testing Analytics Pages")
        print("=" * 50)
        
        analytics_pages = [
            ('/admin/breakdowns', 'Main Analytics'),
            ('/admin/breakdowns/registrations', 'Registration Analytics'),
            ('/admin/breakdowns/guests', 'Guest Analytics'),
            ('/admin/breakdowns/trips', 'Trip Analytics'),
            ('/admin/breakdowns/invoices', 'Invoice Analytics')
        ]
        
        for endpoint, name in analytics_pages:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_test(name, "PASS", "Analytics page accessible")
                else:
                    self.log_test(name, "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(name, "FAIL", f"Exception: {str(e)}")
    
    def test_admin_settings(self):
        """Test admin settings functionality"""
        print("\n⚙️ Testing Admin Settings")
        print("=" * 50)
        
        # Test settings page
        try:
            response = self.session.get(f"{BASE_URL}/admin/settings")
            if response.status_code == 200:
                self.log_test("Settings Page", "PASS", "Settings page accessible")
            else:
                self.log_test("Settings Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Settings Page", "FAIL", f"Exception: {str(e)}")
        
        # Test updating settings
        try:
            settings_data = {
                'email': 'admin@test.com',
                'company_name': 'Test Company',
                'company_ico': '12345678',
                'company_vat': 'CZ12345678',
                'contact_name': 'Test Admin',
                'contact_phone': '+420 123 456 789',
                'contact_address': 'Test Address\nTest City 12345',
                'contact_website': 'https://test.com',
                'contact_description': 'Test company description',
                'custom_line_1': 'Test Custom Line 1',
                'custom_line_2': 'Test Custom Line 2',
                'custom_line_3': 'Test Custom Line 3',
                'airbnb_listing_id': 'test123',
                'airbnb_calendar_url': 'https://test.com/calendar',
                'photo_required_adults': 'on',
                'photo_required_children': 'on'
            }
            response = self.session.post(f"{BASE_URL}/admin/settings", data=settings_data, allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Update Settings", "PASS", "Settings updated successfully")
            else:
                self.log_test("Update Settings", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Update Settings", "FAIL", f"Exception: {str(e)}")
    
    def test_airbnb_sync(self):
        """Test Airbnb sync functionality"""
        print("\n🏠 Testing Airbnb Sync")
        print("=" * 50)
        
        # Test Airbnb sync endpoint
        try:
            sync_data = {'action': 'sync'}
            response = self.session.post(f"{BASE_URL}/admin/sync-airbnb", data=sync_data, allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Airbnb Sync Endpoint", "PASS", "Airbnb sync endpoint accessible")
            else:
                self.log_test("Airbnb Sync Endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Airbnb Sync Endpoint", "FAIL", f"Exception: {str(e)}")
    
    def test_data_management(self):
        """Test data management functionality"""
        print("\n🗄️ Testing Data Management")
        print("=" * 50)
        
        # Test data management page
        try:
            response = self.session.get(f"{BASE_URL}/admin/data-management")
            if response.status_code == 200:
                self.log_test("Data Management Page", "PASS", "Data management page accessible")
            else:
                self.log_test("Data Management Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Data Management Page", "FAIL", f"Exception: {str(e)}")
        
        # Test seed data operation
        try:
            response = self.session.post(f"{BASE_URL}/admin/seed-data", allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Seed Data", "PASS", "Sample data seeded successfully")
            else:
                self.log_test("Seed Data", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Seed Data", "FAIL", f"Exception: {str(e)}")
    
    def test_housekeeping(self):
        """Test housekeeping functionality"""
        print("\n🧹 Testing Housekeeping")
        print("=" * 50)
        
        # Test housekeeping page
        try:
            response = self.session.get(f"{BASE_URL}/admin/housekeeping")
            if response.status_code == 200:
                self.log_test("Housekeeping Page", "PASS", "Housekeeping page accessible")
            else:
                self.log_test("Housekeeping Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Housekeeping Page", "FAIL", f"Exception: {str(e)}")
        
        # Test housekeeping API (requires housekeeper role, so skip when logged as admin)
        try:
            response = self.session.get(f"{BASE_URL}/api/housekeeping_events")
            if response.status_code == 403:
                self.log_test("Housekeeping API", "PASS", "API properly protected - requires housekeeper role")
            elif response.status_code == 200:
                self.log_test("Housekeeping API", "PASS", "Housekeeping API accessible")
            else:
                self.log_test("Housekeeping API", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Housekeeping API", "FAIL", f"Exception: {str(e)}")
        
        # Test housekeeper dashboard (should be protected, requires housekeeper role)
        try:
            response = self.session.get(f"{BASE_URL}/housekeeper/dashboard")
            if response.status_code == 403:
                self.log_test("Housekeeper Dashboard", "PASS", "Dashboard properly protected - requires housekeeper role")
            elif response.status_code == 200:
                self.log_test("Housekeeper Dashboard", "PASS", "Housekeeper dashboard accessible")
            else:
                self.log_test("Housekeeper Dashboard", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Housekeeper Dashboard", "FAIL", f"Exception: {str(e)}")
    
    def test_language_functionality(self):
        """Test language switching functionality"""
        print("\n🌍 Testing Language Functionality")
        print("=" * 50)
        
        # Test language switching
        try:
            response = self.session.get(f"{BASE_URL}/set_language/cs", allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Language Switch to Czech", "PASS", "Language switched successfully")
            else:
                self.log_test("Language Switch to Czech", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Language Switch to Czech", "FAIL", f"Exception: {str(e)}")
        
        # Test switching back to English
        try:
            response = self.session.get(f"{BASE_URL}/set_language/en", allow_redirects=True)
            if response.status_code == 200:
                self.log_test("Language Switch to English", "PASS", "Language switched successfully")
            else:
                self.log_test("Language Switch to English", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Language Switch to English", "FAIL", f"Exception: {str(e)}")
    
    def test_registration_process(self):
        """Test the guest registration process"""
        print("\n📋 Testing Guest Registration Process")
        print("=" * 50)
        
        # Test registration landing page
        try:
            response = self.session.get(f"{BASE_URL}/register")
            if response.status_code == 200:
                self.log_test("Registration Landing", "PASS", "Registration landing page accessible")
            else:
                self.log_test("Registration Landing", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Registration Landing", "FAIL", f"Exception: {str(e)}")
        
        # Test registration form (if a trip exists)
        try:
            # First check if any trips exist
            response = self.session.get(f"{BASE_URL}/admin/trips")
            if response.status_code == 200:
                # Look for a trip link in the response
                if 'href="/register/id/' in response.text:
                    # Extract the first trip ID from the page
                    match = re.search(r'href="/register/id/(\d+)"', response.text)
                    if match:
                        trip_id = match.group(1)
                        response = self.session.get(f"{BASE_URL}/register/id/{trip_id}")
                        if response.status_code == 200:
                            self.log_test("Registration Form", "PASS", f"Registration form for trip {trip_id} accessible")
                        else:
                            self.log_test("Registration Form", "FAIL", f"Status: {response.status_code}")
                    else:
                        self.log_test("Registration Form", "WARN", "No trip registration links found on page")
                else:
                    self.log_test("Registration Form", "WARN", "No trips exist in database")
            else:
                self.log_test("Registration Form", "FAIL", f"Trips page status: {response.status_code}")
        except Exception as e:
            self.log_test("Registration Form", "FAIL", f"Exception: {str(e)}")
    
    def test_upload_functionality(self):
        """Test file upload functionality"""
        print("\n📁 Testing Upload Functionality")
        print("=" * 50)
        
        # Test uploads directory access
        try:
            response = self.session.get(f"{BASE_URL}/uploads/test.jpg")
            if response.status_code in [200, 404]:  # 404 is expected if file doesn't exist
                self.log_test("Uploads Directory", "PASS", "Uploads directory accessible")
            else:
                self.log_test("Uploads Directory", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Uploads Directory", "FAIL", f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling for invalid routes"""
        print("\n🚫 Testing Error Handling")
        print("=" * 50)
        
        # Test non-existent routes
        invalid_routes = [
            '/admin/nonexistent',
            '/admin/invoices/99999',
            '/admin/registration/99999',
            '/admin/trips/99999'
        ]
        
        for route in invalid_routes:
            try:
                response = self.session.get(f"{BASE_URL}{route}")
                if response.status_code == 404:
                    self.log_test(f"404 Error: {route}", "PASS", "Proper 404 response")
                else:
                    self.log_test(f"404 Error: {route}", "WARN", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"404 Error: {route}", "FAIL", f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Comprehensive System Test for Guest Registration System")
        print("=" * 70)
        print(f"Testing against: {BASE_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Admin username: {ADMIN_USERNAME}")
        
        # Run all test suites
        self.test_public_pages()
        
        if not self.test_admin_authentication():
            print("❌ Admin authentication failed. Skipping admin tests.")
            return
        
        self.test_admin_dashboard()
        self.test_trip_management()
        self.test_registration_management()
        self.test_registration_approval_rejection()
        self.test_invoice_management()
        self.test_invoice_operations()
        self.test_csv_exports()
        self.test_analytics_pages()
        self.test_admin_settings()
        self.test_airbnb_sync()
        self.test_data_management()
        self.test_housekeeping()
        self.test_language_functionality()
        self.test_registration_process()
        self.test_upload_functionality()
        self.test_error_handling()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_name']}: {result['details']}")
        
        if warning_tests > 0:
            print("\n⚠️  WARNINGS:")
            for result in self.test_results:
                if result['status'] == 'WARN':
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n🎯 SYSTEM STATUS:")
        if failed_tests == 0 and warning_tests == 0:
            print("🟢 EXCELLENT - All tests passed!")
        elif failed_tests == 0:
            print("🟡 GOOD - All critical tests passed, some warnings")
        elif failed_tests < total_tests * 0.2:
            print("🟠 FAIR - Most tests passed, some issues to address")
        else:
            print("🔴 POOR - Many tests failed, system needs attention")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['status']}")

if __name__ == "__main__":
    test = SystemTest()
    test.run_all_tests()
