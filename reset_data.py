#!/usr/bin/env python3
"""
Reset and Seed Data Script for Guest Registration System
This script allows you to reset all data and optionally seed with sample data.
"""

import os
import sys
import shutil
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from app import app, db, User, Trip, Registration, Guest

def get_table_names():
    """Get the actual table names with prefix."""
    prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
    return {
        'admin': f"{prefix}admin",
        'trip': f"{prefix}trip", 
        'registration': f"{prefix}registration",
        'guest': f"{prefix}guest"
    }

def reset_all_data():
    """Reset all data in the database except admin accounts."""
    print("\n=== Resetting All Data (Preserving Admin) ===")
    
    try:
        with app.app_context():
            # Get table names for display
            tables = get_table_names()
            
            # Import Invoice and InvoiceItem models to handle foreign key constraints
            from app import Invoice, InvoiceItem
            
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
            
            print("✅ Data deleted successfully from all tables")
            print(f"   Tables reset: {tables['trip']}, {tables['registration']}, {tables['guest']}, invoices, invoice_items")
            print(f"   Admin preserved: {tables['admin']}")
            
            return True
    except Exception as e:
        print(f"❌ Error resetting data: {e}")
        return False

def create_sample_admin():
    """Create a sample admin user if none exists."""
    print("\n=== Creating Sample Admin ===")
    
    try:
        with app.app_context():
            # Check if any admin exists (not deleted)
            existing_admin = User.query.filter_by(is_deleted=False).first()
            if existing_admin:
                print(f"✅ Using existing admin: {existing_admin.username}")
                return True
            
            # Create sample admin if none exists
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                company_name='Guest Registration System',
                company_ico='12345678',
                company_vat='CZ12345678',
                # Sample contact information
                contact_name='John Smith',
                contact_phone='+1 (555) 123-4567',
                contact_address='123 Main Street\nAnytown, ST 12345\nUnited States',
                contact_website='https://example.com',
                contact_description='Professional vacation rental management with over 10 years of experience providing exceptional guest experiences.',
                # Custom lines
                custom_line_1='Business Hours: Mon-Fri 9AM-5PM',
                custom_line_2='Emergency Contact: +1 (555) 999-8888',
                custom_line_3='License: VR-12345',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Sample admin created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: admin@example.com")
            print("   Contact: John Smith (+1 (555) 123-4567)")
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample admin: {e}")
        return False

def create_sample_trips():
    """Create sample trips."""
    print("\n=== Creating Sample Trips ===")
    
    try:
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("❌ Admin user not found. Please create admin first.")
                return False
            
            # Sample trip 1: Summer Vacation
            trip1 = Trip(
                title="Summer Beach Vacation 2024",
                start_date=datetime.now().date() + timedelta(days=30),
                end_date=datetime.now().date() + timedelta(days=37),
                max_guests=6,
                admin_id=admin.id,
                airbnb_confirm_code='ABC123'
            )
            db.session.add(trip1)
            
            # Sample trip 2: Mountain Retreat
            trip2 = Trip(
                title="Mountain Retreat Weekend",
                start_date=datetime.now().date() + timedelta(days=14),
                end_date=datetime.now().date() + timedelta(days=16),
                max_guests=4,
                admin_id=admin.id,
                airbnb_confirm_code='XYZ789'
            )
            db.session.add(trip2)
            
            # Sample trip 3: City Break
            trip3 = Trip(
                title="City Break Adventure",
                start_date=datetime.now().date() + timedelta(days=60),
                end_date=datetime.now().date() + timedelta(days=65),
                max_guests=8,
                admin_id=admin.id,
                airbnb_confirm_code='DEF456'
            )
            db.session.add(trip3)
            
            db.session.commit()
            print("✅ Sample trips created successfully!")
            print(f"   - {trip1.title} (ID: {trip1.id}, Code: {trip1.airbnb_confirm_code})")
            print(f"   - {trip2.title} (ID: {trip2.id}, Code: {trip2.airbnb_confirm_code})")
            print(f"   - {trip3.title} (ID: {trip3.id}, Code: {trip3.airbnb_confirm_code})")
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample trips: {e}")
        return False

