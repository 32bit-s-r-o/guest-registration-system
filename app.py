import os
import uuid
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
from collections import defaultdict

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from flask_mail import Mail, Message
import requests
from icalendar import Calendar as iCalCalendar
import pytz

# Import version and migration managers
from version import VersionManager, version_manager, check_version_compatibility, get_version_changelog
from migrations import MigrationManager

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///guest_registration.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['TABLE_PREFIX'] = os.environ.get('TABLE_PREFIX', '')
app.config['VERSION'] = os.environ.get('VERSION', '1.0.0')

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.admin_login'
babel = Babel(app)
mail = Mail(app)

# Initialize migration manager
migration_manager = MigrationManager()

def get_database_url():
    """Get database URL from environment or use default."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Default to SQLite
    return 'sqlite:///guest_registration.db'

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

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

def copy_sample_image(image_filename):
    """Copy a sample image to the uploads folder if it doesn't exist."""
    sample_path = os.path.join('static', 'sample_images', image_filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    
    if os.path.exists(sample_path) and not os.path.exists(upload_path):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        shutil.copy2(sample_path, upload_path)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Contact information
    company_name = db.Column(db.String(200))
    company_ico = db.Column(db.String(50))  # Company identification number
    company_vat = db.Column(db.String(50))  # VAT number
    contact_name = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    contact_address = db.Column(db.Text)
    contact_website = db.Column(db.String(200))
    contact_description = db.Column(db.Text)
    # Photo upload configuration
    photo_required_adults = db.Column(db.Boolean, default=True)  # Require photos for adults
    photo_required_children = db.Column(db.Boolean, default=True)  # Require photos for children
    # Additional custom lines (for future use)
    custom_line_1 = db.Column(db.String(200))
    custom_line_2 = db.Column(db.String(200))
    custom_line_3 = db.Column(db.String(200))
    # Preferred date format
    date_format = db.Column(db.String(32), default='d.m.Y')
    # Default housekeeper pay
    default_housekeeper_pay = db.Column(db.Numeric(10, 2), default=20)
    # Soft delete flag
    is_deleted = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Amenity(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}amenity"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    max_guests = db.Column(db.Integer, nullable=False, default=1)
    admin_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Status
    is_active = db.Column(db.Boolean, default=True)
    # Backward compatibility
    default_housekeeper_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}user.id'))
    
    # Relationships
    admin = db.relationship('User', backref='amenities', foreign_keys=[admin_id])
    default_housekeeper = db.relationship('User', backref='default_amenities', foreign_keys=[default_housekeeper_id])
    trips = db.relationship('Trip', backref='amenity', lazy=True)
    calendars = db.relationship('Calendar', backref='amenity', lazy=True, cascade='all, delete-orphan')
    housekeepers = db.relationship('AmenityHousekeeper', backref='amenity', lazy=True, cascade='all, delete-orphan')

class AmenityHousekeeper(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}amenity_housekeeper"
    
    id = db.Column(db.Integer, primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}amenity.id'), nullable=False)
    housekeeper_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}user.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    housekeeper = db.relationship('User', backref='amenity_assignments')
    
    __table_args__ = (
        db.UniqueConstraint('amenity_id', 'housekeeper_id', name='uq_amenity_housekeeper'),
    )

class Calendar(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}calendar"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amenity_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}amenity.id'), nullable=False)
    # Calendar settings
    calendar_url = db.Column(db.Text, nullable=False)
    calendar_type = db.Column(db.String(50), default='airbnb')  # airbnb, booking, vrbo, custom
    sync_enabled = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    sync_frequency = db.Column(db.String(20), default='daily')  # hourly, daily, weekly
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='calendar', lazy=True)

class Trip(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}trip"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}user.id'), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}amenity.id'), nullable=False)
    calendar_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}calendar.id'))
    registrations = db.relationship('Registration', backref='trip', lazy=True)
    # External sync fields
    external_reservation_id = db.Column(db.String(100), unique=True)
    external_guest_name = db.Column(db.String(200))
    external_guest_email = db.Column(db.String(200))
    external_guest_count = db.Column(db.Integer)
    external_synced_at = db.Column(db.DateTime)
    is_externally_synced = db.Column(db.Boolean, default=False)
    # External confirmation code
    external_confirm_code = db.Column(db.String(50), unique=True)

