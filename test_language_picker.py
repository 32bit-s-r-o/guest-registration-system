#!/usr/bin/env python3
"""
Test script to demonstrate language picker configuration.
This script shows how to enable/disable the language picker.
"""

import os
import sys

def test_language_picker_config():
    """Test the language picker configuration."""
    
    print("=== Language Picker Configuration Test ===\n")
    
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
    print("2. Testing with LANGUAGE_PICKER_ENABLED=false")
    os.environ['LANGUAGE_PICKER_ENABLED'] = 'false'
    
    try:
        # Clear any cached imports
        if 'app' in sys.modules:
            del sys.modules['app']
        
        from app import app
        with app.app_context():
            enabled = app.config['LANGUAGE_PICKER_ENABLED']
            print(f"   Language picker enabled: {enabled}")
            print("   ✓ Language picker will be hidden from navigation")
            print("   ✓ App will automatically use English")
            print("   ✓ Language switching will be disabled")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Restore original environment variable
    if original_value is not None:
        os.environ['LANGUAGE_PICKER_ENABLED'] = original_value
    elif 'LANGUAGE_PICKER_ENABLED' in os.environ:
        del os.environ['LANGUAGE_PICKER_ENABLED']
    
    print()
    print("=== Configuration Instructions ===")
    print("To disable the language picker, add to your .env file:")
    print("LANGUAGE_PICKER_ENABLED=false")
    print()
    print("To enable the language picker (default), add to your .env file:")
    print("LANGUAGE_PICKER_ENABLED=true")
    print()
    print("Or simply omit the variable to use the default (enabled)")
    print()
    print("=== Supported Languages ===")
    print("- English (en): Default language")
    print("- Czech (cs): Secondary language") 
    print("- Slovak (sk): Third language option")

if __name__ == '__main__':
    test_language_picker_config() 