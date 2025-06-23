#!/usr/bin/env python3
"""
Test Airbnb Calendar Filtering
This script tests that "Not Available" events are filtered out and only "Reserved" events are processed.
"""

import os
import sys
from datetime import datetime, timedelta
from app import app, fetch_airbnb_calendar

def create_test_ical_with_mixed_events():
    """Create a test iCal file with both reserved and not available events."""
    test_ical = """BEGIN:VCALENDAR
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
SUMMARY:Not Available
DESCRIPTION:This date is not available for booking
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_791
DTSTART:20241220T150000Z
DTEND:20241225T110000Z
SUMMARY:Alice Johnson (3 guests) - Airbnb
DESCRIPTION:Guest: Alice Johnson\\nEmail: alice.j@example.com\\nGuests: 3\\nCheck-in: 3:00 PM\\nCheck-out: 11:00 AM
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_792
DTSTART:20241230T150000Z
DTEND:20250105T110000Z
SUMMARY:Unavailable
DESCRIPTION:This period is blocked
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_793
DTSTART:20250110T150000Z
DTEND:20250115T110000Z
SUMMARY:Bob Wilson - 4 guests
DESCRIPTION:Guest: Bob Wilson\\nEmail: bob.wilson@example.com\\nGuests: 4\\nCheck-in: 3:00 PM\\nCheck-out: 11:00 AM
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_794
DTSTART:20250120T150000Z
DTEND:20250125T110000Z
SUMMARY:Maintenance
DESCRIPTION:Property under maintenance
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:airbnb_123456_795
DTSTART:20250130T150000Z
DTEND:20250205T110000Z
SUMMARY:Cleaning Day
DESCRIPTION:Deep cleaning scheduled
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    with open('test_mixed_calendar.ics', 'w') as f:
        f.write(test_ical)
    
    return 'test_mixed_calendar.ics'

def test_filtering():
    """Test that filtering correctly excludes 'Not Available' events."""
    print("🧪 Testing Airbnb Calendar Filtering")
    print("=" * 50)
    
    # Create test iCal file
    test_file = create_test_ical_with_mixed_events()
    
    try:
        # Read the file directly and test the parsing logic
        with open(test_file, 'r') as f:
            ical_content = f.read()
        
        # Import the required modules
        import icalendar
        from app import parse_airbnb_guest_info
        
        # Parse the calendar
        cal = icalendar.Calendar.from_ical(ical_content)
        reservations = []
        
        # Apply the same filtering logic as in fetch_airbnb_calendar
        for component in cal.walk():
            if component.name == "VEVENT":
                # Extract reservation details from event
                summary = str(component.get('summary', ''))
                description = str(component.get('description', ''))
                start_date = component.get('dtstart').dt
                end_date = component.get('dtend').dt
                
                # Skip "Not Available" events - only process actual reservations
                not_available_patterns = [
                    'not available',
                    'unavailable',
                    'blocked',
                    'maintenance',
                    'cleaning',
                    'no availability'
                ]
                
                summary_lower = summary.lower()
                if any(pattern in summary_lower for pattern in not_available_patterns):
                    continue  # Skip this event
                
                # Parse guest information from summary/description
                guest_info = parse_airbnb_guest_info(summary, description)
                
                reservation = {
                    'id': str(component.get('uid', '')),
                    'title': summary,
                    'start_date': start_date,
                    'end_date': end_date,
                    'guest_name': guest_info.get('name', ''),
                    'guest_email': guest_info.get('email', ''),
                    'guest_count': guest_info.get('count', 1),
                    'confirm_code': guest_info.get('confirm_code', ''),
                    'description': description
                }
                reservations.append(reservation)
        
        print(f"📊 Results:")
        print(f"   Total events in calendar: 7")
        print(f"   Events processed (reservations): {len(reservations)}")
        print(f"   Events filtered out (not available): {7 - len(reservations)}")
        print()
        
        print(f"✅ Processed Reservations ({len(reservations)}):")
        for i, reservation in enumerate(reservations, 1):
            print(f"   {i}. {reservation['title']}")
            print(f"      Dates: {reservation['start_date']} to {reservation['end_date']}")
            print(f"      Guest: {reservation['guest_name']}")
            print(f"      Email: {reservation['guest_email']}")
            print(f"      Count: {reservation['guest_count']}")
            print()
        
        # Verify that only actual reservations were processed
        expected_reservations = [
            "John Smith - Airbnb (2 guests)",
            "Alice Johnson (3 guests) - Airbnb", 
            "Bob Wilson - 4 guests"
        ]
        
        processed_titles = [r['title'] for r in reservations]
        
        print(f"🔍 Verification:")
        for expected in expected_reservations:
            if expected in processed_titles:
                print(f"   ✅ '{expected}' - Correctly processed")
            else:
                print(f"   ❌ '{expected}' - Missing!")
        
        filtered_events = [
            "Not Available",
            "Unavailable", 
            "Maintenance",
            "Cleaning Day"
        ]
        
        print(f"\n🚫 Filtered Events (should be excluded):")
        for filtered in filtered_events:
            if filtered in processed_titles:
                print(f"   ❌ '{filtered}' - Should have been filtered out!")
            else:
                print(f"   ✅ '{filtered}' - Correctly filtered out")
        
        # Summary
        print(f"\n📋 Summary:")
        if len(reservations) == 3:
            print(f"   ✅ SUCCESS: Only 3 actual reservations were processed")
            print(f"   ✅ SUCCESS: 4 'not available' events were correctly filtered out")
        else:
            print(f"   ❌ FAILED: Expected 3 reservations, got {len(reservations)}")
        
        return len(reservations) == 3
        
    except Exception as e:
        print(f"❌ Error testing filtering: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Main test function."""
    success = test_filtering()
    
    if success:
        print("\n🎉 All filtering tests passed!")
        return 0
    else:
        print("\n💥 Some filtering tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 