class Registration(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}registration"
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}trip.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_comment = db.Column(db.Text)
    language = db.Column(db.String(10), default='en')  # Store selected language
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    guests = db.relationship('Guest', backref='registration', lazy=True, cascade='all, delete-orphan')

class Guest(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}guest"
    
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}registration.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age_category = db.Column(db.String(20), nullable=False, default='adult')  # adult, child
    document_type = db.Column(db.String(50), nullable=False)  # passport, driving_license, citizen_id
    document_number = db.Column(db.String(100), nullable=False)
    document_image = db.Column(db.String(255))  # File path to uploaded image
    gdpr_consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}invoice"
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}user.id'), nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}registration.id'))
    client_name = db.Column(db.String(200), nullable=False)
    client_email = db.Column(db.String(200))
    client_vat_number = db.Column(db.String(50))
    client_address = db.Column(db.Text)
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    due_date = db.Column(db.Date)
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    vat_total = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(3), default='EUR')
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    admin = db.relationship('User', backref='invoices')
    registration = db.relationship('Registration', backref='invoices')

class InvoiceItem(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}invoice_item"
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}invoice.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 2), default=0)  # VAT rate as percentage
    line_total = db.Column(db.Numeric(10, 2), default=0)
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    total_with_vat = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Housekeeping(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}housekeeping"
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}trip.id'), nullable=False)
    housekeeper_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    pay_amount = db.Column(db.Numeric(10, 2), default=0)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    amenity_photo_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', backref='housekeeping_tasks')
    housekeeper = db.relationship('User', backref='housekeeping_tasks')

class HousekeepingPhoto(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}housekeeping_photo"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}housekeeping.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship('Housekeeping', backref=db.backref('photos', lazy=True, cascade='all, delete-orphan'))

# Login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions
def parse_airbnb_guest_info(summary, description):
    """Parse guest information from Airbnb calendar event."""
    guest_info = {
        'name': '',
        'email': '',
        'count': 1,
        'confirmation_code': ''
    }
    
    # Try to extract guest name from summary
    if summary:
        # Common patterns in Airbnb summaries
        import re
        
        # Pattern 1: "Guest Name - Confirmation Code"
        match = re.search(r'^([^-]+?)\s*-\s*([A-Z0-9]+)$', summary.strip())
        if match:
            guest_info['name'] = match.group(1).strip()
            guest_info['confirmation_code'] = match.group(2).strip()
        
        # Pattern 2: "Guest Name (X guests)"
        match = re.search(r'^([^(]+?)\s*\((\d+)\s*guests?\)', summary.strip())
        if match:
            guest_info['name'] = match.group(1).strip()
            guest_info['count'] = int(match.group(2))
        
        # Pattern 3: Just guest name
        if not guest_info['name'] and not re.search(r'[A-Z0-9]{6,}', summary):
            guest_info['name'] = summary.strip()
    
    # Try to extract email from description
    if description:
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', description)
        if email_match:
            guest_info['email'] = email_match.group(0)
    
    return guest_info

