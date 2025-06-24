#!/usr/bin/env python3
"""
Test data seeder for the Guest Registration System
"""

import os
import sys
from datetime import datetime, timedelta
from test_config import TestConfig

def seed_test_data():
    """Seed comprehensive test data"""
    print("🌱 Seeding Test Data")
    print("=" * 50)
    
    # Set up test environment
    TestConfig.setup_test_environment()
    
    try:
        # Import after environment setup
        from app import app
        from database import db, User, Trip, Registration, Guest, Invoice, InvoiceItem
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Clear existing data
            print("🧹 Clearing existing test data...")
            db.session.query(InvoiceItem).delete()
            db.session.query(Invoice).delete()
            db.session.query(Guest).delete()
            db.session.query(Registration).delete()
            db.session.query(Trip).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            # Create test admin user
            print("👤 Creating test admin user...")
            admin = User(
                username=TestConfig.TEST_ADMIN_USERNAME,
                email=TestConfig.TEST_ADMIN_EMAIL,
                password_hash=generate_password_hash(TestConfig.TEST_ADMIN_PASSWORD),
                role='admin',
                photo_required_adults=True,
                photo_required_children=True,
                date_format='d.m.Y'
            )
            db.session.add(admin)
            db.session.flush()
            
            # Create test trips
            print(f"✈️ Creating {TestConfig.TEST_TRIP_COUNT} test trips...")
            trip_titles = [
                "Mountain Retreat - Test Trip 1",
                "Beach House - Test Trip 2", 
                "City Apartment - Test Trip 3",
                "Country Villa - Test Trip 4",
                "Lakeside Cabin - Test Trip 5"
            ]
            
            trips = []
            for i in range(TestConfig.TEST_TRIP_COUNT):
                start_date = datetime.now().date() + timedelta(days=i*7)
                end_date = start_date + timedelta(days=3)
                
                trip = Trip(
                    title=trip_titles[i],
                    start_date=start_date,
                    end_date=end_date,
                    max_guests=4,
                    admin_id=admin.id,
                    external_confirm_code=f'HMTEST{i+1:02d}',
                    amenity_id=1,
                    calendar_id=1
                )
                db.session.add(trip)
                trips.append(trip)
            
            db.session.flush()
            
            # Create test registrations and guests
            print(f"📝 Creating {TestConfig.TEST_REGISTRATION_COUNT} test registrations...")
            guest_names = [
                ("John", "Smith"), ("Jane", "Doe"), ("Bob", "Wilson"),
                ("Alice", "Johnson"), ("Charlie", "Brown"), ("Diana", "Prince"),
                ("Edward", "Norton"), ("Fiona", "Apple"), ("George", "Clooney"),
                ("Helen", "Mirren"), ("Ian", "McKellen"), ("Julia", "Roberts"),
                ("Kevin", "Spacey"), ("Laura", "Linney"), ("Michael", "Douglas"),
                ("Natalie", "Portman"), ("Oscar", "Isaac"), ("Penelope", "Cruz"),
                ("Quentin", "Tarantino"), ("Rachel", "Weisz")
            ]
            
            statuses = ['pending', 'approved', 'rejected']
            languages = ['en', 'cs', 'sk']
            
            for i in range(TestConfig.TEST_REGISTRATION_COUNT):
                # Create registration
                registration = Registration(
                    trip_id=trips[i % len(trips)].id,
                    email=f"guest{i+1}@test.com",
                    status=statuses[i % len(statuses)],
                    language=languages[i % len(languages)],
                    created_at=datetime.now() - timedelta(days=i)
                )
                db.session.add(registration)
                db.session.flush()
                
                # Create guests for this registration
                guest_count = (i % 3) + 1  # 1-3 guests per registration
                for j in range(guest_count):
                    guest_idx = (i + j) % len(guest_names)
                    first_name, last_name = guest_names[guest_idx]
                    
                    guest = Guest(
                        registration_id=registration.id,
                        first_name=first_name,
                        last_name=last_name,
                        age_category='adult' if j == 0 else 'child',
                        document_type='passport',
                        document_number=f'TEST{i+1:03d}{j+1:02d}',
                        gdpr_consent=True
                    )
                    db.session.add(guest)
            
            # Create test invoices
            print(f"💰 Creating {TestConfig.TEST_INVOICE_COUNT} test invoices...")
            client_names = [
                "Test Client 1", "Test Client 2", "Test Client 3",
                "Test Client 4", "Test Client 5", "Test Client 6",
                "Test Client 7", "Test Client 8"
            ]
            
            for i in range(TestConfig.TEST_INVOICE_COUNT):
                # Get a registration for this invoice
                registration = db.session.query(Registration).offset(i % TestConfig.TEST_REGISTRATION_COUNT).first()
                
                invoice = Invoice(
                    invoice_number=f"INV-TEST-{i+1:03d}",
                    admin_id=admin.id,
                    registration_id=registration.id if registration else None,
                    client_name=client_names[i],
                    client_email=f"client{i+1}@test.com",
                    client_vat_number=f"CZ{i+1:06d}",
                    client_address=f"Test Address {i+1}, Test City",
                    issue_date=datetime.now().date() - timedelta(days=i*2),
                    due_date=datetime.now().date() + timedelta(days=30),
                    subtotal=100.0 + (i * 50),
                    vat_rate=21.0,
                    vat_amount=21.0 + (i * 10.5),
                    total=121.0 + (i * 60.5),
                    currency='EUR',
                    status='draft' if i % 2 == 0 else 'sent',
                    notes=f"Test invoice {i+1} notes"
                )
                db.session.add(invoice)
                db.session.flush()
                
                # Create invoice items
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=f"Test Service {i+1}",
                    quantity=1,
                    unit_price=100.0 + (i * 50),
                    total=100.0 + (i * 50)
                )
                db.session.add(item)
            
            # Commit all changes
            db.session.commit()
            
            # Print summary
            print("\n📊 Test Data Summary:")
            print(f"   👤 Admin users: {db.session.query(User).count()}")
            print(f"   ✈️ Trips: {db.session.query(Trip).count()}")
            print(f"   📝 Registrations: {db.session.query(Registration).count()}")
            print(f"   👥 Guests: {db.session.query(Guest).count()}")
            print(f"   💰 Invoices: {db.session.query(Invoice).count()}")
            print(f"   📋 Invoice items: {db.session.query(InvoiceItem).count()}")
            
            print(f"\n🔑 Test Admin Credentials:")
            print(f"   Username: {TestConfig.TEST_ADMIN_USERNAME}")
            print(f"   Password: {TestConfig.TEST_ADMIN_PASSWORD}")
            print(f"   Email: {TestConfig.TEST_ADMIN_EMAIL}")
            
            print(f"\n🌐 Test Server URL: {TestConfig.TEST_SERVER_URL}")
            print(f"🗄️ Test Database: {TestConfig.TEST_DATABASE_NAME}")
            print(f"📁 Test Table Prefix: {TestConfig.TEST_TABLE_PREFIX}")
            
            print("\n✅ Test data seeded successfully!")
            
    except Exception as e:
        print(f"❌ Error seeding test data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def clear_test_data():
    """Clear all test data"""
    print("🧹 Clearing Test Data")
    print("=" * 50)
    
    TestConfig.setup_test_environment()
    
    try:
        from app import app
        from database import db, User, Trip, Registration, Guest, Invoice, InvoiceItem
        
        with app.app_context():
            db.session.query(InvoiceItem).delete()
            db.session.query(Invoice).delete()
            db.session.query(Guest).delete()
            db.session.query(Registration).delete()
            db.session.query(Trip).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            print("✅ Test data cleared successfully!")
            
    except Exception as e:
        print(f"❌ Error clearing test data: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_test_data()
    else:
        seed_test_data() 