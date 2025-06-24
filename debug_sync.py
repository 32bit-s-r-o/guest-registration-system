#!/usr/bin/env python3
"""
Debug script for calendar sync functionality.
This script helps test and debug the calendar sync process.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Calendar, Trip, Amenity, User
from config import Config

def debug_calendar_sync(calendar_id):
    """Debug a specific calendar sync."""
    with app.app_context():
        calendar = Calendar.query.get(calendar_id)
        if not calendar:
            print(f"❌ Calendar with ID {calendar_id} not found")
            return
        
        print(f"🔍 Debugging calendar: {calendar.name}")
        print(f"   URL: {calendar.calendar_url}")
        print(f"   Type: {calendar.calendar_type}")
        print(f"   Sync enabled: {calendar.sync_enabled}")
        print(f"   Amenity: {calendar.amenity.name}")
        print(f"   Amenity max_guests: {calendar.amenity.max_guests}")
        
        # Check existing trips
        existing_trips = Trip.query.filter_by(calendar_id=calendar_id).all()
        print(f"   Existing trips: {len(existing_trips)}")
        
        for trip in existing_trips:
            print(f"     Trip {trip.id}: {trip.title}")
            print(f"       max_guests: {trip.max_guests}")
            print(f"       external_guest_count: {trip.external_guest_count}")
            print(f"       external_reservation_id: {trip.external_reservation_id}")
            print(f"       external_confirm_code: {trip.external_confirm_code}")
        
        # Test the sync function
        from app import sync_calendar_reservations
        print(f"\n🔄 Testing sync function...")
        result = sync_calendar_reservations(calendar_id)
        print(f"   Result: {result}")
        
        # Check trips after sync
        trips_after = Trip.query.filter_by(calendar_id=calendar_id).all()
        print(f"\n📊 After sync - Trips: {len(trips_after)}")
        
        for trip in trips_after:
            print(f"     Trip {trip.id}: {trip.title}")
            print(f"       max_guests: {trip.max_guests}")
            print(f"       external_guest_count: {trip.external_guest_count}")
            print(f"       external_reservation_id: {trip.external_reservation_id}")
            print(f"       external_confirm_code: {trip.external_confirm_code}")

def list_calendars():
    """List all calendars in the system."""
    with app.app_context():
        calendars = Calendar.query.all()
        print(f"📅 Found {len(calendars)} calendars:")
        
        for calendar in calendars:
            print(f"   ID: {calendar.id}")
            print(f"   Name: {calendar.name}")
            print(f"   Amenity: {calendar.amenity.name}")
            print(f"   Type: {calendar.calendar_type}")
            print(f"   Sync enabled: {calendar.sync_enabled}")
            print(f"   URL: {calendar.calendar_url[:50]}...")
            print(f"   Last sync: {calendar.last_sync}")
            print()

def test_guest_count_parsing():
    """Test the guest count parsing function."""
    from app import parse_airbnb_guest_info
    
    test_cases = [
        {
            'summary': 'John Smith - Airbnb (3 guests)',
            'description': 'Guest email: john@example.com\nConfirmation code: ABC1234567'
        },
        {
            'summary': 'Alice Johnson - 2 guests',
            'description': 'alice@example.com\nDetails: https://airbnb.com/details/XYZ9876543'
        },
        {
            'summary': 'Bob Wilson',
            'description': 'bob@example.com\n4 people staying'
        },
        {
            'summary': 'Not Available',
            'description': 'Blocked for maintenance'
        }
    ]
    
    print("🧪 Testing guest count parsing:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        print(f"  Summary: {test_case['summary']}")
        print(f"  Description: {test_case['description']}")
        
        result = parse_airbnb_guest_info(test_case['summary'], test_case['description'])
        print(f"  Result: {result}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python debug_sync.py list                    # List all calendars")
        print("  python debug_sync.py debug <calendar_id>     # Debug specific calendar")
        print("  python debug_sync.py test-parsing            # Test guest count parsing")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_calendars()
    elif command == 'debug':
        if len(sys.argv) < 3:
            print("❌ Please provide a calendar ID")
            sys.exit(1)
        calendar_id = int(sys.argv[2])
        debug_calendar_sync(calendar_id)
    elif command == 'test-parsing':
        test_guest_count_parsing()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1) 