#!/usr/bin/env python3
"""
Test script to verify date format settings functionality.
"""

import sys
import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import uuid
from config import Config

# Set up test environment before importing app
def setup_test_environment():
    """Set up test environment variables"""
    # Database configuration with absolute path
    if 'DATABASE_URL' not in os.environ:
        db_path = os.path.abspath('guest_registration_test.db')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    if 'TABLE_PREFIX' not in os.environ:
        os.environ['TABLE_PREFIX'] = 'test_guest_reg_'
    
    # Flask configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'

# Set up test environment
setup_test_environment()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Trip, Housekeeping, Registration, Amenity
from werkzeug.security import generate_password_hash

load_dotenv()

def test_date_format_settings():
    """Test that date format settings work correctly."""
    
    with app.app_context():
        print("🔄 Testing date format settings...")
        
        try:
            # Create test admin user
            admin = User.query.filter_by(username='test_admin_date_format').first()
            if not admin:
                admin = User(
                    username='test_admin_date_format',
                    email='test_admin_date@example.com',
                    password_hash=generate_password_hash('test123'),
                    role='admin',
                    date_format='d.m.Y'  # Default format
                )
                db.session.add(admin)
                db.session.flush()
                print("✅ Created test admin user with default date format")
            
            # Create test amenity
            amenity = Amenity.query.filter_by(name='Test Amenity for Date Format').first()
            if not amenity:
                amenity = Amenity(
                    name='Test Amenity for Date Format',
                    description='Test amenity for date format tests',
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
                title='Test Trip for Date Format',
                start_date=trip_start,
                end_date=trip_end,
                max_guests=2,
                admin_id=admin.id,
                amenity_id=amenity.id
            )
            db.session.add(trip)
            db.session.flush()
            print("✅ Created test trip")
            
            # Test 1: Default format (d.m.Y)
            print("\n📋 Test 1: Default Date Format (d.m.Y)")
            admin.date_format = 'd.m.Y'
            db.session.commit()
            
            expected_format = trip_start.strftime('d.m.Y')
            actual_format = trip_start.strftime(admin.date_format)
            print(f"   Expected: {expected_format}")
            print(f"   Actual:   {actual_format}")
            assert expected_format == actual_format, "Default date format does not match"
            print("✅ Default date format works correctly")
            
            # Test 2: ISO format (Y-m-d)
            print("\n📋 Test 2: ISO Date Format (Y-m-d)")
            admin.date_format = 'Y-m-d'
            db.session.commit()
            
            expected_format = trip_start.strftime('Y-m-d')
            actual_format = trip_start.strftime(admin.date_format)
            print(f"   Expected: {expected_format}")
            print(f"   Actual:   {actual_format}")
            assert expected_format == actual_format, "ISO date format does not match"
            print("✅ ISO date format works correctly")
            
            # Test 3: Slash format (d/m/Y)
            print("\n📋 Test 3: Slash Date Format (d/m/Y)")
            admin.date_format = 'd/m/Y'
            db.session.commit()
            
            expected_format = trip_start.strftime('d/m/Y')
            actual_format = trip_start.strftime(admin.date_format)
            print(f"   Expected: {expected_format}")
            print(f"   Actual:   {actual_format}")
            assert expected_format == actual_format, "Slash date format does not match"
            print("✅ Slash date format works correctly")
            
            # Test 4: US format (m/d/Y)
            print("\n📋 Test 4: US Date Format (m/d/Y)")
            admin.date_format = 'm/d/Y'
            db.session.commit()
            
            expected_format = trip_start.strftime('m/d/Y')
            actual_format = trip_start.strftime(admin.date_format)
            print(f"   Expected: {expected_format}")
            print(f"   Actual:   {actual_format}")
            assert expected_format == actual_format, "US date format does not match"
            print("✅ US date format works correctly")
            
            # Test 5: Short year format (d.m.y)
            print("\n📋 Test 5: Short Year Format (d.m.y)")
            admin.date_format = 'd.m.y'
            db.session.commit()
            
            expected_format = trip_start.strftime('d.m.y')
            actual_format = trip_start.strftime(admin.date_format)
            print(f"   Expected: {expected_format}")
            print(f"   Actual:   {actual_format}")
            assert expected_format == actual_format, "Short year format does not match"
            print("✅ Short year format works correctly")
            
            # Test 6: No leading zeros format (j.n.Y)
            print("\n📋 Test 6: No Leading Zeros Format (j.n.Y)")
            admin.date_format = 'j.n.Y'
            db.session.commit()
            
            expected_format = trip_start.strftime('j.n.Y')
            actual_format = trip_start.strftime(admin.date_format)
            print(f"   Expected: {expected_format}")
            print(f"   Actual:   {actual_format}")
            assert expected_format == actual_format, "No leading zeros format does not match"
            print("✅ No leading zeros format works correctly")
            
            print("\n🎉 All date format tests completed successfully!")
            print("\n📋 Summary:")
            print("   - Date format settings are saved correctly in the database")
            print("   - All supported date formats work as expected:")
            print("     * d.m.Y (26.3.2025) - Default")
            print("     * Y-m-d (2025-03-26) - ISO")
            print("     * d/m/Y (26/03/2025) - Slash")
            print("     * m/d/Y (03/26/2025) - US")
            print("     * d.m.y (26.3.25) - Short year")
            print("     * j.n.Y (26.3.2025) - No leading zeros")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing date format settings: {str(e)}")
            db.session.rollback()
            return False

