#!/usr/bin/env python3
"""
Script to create sample housekeeper user and housekeeping tasks for testing.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import Config

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Trip, Housekeeping
from werkzeug.security import generate_password_hash

load_dotenv()

def create_housekeeper_data():
    """Create sample housekeeper user and housekeeping tasks."""
    
    with app.app_context():
        print("🔄 Creating housekeeper data...")
        
        try:
            # Create housekeeper user if not exists
            housekeeper = User.query.filter_by(username='housekeeper').first()
            if not housekeeper:
                housekeeper = User(
                    username='housekeeper',
                    email='housekeeper@example.com',
                    password_hash=generate_password_hash('housekeeper123'),
                    role='housekeeper'
                )
                db.session.add(housekeeper)
                db.session.flush()
                print("✅ Created housekeeper user: housekeeper/housekeeper123")
            else:
                print(f"✅ Using existing housekeeper: {housekeeper.username}")
            
            # Get admin user for trip creation
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                print("❌ No admin user found. Please create an admin user first.")
                return False
            
            # Create sample trips if none exist
            trips = Trip.query.all()
            if not trips:
                print("📋 Creating sample trips...")
                sample_trips = [
                    {
                        'title': 'Weekend Getaway',
                        'start_date': datetime.now().date() + timedelta(days=1),
                        'end_date': datetime.now().date() + timedelta(days=3),
                        'max_guests': 4
                    },
                    {
                        'title': 'Family Vacation',
                        'start_date': datetime.now().date() + timedelta(days=5),
                        'end_date': datetime.now().date() + timedelta(days=10),
                        'max_guests': 6
                    },
                    {
                        'title': 'Business Trip',
                        'start_date': datetime.now().date() + timedelta(days=2),
                        'end_date': datetime.now().date() + timedelta(days=4),
                        'max_guests': 2
                    }
                ]
                
                for trip_data in sample_trips:
                    trip = Trip(
                        title=trip_data['title'],
                        start_date=trip_data['start_date'],
                        end_date=trip_data['end_date'],
                        max_guests=trip_data['max_guests'],
                        admin_id=admin.id
                    )
                    db.session.add(trip)
                
                db.session.flush()
                trips = Trip.query.all()
                print(f"✅ Created {len(trips)} sample trips")
            
            # Create housekeeping tasks
            print("📋 Creating housekeeping tasks...")
            existing_tasks = Housekeeping.query.filter_by(housekeeper_id=housekeeper.id).count()
            if existing_tasks == 0:
                # Create tasks for each trip
                for trip in trips:
                    # Create a task for the day after the trip ends
                    task_date = trip.end_date + timedelta(days=1)
                    task = Housekeeping(
                        trip_id=trip.id,
                        housekeeper_id=housekeeper.id,
                        date=task_date,
                        status='pending',
                        pay_amount=50.00,  # Sample pay amount
                        paid=False
                    )
                    db.session.add(task)
                
                db.session.commit()
                print(f"✅ Created housekeeping tasks for {len(trips)} trips")
            else:
                print(f"✅ Housekeeping tasks already exist ({existing_tasks} tasks)")
            
            print("\n🎉 Housekeeper data created successfully!")
            print("\n📋 Login credentials:")
            print("   Username: housekeeper")
            print("   Password: housekeeper123")
            print("   Role: housekeeper")
            print("\n🔗 Access the housekeeper dashboard at: /housekeeper/dashboard")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating housekeeper data: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    create_housekeeper_data() 