def fetch_airbnb_calendar(calendar_url):
    """Fetch calendar data from Airbnb URL."""
    try:
        response = requests.get(calendar_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching calendar: {e}")
        return None

def sync_airbnb_reservations(amenity_id):
    """Sync Airbnb reservations for a specific amenity."""
    amenity = Amenity.query.get(amenity_id)
    if not amenity:
        return {'success': False, 'message': 'Amenity not found'}
    
    # Get all calendars for this amenity
    calendars = Calendar.query.filter_by(amenity_id=amenity_id, sync_enabled=True).all()
    
    if not calendars:
        return {'success': False, 'message': 'No calendars found for this amenity'}
    
    synced_count = 0
    errors = []
    
    for calendar in calendars:
        try:
            result = sync_calendar_reservations(calendar.id)
            if result['success']:
                synced_count += result.get('count', 0)
            else:
                errors.append(f"Calendar {calendar.name}: {result['message']}")
        except Exception as e:
            errors.append(f"Calendar {calendar.name}: {str(e)}")
    
    if errors:
        return {'success': False, 'message': f"Sync completed with errors: {'; '.join(errors)}"}
    
    return {'success': True, 'message': f"Successfully synced {synced_count} reservations"}

def sync_all_amenities_for_admin(admin_id):
    """Sync all amenities for a specific admin."""
    amenities = Amenity.query.filter_by(admin_id=admin_id).all()
    
    total_synced = 0
    errors = []
    
    for amenity in amenities:
        try:
            result = sync_airbnb_reservations(amenity.id)
            if result['success']:
                # Extract count from message if possible
                import re
                count_match = re.search(r'(\d+)', result['message'])
                if count_match:
                    total_synced += int(count_match.group(1))
            else:
                errors.append(f"Amenity {amenity.name}: {result['message']}")
        except Exception as e:
            errors.append(f"Amenity {amenity.name}: {str(e)}")
    
    if errors:
        return {'success': False, 'message': f"Sync completed with errors: {'; '.join(errors)}"}
    
    return {'success': True, 'message': f"Successfully synced {total_synced} reservations across all amenities"}

def sync_calendar_reservations(calendar_id):
    """Sync reservations from a specific calendar."""
    calendar = Calendar.query.get(calendar_id)
    if not calendar:
        return {'success': False, 'message': 'Calendar not found'}
    
    if not calendar.sync_enabled:
        return {'success': False, 'message': 'Calendar sync is disabled'}
    
    try:
        # Fetch calendar data
        calendar_data = fetch_calendar_data(calendar.calendar_url, calendar.calendar_type)
        if not calendar_data:
            return {'success': False, 'message': 'Failed to fetch calendar data'}
        
        # Parse calendar
        cal = iCalCalendar.from_ical(calendar_data)
        
        synced_count = 0
        errors = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                try:
                    # Extract event data
                    summary = str(component.get('summary', ''))
                    description = str(component.get('description', ''))
                    start_date = component.get('dtstart').dt
                    end_date = component.get('dtend').dt
                    
                    # Convert to date if it's a datetime
                    if hasattr(start_date, 'date'):
                        start_date = start_date.date()
                    if hasattr(end_date, 'date'):
                        end_date = end_date.date()
                    
                    # Parse guest information
                    guest_info = parse_airbnb_guest_info(summary, description)
                    
                    # Check if trip already exists
                    existing_trip = Trip.query.filter_by(
                        external_reservation_id=str(component.get('uid', '')),
                        amenity_id=calendar.amenity_id
                    ).first()
                    
                    if existing_trip:
                        # Update existing trip
                        existing_trip.title = summary or f"Reservation {start_date} - {end_date}"
                        existing_trip.start_date = start_date
                        existing_trip.end_date = end_date
                        existing_trip.external_guest_name = guest_info['name']
                        existing_trip.external_guest_email = guest_info['email']
                        existing_trip.external_guest_count = guest_info['count']
                        existing_trip.external_confirm_code = guest_info['confirmation_code']
                        existing_trip.external_synced_at = datetime.utcnow()
                        existing_trip.is_externally_synced = True
                    else:
                        # Create new trip
                        trip = Trip(
                            title=summary or f"Reservation {start_date} - {end_date}",
                            start_date=start_date,
                            end_date=end_date,
                            max_guests=calendar.amenity.max_guests,
                            admin_id=calendar.amenity.admin_id,
                            amenity_id=calendar.amenity_id,
                            calendar_id=calendar.id,
                            external_reservation_id=str(component.get('uid', '')),
                            external_guest_name=guest_info['name'],
                            external_guest_email=guest_info['email'],
                            external_guest_count=guest_info['count'],
                            external_confirm_code=guest_info['confirmation_code'],
                            external_synced_at=datetime.utcnow(),
                            is_externally_synced=True
                        )
                        db.session.add(trip)
                    
                    synced_count += 1
                    
                except Exception as e:
                    errors.append(f"Event {summary}: {str(e)}")
        
        # Update calendar last sync time
        calendar.last_sync = datetime.utcnow()
        db.session.commit()
        
        if errors:
            return {'success': True, 'message': f"Synced {synced_count} reservations with {len(errors)} errors", 'count': synced_count, 'errors': errors}
        
        return {'success': True, 'message': f"Successfully synced {synced_count} reservations", 'count': synced_count}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f"Error syncing calendar: {str(e)}"}

