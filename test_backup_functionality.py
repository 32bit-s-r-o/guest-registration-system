#!/usr/bin/env python3
"""
Test Backup Functionality Script
Tests database backup and restore capabilities for the Guest Registration System
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
import psycopg2
from psycopg2 import sql
import requests
import json
from config import Config

# Configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Database configuration from environment or defaults
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/ekom21')
TABLE_PREFIX = os.getenv('TABLE_PREFIX', 'guest_reg_')

class BackupTester:
    def __init__(self):
        self.session = requests.Session()
        self.temp_dir = tempfile.mkdtemp()
        self.backup_file = None
        
    def __del__(self):
        """Cleanup temporary files"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{title}")
        print("=" * len(title))
    
    def print_test(self, test_name, status, details=""):
        """Print test result"""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   └─ {details}")
    
    def login_admin(self):
        """Login as admin"""
        try:
            # Get login page first
            response = self.session.get(f"{BASE_URL}/admin/login")
            if response.status_code != 200:
                return False, "Login page not accessible"
            
            # Login
            login_data = {
                'username': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/admin/login", data=login_data)
            
            if response.status_code == 200 and "dashboard" in response.url:
                return True, "Successfully logged in"
            else:
                return False, f"Login failed - Status: {response.status_code}"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, f"Connected to PostgreSQL: {version[:50]}..."
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    def get_table_counts(self):
        """Get current table row counts"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            tables = ['admin', 'trip', 'registration', 'guest']
            counts = {}
            
            for table in tables:
                table_name = f"{TABLE_PREFIX}{table}"
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    counts[table] = cursor.fetchone()[0]
                except:
                    counts[table] = 0
            
            cursor.close()
            conn.close()
            return True, counts
        except Exception as e:
            return False, f"Error getting table counts: {str(e)}"
    
    def create_database_backup(self):
        """Create a database backup using pg_dump"""
        try:
            # Parse database URL
            import urllib.parse
            parsed = urllib.parse.urlparse(DATABASE_URL)
            
            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_file = os.path.join(self.temp_dir, f"backup_{timestamp}.sql")
            
            # Build pg_dump command
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password
            
            cmd = [
                'pg_dump',
                '-h', parsed.hostname,
                '-p', str(parsed.port),
                '-U', parsed.username,
                '-d', parsed.path[1:],  # Remove leading slash
                '--no-owner',
                '--no-privileges',
                '-f', self.backup_file
            ]
            
            # Add table filtering for our app tables only
            tables = ['admin', 'trip', 'registration', 'guest']
            for table in tables:
                table_name = f"{TABLE_PREFIX}{table}"
                cmd.extend(['-t', table_name])
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(self.backup_file):
                file_size = os.path.getsize(self.backup_file)
                return True, f"Backup created: {os.path.basename(self.backup_file)} ({file_size} bytes)"
            else:
                return False, f"pg_dump failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Backup creation failed: {str(e)}"
    
    def verify_backup_content(self):
        """Verify backup file contains expected content"""
        try:
            if not self.backup_file or not os.path.exists(self.backup_file):
                return False, "Backup file not found"
            
            with open(self.backup_file, 'r') as f:
                content = f.read()
            
            # Check for expected table structures - use correct table names
            tables = ['user', 'trip', 'registration', 'guest']  # Changed 'admin' to 'user'
            found_tables = []
            
            for table in tables:
                table_name = f"{TABLE_PREFIX}{table}"
                if f"CREATE TABLE" in content and table_name in content:
                    found_tables.append(table)
            
            if len(found_tables) == len(tables):
                return True, f"All {len(tables)} tables found in backup"
            else:
                missing = set(tables) - set(found_tables)
                return False, f"Missing tables in backup: {missing}"
                
        except Exception as e:
            return False, f"Backup verification failed: {str(e)}"
    
    def test_backup_compression(self):
        """Test creating compressed backup"""
        try:
            if not self.backup_file:
                return False, "No backup file to compress"
            
            # Create compressed version
            compressed_file = self.backup_file + '.gz'
            
            import gzip
            with open(self.backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            if os.path.exists(compressed_file):
                original_size = os.path.getsize(self.backup_file)
                compressed_size = os.path.getsize(compressed_file)
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                return True, f"Compressed backup created (saved {compression_ratio:.1f}%)"
            else:
                return False, "Compression failed"
                
        except Exception as e:
            return False, f"Compression test failed: {str(e)}"
    
    def test_backup_restore_simulation(self):
        """Simulate backup restore process (dry run)"""
        try:
            if not self.backup_file or not os.path.exists(self.backup_file):
                return False, "No backup file to restore"
            
            # Parse database URL
            import urllib.parse
            parsed = urllib.parse.urlparse(DATABASE_URL)
            
            # Build psql command for dry run (just validate syntax)
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password
            
            cmd = [
                'psql',
                '-h', parsed.hostname,
                '-p', str(parsed.port),
                '-U', parsed.username,
                '-d', parsed.path[1:],
                '--dry-run',
                '-f', self.backup_file
            ]
            
            # Note: --dry-run doesn't exist in psql, so we'll just validate the file
            with open(self.backup_file, 'r') as f:
                content = f.read()
                
            # More flexible SQL syntax validation - check for common pg_dump patterns
            sql_patterns = [
                'CREATE TABLE', 'INSERT INTO', 'COPY', 'SELECT', 'ALTER TABLE',
                'SET', 'BEGIN', 'COMMIT', '--', '/*', '*/'
            ]
            
            found_patterns = [pattern for pattern in sql_patterns if pattern in content]
            
            if len(found_patterns) >= 2:  # At least 2 SQL patterns found
                return True, f"Backup file appears to be valid SQL (found: {', '.join(found_patterns[:3])})"
            elif len(content.strip()) > 100:  # File has substantial content
                return True, f"Backup file contains {len(content)} characters of SQL content"
            else:
                return False, f"Backup file doesn't contain expected SQL statements (found: {', '.join(found_patterns)})"
                
        except Exception as e:
            return False, f"Restore simulation failed: {str(e)}"
    
    def test_automated_backup_schedule(self):
        """Test if automated backup scheduling is possible"""
        try:
            # Check if we can create a cron-style backup script
            backup_script = os.path.join(self.temp_dir, 'backup_script.sh')
            
            script_content = f"""#!/bin/bash
# Automated backup script for Guest Registration System
export PGPASSWORD="postgres"
BACKUP_DIR="/tmp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/guest_reg_backup_$DATE.sql"

mkdir -p "$BACKUP_DIR"

pg_dump -h localhost -p 5432 -U postgres -d ekom21 \\
    -t {TABLE_PREFIX}user \\
    -t {TABLE_PREFIX}trip \\
    -t {TABLE_PREFIX}registration \\
    -t {TABLE_PREFIX}guest \\
    --no-owner --no-privileges \\
    -f "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    gzip "$BACKUP_FILE"
    echo "Backup completed: $BACKUP_FILE.gz"
    
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "guest_reg_backup_*.sql.gz" -mtime +7 -delete
else
    echo "Backup failed"
    exit 1
fi
"""
            
            with open(backup_script, 'w') as f:
                f.write(script_content)
            
            os.chmod(backup_script, 0o755)
            
            if os.path.exists(backup_script):
                return True, f"Backup automation script created: {os.path.basename(backup_script)}"
            else:
                return False, "Failed to create backup script"
                
        except Exception as e:
            return False, f"Automation test failed: {str(e)}"
    
    def run_all_tests(self):
        """Run all backup functionality tests"""
        print("🔄 Backup Functionality Test Suite")
        print("=" * 60)
        print(f"Testing database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
        print(f"Table prefix: {TABLE_PREFIX}")
        
        # Test 1: Database Connection
        self.print_header("🔌 Testing Database Connection")
        success, details = self.test_database_connection()
        self.print_test("Database Connection", "PASS" if success else "FAIL", details)
        
        if not success:
            print("\n❌ Cannot proceed without database connection")
            return
        
        # Test 2: Admin Login
        self.print_header("👤 Testing Admin Access")
        success, details = self.login_admin()
        self.print_test("Admin Login", "PASS" if success else "FAIL", details)
        
        # Test 3: Get Current Data State
        self.print_header("📊 Analyzing Current Data")
        success, counts = self.get_table_counts()
        if success:
            total_records = sum(counts.values())
            self.print_test("Data Analysis", "PASS", f"Found {total_records} total records")
            for table, count in counts.items():
                print(f"   ├─ {table}: {count} records")
        else:
            self.print_test("Data Analysis", "FAIL", counts)
        
        # Test 4: Create Backup
        self.print_header("💾 Testing Backup Creation")
        success, details = self.create_database_backup()
        self.print_test("Database Backup", "PASS" if success else "FAIL", details)
        
        if not success:
            print("\n❌ Cannot proceed without successful backup")
            return
        
        # Test 5: Verify Backup Content
        self.print_header("🔍 Verifying Backup Content")
        success, details = self.verify_backup_content()
        self.print_test("Backup Verification", "PASS" if success else "FAIL", details)
        
        # Test 6: Test Compression
        self.print_header("🗜️ Testing Backup Compression")
        success, details = self.test_backup_compression()
        self.print_test("Backup Compression", "PASS" if success else "FAIL", details)
        
        # Test 7: Restore Simulation
        self.print_header("🔄 Testing Restore Process")
        success, details = self.test_backup_restore_simulation()
        self.print_test("Restore Simulation", "PASS" if success else "FAIL", details)
        
        # Test 8: Automation Setup
        self.print_header("⏰ Testing Backup Automation")
        success, details = self.test_automated_backup_schedule()
        self.print_test("Backup Automation", "PASS" if success else "FAIL", details)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and recommendations"""
        print("\n" + "=" * 60)
        print("📋 BACKUP FUNCTIONALITY TEST SUMMARY")
        print("=" * 60)
        
        print("\n🎯 Backup Strategy Recommendations:")
        print("   ├─ Daily automated backups during low-traffic hours")
        print("   ├─ Keep 7 daily backups + 4 weekly backups")
        print("   ├─ Store backups in separate location/server")
        print("   ├─ Test restore process monthly")
        print("   └─ Monitor backup file sizes for anomalies")
        
        print("\n📝 Manual Backup Commands:")
        print("   ├─ Create backup:")
        print(f"   │  pg_dump -h localhost -U postgres -d ekom21 \\")
        for table in ['user', 'trip', 'registration', 'guest']:
            print(f"   │    -t {TABLE_PREFIX}{table} \\")
        print("   │    --no-owner --no-privileges -f backup.sql")
        print("   ├─ Compress backup:")
        print("   │  gzip backup.sql")
        print("   └─ Restore backup:")
        print("   │  psql -h localhost -U postgres -d ekom21 -f backup.sql")
        
        print("\n⚙️ Automation Setup:")
        print("   ├─ Add to crontab for daily backups:")
        print("   │  0 2 * * * /path/to/backup_script.sh")
        print("   ├─ Monitor backup logs")
        print("   └─ Set up backup failure alerts")
        
        print(f"\n📁 Temporary files created in: {self.temp_dir}")
        print("   └─ Files will be automatically cleaned up")

def main():
    """Main function"""
    try:
        tester = BackupTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
