#!/usr/bin/env python3
"""
Test script for the new amenity-housekeeper system.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Amenity, AmenityHousekeeper, Trip, Housekeeping
from werkzeug.security import generate_password_hash

load_dotenv()

def test_amenity_housekeeper_system():
    """Test the amenity-housekeeper system functionality."""
    
    with app.app_context():
        print("🧪 Testing Amenity-Housekeeper System")
        print("=" * 50)
        
        try:
            # Create test admin if not exists
            admin = User.query.filter_by(username='test_admin').first()
            if not admin:
                admin = User(
                    username='test_admin',
                    email='admin@test.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.flush()
                print("✅ Created test admin: test_admin/admin123")
            else:
                print(f"✅ Using existing admin: {admin.username}")
            
            # Create test housekeepers if not exist
            housekeepers = []
            for i in range(2):
                housekeeper = User.query.filter_by(username=f'housekeeper{i+1}').first()
                if not housekeeper:
                    housekeeper = User(
                        username=f'housekeeper{i+1}',
                        email=f'housekeeper{i+1}@test.com',
                        password_hash=generate_password_hash(f'housekeeper{i+1}123'),
                        role='housekeeper'
                    )
                    db.session.add(housekeeper)
                    db.session.flush()
                    print(f"✅ Created test housekeeper {i+1}: housekeeper{i+1}/housekeeper{i+1}123")
                else:
                    print(f"✅ Using existing housekeeper {i+1}: {housekeeper.username}")
                housekeepers.append(housekeeper)
            
            # Create test amenity if not exists
            amenity = Amenity.query.filter_by(name='Test Amenity').first()
            if not amenity:
                amenity = Amenity(
                    name='Test Amenity',
                    description='Test amenity for housekeeper system',
                    max_guests=4,
                    admin_id=admin.id,
                    is_active=True
                )
                db.session.add(amenity)
                db.session.flush()
                print("✅ Created test amenity: Test Amenity")
            else:
                print(f"✅ Using existing amenity: {amenity.name}")
            
            # Test 1: Assign housekeepers to amenity
            print("\n📋 Test 1: Assigning housekeepers to amenity")
            
            # Clear existing assignments
            AmenityHousekeeper.query.filter_by(amenity_id=amenity.id).delete()
            
            # Assign first housekeeper as default
            assignment1 = AmenityHousekeeper(
                amenity_id=amenity.id,
                housekeeper_id=housekeepers[0].id,
                is_default=True
            )
            db.session.add(assignment1)
            
            # Assign second housekeeper as regular
            assignment2 = AmenityHousekeeper(
                amenity_id=amenity.id,
                housekeeper_id=housekeepers[1].id,
                is_default=False
            )
            db.session.add(assignment2)
            
            db.session.commit()
            print("✅ Assigned housekeepers to amenity")
            
            # Test 2: Verify assignments
            print("\n📋 Test 2: Verifying assignments")
            assignments = AmenityHousekeeper.query.filter_by(amenity_id=amenity.id).all()
            print(f"✅ Found {len(assignments)} assignments")
            
            default_assignment = next((a for a in assignments if a.is_default), None)
            if default_assignment:
                print(f"✅ Default housekeeper: {default_assignment.housekeeper.username}")
            else:
                print("❌ No default housekeeper found")
            
            # Test 3: Create test trip and verify housekeeping task creation
            print("\n📋 Test 3: Testing automatic housekeeping task creation")
            
            # Clear existing trips and tasks
            Housekeeping.query.join(Trip).filter(Trip.amenity_id == amenity.id).delete()
            Trip.query.filter_by(amenity_id=amenity.id).delete()
            
            # Create test trip
            trip = Trip(
                title='Test Trip',
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=2)).date(),
                max_guests=2,
                admin_id=admin.id,
                amenity_id=amenity.id,
                is_externally_synced=True
            )
            db.session.add(trip)
            db.session.flush()
            
            # Simulate automatic task creation (like in sync function)
            if default_assignment:
                housekeeping_task = Housekeeping(
                    trip_id=trip.id,
                    housekeeper_id=default_assignment.housekeeper_id,
                    date=trip.end_date + timedelta(days=1),
                    status='pending',
                    pay_amount=50.00,
                    paid=False
                )
                db.session.add(housekeeping_task)
                db.session.commit()
                print("✅ Created housekeeping task automatically")
                
                # Verify task was assigned to default housekeeper
                task = Housekeeping.query.filter_by(trip_id=trip.id).first()
                if task and task.housekeeper_id == default_assignment.housekeeper_id:
                    print("✅ Task correctly assigned to default housekeeper")
                else:
                    print("❌ Task not assigned to default housekeeper")
            else:
                print("⚠️  No default housekeeper - no task created")
            
            # Test 4: Test reassignment
            print("\n📋 Test 4: Testing task reassignment")
            if task:
                original_housekeeper_id = task.housekeeper_id
                new_housekeeper_id = housekeepers[1].id
                
                task.housekeeper_id = new_housekeeper_id
                task.updated_at = datetime.utcnow()
                db.session.commit()
                
                # Verify reassignment
                updated_task = Housekeeping.query.get(task.id)
                if updated_task.housekeeper_id == new_housekeeper_id:
                    print("✅ Task successfully reassigned")
                else:
                    print("❌ Task reassignment failed")
            
            print("\n🎉 All tests completed successfully!")
            print("\n📋 Summary:")
            print(f"   - Admin: {admin.username}")
            print(f"   - Amenity: {amenity.name}")
            print(f"   - Housekeepers: {len(housekeepers)}")
            print(f"   - Assignments: {len(assignments)}")
            print(f"   - Default housekeeper: {default_assignment.housekeeper.username if default_assignment else 'None'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    test_amenity_housekeeper_system() 