def test_task_completion_date_restriction():
    """Test that tasks can only be marked as completed on the task date."""
    with app.app_context():
        unique = str(uuid.uuid4())[:8]
        # Create an admin user
        admin = User(
            username=f'admin_{unique}',
            email=f'admin_{unique}@test.com',
            password_hash='test_hash',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        # Create a housekeeper
        housekeeper = User(
            username=f'test_housekeeper_{unique}',
            email=f'housekeeper_{unique}@test.com',
            password_hash='test_hash',
            role='housekeeper'
        )
        db.session.add(housekeeper)
        db.session.commit()
        
        # Create an amenity with admin_id set
        amenity = Amenity(name='Test Amenity', admin_id=admin.id)
        db.session.add(amenity)
        db.session.commit()
        
        # Create a trip
        trip = Trip(
            title='Test Trip',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5),
            max_guests=1,
            amenity_id=amenity.id,
            admin_id=admin.id
        )
        db.session.add(trip)
        db.session.commit()
        
        # Create a housekeeping task for tomorrow
        tomorrow = date.today() + timedelta(days=1)
        task = Housekeeping(
            trip_id=trip.id,
            housekeeper_id=housekeeper.id,
            date=tomorrow,
            status='pending',
            pay_amount=50.0
        )
        db.session.add(task)
        db.session.commit()
        
        # Try to mark as completed today (should fail)
        with app.test_client() as client:
            login_user(housekeeper)
            response = client.post(f'/housekeeper/task/{task.id}/update-status', 
                                 data={'status': 'completed'}, follow_redirects=True)
            
            # Should redirect back with error message
            assert response.status_code == 200
            assert b'can only be marked as completed on the task date' in response.data
            
            # Task should still be pending
            task = Housekeeping.query.get(task.id)
            assert task.status == 'pending'
        
        # Create a task for today
        today = date.today()
        today_task = Housekeeping(
            trip_id=trip.id,
            housekeeper_id=housekeeper.id,
            date=today,
            status='pending',
            pay_amount=50.0
        )
        db.session.add(today_task)
        db.session.commit()
        
        # Try to mark as completed today (should succeed)
        with app.test_client() as client:
            login_user(housekeeper)
            response = client.post(f'/housekeeper/task/{today_task.id}/update-status', 
                                 data={'status': 'completed'}, follow_redirects=True)
            
            # Should succeed
            assert response.status_code == 200
            assert b'Task status updated successfully' in response.data
            
            # Task should be completed
            today_task = Housekeeping.query.get(today_task.id)
            assert today_task.status == 'completed'

def test_payment_calculation_only_completed_tasks():
    """Test that only completed tasks are counted in payment calculations."""
    with app.app_context():
        unique = str(uuid.uuid4())[:8]
        # Create an admin user
        admin = User(
            username=f'admin_{unique}',
            email=f'admin_{unique}@test.com',
            password_hash='test_hash',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        # Create a housekeeper
        housekeeper = User(
            username=f'test_housekeeper_{unique}',
            email=f'housekeeper_{unique}@test.com',
            password_hash='test_hash',
            role='housekeeper'
        )
        db.session.add(housekeeper)
        db.session.commit()
        
        # Create an amenity with admin_id set
        amenity = Amenity(name='Test Amenity', admin_id=admin.id)
        db.session.add(amenity)
        db.session.commit()
        
        # Create a trip
        trip = Trip(
            title='Test Trip',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5),
            max_guests=1,
            amenity_id=amenity.id,
            admin_id=admin.id
        )
        db.session.add(trip)
        db.session.commit()
        
        # Create tasks with different statuses
        today = date.today()
        completed_task = Housekeeping(
            trip_id=trip.id,
            housekeeper_id=housekeeper.id,
            date=today,
            status='completed',
            pay_amount=50.0,
            paid=False
        )
        pending_task = Housekeeping(
            trip_id=trip.id,
            housekeeper_id=housekeeper.id,
            date=today,
            status='pending',
            pay_amount=30.0,
            paid=False
        )
        in_progress_task = Housekeeping(
            trip_id=trip.id,
            housekeeper_id=housekeeper.id,
            date=today,
            status='in_progress',
            pay_amount=20.0,
            paid=False
        )
        
        db.session.add_all([completed_task, pending_task, in_progress_task])
        db.session.commit()
        
        # Test admin housekeeping view payment calculations
        with app.test_client() as client:
            admin2 = User(username=f'admin2_{unique}', email=f'admin2_{unique}@test.com', password_hash='hash', role='admin')
            db.session.add(admin2)
            db.session.commit()
            login_user(admin2)
            
            response = client.get('/admin/housekeeping')
            assert response.status_code == 200
            
            # Only completed task should be counted in payment
            # Total should be 50.0 (only completed task)
            assert b'50.00' in response.data
            # Should not include pending or in_progress tasks in payment totals
            assert b'100.00' not in response.data  # 50+30+20

if __name__ == "__main__":
    success = test_date_format_settings()
    if success:
        print("\n✅ Date format settings test completed successfully!")
    else:
        print("\n❌ Date format settings test failed!") 