def create_sample_registrations():
    """Create sample registrations with guests."""
    print("\n=== Creating Sample Registrations ===")
    
    try:
        with app.app_context():
            trips = Trip.query.all()
            if not trips:
                print("❌ No trips found. Please create trips first.")
                return False
            
            # Sample registration 1: Approved
            reg1 = Registration(
                trip_id=trips[0].id,
                email='john.doe@example.com',
                status='approved',
                created_at=datetime.now() - timedelta(days=5)
            )
            db.session.add(reg1)
            db.session.flush()
            
            # Add guests for registration 1
            guest1_1 = Guest(
                registration_id=reg1.id,
                first_name='John',
                last_name='Doe',
                document_type='passport',
                document_number='AB1234567',
                document_image=copy_sample_image('passport_john_doe.jpg'),
                gdpr_consent=True
            )
            db.session.add(guest1_1)
            
            guest1_2 = Guest(
                registration_id=reg1.id,
                first_name='Jane',
                last_name='Doe',
                document_type='driving_license',
                document_number='DL9876543',
                document_image=copy_sample_image('license_jane_doe.jpg'),
                gdpr_consent=True
            )
            db.session.add(guest1_2)
            
            # Sample registration 2: Pending
            reg2 = Registration(
                trip_id=trips[1].id,
                email='alice.smith@example.com',
                status='pending',
                created_at=datetime.now() - timedelta(days=2)
            )
            db.session.add(reg2)
            db.session.flush()
            
            # Add guests for registration 2
            guest2_1 = Guest(
                registration_id=reg2.id,
                first_name='Alice',
                last_name='Smith',
                document_type='citizen_id',
                document_number='CID123456789',
                document_image=copy_sample_image('citizen_id_mike_doe.jpg'),
                gdpr_consent=True
            )
            db.session.add(guest2_1)
            
            guest2_2 = Guest(
                registration_id=reg2.id,
                first_name='Bob',
                last_name='Smith',
                document_type='passport',
                document_number='CD9876543',
                document_image=copy_sample_image('passport_alice_smith.jpg'),
                gdpr_consent=True
            )
            db.session.add(guest2_2)
            
            # Sample registration 3: Rejected
            reg3 = Registration(
                trip_id=trips[2].id,
                email='charlie.brown@example.com',
                status='rejected',
                admin_comment='Document images were unclear. Please upload clearer photos.',
                created_at=datetime.now() - timedelta(days=1),
                updated_at=datetime.now() - timedelta(hours=6)
            )
            db.session.add(reg3)
            db.session.flush()
            
            # Add guests for registration 3
            guest3_1 = Guest(
                registration_id=reg3.id,
                first_name='Charlie',
                last_name='Brown',
                document_type='driving_license',
                document_number='DL5556667',
                document_image=copy_sample_image('license_bob_smith.jpg'),
                gdpr_consent=True
            )
            db.session.add(guest3_1)
            
            db.session.commit()
            print("✅ Sample registrations created successfully!")
            print(f"   - Approved registration: {reg1.email} ({len(reg1.guests)} guests)")
            print(f"   - Pending registration: {reg2.email} ({len(reg2.guests)} guests)")
            print(f"   - Rejected registration: {reg3.email} ({len(reg3.guests)} guests)")
            print("📸 Sample document images copied to uploads directory")
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample registrations: {e}")
        return False

def show_database_stats():
    """Show current database statistics."""
    print("\n=== Database Statistics ===")
    
    try:
        with app.app_context():
            # Get table names for display
            tables = get_table_names()
            prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
            
            admin_count = User.query.count()
            trip_count = Trip.query.count()
            registration_count = Registration.query.count()
            guest_count = Guest.query.count()
            
            pending_count = Registration.query.filter_by(status='pending').count()
            approved_count = Registration.query.filter_by(status='approved').count()
            rejected_count = Registration.query.filter_by(status='rejected').count()
            
            print(f"📊 Current Database Status:")
            print(f"   Table Prefix: {prefix}")
            print(f"   Tables: {', '.join(tables.values())}")
            print(f"   - Admins: {admin_count}")
            print(f"   - Trips: {trip_count}")
            print(f"   - Registrations: {registration_count}")
            print(f"   - Guests: {guest_count}")
            print(f"   - Pending: {pending_count}")
            print(f"   - Approved: {approved_count}")
            print(f"   - Rejected: {rejected_count}")
            
            if trip_count > 0:
                print(f"\n📋 Sample Registration Links:")
                trips = Trip.query.all()
                for trip in trips:
                    print(f"   - {trip.title}:")
                    print(f"     Trip ID: http://localhost:5001/register/id/{trip.id}")
                    if trip.airbnb_confirm_code:
                        print(f"     Confirmation Code: http://localhost:5001/register/{trip.airbnb_confirm_code}")
                        print(f"     Code: {trip.airbnb_confirm_code}")
                    print()
            
            return True
            
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return False

