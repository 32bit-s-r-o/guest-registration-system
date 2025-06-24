import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///guest_registration.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    TABLE_PREFIX = os.environ.get('TABLE_PREFIX', '')
    VERSION = os.environ.get('VERSION', '1.0.0')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    
    # Language and internationalization settings
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'cs', 'sk']
    LANGUAGE_PICKER_ENABLED = os.environ.get('LANGUAGE_PICKER_ENABLED', 'true').lower() == 'true'
    
    # Feature flags
    DISABLE_LANGUAGE_PICKER = os.environ.get('DISABLE_LANGUAGE_PICKER', 'false').lower() == 'true' 