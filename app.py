from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv
import requests
import icalendar
from dateutil import parser
import re
import threading
import time
import shutil
from markupsafe import Markup
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import tempfile
from decimal import Decimal
from flask_babel import Babel, gettext as _
from functools import wraps
import json
import csv
from io import StringIO, BytesIO
from flask_babel import lazy_gettext as _l
from sqlalchemy import func, and_, or_
from collections import defaultdict
import calendar
import subprocess
import zipfile

# Add version management imports
from version import version_manager, check_version_compatibility, get_version_changelog
from migrations import MigrationManager
import argparse

load_dotenv()

# Create migration manager instance
migration_manager = MigrationManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Table prefix configuration
app.config['TABLE_PREFIX'] = os.getenv('TABLE_PREFIX', 'guest_reg_')

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Flask-Babel setup
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'cs']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Language picker configuration
app.config['LANGUAGE_PICKER_ENABLED'] = os.getenv('LANGUAGE_PICKER_ENABLED', 'true').lower() == 'true'

def get_locale():
    # If language picker is disabled, always return English
    if not app.config['LANGUAGE_PICKER_ENABLED']:
        return 'en'
    
    # Try to get language from session, then from request, fallback to default
    from flask import session, request
    lang = session.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        return lang
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(app, locale_selector=get_locale)

# Make get_locale available in templates
@app.context_processor
def inject_get_locale():
    return dict(
        get_locale=get_locale,
        language_picker_enabled=app.config['LANGUAGE_PICKER_ENABLED']
    )

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def copy_sample_image(image_filename):
    """Copy a sample image from static/sample_images to uploads directory."""
    sample_image_path = os.path.join('static', 'sample_images', image_filename)
    upload_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    
    if os.path.exists(sample_image_path):
        shutil.copy2(sample_image_path, upload_image_path)
        return image_filename
    else:
        print(f"Warning: Sample image not found: {sample_image_path}")
        return None

# Database Models with table prefix support
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
    # Soft delete flag
    is_deleted = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Set password hash for the user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id), is_deleted=False).first()

# Airbnb Calendar Sync Functions
def fetch_airbnb_calendar(calendar_url):
    """Fetch and parse Airbnb calendar data."""
    try:
        response = requests.get(calendar_url, timeout=30)
        response.raise_for_status()
        
        cal = icalendar.Calendar.from_ical(response.content)
        reservations = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                # Extract reservation details from event
                summary = str(component.get('summary', ''))
                description = str(component.get('description', ''))
                start_date = component.get('dtstart').dt
                end_date = component.get('dtend').dt
                
                # Skip "Not Available" events - only process actual reservations
                not_available_patterns = [
                    'not available',
                    'unavailable',
                    'blocked',
                    'maintenance',
                    'cleaning',
                    'no availability'
                ]
                
                summary_lower = summary.lower()
                if any(pattern in summary_lower for pattern in not_available_patterns):
                    continue  # Skip this event
                
                # Parse guest information from summary/description
                guest_info = parse_airbnb_guest_info(summary, description)
                
                reservation = {
                    'id': str(component.get('uid', '')),
                    'title': summary,
                    'start_date': start_date,
                    'end_date': end_date,
                    'guest_name': guest_info.get('name', ''),
                    'guest_email': guest_info.get('email', ''),
                    'guest_count': guest_info.get('count', 1),
                    'confirm_code': guest_info.get('confirm_code', ''),
                    'description': description
                }
                reservations.append(reservation)
        
        return reservations
    except Exception as e:
        print(f"Error fetching Airbnb calendar: {e}")
        return []

def parse_airbnb_guest_info(summary, description):
    """Parse guest information from Airbnb calendar event."""
    guest_info = {
        'name': '',
        'email': '',
        'count': 1,
        'confirm_code': ''
    }
    
    # Try to extract guest name from summary
    # Common patterns: "Guest Name - Airbnb" or "Guest Name (X guests)"
    name_patterns = [
        r'^(.+?)\s*-\s*Airbnb',
        r'^(.+?)\s*\(\d+\s*guests?\)',
        r'^(.+?)\s*-\s*\d+\s*guests?'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            guest_info['name'] = match.group(1).strip()
            break
    
    # Try to extract email from description
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, description)
    if email_match:
        guest_info['email'] = email_match.group(0)
    
    # Try to extract guest count
    count_patterns = [
        r'(\d+)\s*guests?',
        r'(\d+)\s*people'
    ]
    
    for pattern in count_patterns:
        match = re.search(pattern, summary + ' ' + description, re.IGNORECASE)
        if match:
            guest_info['count'] = int(match.group(1))
            break
    
    # Try to extract confirmation code from Airbnb reservation URL
    # Handle the case where URL is split across lines with \n
    confirm_patterns = [
        r'/de\s*\n\s*tails/([A-Z0-9]{10})',  # Handle split URL format
        r'/details/([A-Z0-9]{10})',  # Standard format
        r'tails/([A-Z0-9]{10})',  # Simple tails pattern
        r'confirmation\s+code:\s*([A-Z0-9]{6,})',
        r'code:\s*([A-Z0-9]{6,})',
        r'\b([A-Z0-9]{10})(?=\s|$|\\n)'  # 10-character code followed by space, end, or newline
    ]
    
    # Try patterns on the original description first (for split URLs)
    for pattern in confirm_patterns:
        match = re.search(pattern, summary + ' ' + description, re.IGNORECASE)
        if match:
            guest_info['confirm_code'] = match.group(1).upper()
            break
    
    # If no match found, try with normalized text
    if not guest_info['confirm_code']:
        normalized_text = summary + ' ' + description.replace('\n', ' ').replace('\\n', ' ')
        for pattern in confirm_patterns:
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                guest_info['confirm_code'] = match.group(1).upper()
                break
    
    return guest_info

def sync_airbnb_reservations(amenity_id):
    """Sync Airbnb reservations for a specific amenity, ensuring unique confirmation codes."""
    # This function is deprecated - use sync_calendar_reservations instead
    # Find the first calendar for this amenity and sync it
    calendar = Calendar.query.filter_by(amenity_id=amenity_id, calendar_type='airbnb').first()
    if calendar:
        return sync_calendar_reservations(calendar.id)
    else:
        return {'success': False, 'message': 'No Airbnb calendar found for this amenity'}

