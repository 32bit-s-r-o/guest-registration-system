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
from migrations import MigrationManager

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

# Initialize migration manager lazily (only when needed)
migration_manager = None

def get_migration_manager():
    """Get migration manager instance, creating it if needed"""
    global migration_manager
    if migration_manager is None:
        migration_manager = MigrationManager()
    return migration_manager

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

if __name__ == '__main__':
    app.run(debug=True) 