#!/usr/bin/env python3
"""
Test script to verify the refactored app structure is working correctly
"""

import sys
import os

def test_app_import():
    """Test that the main app can be imported successfully"""
    try:
        from app import app
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_blueprint_registration():
    """Test that all blueprints are properly registered"""
    try:
        from app import app
        
        expected_blueprints = [
            'main', 'auth', 'registration', 'admin', 'amenities', 
            'trips', 'registrations', 'invoices', 'housekeeping', 
            'calendars', 'users', 'export', 'breakdowns', 'api', 'health'
        ]
        
        registered_blueprints = list(app.blueprints.keys())
        
        print(f"📋 Expected blueprints: {expected_blueprints}")
        print(f"📋 Registered blueprints: {registered_blueprints}")
        
        missing_blueprints = set(expected_blueprints) - set(registered_blueprints)
        extra_blueprints = set(registered_blueprints) - set(expected_blueprints)
        
        if missing_blueprints:
            print(f"❌ Missing blueprints: {missing_blueprints}")
            return False
        
        if extra_blueprints:
            print(f"⚠️  Extra blueprints: {extra_blueprints}")
        
        print("✅ All expected blueprints are registered")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint registration test failed: {e}")
        return False

def test_database_models():
    """Test that all database models can be imported"""
    try:
        from database import (
            User, Amenity, AmenityHousekeeper, Calendar, Trip, 
            Registration, Guest, Invoice, InvoiceItem, 
            Housekeeping, HousekeepingPhoto
        )
        print("✅ All database models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False

def test_template_filters():
    """Test that template filters are working"""
    try:
        from template_filters import register_template_filters
        from flask import Flask
        
        test_app = Flask(__name__)
        register_template_filters(test_app)
        
        # Test that filters are registered
        filters = list(test_app.jinja_env.filters.keys())
        expected_filters = ['nl2br', 'format_date', 'registration_name']
        
        for filter_name in expected_filters:
            if filter_name not in filters:
                print(f"❌ Missing template filter: {filter_name}")
                return False
        
        print("✅ All template filters registered successfully")
        return True
        
    except Exception as e:
        print(f"❌ Template filters test failed: {e}")
        return False

def test_utils():
    """Test that utility functions are working"""
    try:
        from utils import role_required, allowed_file
        
        # Test allowed_file function
        assert allowed_file("test.jpg") == True
        assert allowed_file("test.png") == True
        assert allowed_file("test.txt") == False
        
        print("✅ Utility functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False

def test_config():
    """Test that configuration is properly loaded"""
    try:
        from config import Config
        
        config = Config()
        
        # Test that required config values exist
        required_configs = [
            'SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'UPLOAD_FOLDER',
            'BABEL_DEFAULT_LOCALE', 'BABEL_SUPPORTED_LOCALES'
        ]
        
        for config_name in required_configs:
            if not hasattr(config, config_name):
                print(f"❌ Missing config: {config_name}")
                return False
        
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all refactor tests"""
    print("🔍 Testing Refactored App Structure")
    print("=" * 50)
    
    tests = [
        ("App Import", test_app_import),
        ("Blueprint Registration", test_blueprint_registration),
        ("Database Models", test_database_models),
        ("Template Filters", test_template_filters),
        ("Utils", test_utils),
        ("Config", test_config)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)
        if test_func():
            passed_tests += 1
        print("-" * 30)
    
    print(f"\n" + "=" * 50)
    print("📊 Refactor Test Results")
    print("=" * 50)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All refactor tests passed!")
        print("✅ The refactored app structure is working correctly!")
        return True
    else:
        print("⚠️  Some refactor tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 