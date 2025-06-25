#!/usr/bin/env python3
"""
Test configuration for the Guest Registration System
"""

import os
import tempfile
import shutil
from datetime import datetime

class TestConfig:
    """Test-specific configuration"""
    
    # Test-specific settings
    TEST_PORT = 5001
    TEST_TABLE_PREFIX = 'test_guest_reg_'
    TEST_DATABASE_NAME = 'guest_registration_test'
    TEST_UPLOAD_FOLDER = 'test_uploads'
    
    # Test server settings
    TEST_SERVER_URL = f'http://localhost:{TEST_PORT}'
    TEST_SERVER_PROTOCOL = 'http'
    TEST_SERVER_HOST = 'localhost'
    TEST_SERVER_PORT = str(TEST_PORT)
    
    # Test admin credentials
    TEST_ADMIN_USERNAME = 'test_admin'
    TEST_ADMIN_PASSWORD = 'test_password123'
    TEST_ADMIN_EMAIL = 'test_admin@example.com'
    
    # Test data settings
    TEST_TRIP_COUNT = 5
    TEST_REGISTRATION_COUNT = 10
    TEST_GUEST_COUNT = 20
    TEST_INVOICE_COUNT = 8
    
    @classmethod
    def setup_test_environment(cls):
        """Set up test environment variables"""
        # Database configuration (use SQLite for tests)
        db_path = os.path.abspath(f'{cls.TEST_DATABASE_NAME}.db')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        os.environ['TABLE_PREFIX'] = cls.TEST_TABLE_PREFIX
        
        # Server configuration
        os.environ['SERVER_URL'] = cls.TEST_SERVER_URL
        os.environ['SERVER_PROTOCOL'] = cls.TEST_SERVER_PROTOCOL
        os.environ['SERVER_HOST'] = cls.TEST_SERVER_HOST
        os.environ['SERVER_PORT'] = cls.TEST_SERVER_PORT
        
        # Flask configuration
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['TESTING'] = 'true'
        
        # Mail configuration (use test settings)
        os.environ['MAIL_SERVER'] = 'localhost'
        os.environ['MAIL_PORT'] = '1025'  # Test mail server port
        os.environ['MAIL_USE_TLS'] = 'false'
        os.environ['MAIL_USERNAME'] = 'test@example.com'
        os.environ['MAIL_PASSWORD'] = 'test_password'
        
        # Create test upload directory
        os.makedirs(cls.TEST_UPLOAD_FOLDER, exist_ok=True)
        os.environ['UPLOAD_FOLDER'] = cls.TEST_UPLOAD_FOLDER
    
    @classmethod
    def cleanup_test_environment(cls):
        """Clean up test environment"""
        # Remove test upload directory
        if os.path.exists(cls.TEST_UPLOAD_FOLDER):
            shutil.rmtree(cls.TEST_UPLOAD_FOLDER)
        
        # Clear test environment variables
        test_vars = [
            'DATABASE_URL', 'TABLE_PREFIX', 'SERVER_URL', 'SERVER_PROTOCOL',
            'SERVER_HOST', 'SERVER_PORT', 'FLASK_ENV', 'TESTING',
            'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USERNAME',
            'MAIL_PASSWORD', 'UPLOAD_FOLDER'
        ]
        
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]
    
    @classmethod
    def get_test_database_url(cls):
        """Get test database URL"""
        db_path = os.path.abspath(f'{cls.TEST_DATABASE_NAME}.db')
        return f'sqlite:///{db_path}'
    
    @classmethod
    def get_test_app_config(cls):
        """Get test app configuration"""
        return {
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SERVER_NAME': f'localhost:{cls.TEST_PORT}',
            'PREFERRED_URL_SCHEME': 'http'
        } 