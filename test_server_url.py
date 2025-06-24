#!/usr/bin/env python3
"""
Test script to verify server URL configuration and functionality
"""

import os
import sys
from flask import Flask

def clear_server_url_env():
    for var in ['SERVER_URL', 'SERVER_PROTOCOL', 'SERVER_HOST', 'SERVER_PORT']:
        if var in os.environ:
            del os.environ[var]

def test_server_url_configuration():
    """Test server URL configuration"""
    print("🔧 Testing Server URL Configuration")
    print("=" * 50)
    
    # Test environment variables
    test_cases = [
        {
            'name': 'Complete SERVER_URL',
            'env': {
                'SERVER_URL': 'https://myapp.example.com'
            },
            'expected': 'https://myapp.example.com'
        },
        {
            'name': 'HTTP with custom port',
            'env': {
                'SERVER_PROTOCOL': 'http',
                'SERVER_HOST': '192.168.1.100',
                'SERVER_PORT': '8080'
            },
            'expected': 'http://192.168.1.100:8080'
        },
        {
            'name': 'HTTPS with standard port',
            'env': {
                'SERVER_PROTOCOL': 'https',
                'SERVER_HOST': 'myapp.example.com',
                'SERVER_PORT': '443'
            },
            'expected': 'https://myapp.example.com'
        },
        {
            'name': 'HTTP with standard port',
            'env': {
                'SERVER_PROTOCOL': 'http',
                'SERVER_HOST': 'localhost',
                'SERVER_PORT': '80'
            },
            'expected': 'http://localhost'
        },
        {
            'name': 'Default configuration',
            'env': {},
            'expected': 'http://localhost:5000'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        # Clear all relevant env vars before each test
        clear_server_url_env()
        # Set environment variables
        for key, value in test_case['env'].items():
            os.environ[key] = value
        
        try:
            # Create a minimal Flask app to test
            app = Flask(__name__)
            from utils import load_dynamic_server_config
            load_dynamic_server_config(app)
            
            # Import and test the function within app context
            from utils import get_server_url
            with app.app_context():
                result = get_server_url()
                
                if result == test_case['expected']:
                    print(f"✅ PASS: {result}")
                else:
                    print(f"❌ FAIL: Expected {test_case['expected']}, got {result}")
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Clean up environment variables
        clear_server_url_env()

def test_template_integration():
    """Test template integration"""
    print("\n🔧 Testing Template Integration")
    print("=" * 50)
    
    try:
        clear_server_url_env()
        # Create a minimal Flask app
        app = Flask(__name__)
        from utils import load_dynamic_server_config
        load_dynamic_server_config(app)
        app.config.from_object('config.Config')
        
        # Set required Flask config for URL generation
        app.config['SERVER_NAME'] = 'test.example.com'
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        
        # Set test environment
        os.environ['SERVER_URL'] = 'https://test.example.com'
        
        # Register URL utilities
        from utils import register_url_utils
        register_url_utils(app)
        
        # Register the registration blueprint
        from blueprints.registration import registration
        app.register_blueprint(registration, url_prefix='/registration')
        
        from flask import render_template_string
        with app.app_context():
            # Render a template that uses server_url
            template = "Server URL: {{ server_url }}"
            rendered = render_template_string(template)
            if 'https://test.example.com' in rendered:
                print(f"✅ Context processor: {rendered}")
            else:
                print(f"❌ Context processor: {rendered}")
            
            # Test template filter
            filter_func = app.jinja_env.filters['absolute_url']
            result = filter_func('/admin/dashboard')
            expected = 'https://test.example.com/admin/dashboard'
            
            if result == expected:
                print(f"✅ Template filter: {result}")
            else:
                print(f"❌ Template filter: Expected {expected}, got {result}")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        clear_server_url_env()

def test_docker_configuration():
    """Test Docker configuration examples"""
    print("\n🐳 Testing Docker Configuration Examples")
    print("=" * 50)
    
    docker_examples = [
        {
            'name': 'HTTPS with domain',
            'config': {
                'SERVER_URL': 'https://myapp.example.com'
            },
            'description': 'For production with custom domain'
        },
        {
            'name': 'HTTP with IP and port',
            'config': {
                'SERVER_PROTOCOL': 'http',
                'SERVER_HOST': '192.168.1.100',
                'SERVER_PORT': '8000'
            },
            'description': 'For development or internal deployment'
        },
        {
            'name': 'HTTPS with custom port',
            'config': {
                'SERVER_PROTOCOL': 'https',
                'SERVER_HOST': 'myapp.example.com',
                'SERVER_PORT': '8443'
            },
            'description': 'For HTTPS with non-standard port'
        }
    ]
    
    for example in docker_examples:
        print(f"\n📋 {example['name']}")
        print(f"   Description: {example['description']}")
        print("   Environment variables:")
        clear_server_url_env()
        for key, value in example['config'].items():
            print(f"   - {key}={value}")
            os.environ[key] = value
        
        try:
            app = Flask(__name__)
            from utils import load_dynamic_server_config
            load_dynamic_server_config(app)
            app.config.from_object('config.Config')
            from utils import get_server_url
            with app.app_context():
                result = get_server_url()
                print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        finally:
            clear_server_url_env()

def test_email_integration():
    """Test email integration with server URL"""
    print("\n📧 Testing Email Integration")
    print("=" * 50)
    
    try:
        clear_server_url_env()
        # Set test environment
        os.environ['SERVER_URL'] = 'https://myapp.example.com'
        os.environ['MAIL_USERNAME'] = 'test@example.com'
        
        # Create a minimal Flask app
        app = Flask(__name__)
        from utils import load_dynamic_server_config
        load_dynamic_server_config(app)
        app.config.from_object('config.Config')
        
        # Set required Flask config for URL generation
        app.config['SERVER_NAME'] = 'myapp.example.com'
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        
        # Register the registration blueprint
        from blueprints.registration import registration
        app.register_blueprint(registration, url_prefix='/registration')
        
        # Initialize extensions
        from flask_mail import Mail
        mail = Mail(app)
        
        with app.app_context():
            # Test email URL generation
            from utils import get_server_url
            server_url = get_server_url()
            print(f"✅ Server URL for emails: {server_url}")
            
            # Test URL generation for registration
            from flask import url_for
            registration_url = f"{server_url}{url_for('registration.register', trip_id=1)}"
            print(f"✅ Registration URL: {registration_url}")
            
            # Verify it's not localhost
            if 'localhost' not in registration_url:
                print("✅ URL correctly uses external server")
            else:
                print("❌ URL still contains localhost")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        clear_server_url_env()
        if 'MAIL_USERNAME' in os.environ:
            del os.environ['MAIL_USERNAME']

def test_config_loading():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration Loading")
    print("=" * 50)
    
    test_configs = [
        {
            'name': 'Complete URL override',
            'env': {'SERVER_URL': 'https://override.example.com'},
            'expected_protocol': 'https',
            'expected_host': 'override.example.com'
        },
        {
            'name': 'Component-based config',
            'env': {
                'SERVER_PROTOCOL': 'https',
                'SERVER_HOST': 'component.example.com',
                'SERVER_PORT': '8443'
            },
            'expected_protocol': 'https',
            'expected_host': 'component.example.com'
        }
    ]
    
    for test_config in test_configs:
        print(f"\n🧪 Testing: {test_config['name']}")
        
        clear_server_url_env()
        # Set environment
        for key, value in test_config['env'].items():
            os.environ[key] = value
        
        try:
            app = Flask(__name__)
            from utils import load_dynamic_server_config
            load_dynamic_server_config(app)
            
            print(f"   SERVER_URL: {app.config.get('SERVER_URL')}")
            print(f"   SERVER_PROTOCOL: {app.config.get('SERVER_PROTOCOL')}")
            print(f"   SERVER_HOST: {app.config.get('SERVER_HOST')}")
            print(f"   SERVER_PORT: {app.config.get('SERVER_PORT')}")
            
            # Verify config values
            if app.config.get('SERVER_PROTOCOL') == test_config['expected_protocol']:
                print(f"   ✅ Protocol: {app.config.get('SERVER_PROTOCOL')}")
            else:
                print(f"   ❌ Protocol: Expected {test_config['expected_protocol']}, got {app.config.get('SERVER_PROTOCOL')}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        finally:
            clear_server_url_env()

def main():
    """Run all tests"""
    print("🚀 Server URL Configuration Test Suite")
    print("=" * 60)
    
    test_config_loading()
    test_server_url_configuration()
    test_template_integration()
    test_docker_configuration()
    test_email_integration()
    
    print("\n" + "=" * 60)
    print("📋 Configuration Instructions")
    print("=" * 60)
    print("For Docker deployments, set one of these options:")
    print()
    print("Option 1: Complete URL (recommended)")
    print("  SERVER_URL=https://your-domain.com")
    print()
    print("Option 2: Individual components")
    print("  SERVER_PROTOCOL=https")
    print("  SERVER_HOST=your-domain.com")
    print("  SERVER_PORT=443")
    print()
    print("Example docker-compose.yml:")
    print("  environment:")
    print("    - SERVER_URL=https://myapp.example.com")
    print()
    print("Example .env file:")
    print("  SERVER_URL=https://myapp.example.com")
    print()
    print("This ensures all generated URLs (emails, links) use the correct")
    print("external URL instead of localhost when running in Docker.")

if __name__ == '__main__':
    main() 