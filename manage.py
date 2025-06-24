#!/usr/bin/env python3
"""
Universal Management Script for Guest Registration System
Handles tests, migrations, seeds, backups, Docker operations, and system operations
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
            'docker': self.docker_operations,
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

    def docker_operations(self, args=None):
        """Handle Docker operations"""
        print("🐳 Docker Operations")
        print("=" * 50)
        
        if not args:
            print("Available Docker operations:")
            print("  build [platform] [tag] [registry]           - Build Docker image")
            print("  up [service]                                - Start Docker Compose services") 
            print("  down                                        - Stop Docker Compose services")
            print("  logs [service]                              - Show Docker logs")
            print("  status                                      - Show Docker service status")
            print("  clean                                       - Clean Docker resources")
            print("  push [tag] [registry]                       - Push image to registry")
            print("  multi-build [platforms] [tag] [registry]    - Build for multiple platforms")
            print("  all-platforms [tag] [registry] [push]       - Build for ALL processor architectures")
            print("  buildx-setup                                - Setup Docker buildx for multiplatform builds")
            print("  build-individual [platform] [tag] [registry] - Build Docker image for a single platform")
            print("  diagnose                                    - Diagnose Docker build issues")
            print("")
            print("Examples:")
            print("  python manage.py docker build")
            print("  python manage.py docker build linux/amd64 myapp:v1.0")
            print("  python manage.py docker multi-build \"linux/amd64,linux/arm64\" myapp:v1.0 docker.io/myuser")
            print("  python manage.py docker all-platforms myapp:v1.0 ghcr.io/myuser true")
            return True
        
        operation = args[0]
        
        if operation == 'build':
            return self._docker_build(args[1:] if len(args) > 1 else [])
        elif operation == 'up':
            return self._docker_up(args[1:] if len(args) > 1 else [])
        elif operation == 'down':
            return self._docker_down()
        elif operation == 'logs':
            return self._docker_logs(args[1:] if len(args) > 1 else [])
        elif operation == 'status':
            return self._docker_status()
        elif operation == 'clean':
            return self._docker_clean()
        elif operation == 'push':
            return self._docker_push(args[1:] if len(args) > 1 else [])
        elif operation == 'multi-build':
            return self._docker_multi_build(args[1:] if len(args) > 1 else [])
        elif operation == 'all-platforms':
            return self._docker_all_platforms(args[1:] if len(args) > 1 else [])
        elif operation == 'buildx-setup':
            return self._docker_buildx_setup()
        elif operation == 'build-individual':
            return self._docker_build_individual(args[1:] if len(args) > 1 else [])
        elif operation == 'diagnose':
            return self._docker_diagnose()
        else:
            print(f"❌ Unknown Docker operation: {operation}")
            return False

    def _docker_build(self, args):
        """Build Docker image with optional registry support"""
        platform = args[0] if args else 'linux/amd64'  # Default to x86_64
        tag = args[1] if len(args) > 1 else 'guest-registration:latest'
        registry = args[2] if len(args) > 2 else None
        
        # Add registry prefix if provided
        if registry:
            if not tag.startswith(registry):
                full_tag = f"{registry.rstrip('/')}/{tag}"
            else:
                full_tag = tag
        else:
            full_tag = tag
        
        print(f"🔨 Building Docker image for {platform}")
        print(f"Tag: {full_tag}")
        if registry:
            print(f"Registry: {registry}")
        
        try:
            # Setup buildx builder if needed
            self._ensure_buildx_builder()
            
            cmd = [
                'docker', 'buildx', 'build',
                '--platform', platform,
                '--tag', full_tag,
                '--file', 'Dockerfile',
                '--load',  # Load image to local Docker after build
                '.'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("SUCCESS", f"Docker image built successfully: {full_tag}")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log_action("FAILED", f"Docker build failed")
                if result.stderr.strip():
                    print("STDERR:", result.stderr)
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Docker build failed: {e}")
            return False

    def _docker_multi_build(self, args):
        """Build Docker image for multiple platforms with registry support"""
        # Parse arguments
        platforms_arg = args[0] if args else 'linux/amd64,linux/arm64'
        tag = args[1] if len(args) > 1 else 'guest-registration:latest'
        registry = args[2] if len(args) > 2 else None
        
        # Parse platforms
        if ',' in platforms_arg:
            platforms = [p.strip() for p in platforms_arg.split(',')]
        else:
            platforms = [platforms_arg]
        
        # Add registry prefix if provided
        if registry:
            if not tag.startswith(registry):
                full_tag = f"{registry.rstrip('/')}/{tag}"
            else:
                full_tag = tag
        else:
            full_tag = tag
        
        print(f"🔨 Building multi-platform Docker image")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"Tag: {full_tag}")
        if registry:
            print(f"Registry: {registry}")
        
        try:
            # Setup buildx builder with enhanced configuration
            if not self._ensure_buildx_builder():
                self.log_action("ERROR", "Failed to setup buildx builder")
                return False
            
            # Clean up any existing build cache that might be causing issues
            self.log_action("INFO", "Cleaning build cache to prevent context cancellation issues")
            subprocess.run(['docker', 'builder', 'prune', '-f'], capture_output=True)
            
            # Build for multiple platforms with enhanced options
            platform_arg = ','.join(platforms)
            cmd = [
                'docker', 'buildx', 'build',
                '--platform', platform_arg,
                '--tag', full_tag,
                '--file', 'Dockerfile',
                '--progress', 'plain',  # Better progress reporting
                '--no-cache',  # Avoid cache issues
                '--build-arg', 'BUILDKIT_INLINE_CACHE=1'  # Enable inline cache
            ]
            
            # Add push or load flag based on registry
            if registry:
                cmd.append('--push')  # Push to registry
                print("Will push to registry after build")
            else:
                # For local builds without registry, we can't load multi-platform images
                # So we'll build without load/push (just builds and discards)
                print("Local multi-platform build (images will not be loaded to local Docker)")
            
            cmd.append('.')
            
            # Run with increased timeout and better error handling
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 60 min timeout
            
            if result.returncode == 0:
                self.log_action("SUCCESS", f"Multi-platform Docker image built successfully: {full_tag}")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log_action("FAILED", f"Multi-platform Docker build failed with code {result.returncode}")
                if result.stderr.strip():
                    print("STDERR:", result.stderr)
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                
                # Provide specific guidance for common errors
                if "context canceled" in result.stderr.lower():
                    print("\n💡 Context cancellation usually indicates:")
                    print("   - Insufficient memory/CPU resources")
                    print("   - Network timeout during registry push")
                    print("   - Docker daemon issues")
                    print("\n🔧 Try these solutions:")
                    print("   1. Increase Docker memory limit (8GB+ recommended)")
                    print("   2. Build platforms one by one: python manage.py docker build linux/amd64")
                    print("   3. Check Docker daemon logs: docker system info")
                    print("   4. Restart Docker daemon")
                
                return False
                
        except subprocess.TimeoutExpired:
            self.log_action("TIMEOUT", f"Multi-platform Docker build timed out after 60 minutes")
            print("\n💡 Build timeout suggestions:")
            print("   - Try building fewer platforms at once")
            print("   - Increase Docker resources")
            print("   - Check network connectivity")
            return False
        except Exception as e:
            self.log_action("ERROR", f"Multi-platform Docker build failed with exception: {e}")
            return False

    def _docker_up(self, args):
        """Start Docker Compose services"""
        service = args[0] if args else None
        
        print("🚀 Starting Docker Compose services")
        
        try:
            cmd = ['docker-compose', 'up', '-d']
            if service:
                cmd.append(service)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("SUCCESS", "Docker Compose services started")
                print(result.stdout)
                return True
            else:
                self.log_action("FAILED", "Failed to start Docker Compose services")
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Failed to start Docker services: {e}")
            return False

    def _docker_down(self):
        """Stop Docker Compose services"""
        print("🛑 Stopping Docker Compose services")
        
        try:
            result = subprocess.run(['docker-compose', 'down'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("SUCCESS", "Docker Compose services stopped")
                print(result.stdout)
                return True
            else:
                self.log_action("FAILED", "Failed to stop Docker Compose services")
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Failed to stop Docker services: {e}")
            return False

    def _docker_logs(self, args):
        """Show Docker logs"""
        service = args[0] if args else None
        
        print("📋 Showing Docker logs")
        
        try:
            cmd = ['docker-compose', 'logs', '-f']
            if service:
                cmd.append(service)
            
            # Run without capture to show real-time logs
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                return True
            else:
                self.log_action("FAILED", "Failed to show Docker logs")
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Failed to show Docker logs: {e}")
            return False

    def _docker_status(self):
        """Show Docker service status"""
        print("📊 Docker Service Status")
        
        try:
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                self.log_action("FAILED", "Failed to get Docker service status")
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Failed to get Docker status: {e}")
            return False

    def _docker_clean(self):
        """Clean Docker resources"""
        print("🧹 Cleaning Docker resources")
        
        try:
            # Stop and remove containers
            subprocess.run(['docker-compose', 'down', '--volumes', '--remove-orphans'], 
                         capture_output=True)
            
            # Remove unused images
            subprocess.run(['docker', 'image', 'prune', '-f'], capture_output=True)
            
            # Remove unused volumes
            subprocess.run(['docker', 'volume', 'prune', '-f'], capture_output=True)
            
            # Remove unused networks
            subprocess.run(['docker', 'network', 'prune', '-f'], capture_output=True)
            
            self.log_action("SUCCESS", "Docker resources cleaned")
            return True
            
        except Exception as e:
            self.log_action("ERROR", f"Failed to clean Docker resources: {e}")
            return False

    def _docker_push(self, args):
        """Push Docker image to registry"""
        tag = args[0] if args else 'guest-registration:latest'
        registry = args[1] if len(args) > 1 else None
        
        # Add registry prefix if provided
        if registry:
            if not tag.startswith(registry):
                full_tag = f"{registry.rstrip('/')}/{tag}"
            else:
                full_tag = tag
        else:
            full_tag = tag
        
        print(f"📤 Pushing Docker image: {full_tag}")
        if registry:
            print(f"Registry: {registry}")
        
        try:
            result = subprocess.run(['docker', 'push', full_tag], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("SUCCESS", f"Docker image pushed: {full_tag}")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log_action("FAILED", f"Failed to push Docker image: {full_tag}")
                if result.stderr.strip():
                    print("STDERR:", result.stderr)
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Failed to push Docker image: {e}")
            return False

    def _docker_all_platforms(self, args):
        """Build Docker image for ALL supported platforms with registry support"""
        tag = args[0] if args else 'guest-registration:latest'
        registry = args[1] if len(args) > 1 else None
        push = args[2] if len(args) > 2 else 'false'
        
        # Add registry prefix if provided
        if registry:
            if not tag.startswith(registry):
                full_tag = f"{registry.rstrip('/')}/{tag}"
            else:
                full_tag = tag
        else:
            full_tag = tag
        
        # Convert push to boolean
        should_push = push.lower() in ['true', '1', 'yes', 'y']
        
        print(f"🌍 Building Docker image for ALL processor architectures")
        print(f"Tag: {full_tag}")
        if registry:
            print(f"Registry: {registry}")
        print(f"Push to registry: {should_push}")
        
        # All supported platforms
        all_platforms = [
            'linux/amd64',      # x86_64
            'linux/arm64',      # ARM64 (Apple Silicon, ARM servers)
            'linux/arm/v7',     # ARM v7 (Raspberry Pi, etc.)
            'linux/arm/v6',     # ARM v6 (older ARM devices)
            'linux/386',        # 32-bit x86
            'linux/ppc64le',    # PowerPC 64-bit little endian
            'linux/s390x',      # IBM Z architecture
            'linux/riscv64'     # RISC-V 64-bit
        ]
        
        try:
            # Check if dedicated script exists, otherwise use built-in method
            script_path = self.project_root / 'scripts' / 'build_all_platforms.sh'
            
            if script_path.exists():
                # Use the dedicated script
                cmd = [str(script_path), full_tag, str(should_push).lower()]
                
                self.log_action("RUNNING", f"build_all_platforms.sh {full_tag} {should_push}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
                
                if result.returncode == 0:
                    self.log_action("SUCCESS", f"All-platform Docker build completed successfully")
                    if result.stdout.strip():
                        print(result.stdout)
                    return True
                else:
                    self.log_action("FAILED", f"All-platform Docker build failed")
                    if result.stderr.strip():
                        print("STDERR:", result.stderr)
                    if result.stdout.strip():
                        print("STDOUT:", result.stdout)
                    return False
            else:
                # Use built-in method
                print("Script not found, using built-in multi-platform build...")
                
                # Setup buildx builder
                self._ensure_buildx_builder()
                
                platform_arg = ','.join(all_platforms)
                cmd = [
                    'docker', 'buildx', 'build',
                    '--platform', platform_arg,
                    '--tag', full_tag,
                    '--file', 'Dockerfile'
                ]
                
                if should_push and registry:
                    cmd.append('--push')
                    print("Will push to registry after build")
                else:
                    print("Local build (images will not be loaded to local Docker)")
                
                cmd.append('.')
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
                
                if result.returncode == 0:
                    self.log_action("SUCCESS", f"All-platform Docker build completed successfully: {full_tag}")
                    if result.stdout.strip():
                        print(result.stdout)
                    return True
                else:
                    self.log_action("FAILED", f"All-platform Docker build failed")
                    if result.stderr.strip():
                        print("STDERR:", result.stderr)
                    if result.stdout.strip():
                        print("STDOUT:", result.stdout)
                    return False
                
        except subprocess.TimeoutExpired:
            self.log_action("TIMEOUT", f"All-platform Docker build timed out after 30 minutes")
            return False
        except Exception as e:
            self.log_action("ERROR", f"All-platform Docker build failed with exception: {e}")
            return False

    def _ensure_buildx_builder(self):
        """Ensure Docker buildx builder is set up for multi-platform builds"""
        try:
            # Check if a builder exists
            result = subprocess.run(['docker', 'buildx', 'ls'], capture_output=True, text=True)
            
            if 'multi-builder' not in result.stdout:
                self.log_action("INFO", "Creating Docker buildx builder for multi-platform builds")
                
                # Create and use multi-platform builder
                create_result = subprocess.run([
                    'docker', 'buildx', 'create', 
                    '--name', 'multi-builder',
                    '--driver', 'docker-container',
                    '--use'
                ], capture_output=True, text=True)
                
                if create_result.returncode != 0:
                    self.log_action("WARNING", f"Failed to create buildx builder: {create_result.stderr}")
                    return False
                
                # Bootstrap the builder
                bootstrap_result = subprocess.run([
                    'docker', 'buildx', 'inspect', '--bootstrap'
                ], capture_output=True, text=True)
                
                if bootstrap_result.returncode != 0:
                    self.log_action("WARNING", f"Failed to bootstrap buildx builder: {bootstrap_result.stderr}")
                    return False
                
                self.log_action("SUCCESS", "Docker buildx builder created successfully")
            else:
                # Use existing multi-builder if available
                subprocess.run(['docker', 'buildx', 'use', 'multi-builder'], capture_output=True)
            
            return True
            
        except Exception as e:
            self.log_action("ERROR", f"Failed to setup buildx builder: {e}")
            return False

    def _docker_buildx_setup(self):
        """Setup Docker buildx for multi-platform builds"""
        print("🔧 Setting up Docker buildx for multi-platform builds")
        print("=" * 50)
        
        try:
            # Check Docker version
            version_result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if version_result.returncode == 0:
                print(f"Docker version: {version_result.stdout.strip()}")
            
            # Check buildx availability
            buildx_result = subprocess.run(['docker', 'buildx', 'version'], capture_output=True, text=True)
            if buildx_result.returncode != 0:
                self.log_action("ERROR", "Docker buildx is not available")
                print("Please update to a newer version of Docker that includes buildx")
                return False
            
            print(f"Docker buildx version: {buildx_result.stdout.strip()}")
            
            # List current builders
            ls_result = subprocess.run(['docker', 'buildx', 'ls'], capture_output=True, text=True)
            print("\nCurrent builders:")
            print(ls_result.stdout)
            
            # Create/setup multi-platform builder
            if self._ensure_buildx_builder():
                print("\n✅ Multi-platform builder is ready")
                
                # Inspect the builder to show supported platforms
                inspect_result = subprocess.run([
                    'docker', 'buildx', 'inspect', 'multi-builder'
                ], capture_output=True, text=True)
                
                if inspect_result.returncode == 0:
                    print("\nBuilder details:")
                    print(inspect_result.stdout)
                
                return True
            else:
                print("\n❌ Failed to setup multi-platform builder")
                return False
            
        except Exception as e:
            self.log_action("ERROR", f"Buildx setup failed: {e}")
            return False

    def _docker_build_individual(self, args):
        """Build Docker image for a single platform"""
        platform = args[0] if args else 'linux/amd64'
        tag = args[1] if len(args) > 1 else 'guest-registration:latest'
        registry = args[2] if len(args) > 2 else None
        
        # Add registry prefix if provided
        if registry:
            if not tag.startswith(registry):
                full_tag = f"{registry.rstrip('/')}/{tag}"
            else:
                full_tag = tag
        else:
            full_tag = tag
        
        print(f"🔨 Building Docker image for {platform}")
        print(f"Tag: {full_tag}")
        if registry:
            print(f"Registry: {registry}")
        
        try:
            # Setup buildx builder if needed
            self._ensure_buildx_builder()
            
            cmd = [
                'docker', 'buildx', 'build',
                '--platform', platform,
                '--tag', full_tag,
                '--file', 'Dockerfile',
                '--load',  # Load image to local Docker after build
                '.'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("SUCCESS", f"Docker image built successfully: {full_tag}")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log_action("FAILED", f"Docker build failed")
                if result.stderr.strip():
                    print("STDERR:", result.stderr)
                if result.stdout.strip():
                    print("STDOUT:", result.stdout)
                return False
                
        except Exception as e:
            self.log_action("ERROR", f"Docker build failed: {e}")
            return False

    def _docker_diagnose(self):
        """Diagnose Docker build issues"""
        print("🔍 Diagnosing Docker build issues")
        print("=" * 50)
        
        try:
            # Check Docker version
            version_result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if version_result.returncode != 0:
                self.log_action("ERROR", "Docker is not installed")
                print("Please install Docker to diagnose build issues")
                return False
            
            print(f"Docker version: {version_result.stdout.strip()}")
            
            # Check buildx availability
            buildx_result = subprocess.run(['docker', 'buildx', 'version'], capture_output=True, text=True)
            if buildx_result.returncode != 0:
                self.log_action("ERROR", "Docker buildx is not available")
                print("Please update to a newer version of Docker that includes buildx")
                return False
            
            print(f"Docker buildx version: {buildx_result.stdout.strip()}")
            
            # List current builders
            ls_result = subprocess.run(['docker', 'buildx', 'ls'], capture_output=True, text=True)
            print("\nCurrent builders:")
            print(ls_result.stdout)
            
            # Check for common build issues
            print("\n🔍 Checking for common build issues...")
            
            # Check for insufficient memory
            memory_result = subprocess.run(['docker', 'system', 'df', '-v'], capture_output=True, text=True)
            if 'No space left on device' in memory_result.stdout:
                self.log_action("WARNING", "Insufficient Docker disk space")
                print("💡 Consider freeing up disk space")
            
            # Check for insufficient CPU
            cpu_result = subprocess.run(['docker', 'system', 'info'], capture_output=True, text=True)
            if 'CPUs' in cpu_result.stdout:
                cpu_count = int(cpu_result.stdout.split('CPUs: ')[1].split('/')[0])
                if cpu_count < 2:
                    self.log_action("WARNING", "Insufficient Docker CPU resources")
                    print("💡 Consider adding more CPUs")
            
            # Check for network issues
            network_result = subprocess.run(['docker', 'network', 'ls'], capture_output=True, text=True)
            if 'No networks found' in network_result.stdout:
                self.log_action("WARNING", "No Docker networks found")
                print("💡 Consider creating a network")
            
            # Check for Docker daemon issues
            daemon_result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            if 'Error' in daemon_result.stdout:
                self.log_action("ERROR", "Docker daemon is not running")
                print("💡 Consider restarting Docker")
            
            # Check for Docker image issues
            image_result = subprocess.run(['docker', 'images', '-a'], capture_output=True, text=True)
            if 'No images found' in image_result.stdout:
                self.log_action("WARNING", "No Docker images found")
                print("💡 Consider building a new image")
            
            # Check for Docker container issues
            container_result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
            if 'No containers found' in container_result.stdout:
                self.log_action("WARNING", "No Docker containers found")
                print("💡 Consider running a new container")
            
            self.log_action("SUCCESS", "Docker build issues diagnosed")
            return True
            
        except Exception as e:
            self.log_action("ERROR", f"Docker diagnose failed: {e}")
            return False

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Universal Management Script for Guest Registration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic operations
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

  # Docker operations
  python manage.py docker                                    # List Docker operations
  python manage.py docker buildx-setup                       # Setup buildx for multiplatform
  python manage.py docker build                              # Build for current platform
  python manage.py docker build linux/amd64 myapp:v1.0      # Build for specific platform
  python manage.py docker build linux/arm64 myapp:v1.0 docker.io/user  # Build with registry
  
  # Multi-platform builds
  python manage.py docker multi-build                        # Build for amd64,arm64
  python manage.py docker multi-build "linux/amd64,linux/arm64" myapp:v1.0
  python manage.py docker multi-build "linux/amd64,linux/arm64" myapp:v1.0 ghcr.io/user
  
  # Individual platform builds (fallback for multi-platform issues)
  python manage.py docker build-individual linux/amd64 myapp:v1.0
  python manage.py docker build-individual linux/arm64 myapp:v1.0 docker.io/user
  
  # All-platform builds (8 architectures)
  python manage.py docker all-platforms                      # Build for all platforms
  python manage.py docker all-platforms myapp:v1.0          # With custom tag
  python manage.py docker all-platforms myapp:v1.0 docker.io/user  # With registry
  python manage.py docker all-platforms myapp:v1.0 docker.io/user true  # And push
  
  # Troubleshooting
  python manage.py docker diagnose                           # Diagnose build issues
  
  # Docker Compose
  python manage.py docker up               # Start Docker Compose services
  python manage.py docker down             # Stop Docker Compose services
  python manage.py docker status           # Show Docker service status
  python manage.py docker logs app         # Show application logs
        """
    )
    
    parser.add_argument('command', 
                       choices=['test', 'migrate', 'seed', 'backup', 'utility', 'status', 'clean', 'setup', 'docker', 'all'],
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