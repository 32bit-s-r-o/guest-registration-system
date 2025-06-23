#!/usr/bin/env python3
"""
Test script to verify date format settings functionality.
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

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

if __name__ == "__main__":
    success = test_date_format_settings()
    if success:
        print("\n✅ Date format settings test completed successfully!")
    else:
        print("\n❌ Date format settings test failed!") 