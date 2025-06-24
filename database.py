import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import tempfile
import shutil
import subprocess
import sys
from collections import defaultdict

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
import requests
from icalendar import Calendar as iCalCalendar
import pytz
from config import Config

# Initialize SQLAlchemy (will be initialized later with app)
db = SQLAlchemy()

def get_table_name(base_name):
    """Get table name with prefix."""
    try:
        prefix = Config.TABLE_PREFIX
        return f"{prefix}{base_name}"
    except:
        # Fallback for when not in app context
        return base_name

def get_database_url():
    """Get database URL from environment or use default."""
    database_url = Config.SQLALCHEMY_DATABASE_URI
    if database_url:
        return database_url
    
    # Default to SQLite
    return 'sqlite:///guest_registration.db'

def copy_sample_image(image_filename):
    """Copy a sample image to the uploads folder if it doesn't exist."""
    sample_path = os.path.join('static', 'sample_images', image_filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
    
    if os.path.exists(sample_path) and not os.path.exists(upload_path):
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        shutil.copy2(sample_path, upload_path)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = f"{Config.TABLE_PREFIX}user"
    
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
    __tablename__ = f"{Config.TABLE_PREFIX}amenity"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    max_guests = db.Column(db.Integer, nullable=False, default=1)
    admin_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Status
    is_active = db.Column(db.Boolean, default=True)
    # Backward compatibility
    default_housekeeper_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}user.id"))
    
    # Relationships
    admin = db.relationship('User', backref='amenities', foreign_keys=[admin_id])
    default_housekeeper = db.relationship('User', backref='default_amenities', foreign_keys=[default_housekeeper_id])
    trips = db.relationship('Trip', backref='amenity', lazy=True)
    calendars = db.relationship('Calendar', backref='amenity', lazy=True, cascade='all, delete-orphan')
    housekeepers = db.relationship('AmenityHousekeeper', backref='amenity', lazy=True, cascade='all, delete-orphan')

class AmenityHousekeeper(db.Model):
    __tablename__ = f"{Config.TABLE_PREFIX}amenity_housekeeper"
    
    id = db.Column(db.Integer, primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}amenity.id"), nullable=False)
    housekeeper_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}user.id"), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    housekeeper = db.relationship('User', backref='amenity_assignments')
    
    __table_args__ = (
        db.UniqueConstraint('amenity_id', 'housekeeper_id', name='uq_amenity_housekeeper'),
    )

class Calendar(db.Model):
    __tablename__ = f"{Config.TABLE_PREFIX}calendar"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amenity_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}amenity.id"), nullable=False)
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
    __tablename__ = f"{Config.TABLE_PREFIX}trip"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}user.id"), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}amenity.id"), nullable=False)
    calendar_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}calendar.id"))
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
    __tablename__ = f"{Config.TABLE_PREFIX}registration"
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}trip.id"), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_comment = db.Column(db.Text)
    language = db.Column(db.String(10), default='en')  # Store selected language
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    guests = db.relationship('Guest', backref='registration', lazy=True, cascade='all, delete-orphan')

