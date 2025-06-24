from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime, timedelta
import os
import tempfile
import zipfile
import shutil
import subprocess
import re
from io import BytesIO

admin = Blueprint('admin', __name__)

from app import app, db, User, Trip, Registration, Invoice, Amenity, Calendar, migration_manager, version_manager, check_version_compatibility, get_version_changelog

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                from app import login_manager
                return login_manager.unauthorized()
            if current_user.role != role:
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@admin.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    pending_registrations = Registration.query.filter_by(status='pending').count()
    
    # Get all registrations for this admin
    registrations = Registration.query.join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Get all invoices for this admin
    invoices = Invoice.query.filter_by(admin_id=current_user.id).all()
    
    # Get calendars for all amenities owned by this admin
    amenities = Amenity.query.filter_by(admin_id=current_user.id).all()
    calendars = []
    for amenity in amenities:
        calendars.extend(amenity.calendars)
    
    return render_template('admin/dashboard.html', 
                         trips=trips, 
                         pending_registrations=pending_registrations,
                         registrations=registrations,
                         invoices=invoices,
                         calendars=calendars)

@admin.route('/admin/settings', methods=['GET', 'POST'])
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
        
        # Update date format setting
        current_user.date_format = request.form.get('date_format', 'd.m.Y')
        # Update default housekeeper pay
        try:
            current_user.default_housekeeper_pay = float(request.form.get('default_housekeeper_pay', 20))
        except Exception:
            current_user.default_housekeeper_pay = 20
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
        
        db.session.commit()
        flash(_('Settings updated successfully!'), 'success')
        return redirect(url_for('admin.admin_settings'))
    
    # Get calendars for all amenities owned by this admin
    amenities = Amenity.query.filter_by(admin_id=current_user.id).all()
    calendars = []
    for amenity in amenities:
        calendars.extend(amenity.calendars)
    
    return render_template('admin/settings.html', calendars=calendars)

@admin.route('/admin/sync-airbnb', methods=['POST'])
@login_required
def sync_airbnb():
    """Sync with all calendars for the current admin."""
    from app import sync_all_calendars_for_admin
    result = sync_all_calendars_for_admin(current_user.id)
    
    if result['success']:
        flash(_('Calendar sync successful: %(message)s', message=result['message']), 'success')
    else:
        flash(_('Calendar sync failed: %(message)s', message=result['message']), 'error')
    
    return redirect(url_for('trips.admin_trips'))

@admin.route('/admin/sync-calendar/<int:calendar_id>', methods=['POST'])
@login_required
def sync_calendar(calendar_id):
    """Sync with a specific calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    from app import sync_calendar_reservations
    result = sync_calendar_reservations(calendar_id)
    
    if result['success']:
        flash(_('Calendar sync successful for %(calendar)s: %(message)s', 
                calendar=calendar.name, message=result['message']), 'success')
    else:
        flash(_('Calendar sync failed for %(calendar)s: %(message)s', 
                calendar=calendar.name, message=result['message']), 'error')
    
    return redirect(url_for('amenities.admin_amenities'))

@admin.route('/admin/data-management')
@login_required
def data_management():
    """Data management page for admins."""
    # Get database statistics
    admin_count = User.query.count()
    trip_count = Trip.query.count()
    registration_count = Registration.query.count()
    from app import Guest
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

@admin.route('/admin/reset-data', methods=['POST'])
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
        from app import InvoiceItem
        InvoiceItem.query.delete()
        print("✅ Deleted invoice items")
        
        # 2. Delete invoices (references registrations)
        Invoice.query.delete()
        print("✅ Deleted invoices")
        
        # 3. Delete guests (references registrations)
        from app import Guest
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
    
    return redirect(url_for('admin.data_management'))

@admin.route('/admin/seed-data', methods=['POST'])
@login_required
def seed_data():
    """Seed the database with sample data. Only real reservations are seeded. 'Not Available' or blocked events are intentionally excluded to match Airbnb sync logic."""
    try:
        # Create sample admin if not exists
        existing_admin = User.query.filter_by(username='admin').first()
        if not existing_admin:
            from werkzeug.security import generate_password_hash
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
                    from app import copy_sample_image
                    image_filename = copy_sample_image(guest_data['image'])
                
                from app import Guest
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
            from app import InvoiceItem
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
    
    return redirect(url_for('admin.data_management'))

@admin.route('/admin/seed-reset', methods=['POST'])
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
        from app import Guest
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
            from werkzeug.security import generate_password_hash
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
                    from app import copy_sample_image
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
    
    return redirect(url_for('admin.data_management'))

@admin.route('/admin/migrations')
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

@admin.route('/admin/migrations/run', methods=['POST'])
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
    
    return redirect(url_for('admin.admin_migrations'))

@admin.route('/admin/migrations/rollback/<version>', methods=['POST'])
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
        
        return redirect(url_for('admin.admin_migrations'))
        
    except Exception as e:
        flash(_('Rollback error: %(error)s', error=str(e)), 'error')
        return redirect(url_for('admin.admin_migrations'))

@admin.route('/admin/backup', methods=['GET'])
@login_required
@role_required('admin')
def admin_system_backup():
    """Create a system backup (DB dump + uploads, no guest photos) as a ZIP download."""
    # Prepare temp directory
    tmpdir = tempfile.mkdtemp()
    db_dump_path = os.path.join(tmpdir, 'db_backup.sql')
    uploads_dir = app.config['UPLOAD_FOLDER']
    backup_zip_path = os.path.join(tmpdir, f'system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')

    # Parse DB URL
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