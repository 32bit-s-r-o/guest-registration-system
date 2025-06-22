from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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

load_dotenv()

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
class Admin(UserMixin, db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}admin"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Airbnb settings
    airbnb_listing_id = db.Column(db.String(100))
    airbnb_calendar_url = db.Column(db.Text)
    airbnb_sync_enabled = db.Column(db.Boolean, default=False)
    airbnb_last_sync = db.Column(db.DateTime)
    # Contact information
    company_name = db.Column(db.String(200))
    company_ico = db.Column(db.String(50))  # Company identification number
    company_vat = db.Column(db.String(50))  # VAT number
    contact_name = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    contact_address = db.Column(db.Text)
    contact_website = db.Column(db.String(200))
    contact_description = db.Column(db.Text)
    # Additional custom lines (for future use)
    custom_line_1 = db.Column(db.String(200))
    custom_line_2 = db.Column(db.String(200))
    custom_line_3 = db.Column(db.String(200))

class Trip(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}trip"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}admin.id'), nullable=False)
    registrations = db.relationship('Registration', backref='trip', lazy=True)
    # Airbnb sync fields
    airbnb_reservation_id = db.Column(db.String(100), unique=True)
    airbnb_guest_name = db.Column(db.String(200))
    airbnb_guest_email = db.Column(db.String(200))
    airbnb_guest_count = db.Column(db.Integer)
    airbnb_synced_at = db.Column(db.DateTime)
    is_airbnb_synced = db.Column(db.Boolean, default=False)
    # Airbnb confirmation code
    airbnb_confirm_code = db.Column(db.String(50), unique=True)

class Registration(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}registration"
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}trip.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    guests = db.relationship('Guest', backref='registration', lazy=True, cascade='all, delete-orphan')

class Guest(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}guest"
    
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}registration.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # passport, driving_license, citizen_id
    document_number = db.Column(db.String(100), nullable=False)
    document_image = db.Column(db.String(255))  # File path to uploaded image
    gdpr_consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = f"{app.config['TABLE_PREFIX']}invoice"
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey(f'{app.config["TABLE_PREFIX"]}admin.id'), nullable=False)
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
    admin = db.relationship('Admin', backref='invoices')
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

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

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
    
    # Try to extract confirmation code
    # Common patterns: "Confirmation code: ABC123" or "Code: ABC123" or "ABC123"
    confirm_patterns = [
        r'confirmation\s+code:\s*([A-Z0-9]{6,})',
        r'code:\s*([A-Z0-9]{6,})',
        r'\b([A-Z0-9]{6,})\b'
    ]
    
    for pattern in confirm_patterns:
        match = re.search(pattern, summary + ' ' + description, re.IGNORECASE)
        if match:
            guest_info['confirm_code'] = match.group(1).upper()
            break
    
    return guest_info

def sync_airbnb_reservations(admin_id):
    """Sync Airbnb reservations with local trips."""
    admin = Admin.query.get(admin_id)
    if not admin or not admin.airbnb_calendar_url or not admin.airbnb_sync_enabled:
        return {'success': False, 'message': 'Airbnb sync not configured'}
    
    try:
        reservations = fetch_airbnb_calendar(admin.airbnb_calendar_url)
        synced_count = 0
        updated_count = 0
        
        for reservation in reservations:
            # Check if trip already exists
            existing_trip = Trip.query.filter_by(
                airbnb_reservation_id=reservation['id'],
                admin_id=admin_id
            ).first()
            
            if existing_trip:
                # Update existing trip
                existing_trip.title = reservation['title']
                existing_trip.start_date = reservation['start_date']
                existing_trip.end_date = reservation['end_date']
                existing_trip.max_guests = reservation['guest_count']
                existing_trip.airbnb_guest_name = reservation['guest_name']
                existing_trip.airbnb_guest_email = reservation['guest_email']
                existing_trip.airbnb_confirm_code = reservation['confirm_code']
                existing_trip.airbnb_synced_at = datetime.utcnow()
                updated_count += 1
            else:
                # Create new trip
                new_trip = Trip(
                    title=reservation['title'],
                    start_date=reservation['start_date'],
                    end_date=reservation['end_date'],
                    max_guests=reservation['guest_count'],
                    admin_id=admin_id,
                    airbnb_reservation_id=reservation['id'],
                    airbnb_guest_name=reservation['guest_name'],
                    airbnb_guest_email=reservation['guest_email'],
                    airbnb_guest_count=reservation['guest_count'],
                    airbnb_confirm_code=reservation['confirm_code'],
                    airbnb_synced_at=datetime.utcnow(),
                    is_airbnb_synced=True
                )
                db.session.add(new_trip)
                synced_count += 1
        
        # Update admin sync timestamp
        admin.airbnb_last_sync = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Synced {synced_count} new reservations, updated {updated_count} existing',
            'synced': synced_count,
            'updated': updated_count
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Error syncing: {str(e)}'}

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
    # Get the first admin's contact information
    admin_contact = Admin.query.first()
    
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # For now, just show a success message
        # In a real application, you would send an email here
        flash(f'Thank you for your message, {name}! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', admin_contact=admin_contact)

