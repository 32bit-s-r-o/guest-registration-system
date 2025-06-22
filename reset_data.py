#!/usr/bin/env python3
"""
Reset and Seed Data Script for Guest Registration System
This script allows you to reset all data and optionally seed with sample data.
"""

import os
import sys
from datetime import datetime, timedelta
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
    """Reset all data in the database."""
    print("\n=== Resetting All Data ===")
    
    try:
        with app.app_context():
            # Get table names for display
            tables = get_table_names()
            
            # Drop all tables
            db.drop_all()
            print("✅ All tables dropped successfully")
            print(f"   Tables removed: {', '.join(tables.values())}")
            
            # Recreate all tables
            db.create_all()
            print("✅ All tables recreated successfully")
            print(f"   Tables created: {', '.join(tables.values())}")
            
            return True
    except Exception as e:
        print(f"❌ Error resetting data: {e}")
        return False

def create_sample_admin():
    """Create a sample admin user."""
    print("\n=== Creating Sample Admin ===")
    
    try:
        with app.app_context():
            # Check if admin already exists
            existing_admin = Admin.query.filter_by(username='admin').first()
            if existing_admin:
                print("Admin user 'admin' already exists!")
                return True
            
            # Create sample admin
            admin = Admin(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Sample admin created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Email: admin@example.com")
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
                admin_id=admin.id
            )
            db.session.add(trip1)
            
            # Sample trip 2: Mountain Retreat
            trip2 = Trip(
                title="Mountain Retreat Weekend",
                start_date=datetime.now().date() + timedelta(days=14),
                end_date=datetime.now().date() + timedelta(days=16),
                max_guests=4,
                admin_id=admin.id
            )
            db.session.add(trip2)
            
            # Sample trip 3: City Break
            trip3 = Trip(
                title="City Break Adventure",
                start_date=datetime.now().date() + timedelta(days=60),
                end_date=datetime.now().date() + timedelta(days=65),
                max_guests=8,
                admin_id=admin.id
            )
            db.session.add(trip3)
            
            db.session.commit()
            print("✅ Sample trips created successfully!")
            print(f"   - {trip1.title} (ID: {trip1.id})")
            print(f"   - {trip2.title} (ID: {trip2.id})")
            print(f"   - {trip3.title} (ID: {trip3.id})")
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
                gdpr_consent=True
            )
            db.session.add(guest1_1)
            
            guest1_2 = Guest(
                registration_id=reg1.id,
                first_name='Jane',
                last_name='Doe',
                document_type='driving_license',
                document_number='DL9876543',
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
                gdpr_consent=True
            )
            db.session.add(guest2_1)
            
            guest2_2 = Guest(
                registration_id=reg2.id,
                first_name='Bob',
                last_name='Smith',
                document_type='passport',
                document_number='CD9876543',
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
                gdpr_consent=True
            )
            db.session.add(guest3_1)
            
            db.session.commit()
            print("✅ Sample registrations created successfully!")
            print(f"   - Approved registration: {reg1.email} ({len(reg1.guests)} guests)")
            print(f"   - Pending registration: {reg2.email} ({len(reg2.guests)} guests)")
            print(f"   - Rejected registration: {reg3.email} ({len(reg3.guests)} guests)")
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
                    print(f"   - {trip.title}: http://localhost:5000/register/{trip.id}")
            
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

def main():
    """Main function to handle reset and seed operations."""
    print("🔄 Guest Registration System - Data Reset & Seed Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python reset_data.py reset          # Reset all data")
        print("  python reset_data.py seed           # Seed with sample data")
        print("  python reset_data.py reset-seed     # Reset and seed")
        print("  python reset_data.py stats          # Show database statistics")
        print("  python reset_data.py tables         # Show table structure")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'reset':
        if not reset_all_data():
            sys.exit(1)
        print("\n✅ Data reset completed successfully!")
        
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
        print("\n✅ Data reset and seeding completed successfully!")
        
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