def sync_all_calendars_for_admin(admin_id):
    """Sync all calendars for a specific admin."""
    # Get all amenities for this admin
    amenities = Amenity.query.filter_by(admin_id=admin_id).all()
    
    total_synced = 0
    errors = []
    
    for amenity in amenities:
        # Get all calendars for this amenity
        calendars = Calendar.query.filter_by(amenity_id=amenity.id, sync_enabled=True).all()
        
        for calendar in calendars:
            try:
                result = sync_calendar_reservations(calendar.id)
                if result['success']:
                    total_synced += result.get('count', 0)
                else:
                    errors.append(f"Calendar {calendar.name}: {result['message']}")
            except Exception as e:
                errors.append(f"Calendar {calendar.name}: {str(e)}")
    
    if errors:
        return {'success': False, 'message': f"Sync completed with errors: {'; '.join(errors)}"}
    
    return {'success': True, 'message': f"Successfully synced {total_synced} reservations across all calendars"}

def fetch_calendar_data(calendar_url, calendar_type='airbnb'):
    """Fetch calendar data from URL."""
    try:
        response = requests.get(calendar_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching calendar: {e}")
        return None

def create_missing_housekeeping_tasks_for_calendar(calendar_id):
    """Create housekeeping tasks for all trips in a calendar that don't have them."""
    calendar = Calendar.query.get(calendar_id)
    if not calendar:
        return {'success': False, 'message': 'Calendar not found'}
    
    # Get all trips for this calendar
    trips = Trip.query.filter_by(calendar_id=calendar_id).all()
    
    created_count = 0
    errors = []
    
    for trip in trips:
        try:
            # Check if housekeeping tasks already exist for this trip
            existing_tasks = Housekeeping.query.filter_by(trip_id=trip.id).all()
            
            if existing_tasks:
                continue  # Skip if tasks already exist
            
            # Get the default housekeeper for this amenity
            default_housekeeper = None
            if calendar.amenity.default_housekeeper_id:
                default_housekeeper = User.query.get(calendar.amenity.default_housekeeper_id)
            else:
                # Try to find a default housekeeper assignment
                assignment = AmenityHousekeeper.query.filter_by(
                    amenity_id=calendar.amenity_id,
                    is_default=True
                ).first()
                if assignment:
                    default_housekeeper = assignment.housekeeper
            
            if not default_housekeeper:
                errors.append(f"No default housekeeper found for amenity {calendar.amenity.name}")
                continue
            
            # Create housekeeping task for the end date of the trip
            housekeeping_task = Housekeeping(
                trip_id=trip.id,
                housekeeper_id=default_housekeeper.id,
                date=trip.end_date,
                status='pending',
                pay_amount=calendar.amenity.admin.default_housekeeper_pay or 20
            )
            
            db.session.add(housekeeping_task)
            created_count += 1
            
        except Exception as e:
            errors.append(f"Trip {trip.title}: {str(e)}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f"Database error: {str(e)}"}
    
    if errors:
        return {'success': True, 'message': f"Created {created_count} housekeeping tasks with {len(errors)} errors", 'count': created_count, 'errors': errors}
    
    return {'success': True, 'message': f"Successfully created {created_count} housekeeping tasks", 'count': created_count}

# Template filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags."""
    if text:
        return text.replace('\n', '<br>')
    return ''

@app.template_filter('format_date')
def format_date_filter(date_obj):
    """Format date according to user preference."""
    if not date_obj:
        return ''
    
    # Get user's preferred date format
    date_format = 'd.m.Y'  # Default
    if current_user.is_authenticated and hasattr(current_user, 'date_format') and current_user.date_format:
        date_format = current_user.date_format
    
    # Convert PHP/JS style to Python strftime format
    format_map = [
        ('d', '%d'),
        ('j', '%-d'),
        ('m', '%m'),
        ('n', '%-m'),
        ('Y', '%Y'),
        ('y', '%y'),
    ]
    
    py_format = date_format
    for php, py in format_map:
        py_format = py_format.replace(php, py)
    
    try:
        return date_obj.strftime(py_format)
    except:
        return date_obj.strftime('%d.%m.%Y')

@app.template_filter('registration_name')
def registration_name(reg):
    """Get a display name for a registration."""
    if reg.guests:
        first_guest = reg.guests[0]
        return f"{first_guest.first_name} {first_guest.last_name}"
    return reg.email

# Main routes (not moved to blueprints)
# All main routes are now handled by the main blueprint

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