def sync_all_amenities_for_admin(admin_id):
    """Sync all amenities for a specific admin."""
    amenities = Amenity.query.filter_by(admin_id=admin_id, airbnb_sync_enabled=True, is_active=True).all()
    if not amenities:
        return {'success': False, 'message': 'No active amenities with sync enabled found'}
    
    total_synced = 0
    total_updated = 0
    results = []
    
    for amenity in amenities:
        result = sync_airbnb_reservations(amenity.id)
        if result['success']:
            total_synced += result['synced']
            total_updated += result['updated']
        results.append(result)
    
    return {
        'success': True,
        'message': f'Synced {total_synced} new reservations, updated {total_updated} existing across {len(amenities)} amenities',
        'total_synced': total_synced,
        'total_updated': total_updated,
        'amenities_processed': len(amenities),
        'results': results
    }

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to HTML line breaks."""
    if text:
        return Markup(text.replace('\n', '<br>'))
    return text

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with admin contact information."""
    admin_contact = User.query.filter_by(role='admin', is_deleted=False).first()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        flash(_('Thank you for your message, %(name)s! We will get back to you soon.', name=name), 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', admin_contact=admin_contact)

@app.route('/gdpr')
def gdpr():
    admin_contact = User.query.filter_by(role='admin', is_deleted=False).first()
    return render_template('gdpr.html', admin_contact=admin_contact)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files (only accessible to admins)"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/register')
def register_landing():
    """Landing page for registration with confirmation code form."""
    return render_template('register_landing.html')

@app.route('/register', methods=['POST'])
def submit_confirm_code():
    """Handle confirmation code submission and redirect to registration form."""
    confirm_code = request.form.get('confirm_code', '').strip().upper()
    
    if not confirm_code:
        flash(_('Please enter a confirmation code'), 'error')
        return redirect(url_for('register_landing'))
    
    # Check if confirmation code exists
    trip = Trip.query.filter_by(external_confirm_code=confirm_code).first()
    if not trip:
        flash(_('Invalid confirmation code. Please check your code and try again.'), 'error')
        return redirect(url_for('register_landing'))
    
    return redirect(url_for('register', trip_id=trip.id))

@app.route('/register/id/<int:trip_id>')
def register(trip_id):
    """Registration form for a specific trip."""
    trip = Trip.query.get_or_404(trip_id)
    admin = User.query.get(trip.admin_id)
    return render_template('register.html', trip=trip, admin=admin)

@app.route('/register/<confirm_code>')
def register_by_code(confirm_code):
    """Registration form using confirmation code."""
    trip = Trip.query.filter_by(external_confirm_code=confirm_code).first()
    if not trip:
        flash(_('Invalid confirmation code. Please check your code and try again.'), 'error')
        return redirect(url_for('register_landing'))
    
    admin = User.query.get(trip.admin_id)
    return render_template('register.html', trip=trip, admin=admin)

@app.route('/register/id/<int:trip_id>', methods=['POST'])
def submit_registration(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    admin = User.query.get(trip.admin_id)
    
    # Get form data
    email = request.form.get('email')
    language = session.get('lang', 'en')  # Get current language from session
    guests_data = []
    
    # Collect guest data
    guest_index = 1
    while True:
        first_name = request.form.get(f'first_name_{guest_index}')
        last_name = request.form.get(f'last_name_{guest_index}')
        age_category = request.form.get(f'age_category_{guest_index}')
        document_type = request.form.get(f'document_type_{guest_index}')
        document_number = request.form.get(f'document_number_{guest_index}')
        gdpr_consent = request.form.get(f'gdpr_consent_{guest_index}') == 'on'
        
        if not first_name or not last_name:  # Stop if no more guest data
            break
            
        # Check photo requirement based on age category and admin settings
        photo_required = False
        if age_category == 'adult' and admin.photo_required_adults:
            photo_required = True
        elif age_category == 'child' and admin.photo_required_children:
            photo_required = True
        
        # Check if photo is uploaded when required
        document_image = request.files.get(f'document_image_{guest_index}')
        if photo_required and (not document_image or not document_image.filename):
            flash(_('Document photo is required for %(age_category)s guests', age_category=age_category), 'error')
            return redirect(request.url)
        
        guests_data.append({
            'first_name': first_name,
            'last_name': last_name,
            'age_category': age_category,
            'document_type': document_type,
            'document_number': document_number,
            'gdpr_consent': gdpr_consent,
            'photo_required': photo_required
        })
        
        guest_index += 1
    
    # Handle file uploads
    uploaded_files = []
    for i, guest_data in enumerate(guests_data):
        document_image = request.files.get(f'document_image_{i+1}')
        if document_image and document_image.filename:
            filename = secure_filename(f"{uuid.uuid4()}_{document_image.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            document_image.save(file_path)
            uploaded_files.append(filename)
        else:
            uploaded_files.append(None)
    
    # Handle invoice request
    invoice_request = request.form.get('invoice_request') == 'on'
    invoice_data = None
    
    if invoice_request:
        invoice_data = {
            'client_name': request.form.get('invoice_name'),
            'vat_number': request.form.get('invoice_vat'),
            'address': request.form.get('invoice_address')
        }
    
    # Store in session for confirmation
    session['registration_data'] = {
        'trip_id': trip_id,
        'email': email,
        'language': language,
        'guests': guests_data,
        'uploaded_files': uploaded_files,
        'invoice_request': invoice_request,
        'invoice_data': invoice_data
    }
    
    return redirect(url_for('confirm_registration'))

@app.route('/confirm')
def confirm_registration():
    if 'registration_data' not in session:
        return redirect(url_for('index'))
    
    data = session['registration_data']
    trip = Trip.query.get(data['trip_id'])
    
    return render_template('confirm.html', data=data, trip=trip)

@app.route('/submit', methods=['POST'])
def submit_for_approval():
    if 'registration_data' not in session:
        return redirect(url_for('index'))
    
    data = session['registration_data']
    trip = Trip.query.get(data['trip_id'])
    
    # Create registration
    registration = Registration(
        trip_id=data['trip_id'],
        email=data['email'],
        language=data.get('language', 'en')
    )
    db.session.add(registration)
    db.session.flush()  # Get the registration ID
    
    # Create guests
    for i, guest_data in enumerate(data['guests']):
        guest = Guest(
            registration_id=registration.id,
            first_name=guest_data['first_name'],
            last_name=guest_data['last_name'],
            age_category=guest_data['age_category'],
            document_type=guest_data['document_type'],
            document_number=guest_data['document_number'],
            document_image=data['uploaded_files'][i] if i < len(data['uploaded_files']) else None,
            gdpr_consent=guest_data['gdpr_consent']
        )
        db.session.add(guest)
    
    # Create draft invoice if requested
    if data.get('invoice_request') and data.get('invoice_data'):
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{Invoice.query.filter_by(admin_id=trip.admin_id).count() + 1:03d}"
        
        # Determine client name
        client_name = data['invoice_data']['client_name'] if data['invoice_data']['client_name'] else f"{data['guests'][0]['first_name']} {data['guests'][0]['last_name']}"
        
        # Create draft invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            admin_id=trip.admin_id,
            registration_id=registration.id,
            client_name=client_name,
            client_email=data['email'],
            client_vat_number=data['invoice_data']['vat_number'],
            client_address=data['invoice_data']['address'],
            issue_date=datetime.utcnow().date(),
            currency=data['invoice_data']['currency'],
            notes=f"Registration: {trip.title}\nGuest Notes: {data['invoice_data']['notes']}\nVAT Number: {data['invoice_data']['vat_number']}" if data['invoice_data']['vat_number'] else f"Registration: {trip.title}\nGuest Notes: {data['invoice_data']['notes']}",
            status='draft'
        )
        db.session.add(invoice)
        
        # Add a placeholder item for the admin to complete
        placeholder_item = InvoiceItem(
            invoice_id=invoice.id,
            description=f"Registration for {trip.title} - {len(data['guests'])} guest(s)",
            quantity=1,
            unit_price=0,
            vat_rate=0,
            line_total=0,
            vat_amount=0,
            total_with_vat=0
        )
        db.session.add(placeholder_item)
    
    db.session.commit()
    
    # Clear session
    session.pop('registration_data', None)
    # Store last confirmation code registration link for sharing
    if trip.airbnb_confirm_code:
        session['last_confirm_code_url'] = url_for('register_by_code', confirm_code=trip.airbnb_confirm_code, _external=True)
    else:
        session['last_confirm_code_url'] = ''
    
    flash(_('Registration submitted successfully! You will receive an email once it is reviewed.'), 'success')
    return redirect(url_for('registration_success'))

@app.route('/success')
def registration_success():
    return render_template('success.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = User.query.filter_by(username=username, is_deleted=False).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash(_('Invalid username or password'), 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Let Flask-Login handle the redirect
                return login_manager.unauthorized()
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    pending_registrations = Registration.query.filter_by(status='pending').count()
    
    # Get calendars for all amenities owned by this admin
    amenities = Amenity.query.filter_by(admin_id=current_user.id).all()
    calendars = []
    for amenity in amenities:
        calendars.extend(amenity.calendars)
    
    return render_template('admin/dashboard.html', 
                         trips=trips, 
                         pending_registrations=pending_registrations,
                         calendars=calendars)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_settings():
    """Admin settings page for configuration."""
    if request.method == 'POST':
        # Update admin profile
        current_user.email = request.form.get('email')
        current_user.company_name = request.form.get('company_name')
        current_user.company_ico = request.form.get('company_ico')
        current_user.company_vat = request.form.get('company_vat')
        current_user.contact_name = request.form.get('contact_name')
        current_user.contact_phone = request.form.get('contact_phone')
        current_user.contact_address = request.form.get('contact_address')
        current_user.contact_website = request.form.get('contact_website')
        current_user.contact_description = request.form.get('contact_description')
        current_user.custom_line_1 = request.form.get('custom_line_1')
        current_user.custom_line_2 = request.form.get('custom_line_2')
        current_user.custom_line_3 = request.form.get('custom_line_3')
        
        # Update Airbnb settings
        current_user.airbnb_listing_id = request.form.get('airbnb_listing_id')
        current_user.airbnb_calendar_url = request.form.get('airbnb_calendar_url')
        current_user.airbnb_sync_enabled = request.form.get('airbnb_sync_enabled') == 'on'
        
        # Update photo upload settings
        current_user.photo_required_adults = request.form.get('photo_required_adults') == 'on'
        current_user.photo_required_children = request.form.get('photo_required_children') == 'on'
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
        
        db.session.commit()
        flash(_('Settings updated successfully!'), 'success')
        return redirect(url_for('admin_settings'))
    
    # Get calendars for all amenities owned by this admin
    amenities = Amenity.query.filter_by(admin_id=current_user.id).all()
    calendars = []
    for amenity in amenities:
        calendars.extend(amenity.calendars)
    
    return render_template('admin/settings.html', calendars=calendars)

@app.route('/admin/sync-airbnb', methods=['POST'])
@login_required
def sync_airbnb():
    """Sync with all calendars for the current admin."""
    result = sync_all_calendars_for_admin(current_user.id)
    
    if result['success']:
        flash(_('Calendar sync successful: %(message)s', message=result['message']), 'success')
    else:
        flash(_('Calendar sync failed: %(message)s', message=result['message']), 'error')
    
    return redirect(url_for('admin_trips'))

@app.route('/admin/sync-calendar/<int:calendar_id>', methods=['POST'])
@login_required
def sync_calendar(calendar_id):
    """Sync with a specific calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    result = sync_calendar_reservations(calendar_id)
    
    if result['success']:
        flash(_('Calendar sync successful for %(calendar)s: %(message)s', 
                calendar=calendar.name, message=result['message']), 'success')
    else:
        flash(_('Calendar sync failed for %(calendar)s: %(message)s', 
                calendar=calendar.name, message=result['message']), 'error')
    
    return redirect(url_for('admin_amenities'))

@app.route('/admin/amenities')
@login_required
@role_required('admin')
def admin_amenities():
    """Manage amenities."""
    amenities = Amenity.query.filter_by(admin_id=current_user.id).order_by(Amenity.name).all()
    return render_template('admin/amenities.html', amenities=amenities)

@app.route('/admin/amenities/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_amenity():
    """Create a new amenity."""
    if request.method == 'POST':
        amenity = Amenity(
            name=request.form.get('name'),
            description=request.form.get('description'),
            max_guests=int(request.form.get('max_guests', 1)),
            admin_id=current_user.id,
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(amenity)
        db.session.commit()
        flash(_('Amenity created successfully!'), 'success')
        return redirect(url_for('admin_amenities'))
    
    return render_template('admin/new_amenity.html')

@app.route('/admin/amenities/<int:amenity_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_amenity(amenity_id):
    """Edit an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    if request.method == 'POST':
        amenity.name = request.form.get('name')
        amenity.description = request.form.get('description')
        amenity.max_guests = int(request.form.get('max_guests', 1))
        amenity.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash(_('Amenity updated successfully!'), 'success')
        return redirect(url_for('admin_amenities'))
    
    return render_template('admin/edit_amenity.html', amenity=amenity)

@app.route('/admin/amenities/<int:amenity_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_amenity(amenity_id):
    """Delete an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    # Check if amenity has trips
    if amenity.trips:
        flash(_('Cannot delete amenity with existing trips'), 'error')
        return redirect(url_for('admin_amenities'))
    
    db.session.delete(amenity)
    db.session.commit()
    flash(_('Amenity deleted successfully!'), 'success')
    return redirect(url_for('admin_amenities'))

@app.route('/admin/trips')
@login_required
@role_required('admin')
def admin_trips():
    # Get trips grouped by amenity
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    trips_by_amenity = {}
    
    for amenity in amenities:
        trips_by_amenity[amenity] = Trip.query.filter_by(amenity_id=amenity.id).order_by(Trip.start_date).all()
    
    # Flatten trips for the template
    trips = []
    for amenity_trips in trips_by_amenity.values():
        trips.extend(amenity_trips)
    
    return render_template('admin/trips.html', trips=trips, trips_by_amenity=trips_by_amenity, amenities=amenities)

@app.route('/admin/trips/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_trip():
    if request.method == 'POST':
        amenity_id = request.form.get('amenity_id')
        amenity = Amenity.query.get(amenity_id)
        
        if not amenity or amenity.admin_id != current_user.id:
            flash(_('Invalid amenity selected'), 'error')
            return redirect(url_for('new_trip'))
        
        trip = Trip(
            title=request.form.get('title'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            max_guests=int(request.form.get('max_guests')),
            admin_id=current_user.id,
            amenity_id=amenity_id
        )
        db.session.add(trip)
        db.session.commit()
        flash(_('Trip created successfully!'), 'success')
        return redirect(url_for('admin_trips'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/new_trip.html', amenities=amenities)

@app.route('/admin/registrations')
@login_required
@role_required('admin')
def admin_registrations():
    registrations = Registration.query.filter_by(status='pending').all()
    return render_template('admin/registrations.html', registrations=registrations)

@app.route('/admin/registration/<int:registration_id>')
@login_required
@role_required('admin')
def view_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    return render_template('admin/view_registration.html', registration=registration)

@app.route('/admin/registration/<int:registration_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    registration.status = 'approved'
    registration.updated_at = datetime.utcnow()
    
    # Delete document images after approval (GDPR compliance)
    for guest in registration.guests:
        if guest.document_image:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], guest.document_image))
                guest.document_image = None
            except:
                pass  # File might already be deleted
    
    db.session.commit()
    
    # Send approval email
    send_approval_email(registration)
    
    flash(_('Registration approved and email sent to user'), 'success')
    return redirect(url_for('admin_registrations'))

@app.route('/admin/registration/<int:registration_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    registration.status = 'rejected'
    registration.admin_comment = request.form.get('comment')
    registration.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Send rejection email
    send_rejection_email(registration)
    
    flash(_('Registration rejected and email sent to user'), 'success')
    return redirect(url_for('admin_registrations'))

# Invoice Management Routes
@app.route('/admin/invoices')
@login_required
@role_required('admin')
def admin_invoices():
    """Admin invoices list page."""
    invoices = Invoice.query.filter_by(admin_id=current_user.id).order_by(Invoice.created_at.desc()).all()
    return render_template('admin/invoices.html', invoices=invoices)

@app.route('/admin/invoices/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_invoice():
    """Create a new invoice."""
    if request.method == 'POST':
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{Invoice.query.filter_by(admin_id=current_user.id).count() + 1:03d}"
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            admin_id=current_user.id,
            registration_id=request.form.get('registration_id'),
            client_name=request.form.get('client_name'),
            client_email=request.form.get('client_email'),
            client_vat_number=request.form.get('client_vat_number'),
            client_address=request.form.get('client_address'),
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date(),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
            currency=request.form.get('currency', 'EUR'),
            notes=request.form.get('notes')
        )
        
        db.session.add(invoice)
        db.session.flush()  # Get the invoice ID
        
        # Process invoice items
        item_count = int(request.form.get('item_count', 0))
        for i in range(item_count):
            description = request.form.get(f'item_description_{i}')
            quantity = float(request.form.get(f'item_quantity_{i}', 1))
            unit_price = float(request.form.get(f'item_unit_price_{i}', 0))
            vat_rate = float(request.form.get(f'item_vat_rate_{i}', 0))
            
            if description and unit_price > 0:
                line_total = quantity * unit_price
                vat_amount = line_total * (vat_rate / 100)
                total_with_vat = line_total + vat_amount
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=vat_rate,
                    line_total=line_total,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat
                )
                db.session.add(item)
        
        # Calculate totals
        invoice.subtotal = sum(item.line_total for item in invoice.items)
        invoice.vat_total = sum(item.vat_amount for item in invoice.items)
        invoice.total_amount = invoice.subtotal + invoice.vat_total
        
        db.session.commit()
        flash(_('Invoice created successfully!'), 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice.id))
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/new_invoice.html', today=today)

@app.route('/admin/invoices/<int:invoice_id>')
@login_required
@role_required('admin')
def view_invoice(invoice_id):
    """View a specific invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    return render_template('admin/view_invoice.html', invoice=invoice)

@app.route('/admin/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(invoice_id):
    """Edit an existing invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Update invoice details
        invoice.client_name = request.form.get('client_name')
        invoice.client_email = request.form.get('client_email')
        invoice.client_vat_number = request.form.get('client_vat_number')
        invoice.client_address = request.form.get('client_address')
        invoice.issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date()
        invoice.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None
        invoice.currency = request.form.get('currency', 'EUR')
        invoice.notes = request.form.get('notes')
        
        # Clear existing items
        for item in invoice.items:
            db.session.delete(item)
        
        # Add new items
        item_count = int(request.form.get('item_count', 0))
        for i in range(item_count):
            description = request.form.get(f'item_description_{i}')
            quantity = float(request.form.get(f'item_quantity_{i}', 1))
            unit_price = float(request.form.get(f'item_unit_price_{i}', 0))
            vat_rate = float(request.form.get(f'item_vat_rate_{i}', 0))
            
            if description and unit_price > 0:
                line_total = quantity * unit_price
                vat_amount = line_total * (vat_rate / 100)
                total_with_vat = line_total + vat_amount
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=vat_rate,
                    line_total=line_total,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat
                )
                db.session.add(item)
        
        # Recalculate totals
        invoice.subtotal = sum(item.line_total for item in invoice.items)
        invoice.vat_total = sum(item.vat_amount for item in invoice.items)
        invoice.total_amount = invoice.subtotal + invoice.vat_total
        
        db.session.commit()
        flash(_('Invoice updated successfully!'), 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice.id))
    
    # Convert invoice items to dictionaries for JSON serialization
    items_data = []
    for item in invoice.items:
        items_data.append({
            'description': item.description,
            'quantity': float(item.quantity),
            'unit_price': float(item.unit_price),
            'vat_rate': float(item.vat_rate)
        })
    
    return render_template('admin/edit_invoice.html', invoice=invoice, items_data=items_data)

@app.route('/admin/invoices/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    """Delete an invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    db.session.delete(invoice)
    db.session.commit()
    flash(_('Invoice deleted successfully!'), 'success')
    return redirect(url_for('admin_invoices'))

@app.route('/admin/invoices/<int:invoice_id>/change-status', methods=['POST'])
@login_required
def change_invoice_status(invoice_id):
    """Change invoice status."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    new_status = request.form.get('status')
    if new_status in ['draft', 'sent', 'paid', 'overdue']:
        old_status = invoice.status
        invoice.status = new_status
        invoice.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(_('Invoice status changed from %(old_status)s to %(new_status)s successfully!', old_status=old_status.title(), new_status=new_status.title()), 'success')
    else:
        flash(_('Invalid status provided.'), 'error')
    
    return redirect(url_for('view_invoice', invoice_id=invoice.id))

@app.route('/admin/invoices/<int:invoice_id>/pdf')
@login_required
def generate_invoice_pdf(invoice_id):
    """Generate PDF for an invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    # Generate HTML content for the invoice
    html_content = render_template('admin/invoice_pdf.html', invoice=invoice)
    
    # Create PDF
    font_config = FontConfiguration()
    css = CSS(string='''
        @page { 
            size: A4; 
            margin: 1.5cm;
        }
        body { 
            font-family: Arial, sans-serif; 
            font-size: 10px;
            line-height: 1.2;
        }
        .header { 
            text-align: center; 
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }
        .invoice-details {
            margin-top: 10px;
            font-size: 9px;
            color: #666;
        }
        .invoice-details span {
            margin: 0 15px;
        }
        .row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .company-info {
            text-align: left;
            width: 48%;
        }
        .client-info {
            text-align: right;
            width: 48%;
        }
        .invoice-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .invoice-table th,
        .invoice-table td {
            border: 1px solid #ddd;
            padding: 6px;
            text-align: left;
            font-size: 9px;
        }
        .invoice-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .total-row {
            font-weight: bold;
            background-color: #f8f9fa;
        }
        .notes {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            font-size: 9px;
        }
    ''', font_config=font_config)
    
    # Generate PDF
    html_doc = HTML(string=html_content)
    pdf = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf)
        tmp_path = tmp_file.name
    
    # Send file and clean up
    try:
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f'invoice_{invoice.invoice_number}.pdf',
            mimetype='application/pdf'
        )
    finally:
        # Clean up temporary file after sending
        try:
            os.unlink(tmp_path)
        except:
            pass

@app.route('/admin/invoices/<int:invoice_id>/send-pdf', methods=['POST'])
@login_required
@role_required('admin')
def send_invoice_pdf(invoice_id):
    """Send the invoice PDF to the registration/client email."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    # Determine recipient and language
    recipient = invoice.client_email or (invoice.registration.email if invoice.registration else None)
    if not recipient:
        flash(_('No recipient email found for this invoice.'), 'error')
        return redirect(url_for('view_invoice', invoice_id=invoice.id))
    
    # Set language based on registration
    if invoice.registration and invoice.registration.language:
        # Temporarily set the language for this request
        from flask_babel import get_locale
        original_locale = get_locale()
        session['lang'] = invoice.registration.language
    
    # Generate HTML content for the invoice
    html_content = render_template('admin/invoice_pdf.html', invoice=invoice)
    font_config = FontConfiguration()
    css = CSS(string='''
        @page { size: A4; margin: 1.5cm; }
        body { font-family: Arial, sans-serif; font-size: 10px; line-height: 1.2; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 15px; }
        .invoice-details { margin-top: 10px; font-size: 9px; color: #666; }
        .invoice-details span { margin: 0 15px; }
        .row { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .company-info { text-align: left; width: 48%; }
        .client-info { text-align: right; width: 48%; }
        .invoice-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .invoice-table th, .invoice-table td { border: 1px solid #ddd; padding: 6px; text-align: left; font-size: 9px; }
        .invoice-table th { background-color: #f8f9fa; font-weight: bold; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .total-row { font-weight: bold; background-color: #f8f9fa; }
        .notes { margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff; font-size: 9px; }
    ''', font_config=font_config)
    html_doc = HTML(string=html_content)
    pdf_bytes = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
    
    # Send email with PDF attachment
    try:
        msg = Message(
            subject=_('Your Invoice from %(company)s', company=invoice.admin.company_name or _('Our Company')),
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient]
        )
        msg.body = _(
            """Dear %(client_name)s,

Please find attached your invoice %(invoice_number)s.

Thank you for your business!

Best regards,
%(company)s""",
            client_name=invoice.client_name,
            invoice_number=invoice.invoice_number,
            company=invoice.admin.company_name or _('Our Company')
        )
        msg.attach(
            filename=f"invoice_{invoice.invoice_number}.pdf",
            content_type="application/pdf",
            data=pdf_bytes
        )
        mail.send(msg)
        flash(_('Invoice PDF sent to %(email)s', email=recipient), 'success')
    except Exception as e:
        print(f"Error sending invoice PDF: {e}")
        flash(_('Failed to send invoice PDF: %(error)s', error=str(e)), 'error')
    finally:
        # Restore original language if it was changed
        if invoice.registration and invoice.registration.language:
            session['lang'] = original_locale.language if original_locale else 'en'
    
    return redirect(url_for('view_invoice', invoice_id=invoice.id))

# Data management routes
@app.route('/admin/data-management')
@login_required
def data_management():
    """Data management page for admins."""
    # Get database statistics
    admin_count = User.query.count()
    trip_count = Trip.query.count()
    registration_count = Registration.query.count()
    guest_count = Guest.query.count()
    
    pending_count = Registration.query.filter_by(status='pending').count()
    approved_count = Registration.query.filter_by(status='approved').count()
    rejected_count = Registration.query.filter_by(status='rejected').count()
    
    stats = {
        'admins': admin_count,
        'trips': trip_count,
        'registrations': registration_count,
        'guests': guest_count,
        'pending': pending_count,
        'approved': approved_count,
        'rejected': rejected_count
    }
    
    # Get configuration info
    config = {
        'TABLE_PREFIX': app.config.get('TABLE_PREFIX', 'guest_reg_')
    }
    
    return render_template('admin/data_management.html', stats=stats, config=config)

@app.route('/admin/reset-data', methods=['POST'])
@login_required
def reset_data():
    """Reset all data in the database except admin accounts."""
    try:
        # Get table names for logging
        table_prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
        tables_to_reset = [
            f"{table_prefix}trip", 
            f"{table_prefix}registration",
            f"{table_prefix}guest",
            f"{table_prefix}invoice",
            f"{table_prefix}invoice_item"
        ]
        
        print(f"Starting database reset for tables: {', '.join(tables_to_reset)}")
        print(f"Preserving admin table: {table_prefix}user")
        
        # Delete data in the correct order to handle foreign key constraints
        # 1. Delete invoice items first (references invoices)
        InvoiceItem.query.delete()
        print("✅ Deleted invoice items")
        
        # 2. Delete invoices (references registrations)
        Invoice.query.delete()
        print("✅ Deleted invoices")
        
        # 3. Delete guests (references registrations)
        Guest.query.delete()
        print("✅ Deleted guests")
        
        # 4. Delete registrations (references trips)
        Registration.query.delete()
        print("✅ Deleted registrations")
        
        # 5. Delete trips (no dependencies)
        Trip.query.delete()
        print("✅ Deleted trips")
        
        # Commit the deletions
        db.session.commit()
        
        print("Data deleted successfully from all tables")
        print("Admin accounts preserved")
        
        flash(_('All data has been reset successfully! Admin accounts have been preserved.'), 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during reset: {str(e)}")
        flash(_('Error resetting data: %(error)s. Please use the command line tool: python quick_reset.py --confirm', error=str(e)), 'error')
    
    return redirect(url_for('data_management'))

@app.route('/admin/seed-data', methods=['POST'])
@login_required
def seed_data():
    """Seed the database with sample data. Only real reservations are seeded. 'Not Available' or blocked events are intentionally excluded to match Airbnb sync logic."""
    try:
        # Create sample admin if not exists
        existing_admin = User.query.filter_by(username='admin').first()
        if not existing_admin:
            admin = User(
                username='admin',
                email='admin@vacationrentals.com',
                password_hash=generate_password_hash('admin123'),
                # Company information
                company_name='Vacation Rentals Plus',
                company_ico='12345678',
                company_vat='CZ12345678',
                contact_name='John Manager',
                contact_phone='+420 123 456 789',
                contact_address='Vacation Street 123\nPrague 110 00\nCzech Republic',
                contact_website='https://vacationrentals.com',
                contact_description='Professional vacation rental management services',
                custom_line_1='24/7 Customer Support',
                custom_line_2='Free WiFi & Parking',
                custom_line_3='Pet Friendly Options Available'
            )
            db.session.add(admin)
            db.session.flush()
        else:
            # Update existing admin with new fields
            admin = existing_admin
            if not admin.company_name:
                admin.company_name = 'Vacation Rentals Plus'
                admin.company_ico = '12345678'
                admin.company_vat = 'CZ12345678'
                admin.contact_name = 'John Manager'
                admin.contact_phone = '+420 123 456 789'
                admin.contact_address = 'Vacation Street 123\nPrague 110 00\nCzech Republic'
                admin.contact_website = 'https://vacationrentals.com'
                admin.contact_description = 'Professional vacation rental management services'
                admin.custom_line_1 = '24/7 Customer Support'
                admin.custom_line_2 = 'Free WiFi & Parking'
                admin.custom_line_3 = 'Pet Friendly Options Available'
        
        # Create sample trips with variety
        trips_data = [
            {
                'title': "Summer Beach Vacation 2024",
                'start_date': datetime.now().date() + timedelta(days=30),
                'end_date': datetime.now().date() + timedelta(days=37),
                'max_guests': 6,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'John Smith',
                'airbnb_guest_email': 'john.smith@example.com',
                'airbnb_guest_count': 4,
                'airbnb_confirm_code': 'SUMMER2024'
            },
            {
                'title': "Mountain Retreat Weekend",
                'start_date': datetime.now().date() + timedelta(days=14),
                'end_date': datetime.now().date() + timedelta(days=16),
                'max_guests': 4,
                'is_airbnb_synced': False,
                'airbnb_confirm_code': 'MOUNTAIN24'
            },
            {
                'title': "City Break Adventure",
                'start_date': datetime.now().date() + timedelta(days=60),
                'end_date': datetime.now().date() + timedelta(days=65),
                'max_guests': 8,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Alice Johnson',
                'airbnb_guest_email': 'alice.j@example.com',
                'airbnb_guest_count': 3,
                'airbnb_confirm_code': 'CITY2024'
            },
            {
                'title': "Winter Ski Trip",
                'start_date': datetime.now().date() + timedelta(days=90),
                'end_date': datetime.now().date() + timedelta(days=97),
                'max_guests': 5,
                'is_airbnb_synced': False,
                'airbnb_confirm_code': 'SKI2024'
            },
            {
                'title': "Weekend Getaway",
                'start_date': datetime.now().date() + timedelta(days=7),
                'end_date': datetime.now().date() + timedelta(days=9),
                'max_guests': 3,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Bob Wilson',
                'airbnb_guest_email': 'bob.wilson@example.com',
                'airbnb_guest_count': 2,
                'airbnb_confirm_code': 'WEEKEND24'
            }
        ]
        
        created_trips = []
        for trip_data in trips_data:
            trip = Trip(
                title=trip_data['title'],
                start_date=trip_data['start_date'],
                end_date=trip_data['end_date'],
                max_guests=trip_data['max_guests'],
                admin_id=admin.id,
                is_airbnb_synced=trip_data.get('is_airbnb_synced', False),
                airbnb_guest_name=trip_data.get('airbnb_guest_name'),
                airbnb_guest_email=trip_data.get('airbnb_guest_email'),
                airbnb_guest_count=trip_data.get('airbnb_guest_count'),
                airbnb_synced_at=datetime.utcnow() if trip_data.get('is_airbnb_synced') else None,
                airbnb_confirm_code=trip_data.get('airbnb_confirm_code')
            )
            db.session.add(trip)
            created_trips.append(trip)
        
        db.session.flush()  # Get trip IDs
        
        # Create sample registrations with different statuses
        registrations_data = [
            # Approved registrations
            {
                'trip_index': 0,
                'email': 'john.doe@example.com',
                'status': 'approved',
                'created_at': datetime.now() - timedelta(days=5),
                'guests': [
                    {'first_name': 'John', 'last_name': 'Doe', 'document_type': 'passport', 'document_number': 'AB1234567', 'image': 'passport_john_doe.jpg'},
                    {'first_name': 'Jane', 'last_name': 'Doe', 'document_type': 'driving_license', 'document_number': 'DL9876543', 'image': 'license_jane_doe.jpg'},
                    {'first_name': 'Mike', 'last_name': 'Doe', 'document_type': 'citizen_id', 'document_number': 'CID123456789', 'image': 'citizen_id_mike_doe.jpg'}
                ]
            },
            {
                'trip_index': 2,
                'email': 'alice.smith@example.com',
                'status': 'approved',
                'created_at': datetime.now() - timedelta(days=3),
                'guests': [
                    {'first_name': 'Alice', 'last_name': 'Smith', 'document_type': 'passport', 'document_number': 'CD9876543', 'image': 'passport_alice_smith.jpg'},
                    {'first_name': 'Bob', 'last_name': 'Smith', 'document_type': 'driving_license', 'document_number': 'DL5556667', 'image': 'license_bob_smith.jpg'}
                ]
            },
            # Pending registrations
            {
                'trip_index': 1,
                'email': 'charlie.brown@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(days=2),
                'guests': [
                    {'first_name': 'Charlie', 'last_name': 'Brown', 'document_type': 'passport', 'document_number': 'EF1234567', 'image': 'passport_charlie_brown.jpg'},
                    {'first_name': 'Lucy', 'last_name': 'Brown', 'document_type': 'citizen_id', 'document_number': 'CID987654321', 'image': 'citizen_id_lucy_brown.jpg'}
                ]
            },
            {
                'trip_index': 3,
                'email': 'diana.prince@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(days=1),
                'guests': [
                    {'first_name': 'Diana', 'last_name': 'Prince', 'document_type': 'passport', 'document_number': 'GH9876543', 'image': 'passport_diana_prince.jpg'},
                    {'first_name': 'Bruce', 'last_name': 'Wayne', 'document_type': 'driving_license', 'document_number': 'DL1112223', 'image': 'license_bruce_wayne.jpg'},
                    {'first_name': 'Clark', 'last_name': 'Kent', 'document_type': 'citizen_id', 'document_number': 'CID555666777', 'image': 'citizen_id_clark_kent.jpg'}
                ]
            },
            {
                'trip_index': 4,
                'email': 'peter.parker@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(hours=6),
                'guests': [
                    {'first_name': 'Peter', 'last_name': 'Parker', 'document_type': 'passport', 'document_number': 'IJ1234567', 'image': 'passport_peter_parker.jpg'},
                    {'first_name': 'Mary', 'last_name': 'Jane', 'document_type': 'driving_license', 'document_number': 'DL4445556', 'image': 'license_mary_jane.jpg'}
                ]
            },
            # Pending registration with ONE person
            {
                'trip_index': 0,
                'email': 'solo.traveler@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(hours=2),
                'guests': [
                    {'first_name': 'Emma', 'last_name': 'Wilson', 'document_type': 'passport', 'document_number': 'MN1234567', 'image': 'passport_emma_wilson.jpg'}
                ]
            },
            # Rejected registration
            {
                'trip_index': 0,
                'email': 'tony.stark@example.com',
                'status': 'rejected',
                'admin_comment': 'Document images were unclear. Please upload clearer photos.',
                'created_at': datetime.now() - timedelta(days=4),
                'updated_at': datetime.now() - timedelta(days=3),
                'guests': [
                    {'first_name': 'Tony', 'last_name': 'Stark', 'document_type': 'passport', 'document_number': 'KL9876543', 'image': 'passport_tony_stark.jpg'}
                ]
            }
        ]
        
        created_registrations = []
        for reg_data in registrations_data:
            registration = Registration(
                trip_id=created_trips[reg_data['trip_index']].id,
                email=reg_data['email'],
                status=reg_data['status'],
                admin_comment=reg_data.get('admin_comment'),
                created_at=reg_data['created_at'],
                updated_at=reg_data.get('updated_at', reg_data['created_at'])
            )
            db.session.add(registration)
            db.session.flush()
            created_registrations.append(registration)
            
            # Add guests for this registration
            for guest_data in reg_data['guests']:
                # Copy sample image to uploads directory
                image_filename = None
                if guest_data.get('image'):
                    image_filename = copy_sample_image(guest_data['image'])
                
                guest = Guest(
                    registration_id=registration.id,
                    first_name=guest_data['first_name'],
                    last_name=guest_data['last_name'],
                    age_category=guest_data['age_category'],
                    document_type=guest_data['document_type'],
                    document_number=guest_data['document_number'],
                    document_image=image_filename,  # Use copied image filename
                    gdpr_consent=True
                )
                db.session.add(guest)
        
        db.session.flush()
        
        # Create sample invoices
        invoices_data = [
            {
                'registration_index': 0,  # John Doe's approved registration
                'invoice_number': 'INV-2024-001',
                'client_name': 'John Doe',
                'client_email': 'john.doe@example.com',
                'client_vat_number': 'CZ12345678',
                'client_address': '123 Main Street\nPrague 120 00\nCzech Republic',
                'issue_date': datetime.now().date() - timedelta(days=5),
                'due_date': datetime.now().date() + timedelta(days=25),
                'status': 'sent',
                'currency': 'EUR',
                'notes': 'Payment due within 30 days. Bank transfer preferred.',
                'items': [
                    {'description': 'Beach Villa Rental - 7 nights', 'quantity': 1, 'unit_price': 1200.00, 'vat_rate': 21.0},
                    {'description': 'Cleaning Service', 'quantity': 1, 'unit_price': 80.00, 'vat_rate': 21.0},
                    {'description': 'Welcome Package', 'quantity': 1, 'unit_price': 50.00, 'vat_rate': 21.0}
                ]
            },
            {
                'registration_index': 1,  # Alice Smith's approved registration
                'invoice_number': 'INV-2024-002',
                'client_name': 'Alice Smith',
                'client_email': 'alice.smith@example.com',
                'client_vat_number': 'CZ87654321',
                'client_address': '456 Oak Avenue\nBrno 602 00\nCzech Republic',
                'issue_date': datetime.now().date() - timedelta(days=3),
                'due_date': datetime.now().date() + timedelta(days=27),
                'status': 'paid',
                'currency': 'EUR',
                'notes': 'Thank you for your business!',
                'items': [
                    {'description': 'City Apartment Rental - 5 nights', 'quantity': 1, 'unit_price': 800.00, 'vat_rate': 21.0},
                    {'description': 'Airport Transfer', 'quantity': 2, 'unit_price': 25.00, 'vat_rate': 21.0},
                    {'description': 'Late Check-out', 'quantity': 1, 'unit_price': 30.00, 'vat_rate': 21.0}
                ]
            },
            {
                'registration_index': 2,  # Charlie Brown's pending registration
                'invoice_number': 'INV-2024-003',
                'client_name': 'Charlie Brown',
                'client_email': 'charlie.brown@example.com',
                'client_vat_number': 'CZ11122233',
                'client_address': '789 Pine Street\nOstrava 702 00\nCzech Republic',
                'issue_date': datetime.now().date() - timedelta(days=2),
                'due_date': datetime.now().date() + timedelta(days=28),
                'status': 'draft',
                'currency': 'EUR',
                'notes': 'Invoice will be sent after registration approval.',
                'items': [
                    {'description': 'Mountain Cabin Rental - 2 nights', 'quantity': 1, 'unit_price': 300.00, 'vat_rate': 21.0},
                    {'description': 'Ski Equipment Rental', 'quantity': 2, 'unit_price': 45.00, 'vat_rate': 21.0}
                ]
            }
        ]
        
        for invoice_data in invoices_data:
            # Calculate totals
            subtotal = 0
            vat_total = 0
            total_amount = 0
            
            # Calculate line totals and VAT
            for item_data in invoice_data['items']:
                line_total = item_data['quantity'] * item_data['unit_price']
                vat_amount = line_total * (item_data['vat_rate'] / 100)
                item_data['line_total'] = line_total
                item_data['vat_amount'] = vat_amount
                item_data['total_with_vat'] = line_total + vat_amount
                
                subtotal += line_total
                vat_total += vat_amount
                total_amount += item_data['total_with_vat']
            
            invoice = Invoice(
                invoice_number=invoice_data['invoice_number'],
                admin_id=admin.id,
                registration_id=created_registrations[invoice_data['registration_index']].id,
                client_name=invoice_data['client_name'],
                client_email=invoice_data['client_email'],
                client_vat_number=invoice_data['client_vat_number'],
                client_address=invoice_data['client_address'],
                issue_date=invoice_data['issue_date'],
                due_date=invoice_data['due_date'],
                subtotal=subtotal,
                vat_total=vat_total,
                total_amount=total_amount,
                currency=invoice_data['currency'],
                notes=invoice_data['notes'],
                status=invoice_data['status']
            )
            db.session.add(invoice)
            db.session.flush()
            
            # Add invoice items
            for item_data in invoice_data['items']:
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    vat_rate=item_data['vat_rate'],
                    line_total=item_data['line_total'],
                    vat_amount=item_data['vat_amount'],
                    total_with_vat=item_data['total_with_vat']
                )
                db.session.add(invoice_item)
        
        db.session.commit()
        
        flash(_('Sample data has been seeded successfully! Created 5 trips, 7 registrations (including 1 single-person pending), 3 invoices with realistic data, and updated admin contact information.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error seeding data: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('data_management'))

@app.route('/admin/seed-reset', methods=['POST'])
@login_required
def seed_reset():
    """Reset all data except admin accounts and then seed with sample data."""
    try:
        # Get table names for logging
        table_prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
        tables_to_reset = [
            f"{table_prefix}trip", 
            f"{table_prefix}registration",
            f"{table_prefix}guest"
        ]
        
        print(f"Starting database reset and seed for tables: {', '.join(tables_to_reset)}")
        print(f"Preserving admin table: {table_prefix}user")
        
        # Delete data from specific tables instead of dropping all
        Guest.query.delete()
        Registration.query.delete()
        Trip.query.delete()
        
        # Commit the deletions
        db.session.commit()
        print("Data deleted successfully from trips, registrations, and guests tables")
        
        # Now seed with sample data
        print("Starting to seed sample data...")
        
        # Use existing admin or create one if none exists
        admin = User.query.first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.flush()
            print("Created new admin user: admin/admin123")
        else:
            print(f"Using existing admin: {admin.username}")
        
        # Create sample trips with variety
        trips_data = [
            {
                'title': "Summer Beach Vacation 2024",
                'start_date': datetime.now().date() + timedelta(days=30),
                'end_date': datetime.now().date() + timedelta(days=37),
                'max_guests': 6,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'John Smith',
                'airbnb_guest_email': 'john.smith@example.com',
                'airbnb_guest_count': 4,
                'airbnb_confirm_code': 'SUMMER2024'
            },
            {
                'title': "Mountain Retreat Weekend",
                'start_date': datetime.now().date() + timedelta(days=14),
                'end_date': datetime.now().date() + timedelta(days=16),
                'max_guests': 4,
                'is_airbnb_synced': False,
                'airbnb_confirm_code': 'MOUNTAIN24'
            },
            {
                'title': "City Break Adventure",
                'start_date': datetime.now().date() + timedelta(days=60),
                'end_date': datetime.now().date() + timedelta(days=65),
                'max_guests': 8,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Alice Johnson',
                'airbnb_guest_email': 'alice.j@example.com',
                'airbnb_guest_count': 3,
                'airbnb_confirm_code': 'CITY2024'
            },
            {
                'title': "Winter Ski Trip",
                'start_date': datetime.now().date() + timedelta(days=90),
                'end_date': datetime.now().date() + timedelta(days=97),
                'max_guests': 5,
                'is_airbnb_synced': False,
                'airbnb_confirm_code': 'SKI2024'
            },
            {
                'title': "Weekend Getaway",
                'start_date': datetime.now().date() + timedelta(days=7),
                'end_date': datetime.now().date() + timedelta(days=9),
                'max_guests': 3,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Bob Wilson',
                'airbnb_guest_email': 'bob.wilson@example.com',
                'airbnb_guest_count': 2,
                'airbnb_confirm_code': 'WEEKEND24'
            }
        ]
        
        created_trips = []
        for trip_data in trips_data:
            trip = Trip(
                title=trip_data['title'],
                start_date=trip_data['start_date'],
                end_date=trip_data['end_date'],
                max_guests=trip_data['max_guests'],
                admin_id=admin.id,
                is_airbnb_synced=trip_data.get('is_airbnb_synced', False),
                airbnb_guest_name=trip_data.get('airbnb_guest_name'),
                airbnb_guest_email=trip_data.get('airbnb_guest_email'),
                airbnb_guest_count=trip_data.get('airbnb_guest_count'),
                airbnb_synced_at=datetime.utcnow() if trip_data.get('is_airbnb_synced') else None,
                airbnb_confirm_code=trip_data.get('airbnb_confirm_code')
            )
            db.session.add(trip)
            created_trips.append(trip)
        
        db.session.flush()
        
        # Create sample registrations with different statuses
        registrations_data = [
            # Approved registrations
            {
                'trip_index': 0,
                'email': 'john.doe@example.com',
                'status': 'approved',
                'created_at': datetime.now() - timedelta(days=5),
                'guests': [
                    {'first_name': 'John', 'last_name': 'Doe', 'document_type': 'passport', 'document_number': 'AB1234567', 'image': 'passport_john_doe.jpg'},
                    {'first_name': 'Jane', 'last_name': 'Doe', 'document_type': 'driving_license', 'document_number': 'DL9876543', 'image': 'license_jane_doe.jpg'},
                    {'first_name': 'Mike', 'last_name': 'Doe', 'document_type': 'citizen_id', 'document_number': 'CID123456789', 'image': 'citizen_id_mike_doe.jpg'}
                ]
            },
            {
                'trip_index': 2,
                'email': 'alice.smith@example.com',
                'status': 'approved',
                'created_at': datetime.now() - timedelta(days=3),
                'guests': [
                    {'first_name': 'Alice', 'last_name': 'Smith', 'document_type': 'passport', 'document_number': 'CD9876543', 'image': 'passport_alice_smith.jpg'},
                    {'first_name': 'Bob', 'last_name': 'Smith', 'document_type': 'driving_license', 'document_number': 'DL5556667', 'image': 'license_bob_smith.jpg'}
                ]
            },
            # Pending registrations
            {
                'trip_index': 1,
                'email': 'charlie.brown@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(days=2),
                'guests': [
                    {'first_name': 'Charlie', 'last_name': 'Brown', 'document_type': 'passport', 'document_number': 'EF1234567', 'image': 'passport_charlie_brown.jpg'},
                    {'first_name': 'Lucy', 'last_name': 'Brown', 'document_type': 'citizen_id', 'document_number': 'CID987654321', 'image': 'citizen_id_lucy_brown.jpg'}
                ]
            },
            {
                'trip_index': 3,
                'email': 'diana.prince@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(days=1),
                'guests': [
                    {'first_name': 'Diana', 'last_name': 'Prince', 'document_type': 'passport', 'document_number': 'GH9876543', 'image': 'passport_diana_prince.jpg'},
                    {'first_name': 'Bruce', 'last_name': 'Wayne', 'document_type': 'driving_license', 'document_number': 'DL1112223', 'image': 'license_bruce_wayne.jpg'},
                    {'first_name': 'Clark', 'last_name': 'Kent', 'document_type': 'citizen_id', 'document_number': 'CID555666777', 'image': 'citizen_id_clark_kent.jpg'}
                ]
            },
            {
                'trip_index': 4,
                'email': 'peter.parker@example.com',
                'status': 'pending',
                'created_at': datetime.now() - timedelta(hours=6),
                'guests': [
                    {'first_name': 'Peter', 'last_name': 'Parker', 'document_type': 'passport', 'document_number': 'IJ1234567', 'image': 'passport_peter_parker.jpg'},
                    {'first_name': 'Mary', 'last_name': 'Jane', 'document_type': 'driving_license', 'document_number': 'DL4445556', 'image': 'license_mary_jane.jpg'}
                ]
            },
            # Rejected registration
            {
                'trip_index': 0,
                'email': 'tony.stark@example.com',
                'status': 'rejected',
                'admin_comment': 'Document images were unclear. Please upload clearer photos.',
                'created_at': datetime.now() - timedelta(days=4),
                'updated_at': datetime.now() - timedelta(days=3),
                'guests': [
                    {'first_name': 'Tony', 'last_name': 'Stark', 'document_type': 'passport', 'document_number': 'KL9876543', 'image': 'passport_tony_stark.jpg'}
                ]
            }
        ]
        
        for reg_data in registrations_data:
            registration = Registration(
                trip_id=created_trips[reg_data['trip_index']].id,
                email=reg_data['email'],
                status=reg_data['status'],
                admin_comment=reg_data.get('admin_comment'),
                created_at=reg_data['created_at'],
                updated_at=reg_data.get('updated_at', reg_data['created_at'])
            )
            db.session.add(registration)
            db.session.flush()
            
            # Add guests for this registration
            for guest_data in reg_data['guests']:
                # Copy sample image to uploads directory
                image_filename = None
                if guest_data.get('image'):
                    image_filename = copy_sample_image(guest_data['image'])
                
                guest = Guest(
                    registration_id=registration.id,
                    first_name=guest_data['first_name'],
                    last_name=guest_data['last_name'],
                    age_category=guest_data['age_category'],
                    document_type=guest_data['document_type'],
                    document_number=guest_data['document_number'],
                    document_image=image_filename,  # Use copied image filename
                    gdpr_consent=True
                )
                db.session.add(guest)
        
        db.session.commit()
        print("Sample data seeded successfully")
        
        flash(_('Database has been reset and seeded with sample data successfully! Admin accounts have been preserved. Created 5 trips and 6 registrations with various statuses. Sample document images have been copied to uploads directory.'), 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during reset and seed: {str(e)}")
        flash(_('Error during reset and seed: %(error)s. Please use the command line tool: python quick_reset.py --reset-seed', error=str(e)), 'error')
    
    return redirect(url_for('data_management'))

def send_approval_email(registration):
    try:
        # Set language based on registration
        original_lang = session.get('lang', 'en')
        if registration.language:
            session['lang'] = registration.language
        
        msg = Message(
            _('Your registration has been approved!'),
            sender=app.config['MAIL_USERNAME'],
            recipients=[registration.email]
        )
        msg.body = _("""
Dear Guest,

Your registration for %(trip_title)s has been approved!

Your personal data has been processed and all uploaded documents have been securely deleted in compliance with GDPR regulations.

Thank you for choosing our service.

Best regards,
The Admin Team
""", trip_title=registration.trip.title)
        mail.send(msg)
        
        # Restore original language
        session['lang'] = original_lang
    except Exception as e:
        print(f"Error sending email: {e}")

def send_rejection_email(registration):
    try:
        # Set language based on registration
        original_lang = session.get('lang', 'en')
        if registration.language:
            session['lang'] = registration.language
        
        update_link = url_for('register', trip_id=registration.trip_id, _external=True).replace('/register/', '/register/id/')
        msg = Message(
            _('Registration Update Required'),
            sender=app.config['MAIL_USERNAME'],
            recipients=[registration.email]
        )
        msg.body = _("""
Dear Guest,

Your registration for %(trip_title)s requires updates.

Admin Comment: %(admin_comment)s

Please update your information using this link: %(update_link)s

Thank you for your understanding.

Best regards,
The Admin Team
""", trip_title=registration.trip.title, admin_comment=registration.admin_comment, update_link=update_link)
        mail.send(msg)
        
        # Restore original language
        session['lang'] = original_lang
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    # If language picker is disabled, redirect back without changing language
    if not app.config['LANGUAGE_PICKER_ENABLED']:
        return redirect(request.referrer or url_for('index'))
    
    if lang_code in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/housekeeper')
def housekeeper_landing():
    """Housekeeper landing page."""
    return render_template('housekeeper/landing.html')

@app.route('/housekeeper/login', methods=['GET', 'POST'])
def housekeeper_login():
    """Housekeeper login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_deleted=False).first()
        if user and user.check_password(password) and user.role == 'housekeeper':
            login_user(user)
            return redirect(url_for('housekeeper_dashboard'))
        else:
            flash(_('Invalid username or password'), 'error')
    
    return render_template('housekeeper/login.html')

@app.route('/housekeeper/dashboard')
@login_required
@role_required('housekeeper')
def housekeeper_dashboard():
    # Show assigned housekeeping tasks (for now, all tasks)
    tasks = Housekeeping.query.filter_by(housekeeper_id=current_user.id).all()
    return render_template('housekeeper/dashboard.html', tasks=tasks)

@app.route('/housekeeper/calendar')
@login_required
@role_required('housekeeper')
def housekeeper_calendar():
    return render_template('housekeeper/calendar.html')

@app.route('/api/housekeeping_events')
@login_required
@role_required('housekeeper')
def housekeeping_events_api():
    # Return housekeeping tasks as JSON for the calendar
    tasks = Housekeeping.query.filter_by(housekeeper_id=current_user.id).all()
    events = []
    for task in tasks:
        events.append({
            'id': task.id,
            'title': f'Housekeeping for Trip #{task.trip_id}',
            'start': task.date.isoformat(),
            'end': task.date.isoformat(),
            'status': task.status,
            'pay_amount': float(task.pay_amount),
            'paid': task.paid,
        })
    return jsonify(events)

@app.route('/housekeeper/upload_photo/<int:task_id>', methods=['POST'])
@login_required
@role_required('housekeeper')
def upload_amenity_photo(task_id):
    """Upload amenity photo for a housekeeping task."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Verify the task belongs to the current housekeeper
    if task.housekeeper_id != current_user.id:
        abort(403)
    
    if 'photo' not in request.files:
        flash(_('No photo selected'), 'error')
        return redirect(url_for('housekeeper_dashboard'))
    
    file = request.files['photo']
    if file.filename == '':
        flash(_('No photo selected'), 'error')
        return redirect(url_for('housekeeper_dashboard'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(f"amenity_{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Update the task with photo path
        task.amenity_photo_path = filename
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(_('Photo uploaded successfully'), 'success')
    else:
        flash(_('Invalid file type. Please upload JPG or PNG files only.'), 'error')
    
    return redirect(url_for('housekeeper_dashboard'))

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/housekeeping', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_housekeeping():
    # Filtering
    housekeeper_id = request.args.get('housekeeper_id', type=int)
    status = request.args.get('status')
    query = Housekeeping.query
    if housekeeper_id:
        query = query.filter_by(housekeeper_id=housekeeper_id)
    if status:
        query = query.filter_by(status=status)
    tasks = query.order_by(Housekeeping.date.desc()).all()
    housekeepers = User.query.filter_by(role='housekeeper').all()

    # Pay summaries
    pay_summary = {}
    for hk in housekeepers:
        hk_tasks = [t for t in tasks if t.housekeeper_id == hk.id]
        pay_summary[hk.id] = {
            'username': hk.username,
            'total': sum(float(t.pay_amount) for t in hk_tasks),
            'paid': sum(float(t.pay_amount) for t in hk_tasks if t.paid),
            'pending': sum(float(t.pay_amount) for t in hk_tasks if not t.paid),
        }
    grand_total = sum(float(t.pay_amount) for t in tasks)
    grand_paid = sum(float(t.pay_amount) for t in tasks if t.paid)
    grand_pending = sum(float(t.pay_amount) for t in tasks if not t.paid)

    # Handle pay status/amount update
    if request.method == 'POST':
        task_id = request.form.get('task_id', type=int)
        pay_amount = request.form.get('pay_amount', type=float)
        paid = request.form.get('paid') == 'on'
        task = Housekeeping.query.get_or_404(task_id)
        task.pay_amount = pay_amount
        task.paid = paid
        if paid:
            task.paid_date = datetime.utcnow()
        db.session.commit()
        flash(_('Housekeeping pay updated.'), 'success')
        return redirect(url_for('admin_housekeeping', housekeeper_id=housekeeper_id, status=status))

    return render_template('admin/housekeeping.html', tasks=tasks, housekeepers=housekeepers, selected_housekeeper=housekeeper_id, selected_status=status, pay_summary=pay_summary, grand_total=grand_total, grand_paid=grand_paid, grand_pending=grand_pending)

# CSV Export Routes
@app.route('/admin/export/registrations')
@login_required
@role_required('admin')
def export_registrations_csv():
    """Export registrations to CSV."""
    # Get all registrations for the current admin
    registrations = Registration.query.join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Registration ID'),
        _('Trip Title'),
        _('Email'),
        _('Status'),
        _('Language'),
        _('Created Date'),
        _('Updated Date'),
        _('Guest Count'),
        _('Admin Comment')
    ])
    
    # Write data
    for reg in registrations:
        writer.writerow([
            reg.id,
            reg.trip.title,
            reg.email,
            reg.status,
            reg.language,
            reg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            reg.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            len(reg.guests),
            reg.admin_comment or ''
        ])
    
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'registrations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/admin/export/guests')
@login_required
@role_required('admin')
def export_guests_csv():
    """Export guests to CSV."""
    # Get all guests for registrations belonging to the current admin
    guests = Guest.query.join(Registration).join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Guest ID'),
        _('Registration ID'),
        _('Trip Title'),
        _('First Name'),
        _('Last Name'),
        _('Age Category'),
        _('Document Type'),
        _('Document Number'),
        _('GDPR Consent'),
        _('Created Date')
    ])
    
    # Write data
    for guest in guests:
        writer.writerow([
            guest.id,
            guest.registration_id,
            guest.registration.trip.title,
            guest.first_name,
            guest.last_name,
            guest.age_category,
            guest.document_type,
            guest.document_number,
            'Yes' if guest.gdpr_consent else 'No',
            guest.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'guests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/admin/export/trips')
@login_required
@role_required('admin')
def export_trips_csv():
    """Export trips to CSV."""
    # Get all trips for the current admin
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Trip ID'),
        _('Title'),
        _('Start Date'),
        _('End Date'),
        _('Max Guests'),
        _('Created Date'),
        _('Amenity'),
        _('Calendar'),
        _('Externally Synced'),
        _('External Guest Name'),
        _('External Guest Email'),
        _('External Guest Count'),
        _('External Confirmation Code'),
        _('Registration Count'),
        _('Pending Count'),
        _('Approved Count'),
        _('Rejected Count')
    ])
    
    # Write data
    for trip in trips:
        registrations = trip.registrations
        pending_count = len([r for r in registrations if r.status == 'pending'])
        approved_count = len([r for r in registrations if r.status == 'approved'])
        rejected_count = len([r for r in registrations if r.status == 'rejected'])
        
        writer.writerow([
            trip.id,
            trip.title,
            trip.start_date.strftime('%Y-%m-%d'),
            trip.end_date.strftime('%Y-%m-%d'),
            trip.max_guests,
            trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            trip.amenity.name if trip.amenity else '',
            trip.calendar.name if trip.calendar else '',
            'Yes' if trip.is_externally_synced else 'No',
            trip.external_guest_name or '',
            trip.external_guest_email or '',
            trip.external_guest_count or '',
            trip.external_confirm_code or '',
            len(registrations),
            pending_count,
            approved_count,
            rejected_count
        ])
    
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'trips_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/admin/export/invoices')
@login_required
@role_required('admin')
def export_invoices_csv():
    """Export invoices to CSV."""
    # Get all invoices for the current admin
    invoices = Invoice.query.filter_by(admin_id=current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Invoice ID'),
        _('Invoice Number'),
        _('Client Name'),
        _('Client Email'),
        _('Client VAT Number'),
        _('Issue Date'),
        _('Due Date'),
        _('Subtotal'),
        _('VAT Total'),
        _('Total Amount'),
        _('Currency'),
        _('Status'),
        _('Created Date'),
        _('Updated Date'),
        _('Registration ID'),
        _('Trip Title')
    ])
    
    # Write data
    for invoice in invoices:
        trip_title = invoice.registration.trip.title if invoice.registration else ''
        writer.writerow([
            invoice.id,
            invoice.invoice_number,
            invoice.client_name,
            invoice.client_email or '',
            invoice.client_vat_number or '',
            invoice.issue_date.strftime('%Y-%m-%d'),
            invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
            float(invoice.subtotal),
            float(invoice.vat_total),
            float(invoice.total_amount),
            invoice.currency,
            invoice.status,
            invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            invoice.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            invoice.registration_id or '',
            trip_title
        ])
    
    output.seek(0)
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'invoices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

# Breakdown/Analytics Routes
@app.route('/admin/breakdowns')
@login_required
@role_required('admin')
def admin_breakdowns():
    """Main breakdowns/analytics page."""
    return render_template('admin/breakdowns.html')

@app.route('/admin/breakdowns/registrations')
@login_required
@role_required('admin')
def registration_breakdown():
    """Registration statistics and breakdowns."""
    # Get all registrations for the current admin
    registrations = Registration.query.join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Status breakdown
    status_counts = defaultdict(int)
    for reg in registrations:
        status_counts[reg.status] += 1
    
    # Monthly breakdown
    monthly_counts = defaultdict(int)
    for reg in registrations:
        month_key = reg.created_at.strftime('%Y-%m')
        monthly_counts[month_key] += 1
    
    # Trip breakdown
    trip_counts = defaultdict(int)
    for reg in registrations:
        trip_counts[reg.trip.title] += 1
    
    # Language breakdown
    language_counts = defaultdict(int)
    for reg in registrations:
        language_counts[reg.language] += 1
    
    # Guest count distribution
    guest_count_distribution = defaultdict(int)
    for reg in registrations:
        guest_count_distribution[len(reg.guests)] += 1
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_registrations = [reg for reg in registrations if reg.created_at >= thirty_days_ago]
    
    stats = {
        'total_registrations': len(registrations),
        'pending_count': status_counts['pending'],
        'approved_count': status_counts['approved'],
        'rejected_count': status_counts['rejected'],
        'recent_count': len(recent_registrations),
        'status_breakdown': dict(status_counts),
        'monthly_breakdown': dict(monthly_counts),
        'trip_breakdown': dict(trip_counts),
        'language_breakdown': dict(language_counts),
        'guest_count_distribution': dict(guest_count_distribution)
    }
    
    return render_template('admin/registration_breakdown.html', stats=stats, registrations=registrations)

@app.route('/admin/breakdowns/guests')
@login_required
@role_required('admin')
def guest_breakdown():
    """Guest statistics and breakdowns."""
    # Get all guests for registrations belonging to the current admin
    guests = Guest.query.join(Registration).join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Age category breakdown
    age_category_counts = defaultdict(int)
    for guest in guests:
        age_category_counts[guest.age_category] += 1
    
    # Document type breakdown
    document_type_counts = defaultdict(int)
    for guest in guests:
        document_type_counts[guest.document_type] += 1
    
    # GDPR consent breakdown
    gdpr_consent_count = sum(1 for guest in guests if guest.gdpr_consent)
    gdpr_no_consent_count = len(guests) - gdpr_consent_count
    
    # Monthly guest registration
    monthly_guest_counts = defaultdict(int)
    for guest in guests:
        month_key = guest.created_at.strftime('%Y-%m')
        monthly_guest_counts[month_key] += 1
    
    # Trip breakdown for guests
    trip_guest_counts = defaultdict(int)
    for guest in guests:
        trip_guest_counts[guest.registration.trip.title] += 1
    
    stats = {
        'total_guests': len(guests),
        'adult_count': age_category_counts['adult'],
        'child_count': age_category_counts['child'],
        'gdpr_consent_count': gdpr_consent_count,
        'gdpr_no_consent_count': gdpr_no_consent_count,
        'age_category_breakdown': dict(age_category_counts),
        'document_type_breakdown': dict(document_type_counts),
        'monthly_guest_counts': dict(monthly_guest_counts),
        'trip_guest_counts': dict(trip_guest_counts)
    }
    
    return render_template('admin/guest_breakdown.html', stats=stats, guests=guests)

@app.route('/admin/breakdowns/trips')
@login_required
@role_required('admin')
def trip_breakdown():
    """Trip statistics and breakdowns."""
    # Get all trips for the current admin
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    
    # Registration count per trip
    trip_registration_counts = {}
    trip_guest_counts = {}
    trip_status_breakdowns = {}
    
    for trip in trips:
        registrations = trip.registrations
        trip_registration_counts[trip.title] = len(registrations)
        
        # Count guests per trip
        guest_count = sum(len(reg.guests) for reg in registrations)
        trip_guest_counts[trip.title] = guest_count
        
        # Status breakdown per trip
        status_counts = defaultdict(int)
        for reg in registrations:
            status_counts[reg.status] += 1
        trip_status_breakdowns[trip.title] = dict(status_counts)
    
    # Monthly trip creation
    monthly_trip_counts = defaultdict(int)
    for trip in trips:
        month_key = trip.created_at.strftime('%Y-%m')
        monthly_trip_counts[month_key] += 1
    
    # External sync statistics
    externally_synced_count = sum(1 for trip in trips if trip.is_externally_synced)
    externally_not_synced_count = len(trips) - externally_synced_count
    
    # Duration statistics
    trip_durations = []
    for trip in trips:
        duration = (trip.end_date - trip.start_date).days
        trip_durations.append(duration)
    
    avg_duration = sum(trip_durations) / len(trip_durations) if trip_durations else 0
    
    stats = {
        'total_trips': len(trips),
        'externally_synced_count': externally_synced_count,
        'externally_not_synced_count': externally_not_synced_count,
        'avg_duration_days': round(avg_duration, 1),
        'trip_registration_counts': trip_registration_counts,
        'trip_guest_counts': trip_guest_counts,
        'trip_status_breakdowns': trip_status_breakdowns,
        'monthly_trip_counts': dict(monthly_trip_counts)
    }
    
    return render_template('admin/trip_breakdown.html', stats=stats, trips=trips)

@app.route('/admin/breakdowns/invoices')
@login_required
@role_required('admin')
def invoice_breakdown():
    """Invoice statistics and breakdowns."""
    # Get all invoices for the current admin
    invoices = Invoice.query.filter_by(admin_id=current_user.id).all()
    
    # Status breakdown
    status_counts = defaultdict(int)
    for invoice in invoices:
        status_counts[invoice.status] += 1
    
    # Monthly invoice creation
    monthly_invoice_counts = defaultdict(int)
    for invoice in invoices:
        month_key = invoice.created_at.strftime('%Y-%m')
        monthly_invoice_counts[month_key] += 1
    
    # Amount statistics
    total_amount = sum(float(invoice.total_amount) for invoice in invoices)
    avg_amount = total_amount / len(invoices) if invoices else 0
    
    # Status-based amounts
    status_amounts = defaultdict(float)
    for invoice in invoices:
        status_amounts[invoice.status] += float(invoice.total_amount)
    
    # Currency breakdown
    currency_counts = defaultdict(int)
    for invoice in invoices:
        currency_counts[invoice.currency] += 1
    
    # Monthly revenue
    monthly_revenue = defaultdict(float)
    for invoice in invoices:
        month_key = invoice.created_at.strftime('%Y-%m')
        monthly_revenue[month_key] += float(invoice.total_amount)
    
    stats = {
        'total_invoices': len(invoices),
        'total_amount': total_amount,
        'avg_amount': round(avg_amount, 2),
        'status_counts': dict(status_counts),
        'status_amounts': dict(status_amounts),
        'currency_counts': dict(currency_counts),
        'monthly_invoice_counts': dict(monthly_invoice_counts),
        'monthly_revenue': dict(monthly_revenue)
    }
    
    return render_template('admin/invoice_breakdown.html', stats=stats, invoices=invoices)

# User Management Routes
@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Admin users list page."""
    users = User.query.filter_by(is_deleted=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_user():
    """Create a new user."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'admin')
        
        # Check if username or email already exists (not deleted)
        if User.query.filter_by(username=username, is_deleted=False).first():
            flash(_('Username already exists'), 'error')
            return render_template('admin/new_user.html')
        
        if User.query.filter_by(email=email, is_deleted=False).first():
            flash(_('Email already exists'), 'error')
            return render_template('admin/new_user.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('User created successfully!'), 'success')
        return redirect(url_for('admin_users'))
    
    # Get role from query parameter for pre-filling
    default_role = request.args.get('role', 'admin')
    return render_template('admin/new_user.html', default_role=default_role)

@app.route('/admin/users/<int:user_id>')
@login_required
@role_required('admin')
def view_user(user_id):
    """View a specific user."""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    return render_template('admin/view_user.html', user=user)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    """Edit an existing user."""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'admin')
        new_password = request.form.get('new_password')
        
        # Check if username or email already exists (excluding current user, not deleted)
        existing_user = User.query.filter_by(username=username, is_deleted=False).first()
        if existing_user and existing_user.id != user.id:
            flash(_('Username already exists'), 'error')
            return render_template('admin/edit_user.html', user=user)
        
        existing_user = User.query.filter_by(email=email, is_deleted=False).first()
        if existing_user and existing_user.id != user.id:
            flash(_('Email already exists'), 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Update user
        user.username = username
        user.email = email
        user.role = role
        
        # Update password if provided
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        
        flash(_('User updated successfully!'), 'success')
        return redirect(url_for('view_user', user_id=user.id))
    
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Soft delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current user
    if user.id == current_user.id:
        flash(_('You cannot delete your own account'), 'error')
        return redirect(url_for('admin_users'))
    
    # Check if user is already deleted
    if user.is_deleted:
        flash(_('User is already deleted.'), 'info')
        return redirect(url_for('admin_users'))
    try:
        user.is_deleted = True
        db.session.commit()
        flash(_('User deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to soft delete user {user_id}: {e}")
        flash(_('Error deleting user: %(error)s', error=str(e)), 'error')
    return redirect(url_for('admin_users'))

@app.route('/api/backup/guests', methods=['GET'])
@login_required
@role_required('admin')
def api_backup_guests():
    """Export all registered guests for a given month (no photos, admin only)."""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    fmt = request.args.get('format', 'csv')
    if not year or not month:
        return jsonify({'error': 'Missing year or month parameter'}), 400

    # Get guests for the given month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    guests = Guest.query.join(Registration).filter(
        Registration.created_at >= start_date,
        Registration.created_at < end_date
    ).all()

    # Prepare data (no photos)
    guest_data = []
    for g in guests:
        guest_data.append({
            'id': g.id,
            'registration_id': g.registration_id,
            'first_name': g.first_name,
            'last_name': g.last_name,
            'age_category': g.age_category,
            'document_type': g.document_type,
            'document_number': g.document_number,
            'gdpr_consent': g.gdpr_consent,
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'trip_title': g.registration.trip.title if g.registration and g.registration.trip else '',
            'registration_email': g.registration.email if g.registration else '',
            'registration_language': g.registration.language if g.registration else '',
        })

    if fmt == 'json':
        return jsonify(guest_data)
    else:
        # CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=guest_data[0].keys() if guest_data else [
            'id','registration_id','first_name','last_name','age_category','document_type','document_number','gdpr_consent','created_at','trip_title','registration_email','registration_language'])
        writer.writeheader()
        for row in guest_data:
            writer.writerow(row)
        csv_data = output.getvalue().encode('utf-8')
        output.close()
        return send_file(
            BytesIO(csv_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'guests_{year}_{month:02d}.csv'
        )

@app.route('/admin/backup', methods=['GET'])
@login_required
@role_required('admin')
def admin_system_backup():
    """Create a system backup (DB dump + uploads, no guest photos) as a ZIP download."""
    import subprocess, tempfile, zipfile, shutil
    from flask import current_app

    # Prepare temp directory
    tmpdir = tempfile.mkdtemp()
    db_dump_path = os.path.join(tmpdir, 'db_backup.sql')
    uploads_dir = app.config['UPLOAD_FOLDER']
    backup_zip_path = os.path.join(tmpdir, f'system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')

    # Parse DB URL
    import re
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    m = re.match(r'postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)', db_url)
    if not m:
        shutil.rmtree(tmpdir)
        return 'Invalid database URL', 500
    db_user, db_pass, db_host, db_port, db_name = m.groups()
    db_port = db_port or '5432'

    # Run pg_dump
    env = os.environ.copy()
    env['PGPASSWORD'] = db_pass
    try:
        subprocess.check_call([
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-F', 'plain',
            '-f', db_dump_path,
            db_name
        ], env=env)
    except Exception as e:
        shutil.rmtree(tmpdir)
        return f'Error running pg_dump: {e}', 500

    # Prepare uploads (excluding guest document photos)
    uploads_tmp = os.path.join(tmpdir, 'uploads')
    os.makedirs(uploads_tmp, exist_ok=True)
    for fname in os.listdir(uploads_dir):
        # Exclude files that look like guest document images (by convention: uuid_*.jpg/png)
        if re.match(r'[0-9a-fA-F\-]{36}_', fname):
            continue
        src = os.path.join(uploads_dir, fname)
        dst = os.path.join(uploads_tmp, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst)

    # Create ZIP
    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_dump_path, arcname='db_backup.sql')
        for root, dirs, files in os.walk(uploads_tmp):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, uploads_tmp)
                zf.write(full_path, arcname=os.path.join('uploads', rel_path))

    # Serve ZIP
    with open(backup_zip_path, 'rb') as f:
        data = f.read()
    shutil.rmtree(tmpdir)
    return send_file(
        BytesIO(data),
        mimetype='application/zip',
        as_attachment=True,
        download_name=os.path.basename(backup_zip_path)
    )

@app.route('/api/version')
def api_version():
    """Get application version information"""
    return jsonify(version_manager.get_version_info())

@app.route('/api/version/compatibility')
def api_version_compatibility():
    """Check version compatibility"""
    current_db_version = migration_manager.get_current_version()
    app_version = version_manager.get_current_version()
    
    compatibility = check_version_compatibility(app_version, current_db_version)
    
    return jsonify({
        'app_version': app_version,
        'database_version': current_db_version,
        'compatible': compatibility['compatible'],
        'recommendation': compatibility['recommendation']
    })

@app.route('/api/version/changelog/<version>')
def api_version_changelog(version):
    """Get changelog for a specific version"""
    changelog = get_version_changelog(version)
    return jsonify(changelog)

@app.route('/admin/migrations')
@login_required
@role_required('admin')
def admin_migrations():
    """Migration management page"""
    current_version = migration_manager.get_current_version()
    app_version = version_manager.get_current_version()
    applied_migrations = migration_manager.get_applied_migrations()
    pending_migrations = migration_manager.get_pending_migrations()
    
    # Check compatibility
    compatibility = check_version_compatibility(app_version, current_version)
    
    return render_template('admin/migrations.html',
                         current_version=current_version,
                         app_version=app_version,
                         applied_migrations=applied_migrations,
                         pending_migrations=pending_migrations,
                         compatibility=compatibility)

@app.route('/admin/migrations/run', methods=['POST'])
@login_required
@role_required('admin')
def run_migrations():
    """Run pending migrations"""
    try:
        # Create backup before migration
        backup_file = migration_manager.create_backup_before_migration()
        
        # Run migrations
        success = migration_manager.migrate()
        
        if success:
            flash('Migrations applied successfully!', 'success')
        else:
            flash('Some migrations failed to apply.', 'error')
            
    except Exception as e:
        flash(f'Migration error: {str(e)}', 'error')
    
    return redirect(url_for('admin_migrations'))

@app.route('/admin/migrations/rollback/<version>', methods=['POST'])
@login_required
@role_required('admin')
def rollback_migration(version):
    """Rollback specific migration"""
    try:
        success = migration_manager.rollback_migration(version)
        
        if success:
            flash(_('Migration %(version)s rolled back successfully!', version=version), 'success')
        else:
            flash(_('Failed to rollback migration %(version)s', version=version), 'error')
        
        return redirect(url_for('admin_migrations'))
        
    except Exception as e:
        flash(_('Rollback error: %(error)s', error=str(e)), 'error')
        return redirect(url_for('admin_migrations'))

def sync_calendar_reservations(calendar_id):
    """Sync reservations for a specific calendar, ensuring unique confirmation codes."""
    calendar = Calendar.query.get(calendar_id)
    if not calendar or not calendar.calendar_url or not calendar.sync_enabled:
        return {'success': False, 'message': 'Calendar sync not configured or disabled'}
    
    try:
        reservations = fetch_calendar_data(calendar.calendar_url, calendar.calendar_type)
        synced_count = 0
        updated_count = 0
        housekeeping_tasks_created = 0
        
        for reservation in reservations:
            # Check if trip already exists by external reservation ID
            existing_trip = Trip.query.filter_by(
                external_reservation_id=reservation['id'],
                calendar_id=calendar_id
            ).first()
            
            # Also check if trip exists by confirmation code
            confirm_code = reservation['confirm_code']
            existing_code_trip = None
            if confirm_code:
                existing_code_trip = Trip.query.filter_by(
                    external_confirm_code=confirm_code
                ).first()
            
            # Use amenity's max_guests if guest count not parsed from calendar
            guest_count = reservation['guest_count'] if reservation['guest_count'] > 0 else calendar.amenity.max_guests
            
            if existing_trip:
                # Update existing trip by reservation ID
                existing_trip.title = reservation['title']
                existing_trip.start_date = reservation['start_date']
                existing_trip.end_date = reservation['end_date']
                existing_trip.max_guests = guest_count
                existing_trip.external_guest_name = reservation['guest_name']
                existing_trip.external_guest_email = reservation['guest_email']
                existing_trip.external_confirm_code = reservation['confirm_code']
                existing_trip.external_synced_at = datetime.utcnow()
                updated_count += 1
            elif existing_code_trip:
                # Update existing trip by confirmation code (dates may have changed)
                existing_code_trip.title = reservation['title']
                existing_code_trip.start_date = reservation['start_date']
                existing_code_trip.end_date = reservation['end_date']
                existing_code_trip.max_guests = guest_count
                existing_code_trip.external_guest_name = reservation['guest_name']
                existing_code_trip.external_guest_email = reservation['guest_email']
                existing_code_trip.external_reservation_id = reservation['id']
                existing_code_trip.calendar_id = calendar_id
                existing_code_trip.external_synced_at = datetime.utcnow()
                updated_count += 1
            else:
                # Create new trip
                trip = Trip(
                    title=reservation['title'],
                    start_date=reservation['start_date'],
                    end_date=reservation['end_date'],
                    max_guests=guest_count,
                    admin_id=calendar.amenity.admin_id,
                    amenity_id=calendar.amenity_id,
                    calendar_id=calendar_id,
                    external_reservation_id=reservation['id'],
                    external_guest_name=reservation['guest_name'],
                    external_guest_email=reservation['guest_email'],
                    external_confirm_code=reservation['confirm_code'],
                    external_synced_at=datetime.utcnow(),
                    is_externally_synced=True
                )
                db.session.add(trip)
                db.session.flush()  # Get the trip ID
                
                # Create housekeeping task for the new trip
                # First try to get the default housekeeper from the new system
                default_housekeeper_assignment = AmenityHousekeeper.query.filter_by(
                    amenity_id=calendar.amenity_id,
                    is_default=True
                ).first()
                
                # Fallback to the old system if no default housekeeper is set
                if not default_housekeeper_assignment and calendar.amenity.default_housekeeper_id:
                    default_housekeeper_id = calendar.amenity.default_housekeeper_id
                elif default_housekeeper_assignment:
                    default_housekeeper_id = default_housekeeper_assignment.housekeeper_id
                else:
                    default_housekeeper_id = None
                
                if default_housekeeper_id:
                    # Create housekeeping task for the day after the trip ends
                    housekeeping_task = Housekeeping(
                        trip_id=trip.id,
                        housekeeper_id=default_housekeeper_id,
                        date=reservation['end_date'] + timedelta(days=1),
                        status='pending',
                        pay_amount=50.00,  # Default pay amount
                        paid=False
                    )
                    db.session.add(housekeeping_task)
                    housekeeping_tasks_created += 1
                
                synced_count += 1
        
        # Update calendar last sync time
        calendar.last_sync = datetime.utcnow()
        db.session.commit()
        
        message = f"Synced {synced_count} new reservations, updated {updated_count} existing reservations"
        if housekeeping_tasks_created > 0:
            message += f", created {housekeeping_tasks_created} housekeeping tasks"
        
        return {'success': True, 'message': message, 'synced': synced_count, 'updated': updated_count, 'housekeeping_tasks': housekeeping_tasks_created}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Sync failed: {str(e)}'}

def sync_all_calendars_for_admin(admin_id):
    """Sync all calendars for a specific admin."""
    try:
        # Get all active calendars for the admin
        calendars = Calendar.query.join(Amenity).filter(
            Amenity.admin_id == admin_id,
            Calendar.sync_enabled == True,
            Calendar.is_active == True
        ).all()
        
        total_synced = 0
        total_updated = 0
        failed_calendars = []
        
        for calendar in calendars:
            result = sync_calendar_reservations(calendar.id)
            if result['success']:
                total_synced += result.get('synced', 0)
                total_updated += result.get('updated', 0)
            else:
                failed_calendars.append(f"{calendar.name}: {result['message']}")
        
        if failed_calendars:
            message = f"Synced {total_synced} new, updated {total_updated} existing reservations. Failed: {'; '.join(failed_calendars)}"
        else:
            message = f"Successfully synced {total_synced} new reservations and updated {total_updated} existing reservations"
        
        return {'success': True, 'message': message, 'synced': total_synced, 'updated': total_updated}
        
    except Exception as e:
        return {'success': False, 'message': f'Sync failed: {str(e)}'}

def fetch_calendar_data(calendar_url, calendar_type='airbnb'):
    """Fetch and parse calendar data based on type."""
    if calendar_type == 'airbnb':
        return fetch_airbnb_calendar(calendar_url)
    else:
        # For other calendar types, use the same parsing logic for now
        return fetch_airbnb_calendar(calendar_url)

# Calendar Management Routes
@app.route('/admin/calendars')
@login_required
@role_required('admin')
def admin_calendars():
    """Manage calendars."""
    amenities = Amenity.query.filter_by(admin_id=current_user.id).order_by(Amenity.name).all()
    calendars_by_amenity = {}
    for amenity in amenities:
        calendars_by_amenity[amenity] = Calendar.query.filter_by(amenity_id=amenity.id).order_by(Calendar.name).all()

    # Precompute statistics
    def count_sync_enabled(calendars):
        return sum(1 for c in calendars if getattr(c, 'sync_enabled', False))
    def count_trips(calendars):
        return sum(len(getattr(c, 'trips', [])) for c in calendars)
    def count_synced_trips(calendars):
        return sum(
            sum(1 for t in getattr(c, 'trips', []) if getattr(t, 'is_externally_synced', False))
            for c in calendars
        )
    total_calendars = sum(len(cals) for cals in calendars_by_amenity.values())
    sync_enabled = sum(count_sync_enabled(cals) for cals in calendars_by_amenity.values())
    total_trips = sum(count_trips(cals) for cals in calendars_by_amenity.values())
    synced_trips = sum(count_synced_trips(cals) for cals in calendars_by_amenity.values())

    return render_template(
        'admin/calendars.html',
        calendars_by_amenity=calendars_by_amenity,
        amenities=amenities,
        total_calendars=total_calendars,
        sync_enabled=sync_enabled,
        total_trips=total_trips,
        synced_trips=synced_trips
    )

@app.route('/admin/calendars/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_calendar():
    """Create a new calendar."""
    if request.method == 'POST':
        amenity_id = request.form.get('amenity_id')
        amenity = Amenity.query.get(amenity_id)
        
        if not amenity or amenity.admin_id != current_user.id:
            flash(_('Invalid amenity selected'), 'error')
            return redirect(url_for('new_calendar'))
        
        calendar = Calendar(
            name=request.form.get('name'),
            description=request.form.get('description'),
            amenity_id=amenity_id,
            calendar_url=request.form.get('calendar_url'),
            calendar_type=request.form.get('calendar_type', 'airbnb'),
            sync_enabled=request.form.get('sync_enabled') == 'on',
            sync_frequency=request.form.get('sync_frequency', 'daily'),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(calendar)
        db.session.commit()
        flash(_('Calendar created successfully!'), 'success')
        return redirect(url_for('admin_calendars'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/new_calendar.html', amenities=amenities)

@app.route('/admin/calendars/<int:calendar_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_calendar(calendar_id):
    """Edit a calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_calendars'))
    
    if request.method == 'POST':
        calendar.name = request.form.get('name')
        calendar.description = request.form.get('description')
        calendar.calendar_url = request.form.get('calendar_url')
        calendar.calendar_type = request.form.get('calendar_type', 'airbnb')
        calendar.sync_enabled = request.form.get('sync_enabled') == 'on'
        calendar.sync_frequency = request.form.get('sync_frequency', 'daily')
        calendar.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash(_('Calendar updated successfully!'), 'success')
        return redirect(url_for('admin_calendars'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/edit_calendar.html', calendar=calendar, amenities=amenities)

@app.route('/admin/calendars/<int:calendar_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_calendar(calendar_id):
    """Delete a calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_calendars'))
    
    # Check if calendar has trips
    if calendar.trips:
        flash(_('Cannot delete calendar with existing trips'), 'error')
        return redirect(url_for('admin_calendars'))
    
    db.session.delete(calendar)
    db.session.commit()
    flash(_('Calendar deleted successfully!'), 'success')
    return redirect(url_for('admin_calendars'))

@app.route('/admin/amenities/<int:amenity_id>/housekeepers')
@login_required
@role_required('admin')
def amenity_housekeepers(amenity_id):
    """Manage housekeepers for a specific amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    # Get all housekeepers
    housekeepers = User.query.filter_by(role='housekeeper').all()
    
    # Get current assignments
    assignments = AmenityHousekeeper.query.filter_by(amenity_id=amenity_id).all()
    assigned_housekeeper_ids = [a.housekeeper_id for a in assignments]
    
    # Get default housekeeper
    default_assignment = next((a for a in assignments if a.is_default), None)
    
    return render_template('admin/amenity_housekeepers.html', 
                         amenity=amenity, 
                         housekeepers=housekeepers,
                         assignments=assignments,
                         assigned_housekeeper_ids=assigned_housekeeper_ids,
                         default_assignment=default_assignment)

@app.route('/admin/amenities/<int:amenity_id>/housekeepers/assign', methods=['POST'])
@login_required
@role_required('admin')
def assign_housekeeper_to_amenity(amenity_id):
    """Assign a housekeeper to an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    housekeeper_id = request.form.get('housekeeper_id', type=int)
    is_default = request.form.get('is_default') == 'on'
    
    if not housekeeper_id:
        flash(_('Please select a housekeeper'), 'error')
        return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))
    
    # Check if housekeeper exists and is actually a housekeeper
    housekeeper = User.query.filter_by(id=housekeeper_id, role='housekeeper').first()
    if not housekeeper:
        flash(_('Invalid housekeeper selected'), 'error')
        return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))
    
    # Check if assignment already exists
    existing_assignment = AmenityHousekeeper.query.filter_by(
        amenity_id=amenity_id, 
        housekeeper_id=housekeeper_id
    ).first()
    
    if existing_assignment:
        flash(_('Housekeeper is already assigned to this amenity'), 'error')
        return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))
    
    # Create new assignment
    assignment = AmenityHousekeeper(
        amenity_id=amenity_id,
        housekeeper_id=housekeeper_id,
        is_default=is_default
    )
    
    # If this is set as default, unset other defaults for this amenity
    if is_default:
        AmenityHousekeeper.query.filter_by(
            amenity_id=amenity_id, 
            is_default=True
        ).update({'is_default': False})
    
    db.session.add(assignment)
    db.session.commit()
    
    flash(_('Housekeeper assigned successfully'), 'success')
    return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))

@app.route('/admin/amenities/<int:amenity_id>/housekeepers/<int:assignment_id>/set-default', methods=['POST'])
@login_required
@role_required('admin')
def set_default_housekeeper(amenity_id, assignment_id):
    """Set a housekeeper as default for an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    assignment = AmenityHousekeeper.query.get_or_404(assignment_id)
    if assignment.amenity_id != amenity_id:
        flash(_('Invalid assignment'), 'error')
        return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))
    
    # Unset all other defaults for this amenity
    AmenityHousekeeper.query.filter_by(
        amenity_id=amenity_id, 
        is_default=True
    ).update({'is_default': False})
    
    # Set this assignment as default
    assignment.is_default = True
    db.session.commit()
    
    flash(_('Default housekeeper updated successfully'), 'success')
    return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))

@app.route('/admin/amenities/<int:amenity_id>/housekeepers/<int:assignment_id>/remove', methods=['POST'])
@login_required
@role_required('admin')
def remove_housekeeper_from_amenity(amenity_id, assignment_id):
    """Remove a housekeeper from an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_amenities'))
    
    assignment = AmenityHousekeeper.query.get_or_404(assignment_id)
    if assignment.amenity_id != amenity_id:
        flash(_('Invalid assignment'), 'error')
        return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))
    
    db.session.delete(assignment)
    db.session.commit()
    
    flash(_('Housekeeper removed from amenity successfully'), 'success')
    return redirect(url_for('amenity_housekeepers', amenity_id=amenity_id))

@app.route('/admin/housekeeping/<int:task_id>/reassign', methods=['POST'])
@login_required
@role_required('admin')
def reassign_housekeeping_task(task_id):
    """Reassign a housekeeping task to a different housekeeper."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Check if admin has access to this task (through amenity ownership)
    if task.trip.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin_housekeeping'))
    
    new_housekeeper_id = request.form.get('housekeeper_id', type=int)
    
    if not new_housekeeper_id:
        flash(_('Please select a housekeeper'), 'error')
        return redirect(url_for('admin_housekeeping'))
    
    # Check if housekeeper exists and is actually a housekeeper
    housekeeper = User.query.filter_by(id=new_housekeeper_id, role='housekeeper').first()
    if not housekeeper:
        flash(_('Invalid housekeeper selected'), 'error')
        return redirect(url_for('admin_housekeeping'))
    
    # Update the task
    task.housekeeper_id = new_housekeeper_id
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(_('Housekeeping task reassigned successfully'), 'success')
    return redirect(url_for('admin_housekeeping'))

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Guest Registration System')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload on code changes')
    parser.add_argument('--threaded', action='store_true', help='Enable threading')
    parser.add_argument('--ssl-context', help='SSL context for HTTPS (e.g., "adhoc" for self-signed)')
    
    args = parser.parse_args()
    
    # Determine debug mode
    debug_mode = True  # Default to True for development
    if args.no_debug:
        debug_mode = False
    elif args.debug:
        debug_mode = True
    
    # SSL context
    ssl_context = None
    if args.ssl_context:
        if args.ssl_context == 'adhoc':
            try:
                import ssl
                ssl_context = 'adhoc'
            except ImportError:
                print("Warning: 'adhoc' SSL context requires 'pyOpenSSL' package. Install with: pip install pyOpenSSL")
                ssl_context = None
        else:
            ssl_context = args.ssl_context
    
    print(f"Starting Guest Registration System...")
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Debug: {debug_mode}")
    print(f"  Auto-reload: {args.reload}")
    print(f"  Threaded: {args.threaded}")
    if ssl_context:
        print(f"  SSL: {ssl_context}")
    print(f"  URL: http{'s' if ssl_context else ''}://{args.host}:{args.port}")
    print()
    
    # Run the application
    app.run(
        host=args.host,
        port=args.port,
        debug=debug_mode,
        use_reloader=args.reload,
        threaded=args.threaded,
        ssl_context=ssl_context
    ) 