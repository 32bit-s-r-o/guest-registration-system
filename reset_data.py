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
from app import app, db, Admin, Trip, Registration, Guest

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
            
            # Delete data from specific tables instead of dropping all
            Guest.query.delete()
            Registration.query.delete()
            Trip.query.delete()
            
            # Commit the deletions
            db.session.commit()
            
            print("✅ Data deleted successfully from trips, registrations, and guests tables")
            print(f"   Tables reset: {tables['trip']}, {tables['registration']}, {tables['guest']}")
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
            # Check if any admin exists
            existing_admin = Admin.query.first()
            if existing_admin:
                print(f"✅ Using existing admin: {existing_admin.username}")
                return True
            
            # Create sample admin if none exists
            admin = Admin(
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
                custom_line_3='License: VR-12345'
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
            admin = Admin.query.filter_by(username='admin').first()
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
            
            admin_count = Admin.query.count()
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
    """Seed the database with sample data."""
    print("🌱 Seeding database with sample data...")
    
    # Create sample trips
    trips_data = [
        {
            'title': 'Weekend Getaway',
            'start_date': date.today() + timedelta(days=7),
            'end_date': date.today() + timedelta(days=9),
            'max_guests': 4,
            'airbnb_confirm_code': 'ABC123'
        },
        {
            'title': 'Summer Vacation',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=37),
            'max_guests': 6,
            'airbnb_confirm_code': 'XYZ789'
        },
        {
            'title': 'Business Trip',
            'start_date': date.today() + timedelta(days=14),
            'end_date': date.today() + timedelta(days=16),
            'max_guests': 2,
            'airbnb_confirm_code': 'DEF456'
        },
        {
            'title': 'Family Holiday',
            'start_date': date.today() + timedelta(days=60),
            'end_date': date.today() + timedelta(days=67),
            'max_guests': 8,
            'airbnb_confirm_code': 'GHI789'
        },
        {
            'title': 'Romantic Weekend',
            'start_date': date.today() + timedelta(days=21),
            'end_date': date.today() + timedelta(days=23),
            'max_guests': 2,
            'airbnb_confirm_code': 'JKL012'
        }
    ]

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
        if not create_sample_admin():
            sys.exit(1)
        if not create_sample_trips():
            sys.exit(1)
        if not create_sample_registrations():
            sys.exit(1)
        print("\n✅ Sample data seeded successfully!")
        
    elif command == 'reset-seed':
        if not reset_all_data():
            sys.exit(1)
        if not create_sample_admin():
            sys.exit(1)
        if not create_sample_trips():
            sys.exit(1)
        if not create_sample_registrations():
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