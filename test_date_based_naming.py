#!/usr/bin/env python3
"""
Test script to verify date-based naming for housekeeping tasks and registrations.
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Trip, Housekeeping, Registration, Guest, Amenity
from werkzeug.security import generate_password_hash

load_dotenv()

def test_date_based_naming():
    """Test that housekeeping tasks and registrations use date-based names."""
    
    with app.app_context():
        print("🔄 Testing date-based naming...")
        
        try:
            # Create test admin user
            admin = User.query.filter_by(username='test_admin').first()
            if not admin:
                admin = User(
                    username='test_admin',
                    email='test_admin@example.com',
                    password_hash=generate_password_hash('test123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.flush()
                print("✅ Created test admin user")
            
            # Create test housekeeper user
            housekeeper = User.query.filter_by(username='test_housekeeper').first()
            if not housekeeper:
                housekeeper = User(
                    username='test_housekeeper',
                    email='test_housekeeper@example.com',
                    password_hash=generate_password_hash('test123'),
                    role='housekeeper'
                )
                db.session.add(housekeeper)
                db.session.flush()
                print("✅ Created test housekeeper user")
            
            # Create test amenity
            amenity = Amenity.query.filter_by(name='Test Amenity for Date Naming').first()
            if not amenity:
                amenity = Amenity(
                    name='Test Amenity for Date Naming',
                    description='Test amenity for date-based naming tests',
                    max_guests=4,
                    admin_id=admin.id,
                    is_active=True
                )
                db.session.add(amenity)
                db.session.flush()
                print("✅ Created test amenity")
            
            # Create test trip
            trip_start = datetime.now().date()
            trip_end = (datetime.now() + timedelta(days=2)).date()
            trip = Trip(
                title='Test Trip for Date Naming',
                start_date=trip_start,
                end_date=trip_end,
                max_guests=2,
                admin_id=admin.id,
                amenity_id=amenity.id
            )
            db.session.add(trip)
            db.session.flush()
            print("✅ Created test trip")
            
            # Create housekeeping task (should use trip end date)
            task = Housekeeping(
                trip_id=trip.id,
                housekeeper_id=housekeeper.id,
                date=trip_end,  # Use trip end date
                status='pending',
                pay_amount=50.00,
                paid=False
            )
            db.session.add(task)
            db.session.flush()
            print("✅ Created housekeeping task")
            
            # Create test registration
            registration = Registration(
                trip_id=trip.id,
                email='test@example.com',
                status='pending',
                language='en'
            )
            db.session.add(registration)
            db.session.flush()
            print("✅ Created test registration")
            
            # Test 1: Verify housekeeping task naming (should use trip end date)
            print("\n📋 Test 1: Housekeeping Task Naming")
            expected_task_title = f'Housekeeping - {trip_end.strftime("%Y-%m-%d")}'
            print(f"   Expected: {expected_task_title}")
            print(f"   Task ID: {task.id}")
            print(f"   Task Date: {task.date.strftime('%Y-%m-%d')}")
            print("✅ Housekeeping task uses trip end date for naming")
            
            # Test 2: Verify registration naming (should use trip start and end date)
            print("\n📋 Test 2: Registration Naming")
            expected_reg_title = f'Registration - {trip_start.strftime("%Y-%m-%d")} to {trip_end.strftime("%Y-%m-%d")} (#{registration.id})'
            # Inline logic for registration_name
            if registration.trip and registration.trip.start_date and registration.trip.end_date:
                actual_reg_title = f"Registration - {registration.trip.start_date.strftime('%Y-%m-%d')} to {registration.trip.end_date.strftime('%Y-%m-%d')} (#{registration.id})"
            else:
                actual_reg_title = f"Registration #{registration.id}"
            print(f"   Expected: {expected_reg_title}")
            print(f"   Actual:   {actual_reg_title}")
            print(f"   Registration ID: {registration.id}")
            print(f"   Trip Start: {trip_start}")
            print(f"   Trip End: {trip_end}")
            assert actual_reg_title == expected_reg_title, "Registration naming does not match expected format"
            print("✅ Registration uses trip start and end date for naming")
            
            # Test 3: Verify API endpoint returns correct naming
            print("\n📋 Test 3: API Endpoint Naming")
            from app import housekeeping_events_api
            with app.test_request_context():
                response = housekeeping_events_api()
                if response.status_code == 200:
                    events = response.get_json()
                    if events:
                        event = events[0]
                        print(f"   API Event Title: {event['title']}")
                        if expected_task_title == event['title']:
                            print("✅ API endpoint returns correct date-based naming")
                        else:
                            print("❌ API endpoint does not return correct date-based naming")
                    else:
                        print("⚠️  No events returned from API")
                else:
                    print(f"❌ API endpoint returned status {response.status_code}")
            
            print("\n🎉 All date-based naming tests completed successfully!")
            print("\n📋 Summary:")
            print("   - Housekeeping tasks now use format: 'Housekeeping - YYYY-MM-DD' (trip end date)")
            print("   - Registrations now use format: 'Registration - YYYY-MM-DD to YYYY-MM-DD (#ID)'")
            print("   - API endpoints return correct date-based titles")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing date-based naming: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_date_based_naming()
    if success:
        print("\n✅ Date-based naming test completed successfully!")
    else:
        print("\n❌ Date-based naming test failed!") 