@app.route('/gdpr')
def gdpr():
    admin_contact = Admin.query.first()
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
        flash('Please enter a confirmation code', 'error')
        return redirect(url_for('register_landing'))
    
    # Find trip by confirmation code
    trip = Trip.query.filter_by(airbnb_confirm_code=confirm_code).first()
    
    if not trip:
        flash('Invalid confirmation code. Please check your code and try again.', 'error')
        return redirect(url_for('register_landing'))
    
    # Redirect to the registration form with confirmation code
    return redirect(url_for('register_by_code', confirm_code=confirm_code))

@app.route('/register/id/<int:trip_id>')
def register(trip_id):
    """Registration using trip ID."""
    trip = Trip.query.get_or_404(trip_id)
    return render_template('register.html', trip=trip)

@app.route('/register/<confirm_code>')
def register_by_code(confirm_code):
    """Registration using confirmation code in URL."""
    # Try to find by confirmation code
    trip = Trip.query.filter_by(airbnb_confirm_code=confirm_code.upper()).first()
    
    if trip:
        return render_template('register.html', trip=trip)
    
    # If not found by confirmation code, redirect to landing page
    flash('Invalid confirmation code. Please check your code and try again.', 'error')
    return redirect(url_for('register_landing'))

@app.route('/register/id/<int:trip_id>', methods=['POST'])
def submit_registration(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    # Get form data
    email = request.form.get('email')
    guests_data = []
    
    # Collect guest data
    for i in range(trip.max_guests):
        first_name = request.form.get(f'first_name_{i}')
        last_name = request.form.get(f'last_name_{i}')
        document_type = request.form.get(f'document_type_{i}')
        document_number = request.form.get(f'document_number_{i}')
        gdpr_consent = request.form.get(f'gdpr_consent_{i}') == 'on'
        
        if first_name and last_name:  # Only add if guest data is provided
            guests_data.append({
                'first_name': first_name,
                'last_name': last_name,
                'document_type': document_type,
                'document_number': document_number,
                'gdpr_consent': gdpr_consent
            })
    
    # Handle file uploads
    files = request.files.getlist('document_images')
    uploaded_files = []
    
    for file in files:
        if file and file.filename:
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(filename)
    
    # Handle invoice request
    invoice_request = request.form.get('request_invoice') == 'on'
    invoice_data = None
    
    if invoice_request:
        invoice_data = {
            'company_name': request.form.get('invoice_company_name'),
            'vat_number': request.form.get('invoice_vat_number'),
            'address': request.form.get('invoice_address'),
            'currency': request.form.get('invoice_currency', 'EUR'),
            'notes': request.form.get('invoice_notes')
        }
    
    # Store in session for confirmation
    session['registration_data'] = {
        'trip_id': trip_id,
        'email': email,
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
        email=data['email']
    )
    db.session.add(registration)
    db.session.flush()  # Get the registration ID
    
    # Create guests
    for i, guest_data in enumerate(data['guests']):
        guest = Guest(
            registration_id=registration.id,
            first_name=guest_data['first_name'],
            last_name=guest_data['last_name'],
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
        client_name = data['invoice_data']['company_name'] if data['invoice_data']['company_name'] else f"{data['guests'][0]['first_name']} {data['guests'][0]['last_name']}"
        
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
    
    flash('Registration submitted successfully! You will receive an email once it is reviewed.', 'success')
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
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    pending_registrations = Registration.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html', trips=trips, pending_registrations=pending_registrations)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
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
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html')

@app.route('/admin/sync-airbnb', methods=['POST'])
@login_required
def sync_airbnb():
    """Sync with Airbnb calendar."""
    result = sync_airbnb_reservations(current_user.id)
    
    if result['success']:
        flash(f"Airbnb sync successful: {result['message']}", 'success')
    else:
        flash(f"Airbnb sync failed: {result['message']}", 'error')
    
    return redirect(url_for('admin_trips'))

@app.route('/admin/trips')
@login_required
def admin_trips():
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    return render_template('admin/trips.html', trips=trips)

@app.route('/admin/trips/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    if request.method == 'POST':
        trip = Trip(
            title=request.form.get('title'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            max_guests=int(request.form.get('max_guests')),
            admin_id=current_user.id
        )
        db.session.add(trip)
        db.session.commit()
        flash('Trip created successfully!', 'success')
        return redirect(url_for('admin_trips'))
    
    return render_template('admin/new_trip.html')

@app.route('/admin/registrations')
@login_required
def admin_registrations():
    registrations = Registration.query.filter_by(status='pending').all()
    return render_template('admin/registrations.html', registrations=registrations)

@app.route('/admin/registration/<int:registration_id>')
@login_required
def view_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    return render_template('admin/view_registration.html', registration=registration)

@app.route('/admin/registration/<int:registration_id>/approve', methods=['POST'])
@login_required
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
    
    flash('Registration approved and email sent to user', 'success')
    return redirect(url_for('admin_registrations'))

@app.route('/admin/registration/<int:registration_id>/reject', methods=['POST'])
@login_required
def reject_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    registration.status = 'rejected'
    registration.admin_comment = request.form.get('comment')
    registration.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Send rejection email
    send_rejection_email(registration)
    
    flash('Registration rejected and email sent to user', 'success')
    return redirect(url_for('admin_registrations'))

# Invoice Management Routes
@app.route('/admin/invoices')
@login_required
def admin_invoices():
    """Admin invoices list page."""
    invoices = Invoice.query.filter_by(admin_id=current_user.id).order_by(Invoice.created_at.desc()).all()
    return render_template('admin/invoices.html', invoices=invoices)

@app.route('/admin/invoices/new', methods=['GET', 'POST'])
@login_required
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
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice.id))
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/new_invoice.html', today=today)

@app.route('/admin/invoices/<int:invoice_id>')
@login_required
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
        flash('Invoice updated successfully!', 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice.id))
    
    return render_template('admin/edit_invoice.html', invoice=invoice)

@app.route('/admin/invoices/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    """Delete an invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    db.session.delete(invoice)
    db.session.commit()
    flash('Invoice deleted successfully!', 'success')
    return redirect(url_for('admin_invoices'))

# Data management routes
@app.route('/admin/data-management')
@login_required
def data_management():
    """Data management page for admins."""
    # Get database statistics
    admin_count = Admin.query.count()
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
            f"{table_prefix}guest"
        ]
        
        print(f"Starting database reset for tables: {', '.join(tables_to_reset)}")
        print(f"Preserving admin table: {table_prefix}admin")
        
        # Delete data from specific tables instead of dropping all
        Guest.query.delete()
        Registration.query.delete()
        Trip.query.delete()
        
        # Commit the deletions
        db.session.commit()
        
        print("Data deleted successfully from trips, registrations, and guests tables")
        print("Admin accounts preserved")
        
        flash('All data has been reset successfully! Admin accounts have been preserved.', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during reset: {str(e)}")
        flash(f'Error resetting data: {str(e)}. Please use the command line tool: python quick_reset.py --confirm', 'error')
    
    return redirect(url_for('data_management'))

@app.route('/admin/seed-data', methods=['POST'])
@login_required
def seed_data():
    """Seed the database with sample data."""
    try:
        # Create sample admin if not exists
        existing_admin = Admin.query.filter_by(username='admin').first()
        if not existing_admin:
            admin = Admin(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.flush()
        else:
            admin = existing_admin
        
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
                'airbnb_guest_count': 4
            },
            {
                'title': "Mountain Retreat Weekend",
                'start_date': datetime.now().date() + timedelta(days=14),
                'end_date': datetime.now().date() + timedelta(days=16),
                'max_guests': 4,
                'is_airbnb_synced': False
            },
            {
                'title': "City Break Adventure",
                'start_date': datetime.now().date() + timedelta(days=60),
                'end_date': datetime.now().date() + timedelta(days=65),
                'max_guests': 8,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Alice Johnson',
                'airbnb_guest_email': 'alice.j@example.com',
                'airbnb_guest_count': 3
            },
            {
                'title': "Winter Ski Trip",
                'start_date': datetime.now().date() + timedelta(days=90),
                'end_date': datetime.now().date() + timedelta(days=97),
                'max_guests': 5,
                'is_airbnb_synced': False
            },
            {
                'title': "Weekend Getaway",
                'start_date': datetime.now().date() + timedelta(days=7),
                'end_date': datetime.now().date() + timedelta(days=9),
                'max_guests': 3,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Bob Wilson',
                'airbnb_guest_email': 'bob.wilson@example.com',
                'airbnb_guest_count': 2
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
                airbnb_synced_at=datetime.utcnow() if trip_data.get('is_airbnb_synced') else None
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
                    document_type=guest_data['document_type'],
                    document_number=guest_data['document_number'],
                    document_image=image_filename,  # Use copied image filename
                    gdpr_consent=True
                )
                db.session.add(guest)
        
        db.session.commit()
        
        flash('Sample data has been seeded successfully! Created 5 trips and 6 registrations with various statuses. Sample document images have been copied to uploads directory.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error seeding data: {str(e)}', 'error')
    
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
        print(f"Preserving admin table: {table_prefix}admin")
        
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
        admin = Admin.query.first()
        if not admin:
            admin = Admin(
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
                'airbnb_guest_count': 4
            },
            {
                'title': "Mountain Retreat Weekend",
                'start_date': datetime.now().date() + timedelta(days=14),
                'end_date': datetime.now().date() + timedelta(days=16),
                'max_guests': 4,
                'is_airbnb_synced': False
            },
            {
                'title': "City Break Adventure",
                'start_date': datetime.now().date() + timedelta(days=60),
                'end_date': datetime.now().date() + timedelta(days=65),
                'max_guests': 8,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Alice Johnson',
                'airbnb_guest_email': 'alice.j@example.com',
                'airbnb_guest_count': 3
            },
            {
                'title': "Winter Ski Trip",
                'start_date': datetime.now().date() + timedelta(days=90),
                'end_date': datetime.now().date() + timedelta(days=97),
                'max_guests': 5,
                'is_airbnb_synced': False
            },
            {
                'title': "Weekend Getaway",
                'start_date': datetime.now().date() + timedelta(days=7),
                'end_date': datetime.now().date() + timedelta(days=9),
                'max_guests': 3,
                'is_airbnb_synced': True,
                'airbnb_guest_name': 'Bob Wilson',
                'airbnb_guest_email': 'bob.wilson@example.com',
                'airbnb_guest_count': 2
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
                airbnb_synced_at=datetime.utcnow() if trip_data.get('is_airbnb_synced') else None
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
                    document_type=guest_data['document_type'],
                    document_number=guest_data['document_number'],
                    document_image=image_filename,  # Use copied image filename
                    gdpr_consent=True
                )
                db.session.add(guest)
        
        db.session.commit()
        print("Sample data seeded successfully")
        
        flash('Database has been reset and seeded with sample data successfully! Admin accounts have been preserved. Created 5 trips and 6 registrations with various statuses. Sample document images have been copied to uploads directory.', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during reset and seed: {str(e)}")
        flash(f'Error during reset and seed: {str(e)}. Please use the command line tool: python quick_reset.py --reset-seed', 'error')
    
    return redirect(url_for('data_management'))

def send_approval_email(registration):
    try:
        msg = Message(
            'Registration Approved',
            sender=app.config['MAIL_USERNAME'],
            recipients=[registration.email]
        )
        msg.body = f"""
        Dear Guest,
        
        Your registration for {registration.trip.title} has been approved!
        
        Your personal data has been processed and all uploaded documents have been securely deleted in compliance with GDPR regulations.
        
        Thank you for choosing our service.
        
        Best regards,
        The Admin Team
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def send_rejection_email(registration):
    try:
        update_link = url_for('register', trip_id=registration.trip_id, _external=True).replace('/register/', '/register/id/')
        msg = Message(
            'Registration Update Required',
            sender=app.config['MAIL_USERNAME'],
            recipients=[registration.email]
        )
        msg.body = f"""
        Dear Guest,
        
        Your registration for {registration.trip.title} requires updates.
        
        Admin Comment: {registration.admin_comment}
        
        Please update your information using this link: {update_link}
        
        Thank you for your understanding.
        
        Best regards,
        The Admin Team
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 