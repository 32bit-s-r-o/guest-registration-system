#!/usr/bin/env python3
"""
Test Airbnb Calendar Sync Functionality
This script tests the Airbnb calendar sync with sample iCal data.
"""

import os
import sys
from datetime import datetime, timedelta
from app import app, db, Admin, Trip
from app import fetch_airbnb_calendar, parse_airbnb_guest_info, sync_airbnb_reservations

def create_sample_ical():
    """Create a sample iCal file for testing."""
    sample_ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Airbnb//Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:airbnb_123456_789
DTSTART:20241201T150000Z
DTEND:20241205T110000Z
SUMMARY:John Smith - Airbnb (2 guests)
DESCRIPTION:Guest: John Smith\\nEmail: john.smith@example.com\\nGuests: 2\\nCheck-in: 3:00 PM\\nCheck-out: 11:00 AM
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_790
DTSTART:20241210T150000Z
DTEND:20241215T110000Z
SUMMARY:Alice Johnson (3 guests) - Airbnb
DESCRIPTION:Guest: Alice Johnson\\nEmail: alice.j@example.com\\nGuests: 3\\nCheck-in: 3:00 PM\\nCheck-out: 11:00 AM
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_791
DTSTART:20241220T150000Z
DTEND:20241225T110000Z
SUMMARY:Bob Wilson - 4 guests
DESCRIPTION:Guest: Bob Wilson\\nEmail: bob.wilson@example.com\\nGuests: 4\\nCheck-in: 3:00 PM\\nCheck-out: 11:00 AM
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    with open('sample_airbnb_calendar.ics', 'w') as f:
        f.write(sample_ical)
    
    return 'sample_airbnb_calendar.ics'

def test_guest_info_parsing():
    """Test guest information parsing from Airbnb calendar events."""
    print("=== Testing Guest Information Parsing ===")
    
    test_cases = [
        {
            'summary': 'John Smith - Airbnb (2 guests)',
            'description': 'Guest: John Smith\nEmail: john.smith@example.com\nGuests: 2',
            'expected': {'name': 'John Smith', 'email': 'john.smith@example.com', 'count': 2}
        },
        {
            'summary': 'Alice Johnson (3 guests) - Airbnb',
            'description': 'Guest: Alice Johnson\nEmail: alice.j@example.com\nGuests: 3',
            'expected': {'name': 'Alice Johnson', 'email': 'alice.j@example.com', 'count': 3}
        },
        {
            'summary': 'Bob Wilson - 4 guests',
            'description': 'Guest: Bob Wilson\nEmail: bob.wilson@example.com\nGuests: 4',
            'expected': {'name': 'Bob Wilson', 'email': 'bob.wilson@example.com', 'count': 4}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = parse_airbnb_guest_info(test_case['summary'], test_case['description'])
        print(f"Test {i}:")
        print(f"  Input: {test_case['summary']}")
        print(f"  Expected: {test_case['expected']}")
        print(f"  Result: {result}")
        print(f"  Pass: {result == test_case['expected']}")
        print()

def test_calendar_fetching():
    """Test calendar fetching with sample file."""
    print("=== Testing Calendar Fetching ===")
    
    # Create sample iCal file
    sample_file = create_sample_ical()
    
    try:
        # Test with file URL
        file_url = f"file://{os.path.abspath(sample_file)}"
        reservations = fetch_airbnb_calendar(file_url)
        
        print(f"Found {len(reservations)} reservations:")
        for i, reservation in enumerate(reservations, 1):
            print(f"  {i}. {reservation['title']}")
            print(f"     Dates: {reservation['start_date']} to {reservation['end_date']}")
            print(f"     Guest: {reservation['guest_name']}")
            print(f"     Email: {reservation['guest_email']}")
            print(f"     Count: {reservation['guest_count']}")
            print()
        
        return reservations
        
    except Exception as e:
        print(f"Error testing calendar fetching: {e}")
        return []

def test_sync_functionality():
    """Test the complete sync functionality."""
    print("=== Testing Complete Sync Functionality ===")
    
    try:
        with app.app_context():
            # Create test admin if not exists
            admin = Admin.query.filter_by(username='test_admin').first()
            if not admin:
                admin = Admin(
                    username='test_admin',
                    email='test@example.com',
                    password_hash='dummy_hash',
                    airbnb_calendar_url='file://sample_airbnb_calendar.ics',
                    airbnb_sync_enabled=True
                )
                db.session.add(admin)
                db.session.commit()
            
            # Test sync
            result = sync_airbnb_reservations(admin.id)
            print(f"Sync result: {result}")
            
            # Check created trips
            trips = Trip.query.filter_by(admin_id=admin.id).all()
            print(f"Created {len(trips)} trips:")
            for trip in trips:
                print(f"  - {trip.title}")
                print(f"    Airbnb ID: {trip.airbnb_reservation_id}")
                print(f"    Guest: {trip.airbnb_guest_name}")
                print(f"    Email: {trip.airbnb_guest_email}")
                print(f"    Count: {trip.airbnb_guest_count}")
                print(f"    Synced: {trip.airbnb_synced_at}")
                print()
            
            return result
            
    except Exception as e:
        print(f"Error testing sync functionality: {e}")
        return None

def cleanup():
    """Clean up test files."""
    try:
        if os.path.exists('sample_airbnb_calendar.ics'):
            os.remove('sample_airbnb_calendar.ics')
        print("Cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """Main test function."""
    print("🧪 Airbnb Calendar Sync Test Suite")
    print("=" * 50)
    
    try:
        # Test guest info parsing
        test_guest_info_parsing()
        
        # Test calendar fetching
        reservations = test_calendar_fetching()
        
        if reservations:
            # Test complete sync functionality
            test_sync_functionality()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 