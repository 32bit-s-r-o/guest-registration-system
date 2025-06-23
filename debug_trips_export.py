#!/usr/bin/env python3
"""
Debug script to test trips export functionality
"""

from app import app, db, Trip, current_user
from flask_login import login_user
from io import StringIO
import csv

def test_trips_export():
    with app.app_context():
        # Get all trips
        trips = Trip.query.all()
        print(f"Found {len(trips)} trips")
        
        # Create CSV data
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Trip ID',
            'Title',
            'Start Date',
            'End Date',
            'Max Guests',
            'Created Date',
            'Amenity',
            'Calendar',
            'Externally Synced',
            'External Guest Name',
            'External Guest Email',
            'External Guest Count',
            'External Confirmation Code',
            'Registration Count',
            'Pending Count',
            'Approved Count',
            'Rejected Count'
        ])
        
        # Write data
        for trip in trips:
            try:
                registrations = trip.registrations
                pending_count = len([r for r in registrations if r.status == 'pending'])
                approved_count = len([r for r in registrations if r.status == 'approved'])
                rejected_count = len([r for r in registrations if r.status == 'rejected'])
                
                writer.writerow([
                    trip.id,
                    trip.title,
                    trip.start_date.strftime('%Y-%m-%d'),
                    trip.end_date.strftime('%Y-%m-%d'),
                    trip.max_guests,
                    trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    trip.amenity.name if trip.amenity else '',
                    trip.calendar.name if trip.calendar else '',
                    'Yes' if trip.is_externally_synced else 'No',
                    trip.external_guest_name or '',
                    trip.external_guest_email or '',
                    trip.external_guest_count or '',
                    trip.external_confirm_code or '',
                    len(registrations),
                    pending_count,
                    approved_count,
                    rejected_count
                ])
                print(f"Successfully processed trip {trip.id}: {trip.title}")
            except Exception as e:
                print(f"Error processing trip {trip.id}: {e}")
                import traceback
                traceback.print_exc()
        
        # Convert to bytes and create BytesIO
        csv_data = output.getvalue().encode('utf-8')
        output.close()
        
        print(f"CSV data length: {len(csv_data)} bytes")
        print("Trips export test completed successfully!")

if __name__ == "__main__":
    test_trips_export() 