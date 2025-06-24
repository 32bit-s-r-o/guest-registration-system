#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner for the Guest Registration System
"""

import os
import sys
import subprocess
import time
import signal
import threading
from datetime import datetime
from test_config import TestConfig

class TestSuiteRunner:
    """Test suite runner with full environment setup"""
    
    def __init__(self):
        self.server_process = None
        self.test_results = {}
        
    def setup_test_environment(self):
        """Set up the complete test environment"""
        print("🔧 Setting Up Test Environment")
        print("=" * 60)
        
        # Set up test environment variables
        TestConfig.setup_test_environment()
        
        # Create test database if needed
        self.create_test_database()
        
        # Run migrations
        self.run_migrations()
        
        # Seed test data
        self.seed_test_data()
        
        print("✅ Test environment setup complete!")
        
    def create_test_database(self):
        """Create test database if it doesn't exist"""
        print("🗄️ Creating test database...")
        try:
            # Use psql to create database
            cmd = [
                'psql', '-h', '192.168.13.113', '-p', '5433', '-U', 'postgres',
                '-d', 'postgres', '-c', f'CREATE DATABASE {TestConfig.TEST_DATABASE_NAME};'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = '4c4d90dfc806dcaa7b21bab49bee72eadd78cbb757a36ff3988d62a9385d5cc3'
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0 or "already exists" in result.stderr:
                print("✅ Test database ready")
            else:
                print(f"⚠️ Database creation: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️ Database creation warning: {e}")
    
    def run_migrations(self):
        """Run database migrations"""
        print("🔄 Running database migrations...")
        try:
            # Pass the test environment variables to the migrations script
            env = os.environ.copy()
            env['DATABASE_URL'] = TestConfig.get_test_database_url()
            env['TABLE_PREFIX'] = TestConfig.TEST_TABLE_PREFIX
            
            result = subprocess.run(['python', 'migrations.py', 'migrate'], 
                                  env=env, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Migrations completed")
            else:
                print(f"⚠️ Migration warning: {result.stderr}")
                print(f"STDOUT: {result.stdout}")
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")
    
    def seed_test_data(self):
        """Seed test data"""
        print("🌱 Seeding test data...")
        try:
            # Pass the test environment variables to the seeder script
            env = os.environ.copy()
            env['DATABASE_URL'] = TestConfig.get_test_database_url()
            env['TABLE_PREFIX'] = TestConfig.TEST_TABLE_PREFIX
            
            result = subprocess.run(['python', 'test_seeder.py'], 
                                  env=env, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("✅ Test data seeded")
            else:
                print(f"❌ Test data seeding failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Test data seeding failed: {e}")
            return False
        return True
    
    def start_test_server(self):
        """Start the test server"""
        print("🚀 Starting Test Server")
        print("=" * 60)
        
        try:
            # Pass the test environment variables to the server script
            env = os.environ.copy()
            env['DATABASE_URL'] = TestConfig.get_test_database_url()
            env['TABLE_PREFIX'] = TestConfig.TEST_TABLE_PREFIX
            
            # Start server in background
            self.server_process = subprocess.Popen([
                'python', 'test_server.py'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is running
            if self.server_process.poll() is None:
                print("✅ Test server started successfully!")
                print(f"🌐 Server URL: {TestConfig.TEST_SERVER_URL}")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ Server failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_test_server(self):
        """Stop the test server"""
        if self.server_process:
            print("🛑 Stopping test server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Test server stopped")
    
    def run_test(self, test_script):
        """Run a single test script"""
        print(f"\n🧪 Running: {test_script}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # Update test scripts to use test server URL
            env = os.environ.copy()
            env['BASE_URL'] = TestConfig.TEST_SERVER_URL
            
            result = subprocess.run(['python', test_script], 
                                  env=env, capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ {test_script}: PASS ({duration:.1f}s)")
                self.test_results[test_script] = {
                    'status': 'PASS',
                    'duration': duration,
                    'output': result.stdout
                }
                return True
            else:
                print(f"❌ {test_script}: FAIL ({duration:.1f}s)")
                print(f"Error: {result.stderr}")
                self.test_results[test_script] = {
                    'status': 'FAIL',
                    'duration': duration,
                    'output': result.stdout,
                    'error': result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_script}: TIMEOUT")
            self.test_results[test_script] = {
                'status': 'TIMEOUT',
                'duration': 300,
                'output': '',
                'error': 'Test timed out after 5 minutes'
            }
            return False
        except Exception as e:
            print(f"❌ {test_script}: ERROR - {e}")
            self.test_results[test_script] = {
                'status': 'ERROR',
                'duration': time.time() - start_time,
                'output': '',
                'error': str(e)
            }
            return False
    
    def run_all_tests(self):
        """Run all test scripts"""
        print("🧪 Running All Tests")
        print("=" * 60)
        
        # List of test scripts to run
        test_scripts = [
            'test_backup_api.py',
            'test_backup_functionality.py',
            'test_migration_system.py',
            'system_test.py',
            'test_email_functionality.py',
            'test_csv_export.py',
            'test_language_picker.py',
            'test_fixes.py',
            'test_refactor.py',
            'test_standalone.py',
            'test_server_url.py'
        ]
        
        passed = 0
        failed = 0
        
        for test_script in test_scripts:
            if os.path.exists(test_script):
                if self.run_test(test_script):
                    passed += 1
                else:
                    failed += 1
            else:
                print(f"⚠️ {test_script}: NOT FOUND")
        
        return passed, failed
    
    def print_summary(self, passed, failed):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for test_script, result in self.test_results.items():
                if result['status'] in ['FAIL', 'ERROR', 'TIMEOUT']:
                    print(f"   - {test_script}: {result['status']}")
                    if result.get('error'):
                        print(f"     Error: {result['error'][:100]}...")
        
        print(f"\n🌐 Test Server: {TestConfig.TEST_SERVER_URL}")
        print(f"🔑 Admin Login: {TestConfig.TEST_ADMIN_USERNAME} / {TestConfig.TEST_ADMIN_PASSWORD}")
        print(f"🗄️ Test Database: {TestConfig.TEST_DATABASE_NAME}")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT - Test suite passed with high success rate!")
        elif success_rate >= 80:
            print("\n✅ GOOD - Test suite passed with acceptable success rate")
        else:
            print("\n⚠️ NEEDS ATTENTION - Some tests failed")
    
    def cleanup(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        # Stop server
        self.stop_test_server()
        
        # Clean up environment
        TestConfig.cleanup_test_environment()
        
        print("✅ Cleanup complete!")
    
    def run_full_suite(self):
        """Run the complete test suite"""
        start_time = time.time()
        
        try:
            print("🚀 Starting Comprehensive Test Suite")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Setup
            self.setup_test_environment()
            
            # Start server
            if not self.start_test_server():
                print("❌ Failed to start test server. Aborting.")
                return False
            
            # Run tests
            passed, failed = self.run_all_tests()
            
            # Print summary
            self.print_summary(passed, failed)
            
            # Calculate total time
            total_time = time.time() - start_time
            print(f"\n⏱️ Total test suite time: {total_time:.1f} seconds")
            
            return failed == 0
            
        except KeyboardInterrupt:
            print("\n🛑 Test suite interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    runner = TestSuiteRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'setup':
            runner.setup_test_environment()
        elif command == 'seed':
            runner.seed_test_data()
        elif command == 'server':
            runner.setup_test_environment()
            runner.start_test_server()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                runner.cleanup()
        elif command == 'cleanup':
            runner.cleanup()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, seed, server, cleanup")
    else:
        # Run full test suite
        success = runner.run_full_suite()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 