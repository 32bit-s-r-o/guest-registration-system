import os
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO, BytesIO
import tempfile
import zipfile
import csv
import shutil
import subprocess
import sys

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file, jsonify
from flask_login import LoginManager, login_required, current_user
from flask_babel import Babel, gettext as _
from flask_mail import Mail, Message
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from werkzeug.exceptions import RequestEntityTooLarge

# Import version and migration managers
from version import VersionManager, version_manager, check_version_compatibility, get_version_changelog
from migrations import MigrationManager, get_migration_manager

# Import all database models and utilities from database.py
from database import (
    db, User, Amenity, AmenityHousekeeper, Calendar, Trip, Registration, Guest, 
    Invoice, InvoiceItem, Housekeeping, HousekeepingPhoto,
    get_database_url, copy_sample_image,
    parse_airbnb_guest_info, fetch_airbnb_calendar, sync_airbnb_reservations,
    sync_all_amenities_for_admin, sync_calendar_reservations, sync_all_calendars_for_admin,
    fetch_calendar_data, create_missing_housekeeping_tasks_for_calendar
)

# Import config
from config import Config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Note: get_migration_manager is now imported from migrations.py

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Startup logging
def log_startup_info():
    """Log startup information including database and table prefix"""
    print("🚀 Guest Registration System Starting Up")
    print("=" * 50)
    
    # Get version information
    from version import __version__
    print(f"📦 Version: {__version__}")
    
    # Get system information
    import sys
    import os
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📂 Working Directory: {os.getcwd()}")
    
    # Get database information
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
    table_prefix = app.config.get('TABLE_PREFIX', 'Not configured')
    
    # Mask sensitive database credentials for security
    if 'postgresql://' in db_url:
        # Parse PostgreSQL URL to show host and database name
        try:
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            masked_url = f"postgresql://***:***@{host}:{port}/{database}"
        except:
            masked_url = "postgresql://***:***@***/***"
        print(f"🗄️  Database: {masked_url}")
    elif 'sqlite:///' in db_url:
        db_file = db_url.replace('sqlite:///', '')
        print(f"🗄️  Database: SQLite ({db_file})")
    else:
        print(f"🗄️  Database: {db_url}")
    
    print(f"🏷️  Table Prefix: {table_prefix}")
    print(f"📁 Upload Folder: {app.config.get('UPLOAD_FOLDER', 'Not configured')}")
    
    # Get server URL properly (it's a property)
    try:
        server_url = app.config.SERVER_URL
        if server_url is None:
            server_url = "Not configured"
    except:
        server_url = "Not configured"
    print(f"🌐 Server URL: {server_url}")
    
    print(f"🔧 Debug Mode: {app.config.get('DEBUG', False)}")
    print("=" * 50)

# Log startup information
log_startup_info()

def get_locale():
    # If language picker is disabled, always return English
    if os.environ.get('DISABLE_LANGUAGE_PICKER', 'false').lower() == 'true':
        return 'en'
    
    # Check if user has selected a language
    if 'language' in session:
        return session['language']
    
    # Try to get language from request
    if request:
        return request.accept_languages.best_match(['en', 'cs', 'sk'])
    
    return 'en'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.admin_login'
babel = Babel(app, locale_selector=get_locale)
mail = Mail(app)

# Test database connection and log status
def test_database_connection():
    """Test database connection and log the result"""
    try:
        with app.app_context():
            # Test the connection by executing a simple query
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection: SUCCESS")
            
            # Get database info
            if 'postgresql://' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
                result = db.session.execute(text('SELECT current_database(), current_user, version()'))
                db_info = result.fetchone()
                print(f"   📊 Database: {db_info[0]}")
                print(f"   👤 User: {db_info[1]}")
                print(f"   🔧 Version: {db_info[2].split()[1]}")
            else:
                print("   📊 Database: SQLite")
                
    except Exception as e:
        print(f"❌ Database connection: FAILED - {str(e)}")

# Test database connection
test_database_connection()

@app.context_processor
def inject_get_locale():
    return dict(
        get_locale=get_locale,
        language_picker_enabled=app.config['LANGUAGE_PICKER_ENABLED']
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash(_('File too large. Maximum file size is 16MB.'), 'error')
    return redirect(request.referrer or url_for('main.index'))

# Register template filters
from template_filters import register_template_filters
register_template_filters(app)

# Register URL utilities
from utils import register_url_utils
register_url_utils(app)

# Register blueprints
from blueprints.main import main
from blueprints.auth import auth
from blueprints.registration import registration
from blueprints.admin import admin
from blueprints.amenities import amenities
from blueprints.trips import trips
from blueprints.registrations import registrations
from blueprints.invoices import invoices
from blueprints.housekeeping import housekeeping
from blueprints.calendars import calendars
from blueprints.users import users
from blueprints.export import export
from blueprints.breakdowns import breakdowns
from blueprints.api import api
from blueprints.health import health

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(registration)
app.register_blueprint(admin)
app.register_blueprint(amenities)
app.register_blueprint(trips)
app.register_blueprint(registrations)
app.register_blueprint(invoices)
app.register_blueprint(housekeeping)
app.register_blueprint(calendars)
app.register_blueprint(users)
app.register_blueprint(export)
app.register_blueprint(breakdowns)
app.register_blueprint(api)
app.register_blueprint(health)

# Final startup logging
def log_startup_complete():
    """Log that the application startup is complete"""
    print("🎯 Application startup complete!")
    print(f"📋 Registered {len(app.blueprints)} blueprints:")
    for blueprint_name in app.blueprints.keys():
        print(f"   - {blueprint_name}")
    print("=" * 50)
    print("🌐 Ready to serve requests!")
    print("=" * 50)

# Log startup completion
log_startup_complete()

if __name__ == '__main__':
    app.run(debug=True) 