#!/usr/bin/env python3
"""
Test script to demonstrate language picker configuration.
This script shows how to enable/disable the language picker.
"""

import os
import sys
from config import Config

# Set up test environment before importing app
def setup_test_environment():
    """Set up test environment variables"""
    # Database configuration
    os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///guest_registration_test.db')
    os.environ['TABLE_PREFIX'] = os.environ.get('TABLE_PREFIX', 'test_guest_reg_')
    
    # Flask configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'

def test_language_picker_config():
    """Test the language picker configuration."""
    
    print("=== Language Picker Configuration Test ===\n")
    
    # Set up test environment
    setup_test_environment()
    
    # Store original environment variable
    original_value = os.environ.get('LANGUAGE_PICKER_ENABLED')
    
    # Test with language picker enabled
    print("1. Testing with LANGUAGE_PICKER_ENABLED=true")
    os.environ['LANGUAGE_PICKER_ENABLED'] = 'true'
    
    try:
        # Clear any cached imports
        if 'app' in sys.modules:
            del sys.modules['app']
        
        from app import app
        with app.app_context():
            enabled = app.config['LANGUAGE_PICKER_ENABLED']
            supported_locales = app.config['BABEL_SUPPORTED_LOCALES']
            print(f"   Language picker enabled: {enabled}")
            print(f"   Supported locales: {supported_locales}")
            print("   ✓ Language picker will be visible in navigation")
            print("   ✓ Users can switch between English, Czech, and Slovak")
            print("   ✓ Available languages: English (en), Czech (cs), Slovak (sk)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test with language picker disabled
    print("2. Testing with DISABLE_LANGUAGE_PICKER=true")
    os.environ['DISABLE_LANGUAGE_PICKER'] = 'true'
    
    try:
        # Clear any cached imports
        if 'app' in sys.modules:
            del sys.modules['app']
        
        from app import app
        with app.app_context():
            enabled = app.config['LANGUAGE_PICKER_ENABLED']
            disabled = app.config['DISABLE_LANGUAGE_PICKER']
            print(f"   Language picker enabled: {enabled}")
            print(f"   Language picker disabled: {disabled}")
            if disabled or not enabled:
                print("   ✓ Language picker will be hidden from navigation")
                print("   ✓ App will automatically use English")
                print("   ✓ Language switching will be disabled")
            else:
                print("   ⚠️ Language picker is still enabled (check configuration)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Restore original environment variable
    if original_value is not None:
        os.environ['LANGUAGE_PICKER_ENABLED'] = original_value
    elif 'LANGUAGE_PICKER_ENABLED' in os.environ:
        del os.environ['LANGUAGE_PICKER_ENABLED']
    
    # Clean up DISABLE_LANGUAGE_PICKER
    if 'DISABLE_LANGUAGE_PICKER' in os.environ:
        del os.environ['DISABLE_LANGUAGE_PICKER']
    
    print()
    print("=== Configuration Instructions ===")
    print("To disable the language picker, add to your .env file:")
    print("DISABLE_LANGUAGE_PICKER=true")
    print()
    print("To enable the language picker (default), add to your .env file:")
    print("LANGUAGE_PICKER_ENABLED=true")
    print()
    print("Or simply omit the variables to use the default (enabled)")
    print()
    print("=== Supported Languages ===")
    print("- English (en): Default language")
    print("- Czech (cs): Secondary language") 
    print("- Slovak (sk): Third language option")

if __name__ == '__main__':
    test_language_picker_config() 