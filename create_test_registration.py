#!/usr/bin/env python3
"""
Script to create a test registration for system testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Trip, Registration, Guest, User
from datetime import datetime, timedelta

def create_test_registration():
    """Create a test registration for system testing"""
    with app.app_context():
        # Get or create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found. Please ensure the admin user exists.")
            return None
        
        # Get or create a trip
        trip = Trip.query.first()
        if not trip:
            # Create a test trip
            trip = Trip(
                title=f'Test Trip {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                start_date=(datetime.now() + timedelta(days=1)).date(),
                end_date=(datetime.now() + timedelta(days=2)).date(),
                max_guests=2,
                admin_id=admin.id
            )
            db.session.add(trip)
            db.session.flush()  # Get the trip ID
            print(f"Created test trip: {trip.title}")
        
        # Create a test registration
        registration = Registration(
            trip_id=trip.id,
            email='test@example.com',
            status='pending',
            language='en'
        )
        db.session.add(registration)
        db.session.flush()  # Get the registration ID
        
        # Create a test guest
        guest = Guest(
            registration_id=registration.id,
            first_name='Test',
            last_name='Guest',
            age_category='adult',
            document_type='passport',
            document_number='TEST123456',
            gdpr_consent=True
        )
        db.session.add(guest)
        
        # Commit everything
        db.session.commit()
        
        print(f"Created test registration {registration.id} with guest {guest.id}")
        print(f"Trip ID: {trip.id}")
        print(f"Registration ID: {registration.id}")
        
        return registration.id

if __name__ == "__main__":
    reg_id = create_test_registration()
    if reg_id:
        print(f"✅ Test registration created successfully with ID: {reg_id}")
    else:
        print("❌ Failed to create test registration") 