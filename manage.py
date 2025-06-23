#!/usr/bin/env python3
"""
Universal Management Script for Guest Registration System
Handles tests, migrations, seeds, backups, and system operations
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime
from pathlib import Path

class SystemManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.scripts = {
            'tests': [
                'test_backup_api.py',
                'test_backup_functionality.py', 
                'test_migration_system.py',
                'system_test.py',
                'test_email_functionality.py',
                'test_csv_export.py',
                'test_language_picker.py'
            ],
            'migrations': [
                'migrations.py'
            ],
            'seeds': [
                'create_test_registration.py',
                'create_housekeeper_data.py'
            ],
            'backups': [
                'test_backup_functionality.py'
            ],
            'utilities': [
                'extract_translations.py',
                'add_missing_czech_translations.py',
                'fix_fuzzy_translations.py',
                'fix_user_sequence.py',
                'migrate_age_language_photo.py',
                'migrate_confirm_code.py',
                'migrate_to_user_role_system.py',
                'quick_reset.py',
                'reset_data.py',
                'setup.py'
            ]
        }
        
        self.available_commands = {
            'test': self.run_tests,
            'migrate': self.run_migrations,
            'seed': self.run_seeds,
            'backup': self.run_backups,
            'utility': self.run_utilities,
            'status': self.show_status,
            'clean': self.cleanup,
            'setup': self.setup_system,
            'all': self.run_all
        }
    
    def log_action(self, action, message=""):
        """Log actions with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {action}: {message}")
    
    def run_script(self, script_name, args=None):
        """Run a Python script and return success status"""
        try:
            script_path = self.project_root / script_name
            if not script_path.exists():
                self.log_action("ERROR", f"Script not found: {script_name}")
                return False
            
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
            
            self.log_action("RUNNING", f"{script_name} {' '.join(args) if args else ''}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_action("SUCCESS", f"{script_name} completed successfully")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log_action("FAILED", f"{script_name} failed with return code {result.returncode}")
                if result.stderr.strip():
                    print("STDERR:", result.stderr)
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_action("TIMEOUT", f"{script_name} timed out after 5 minutes")
            return False
        except Exception as e:
            self.log_action("ERROR", f"{script_name} failed with exception: {e}")
            return False
    
    def run_tests(self, args=None):
        """Run all available tests"""
        print("🧪 Running All Tests")
        print("=" * 50)
        
        test_results = {}
        total_tests = len(self.scripts['tests'])
        passed_tests = 0
        
        for test_script in self.scripts['tests']:
            if self.run_script(test_script, args):
                test_results[test_script] = "PASS"
                passed_tests += 1
            else:
                test_results[test_script] = "FAIL"
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        for test, result in test_results.items():
            status_emoji = "✅" if result == "PASS" else "❌"
            print(f"{status_emoji} {test}: {result}")
        
        print(f"\nTests Passed: {passed_tests}/{total_tests}")
        return passed_tests == total_tests
    
    def run_migrations(self, args=None):
        """Run migration operations"""
        print("🔄 Running Migration Operations")
        print("=" * 50)
        
        if not args:
            args = ['status']
        
        migration_script = self.scripts['migrations'][0]
        return self.run_script(migration_script, args)
    
    def run_seeds(self, args=None):
        """Run seed data operations"""
        print("🌱 Running Seed Operations")
        print("=" * 50)
        
        seed_results = {}
        for seed_script in self.scripts['seeds']:
            if self.run_script(seed_script, args):
                seed_results[seed_script] = "SUCCESS"
            else:
                seed_results[seed_script] = "FAILED"
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Seed Results Summary")
        print("=" * 50)
        for seed, result in seed_results.items():
            status_emoji = "✅" if result == "SUCCESS" else "❌"
            print(f"{status_emoji} {seed}: {result}")
        
        return all(result == "SUCCESS" for result in seed_results.values())
    
    def run_backups(self, args=None):
        """Run backup operations"""
        print("💾 Running Backup Operations")
        print("=" * 50)
        
        backup_script = self.scripts['backups'][0]
        return self.run_script(backup_script, args)
    
    def run_utilities(self, args=None):
        """Run utility scripts"""
        print("🔧 Running Utility Operations")
        print("=" * 50)
        
        if not args:
            print("Available utilities:")
            for i, utility in enumerate(self.scripts['utilities'], 1):
                print(f"  {i}. {utility}")
            return True
        
        utility_results = {}
        for utility_script in self.scripts['utilities']:
            if self.run_script(utility_script, args):
                utility_results[utility_script] = "SUCCESS"
            else:
                utility_results[utility_script] = "FAILED"
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Utility Results Summary")
        print("=" * 50)
        for utility, result in utility_results.items():
            status_emoji = "✅" if result == "SUCCESS" else "❌"
            print(f"{status_emoji} {utility}: {result}")
        
        return all(result == "SUCCESS" for result in utility_results.values())
    
    def show_status(self, args=None):
        """Show system status"""
        print("📊 System Status")
        print("=" * 50)
        
        # Check if Flask app is running
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'python app.py' in result.stdout:
                print("✅ Flask application is running")
            else:
                print("❌ Flask application is not running")
        except:
            print("⚠️ Could not check Flask application status")
        
        # Check database connection
        try:
            from migrations import MigrationManager
            manager = MigrationManager()
            current_version = manager.get_current_version()
            applied_migrations = manager.get_applied_migrations()
            pending_migrations = manager.get_pending_migrations()
            
            print(f"📊 Database Version: {current_version}")
            print(f"📊 Applied Migrations: {len(applied_migrations)}")
            print(f"📊 Pending Migrations: {len(pending_migrations)}")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
        
        # Check available scripts
        print(f"\n📁 Available Scripts:")
        for category, scripts in self.scripts.items():
            print(f"  {category.title()}: {len(scripts)} scripts")
        
        return True
    
    def cleanup(self, args=None):
        """Clean up temporary files and caches"""
        print("🧹 Running Cleanup Operations")
        print("=" * 50)
        
        cleanup_items = [
            '*.pyc',
            '__pycache__',
            '*.log',
            '*.tmp',
            'backup_*.sql',
            'backup_*.sql.gz'
        ]
        
        cleaned_count = 0
        for pattern in cleanup_items:
            try:
                if '*' in pattern:
                    # Use find command for wildcard patterns
                    result = subprocess.run(['find', '.', '-name', pattern, '-type', 'f'], 
                                          capture_output=True, text=True)
                    files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                    
                    for file in files:
                        if file and os.path.exists(file):
                            os.remove(file)
                            self.log_action("CLEANED", f"Removed {file}")
                            cleaned_count += 1
                else:
                    # Remove directories
                    if os.path.exists(pattern):
                        import shutil
                        shutil.rmtree(pattern)
                        self.log_action("CLEANED", f"Removed directory {pattern}")
                        cleaned_count += 1
                        
            except Exception as e:
                self.log_action("ERROR", f"Failed to clean {pattern}: {e}")
        
        print(f"\n✅ Cleanup completed. Removed {cleaned_count} items.")
        return True
    
    def setup_system(self, args=None):
        """Setup the system from scratch"""
        print("🚀 Setting Up System")
        print("=" * 50)
        
        setup_steps = [
            ("Creating directories", self._create_directories),
            ("Running migrations", lambda: self.run_migrations(['migrate'])),
            ("Creating seed data", lambda: self.run_seeds()),
            ("Running tests", lambda: self.run_tests()),
            ("Creating backup", lambda: self.run_backups())
        ]
        
        for step_name, step_func in setup_steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"❌ {step_name} failed")
                return False
            print(f"✅ {step_name} completed")
        
        print("\n🎉 System setup completed successfully!")
        return True
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = ['migrations', 'uploads', 'static/sample_images', 'translations']
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.log_action("CREATED", f"Directory: {directory}")
        
        return True
    
    def run_all(self, args=None):
        """Run all operations in sequence"""
        print("🎯 Running All Operations")
        print("=" * 50)
        
        operations = [
            ("Status Check", self.show_status),
            ("Cleanup", self.cleanup),
            ("Migrations", lambda: self.run_migrations(['migrate'])),
            ("Seeds", self.run_seeds),
            ("Tests", self.run_tests),
            ("Backups", self.run_backups)
        ]
        
        results = {}
        for op_name, op_func in operations:
            print(f"\n🔄 Running {op_name}...")
            try:
                results[op_name] = op_func()
            except Exception as e:
                self.log_action("ERROR", f"{op_name} failed: {e}")
                results[op_name] = False
        
        # Print final summary
        print("\n" + "=" * 50)
        print("📊 All Operations Summary")
        print("=" * 50)
        
        for op_name, result in results.items():
            status_emoji = "✅" if result else "❌"
            print(f"{status_emoji} {op_name}: {'SUCCESS' if result else 'FAILED'}")
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        print(f"\nOverall Success: {success_count}/{total_count}")
        return success_count == total_count

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Universal Management Script for Guest Registration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage.py test                    # Run all tests
  python manage.py migrate status          # Check migration status
  python manage.py migrate migrate         # Run pending migrations
  python manage.py seed                    # Run seed operations
  python manage.py backup                  # Run backup operations
  python manage.py utility                 # List available utilities
  python manage.py status                  # Show system status
  python manage.py clean                   # Clean up temporary files
  python manage.py setup                   # Setup system from scratch
  python manage.py all                     # Run all operations
        """
    )
    
    parser.add_argument('command', 
                       choices=['test', 'migrate', 'seed', 'backup', 'utility', 'status', 'clean', 'setup', 'all'],
                       help='Command to execute')
    
    parser.add_argument('args', nargs='*', 
                       help='Additional arguments for the command')
    
    args = parser.parse_args()
    
    # Initialize system manager
    manager = SystemManager()
    
    # Execute command
    if args.command in manager.available_commands:
        try:
            success = manager.available_commands[args.command](args.args)
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\n⚠️ Operation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Command failed: {e}")
            sys.exit(1)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 