class Guest(db.Model):
    __tablename__ = f"{Config.TABLE_PREFIX}guest"
    
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}registration.id"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age_category = db.Column(db.String(20), nullable=False, default='adult')  # adult, child
    document_type = db.Column(db.String(50), nullable=False)  # passport, driving_license, citizen_id
    document_number = db.Column(db.String(100), nullable=False)
    document_image = db.Column(db.String(255))  # File path to uploaded image
    gdpr_consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = f"{Config.TABLE_PREFIX}invoice"
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}user.id"), nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}registration.id"))
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
    __tablename__ = f"{Config.TABLE_PREFIX}invoice_item"
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}invoice.id"), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 2), default=0)  # VAT rate as percentage
    line_total = db.Column(db.Numeric(10, 2), default=0)
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    total_with_vat = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Housekeeping(db.Model):
    __tablename__ = f"{Config.TABLE_PREFIX}housekeeping"
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}trip.id"), nullable=False)
    housekeeper_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}user.id"), nullable=False)
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
    __tablename__ = f"{Config.TABLE_PREFIX}housekeeping_photo"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey(f"{Config.TABLE_PREFIX}housekeeping.id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship('Housekeeping', backref=db.backref('photos', lazy=True, cascade='all, delete-orphan'))

# Business logic functions
def parse_airbnb_guest_info(summary, description):
    """Parse guest information from Airbnb calendar event."""
    guest_info = {}
    
    if summary and 'reserved' in summary.lower():
        # Extract guest name from "Reserved by John Smith"
        parts = summary.replace('Reserved by', '').replace('Reserved for', '').strip()
        if parts:
            guest_info['name'] = parts
    
    if description:
        lines = description.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Email:'):
                guest_info['email'] = line.replace('Email:', '').strip()
            elif line.startswith('Phone:'):
                guest_info['phone'] = line.replace('Phone:', '').strip()
            elif line.startswith('Guests:'):
                try:
                    guest_count = int(line.replace('Guests:', '').strip())
                    guest_info['guest_count'] = guest_count
                except ValueError:
                    pass
    
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
    """Sync reservations from Airbnb calendar."""
    amenity = Amenity.query.get(amenity_id)
    if not amenity:
        return {'success': False, 'message': 'Amenity not found'}
    
    # Get all calendars for this amenity
    calendars = Calendar.query.filter_by(amenity_id=amenity_id, sync_enabled=True).all()
    
    if not calendars:
        return {'success': False, 'message': 'No active calendars found for this amenity'}
    
    total_synced = 0
    errors = []
    
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
    
    return {'success': True, 'message': f"Successfully synced {total_synced} reservations"}

def sync_all_amenities_for_admin(admin_id):
    """Sync all amenities for a specific admin."""
    # Get all amenities for this admin
    amenities = Amenity.query.filter_by(admin_id=admin_id).all()
    
    total_synced = 0
    errors = []
    
    for amenity in amenities:
        try:
            result = sync_airbnb_reservations(amenity.id)
            if result['success']:
                # Extract number from message like "Successfully synced 5 reservations"
                message = result['message']
                if 'synced' in message:
                    parts = message.split('synced')
                    if len(parts) > 1:
                        number_part = parts[1].split()[0]
                        try:
                            total_synced += int(number_part)
                        except ValueError:
                            pass
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
                    # Extract event details
                    summary = str(component.get('summary', ''))
                    description = str(component.get('description', ''))
                    start_date = component.get('dtstart').dt
                    end_date = component.get('dtend').dt
                    uid = str(component.get('uid', ''))
                    
                    # Convert datetime to date if needed
                    if hasattr(start_date, 'date'):
                        start_date = start_date.date()
                    if hasattr(end_date, 'date'):
                        end_date = end_date.date()
                    
                    # Parse guest information
                    guest_info = parse_airbnb_guest_info(summary, description)
                    
                    # Check if trip already exists
                    existing_trip = Trip.query.filter_by(
                        external_reservation_id=uid,
                        calendar_id=calendar.id
                    ).first()
                    
                    if not existing_trip:
                        # Create new trip
                        trip = Trip(
                            title=summary or f"Reservation {start_date}",
                            start_date=start_date,
                            end_date=end_date,
                            max_guests=guest_info.get('guest_count', calendar.amenity.max_guests),
                            admin_id=calendar.amenity.admin_id,
                            amenity_id=calendar.amenity_id,
                            calendar_id=calendar.id,
                            external_reservation_id=uid,
                            external_guest_name=guest_info.get('name', ''),
                            external_guest_email=guest_info.get('email', ''),
                            external_guest_count=guest_info.get('guest_count'),
                            external_synced_at=datetime.utcnow(),
                            is_externally_synced=True,
                            external_confirm_code=str(uuid.uuid4())[:8]
                        )
                        
                        db.session.add(trip)
                        synced_count += 1
                    else:
                        # Update existing trip
                        existing_trip.title = summary or existing_trip.title
                        existing_trip.start_date = start_date
                        existing_trip.end_date = end_date
                        existing_trip.max_guests = guest_info.get('guest_count', existing_trip.max_guests)
                        existing_trip.external_guest_name = guest_info.get('name', existing_trip.external_guest_name)
                        existing_trip.external_guest_email = guest_info.get('email', existing_trip.external_guest_email)
                        existing_trip.external_guest_count = guest_info.get('guest_count', existing_trip.external_guest_count)
                        existing_trip.external_synced_at = datetime.utcnow()
                
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