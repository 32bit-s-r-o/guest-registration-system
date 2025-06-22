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

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

# Database Models
class Admin(UserMixin, db.Model):
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

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    registrations = db.relationship('Registration', backref='trip', lazy=True)
    # Airbnb sync fields
    airbnb_reservation_id = db.Column(db.String(100), unique=True)
    airbnb_guest_name = db.Column(db.String(200))
    airbnb_guest_email = db.Column(db.String(200))
    airbnb_guest_count = db.Column(db.Integer)
    airbnb_synced_at = db.Column(db.DateTime)
    is_airbnb_synced = db.Column(db.Boolean, default=False)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    guests = db.relationship('Guest', backref='registration', lazy=True, cascade='all, delete-orphan')

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # passport, driving_license, citizen_id
    document_number = db.Column(db.String(100), nullable=False)
    document_image = db.Column(db.String(255))  # File path to uploaded image
    gdpr_consent = db.Column(db.Boolean, default=False)
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
        'count': 1
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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gdpr')
def gdpr():
    return render_template('gdpr.html')

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files (only accessible to admins)"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/register/<int:trip_id>')
def register(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    return render_template('register.html', trip=trip)

@app.route('/register/<int:trip_id>', methods=['POST'])
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
    
    # Store in session for confirmation
    session['registration_data'] = {
        'trip_id': trip_id,
        'email': email,
        'guests': guests_data,
        'uploaded_files': uploaded_files
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
    
    db.session.commit()
    
    # Clear session
    session.pop('registration_data', None)
    
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
    
    return render_template('admin/data_management.html', stats=stats)

@app.route('/admin/reset-data', methods=['POST'])
@login_required
def reset_data():
    """Reset all data in the database."""
    try:
        # Drop all tables
        db.drop_all()
        # Recreate all tables
        db.create_all()
        flash('All data has been reset successfully!', 'success')
    except Exception as e:
        flash(f'Error resetting data: {str(e)}', 'error')
    
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
        
        # Create sample trips
        trip1 = Trip(
            title="Summer Beach Vacation 2024",
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=37),
            max_guests=6,
            admin_id=admin.id
        )
        db.session.add(trip1)
        
        trip2 = Trip(
            title="Mountain Retreat Weekend",
            start_date=datetime.now().date() + timedelta(days=14),
            end_date=datetime.now().date() + timedelta(days=16),
            max_guests=4,
            admin_id=admin.id
        )
        db.session.add(trip2)
        
        db.session.commit()
        
        flash('Sample data has been seeded successfully!', 'success')
    except Exception as e:
        flash(f'Error seeding data: {str(e)}', 'error')
    
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
        update_link = url_for('register', trip_id=registration.trip_id, _external=True)
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