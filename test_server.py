#!/usr/bin/env python3
"""
Test server runner for the Guest Registration System
"""

import os
import sys
import signal
import threading
import time
from test_config import TestConfig

def start_test_server():
    """Start the test server"""
    print("🚀 Starting Test Server")
    print("=" * 50)
    
    # Set up test environment
    TestConfig.setup_test_environment()
    
    try:
        from app import app
        
        # Configure app for testing
        app.config.update(TestConfig.get_test_app_config())
        
        print(f"🌐 Test Server Configuration:")
        print(f"   URL: {TestConfig.TEST_SERVER_URL}")
        print(f"   Port: {TestConfig.TEST_PORT}")
        print(f"   Database: {TestConfig.TEST_DATABASE_NAME}")
        print(f"   Table Prefix: {TestConfig.TEST_TABLE_PREFIX}")
        print(f"   Upload Folder: {TestConfig.TEST_UPLOAD_FOLDER}")
        
        print(f"\n🔑 Test Admin Credentials:")
        print(f"   Username: {TestConfig.TEST_ADMIN_USERNAME}")
        print(f"   Password: {TestConfig.TEST_ADMIN_PASSWORD}")
        print(f"   Email: {TestConfig.TEST_ADMIN_EMAIL}")
        
        print(f"\n📊 Available Test Data:")
        with app.app_context():
            from database import db, User, Trip, Registration, Guest, Invoice
            print(f"   👤 Users: {db.session.query(User).count()}")
            print(f"   ✈️ Trips: {db.session.query(Trip).count()}")
            print(f"   📝 Registrations: {db.session.query(Registration).count()}")
            print(f"   👥 Guests: {db.session.query(Guest).count()}")
            print(f"   💰 Invoices: {db.session.query(Invoice).count()}")
        
        print(f"\n🎯 Server starting on {TestConfig.TEST_SERVER_URL}")
        print("   Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start server in a separate thread
        def run_server():
            app.run(
                host='0.0.0.0',
                port=TestConfig.TEST_PORT,
                debug=False,
                use_reloader=False
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        print("✅ Test server is running!")
        print(f"   🌐 Access: {TestConfig.TEST_SERVER_URL}")
        print(f"   🔑 Login: {TestConfig.TEST_SERVER_URL}/admin/login")
        print(f"   📊 Dashboard: {TestConfig.TEST_SERVER_URL}/admin/dashboard")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping test server...")
            
    except Exception as e:
        print(f"❌ Error starting test server: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test environment
        TestConfig.cleanup_test_environment()
    
    return True

def stop_test_server():
    """Stop the test server"""
    print("🛑 Stopping Test Server")
    print("=" * 50)
    
    # Clean up test environment
    TestConfig.cleanup_test_environment()
    print("✅ Test server stopped!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stop':
        stop_test_server()
    else:
        start_test_server() 