def show_table_info():
    """Show information about table structure."""
    print("\n=== Table Structure Information ===")
    
    try:
        with app.app_context():
            tables = get_table_names()
            prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
            
            print(f"📋 Database Tables (Prefix: '{prefix}'):")
            for table_type, table_name in tables.items():
                print(f"   - {table_type}: {table_name}")
            
            print(f"\n🔗 Foreign Key Relationships:")
            print(f"   - {tables['trip']}.admin_id → {tables['admin']}.id")
            print(f"   - {tables['registration']}.trip_id → {tables['trip']}.id")
            print(f"   - {tables['guest']}.registration_id → {tables['registration']}.id")
            
            return True
            
    except Exception as e:
        print(f"❌ Error getting table info: {e}")
        return False

def copy_sample_image(image_filename):
    """Copy a sample image from static/sample_images to uploads directory."""
    # Ensure uploads directory exists
    os.makedirs('uploads', exist_ok=True)
    
    sample_image_path = os.path.join('static', 'sample_images', image_filename)
    upload_image_path = os.path.join('uploads', image_filename)
    
    if os.path.exists(sample_image_path):
        shutil.copy2(sample_image_path, upload_image_path)
        return image_filename
    else:
        print(f"Warning: Sample image not found: {sample_image_path}")
        return None

def seed_data():
    """Seed the database with sample data. Only real reservations are seeded. 'Not Available' or blocked events are intentionally excluded to match Airbnb sync logic."""
    print("🌱 Seeding database with sample data...")
    
    try:
        with app.app_context():
            # Create sample admin if not exists (not deleted)
            existing_admin = User.query.filter_by(username='admin', is_deleted=False).first()
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
                    custom_line_3='Pet Friendly Options Available',
                    role='admin'
                )
                db.session.add(admin)
                db.session.flush()
            else:
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
                        document_type=guest_data['document_type'],
                        document_number=guest_data['document_number'],
                        document_image=image_filename,  # Use copied image filename
                        gdpr_consent=True
                    )
                    db.session.add(guest)
            
            db.session.flush()
            
            # Import Invoice models for invoice creation
            from app import Invoice, InvoiceItem
            
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
            
            print("✅ Sample data has been seeded successfully!")
            print("   Created 5 trips, 7 registrations (including 1 single-person pending), 3 invoices with realistic data")
            print("   Updated admin contact information with professional details")
            print("📸 Sample document images copied to uploads directory")
            return True
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        return False

def main():
    """Main function to handle reset and seed operations."""
    print("🔄 Guest Registration System - Data Reset & Seed Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python reset_data.py reset          # Reset all data (preserves admin)")
        print("  python reset_data.py seed           # Seed with sample data")
        print("  python reset_data.py reset-seed     # Reset and seed (preserves admin)")
        print("  python reset_data.py stats          # Show database statistics")
        print("  python reset_data.py tables         # Show table structure")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'reset':
        if not reset_all_data():
            sys.exit(1)
        print("\n✅ Data reset completed successfully! Admin accounts preserved.")
        
    elif command == 'seed':
        if not seed_data():
            sys.exit(1)
        print("\n✅ Sample data seeded successfully!")
        
    elif command == 'reset-seed':
        if not reset_all_data():
            sys.exit(1)
        if not seed_data():
            sys.exit(1)
        print("\n✅ Data reset and seeding completed successfully! Admin accounts preserved.")
        
    elif command == 'stats':
        if not show_database_stats():
            sys.exit(1)
        
    elif command == 'tables':
        if not show_table_info():
            sys.exit(1)
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: reset, seed, reset-seed, stats, tables")
        sys.exit(1)
    
    if command in ['seed', 'reset-seed']:
        print("\n🎉 Setup completed! You can now:")
        print("1. Run the application: python app.py")
        print("2. Login to admin panel: http://localhost:5000/admin/login")
        print("3. Use sample admin credentials: admin / admin123")
        print("4. View sample registration links above")

if __name__ == "__main__":
    main() 