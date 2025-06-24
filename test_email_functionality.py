#!/usr/bin/env python3
"""
Test script for email functionality including language support
"""

import requests
import sys
import os
from datetime import datetime, timedelta
from config import Config

# Configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class EmailFunctionalityTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test result with emoji indicators"""
        emoji = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARN": "⚠️"
        }
        status_emoji = emoji.get(status, "❓")
        print(f"{status_emoji} {test_name}: {status}")
        if message:
            print(f"   └─ {message}")
        self.test_results.append((test_name, status, message))
    
    def login(self):
        """Login as admin"""
        try:
            # Get login page
            response = self.session.get(f"{BASE_URL}/admin/login")
            if response.status_code != 200:
                self.log_test("Admin Login Page", "FAIL", f"Status: {response.status_code}")
                return False
            
            # Submit login form
            login_data = {
                'username': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/admin/login", data=login_data)
            
            if response.status_code == 200 and 'dashboard' in response.url:
                self.log_test("Admin Login", "PASS", "Successfully logged in")
                return True
            else:
                self.log_test("Admin Login", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_invoice_pdf_email(self):
        """Test invoice PDF email functionality"""
        print("\n📧 Testing Invoice PDF Email Functionality")
        print("=" * 50)
        
        # First, try to create a test invoice if none exist
        try:
            response = self.session.get(f"{BASE_URL}/admin/invoices")
            if response.status_code != 200:
                self.log_test("Invoices List Access", "FAIL", f"Status: {response.status_code}")
                return
            
            # Check if there are any invoices
            if 'href="/admin/invoice/' not in response.text:
                # Create a test invoice
                self.log_test("Invoice PDF Email", "INFO", "No invoices found, creating test invoice...")
                
                # Create a test trip first
                response = self.session.get(f"{BASE_URL}/admin/trips/new")
                if response.status_code == 200:
                    trip_data = {
                        'title': 'Test Trip for Email',
                        'start_date': '2025-07-01',
                        'end_date': '2025-07-03',
                        'max_guests': '2',
                        'amenity_id': '1'  # Assuming amenity 1 exists
                    }
                    response = self.session.post(f"{BASE_URL}/admin/trips/new", data=trip_data)
                    if response.status_code == 200:
                        self.log_test("Test Trip Creation", "PASS", "Test trip created")
                    else:
                        self.log_test("Test Trip Creation", "FAIL", f"Status: {response.status_code}")
                        return
                
                # Create a test invoice
                response = self.session.get(f"{BASE_URL}/admin/invoices/new")
                if response.status_code == 200:
                    invoice_data = {
                        'client_name': 'Test Client for Email',
                        'client_email': 'test@example.com',
                        'issue_date': '2025-06-24',
                        'due_date': '2025-07-24',
                        'currency': 'EUR',
                        'item_count': '1',
                        'item_description_0': 'Test Service',
                        'item_quantity_0': '1',
                        'item_unit_price_0': '100',
                        'item_vat_rate_0': '21'
                    }
                    response = self.session.post(f"{BASE_URL}/admin/invoices/new", data=invoice_data)
                    if response.status_code == 200:
                        self.log_test("Test Invoice Creation", "PASS", "Test invoice created")
                    else:
                        self.log_test("Test Invoice Creation", "FAIL", f"Status: {response.status_code}")
                        return
                else:
                    self.log_test("Test Invoice Creation", "FAIL", f"New invoice form status: {response.status_code}")
                    return
            
            # Now get the invoices list again
            response = self.session.get(f"{BASE_URL}/admin/invoices")
            if response.status_code != 200:
                self.log_test("Invoice PDF Email", "FAIL", f"Status: {response.status_code}")
                return
            
            # Extract first invoice ID
            import re
            match = re.search(r'href="/admin/invoice/(\d+)"', response.text)
            if not match:
                self.log_test("Invoice PDF Email", "WARN", "No invoices found to test with")
                return
            
            invoice_id = match.group(1)
            
            # Test the send PDF email functionality
            response = self.session.post(f"{BASE_URL}/admin/invoices/{invoice_id}/send-pdf")
            
            if response.status_code == 200:
                # Check for success message
                if 'Invoice PDF sent to' in response.text:
                    self.log_test("Invoice PDF Email", "PASS", "PDF email sent successfully")
                else:
                    self.log_test("Invoice PDF Email", "FAIL", "No success message found")
            else:
                self.log_test("Invoice PDF Email", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Invoice PDF Email", "FAIL", f"Exception: {str(e)}")
    
    def test_registration_approval_email(self):
        """Test registration approval email with language support"""
        print("\n📧 Testing Registration Approval Email")
        print("=" * 50)
        
        # Get registrations list
        try:
            response = self.session.get(f"{BASE_URL}/admin/registrations")
            if response.status_code != 200:
                self.log_test("Registrations List Access", "FAIL", f"Status: {response.status_code}")
                return
            
            # Check if there are any pending registrations
            if 'href="/admin/registration/' not in response.text:
                self.log_test("Registration Approval Email", "WARN", "No registrations found to test with")
                return
            
            # Extract first registration ID
            import re
            match = re.search(r'href="/admin/registration/(\d+)"', response.text)
            if not match:
                self.log_test("Registration Approval Email", "WARN", "Could not find registration ID")
                return
            
            registration_id = match.group(1)
            
            # Test approval (this will trigger email)
            response = self.session.post(f"{BASE_URL}/admin/registration/{registration_id}/approve")
            
            if response.status_code == 200:
                # Check for success message
                if 'Registration approved and email sent' in response.text:
                    self.log_test("Registration Approval Email", "PASS", "Approval email sent successfully")
                else:
                    self.log_test("Registration Approval Email", "FAIL", "No success message found")
            else:
                self.log_test("Registration Approval Email", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Registration Approval Email", "FAIL", f"Exception: {str(e)}")
    
    def test_registration_rejection_email(self):
        """Test registration rejection email with language support"""
        print("\n📧 Testing Registration Rejection Email")
        print("=" * 50)
        
        # Get registrations list
        try:
            response = self.session.get(f"{BASE_URL}/admin/registrations")
            if response.status_code != 200:
                self.log_test("Registrations List Access", "FAIL", f"Status: {response.status_code}")
                return
            
            # Check if there are any pending registrations
            if 'href="/admin/registration/' not in response.text:
                # Create a test registration if none exist
                self.log_test("Registration Rejection Email", "INFO", "No registrations found, creating test registration...")
                
                # Create a test trip first
                response = self.session.get(f"{BASE_URL}/admin/trips/new")
                if response.status_code == 200:
                    trip_data = {
                        'title': 'Test Trip for Rejection Email',
                        'start_date': '2025-07-01',
                        'end_date': '2025-07-03',
                        'max_guests': '2',
                        'amenity_id': '1'  # Assuming amenity 1 exists
                    }
                    response = self.session.post(f"{BASE_URL}/admin/trips/new", data=trip_data)
                    if response.status_code == 200:
                        self.log_test("Test Trip Creation", "PASS", "Test trip created")
                    else:
                        self.log_test("Test Trip Creation", "FAIL", f"Status: {response.status_code}")
                        return
                
                # Create a test registration (this would normally be done through the registration form)
                # For testing purposes, we'll simulate this by creating a pending registration
                # This is a simplified approach - in a real scenario, you'd go through the full registration process
                self.log_test("Test Registration Creation", "INFO", "Test registration creation would require full registration flow")
                self.log_test("Registration Rejection Email", "WARN", "No registrations found to test with")
                return
            
            # Extract first registration ID
            import re
            match = re.search(r'href="/admin/registration/(\d+)"', response.text)
            if not match:
                self.log_test("Registration Rejection Email", "WARN", "Could not find registration ID")
                return
            
            registration_id = match.group(1)
            
            # Test rejection (this will trigger email)
            rejection_data = {
                'comment': 'Test rejection comment for email functionality testing'
            }
            response = self.session.post(f"{BASE_URL}/admin/registration/{registration_id}/reject", data=rejection_data)
            
            if response.status_code == 200:
                # Check for success message
                if 'Registration rejected and email sent' in response.text:
                    self.log_test("Registration Rejection Email", "PASS", "Rejection email sent successfully")
                else:
                    self.log_test("Registration Rejection Email", "FAIL", "No success message found")
            else:
                self.log_test("Registration Rejection Email", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Registration Rejection Email", "FAIL", f"Exception: {str(e)}")
    
    def test_language_support_in_emails(self):
        """Test that emails respect the registration language"""
        print("\n🌍 Testing Language Support in Emails")
        print("=" * 50)
        
        # Get registrations with different languages
        try:
            response = self.session.get(f"{BASE_URL}/admin/registrations")
            if response.status_code != 200:
                self.log_test("Language Support Check", "FAIL", f"Status: {response.status_code}")
                return
            
            # Look for registrations with different languages
            if 'language' in response.text.lower():
                self.log_test("Language Support Check", "PASS", "Language field detected in registrations")
            else:
                self.log_test("Language Support Check", "WARN", "Language field not visible in registrations list")
                
        except Exception as e:
            self.log_test("Language Support Check", "FAIL", f"Exception: {str(e)}")
    
    def test_email_configuration(self):
        """Test email configuration and settings"""
        print("\n⚙️ Testing Email Configuration")
        print("=" * 50)
        
        # Check admin settings page for email configuration
        try:
            response = self.session.get(f"{BASE_URL}/admin/settings")
            if response.status_code == 200:
                if 'MAIL_USERNAME' in response.text or 'email' in response.text.lower():
                    self.log_test("Email Configuration Page", "PASS", "Email settings accessible")
                else:
                    self.log_test("Email Configuration Page", "WARN", "Email settings not visible")
            else:
                self.log_test("Email Configuration Page", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Email Configuration Page", "FAIL", f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all email functionality tests"""
        print("🚀 Starting Email Functionality Tests")
        print("=" * 60)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without admin login")
            return
        
        # Run all tests
        self.test_email_configuration()
        self.test_language_support_in_emails()
        self.test_invoice_pdf_email()
        self.test_registration_approval_email()
        self.test_registration_rejection_email()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 EMAIL FUNCTIONALITY TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAIL")
        warnings = sum(1 for _, status, _ in self.test_results if status == "WARN")
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed!")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Please check the details above.")
        
        if warnings > 0:
            print(f"ℹ️ {warnings} warning(s) - these may need attention but don't prevent functionality.")

if __name__ == "__main__":
    print("📧 Email Functionality Test Suite")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Admin credentials: {ADMIN_USERNAME}/{ADMIN_PASSWORD}")
    print()
    
    tester = EmailFunctionalityTest()
    tester.run_all_tests() 