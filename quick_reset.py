#!/usr/bin/env python3
"""
Quick Database Reset Script
This script provides a fast way to reset the database without the web interface.
"""

import os
import sys
import argparse
import shutil
from app import app, db, User, Trip, Registration, Guest, Invoice, InvoiceItem
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from utils import check_production_lock

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

def quick_reset():
    """Quickly reset all database tables except admin."""
    print("🔄 Quick Database Reset (Preserving Admin)")
    print("=" * 40)
    
    try:
        # Check production lock
        check_production_lock("Database reset")
        
        with app.app_context():
            # Get table prefix
            table_prefix = app.config.get('TABLE_PREFIX', 'guest_reg_')
            tables_to_reset = [
                f"{table_prefix}trip", 
                f"{table_prefix}registration",
                f"{table_prefix}guest",
                f"{table_prefix}invoice",
                f"{table_prefix}invoice_item"
            ]
            admin_table = f"{table_prefix}admin"
            
            print(f"📋 Tables to reset: {', '.join(tables_to_reset)}")
            print(f"🔒 Preserving admin table: {admin_table}")
            
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
            
            print("✅ Database reset completed successfully!")
            print(f"🗑️  Data deleted from: {', '.join(tables_to_reset)}")
            print(f"🔒 Admin accounts preserved in: {admin_table}")
            
            return True
            
    except RuntimeError as e:
        print(f"❌ Production lock prevented database reset: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        return False

def quick_seed():
    """Quickly seed the database with sample data. Only real reservations are seeded. 'Not Available' or blocked events are intentionally excluded to match Airbnb sync logic."""
    print("🌱 Quick Database Seed")
    print("=" * 30)
    
    try:
        # Check production lock
        check_production_lock("Database seeding")
        
        with app.app_context():
            # Use existing admin or create one if none exists (not deleted)
            existing_admin = User.query.filter_by(is_deleted=False).first()
            if not existing_admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.flush()
                print("👤 Created admin user: admin/admin123")
            else:
                admin = existing_admin
                print(f"👤 Using existing admin: {admin.username}")
            
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
            print(f"🏖️  Created {len(created_trips)} sample trips")
            
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
            print(f"📝 Created {len(registrations_data)} sample registrations")
            print("✅ Database seeding completed successfully!")
            print("📸 Sample document images copied to uploads directory")
            
            return True
            
    except RuntimeError as e:
        print(f"❌ Production lock prevented database seeding: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        return False

def quick_reset_seed():
    """Quickly reset and seed the database."""
    print("🔄 Quick Database Reset and Seed")
    print("=" * 40)
    
    if quick_reset():
        print("\n" + "=" * 40)
        quick_seed()
    else:
        print("❌ Reset failed, skipping seed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python quick_reset.py --confirm     # Reset all data")
        print("  python quick_reset.py --seed        # Seed sample data")
        print("  python quick_reset.py --reset-seed  # Reset and seed")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--confirm":
        quick_reset()
    elif command == "--seed":
        quick_seed()
    elif command == "--reset-seed":
        quick_reset_seed()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: --confirm, --seed, --reset-seed")
        sys.exit(1) 