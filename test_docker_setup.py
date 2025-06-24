#!/usr/bin/env python3
"""
Test Docker Setup for Guest Registration System
Verifies Docker configuration, files, and build readiness
"""

import os
import sys
import subprocess
from pathlib import Path

def test_docker_files():
    """Test that all required Docker files exist"""
    print("🔍 Testing Docker Files")
    print("=" * 50)
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        'nginx.conf',
        '.dockerignore',
        'config.env.production'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("\n✅ All Docker files present")
    return True

def test_docker_commands():
    """Test Docker command availability"""
    print("\n🔍 Testing Docker Commands")
    print("=" * 50)
    
    commands = {
        'docker': 'Docker Engine',
        'docker-compose': 'Docker Compose'
    }
    
    missing_commands = []
    for cmd, description in commands.items():
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"✅ {description}: {version}")
            else:
                print(f"❌ {description}: Not available")
                missing_commands.append(cmd)
        except FileNotFoundError:
            print(f"❌ {description}: Not installed")
            missing_commands.append(cmd)
    
    # Test Docker Buildx separately
    try:
        result = subprocess.run(['docker', 'buildx', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Docker Buildx: {version}")
        else:
            print("❌ Docker Buildx: Not available")
            missing_commands.append('docker buildx')
    except Exception:
        print("❌ Docker Buildx: Not installed")
        missing_commands.append('docker buildx')
    
    if missing_commands:
        print(f"\n❌ Missing commands: {', '.join(missing_commands)}")
        return False
    
    print("\n✅ All Docker commands available")
    return True

def test_platform_support():
    """Test multi-platform support"""
    print("\n🔍 Testing Platform Support")
    print("=" * 50)
    
    platforms = [
        'linux/amd64',  # x86_64 architecture
        'linux/arm64',  # ARM 64-bit
        'linux/arm/v7'  # ARM 32-bit
    ]
    
    try:
        # Check if buildx is available
        result = subprocess.run(['docker', 'buildx', 'version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker Buildx not available - multi-platform builds not supported")
            return False
        
        print("✅ Docker Buildx available for multi-platform builds")
        
        # Check available platforms
        result = subprocess.run(['docker', 'buildx', 'inspect', '--bootstrap'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Multi-platform builder ready")
            
            # List supported platforms
            for platform in platforms:
                print(f"  - {platform}")
            
            return True
        else:
            print("❌ Multi-platform builder not ready")
            return False
            
    except Exception as e:
        print(f"❌ Could not test platform support: {e}")
        return False

def test_dockerfile_syntax():
    """Test Dockerfile syntax"""
    print("\n🔍 Testing Dockerfile Syntax")
    print("=" * 50)
    
    try:
        # Test basic syntax by trying to build with --dry-run (if supported)
        result = subprocess.run(['docker', 'buildx', 'build', '--dry-run', '.'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dockerfile syntax is valid")
            return True
        else:
            # If --dry-run is not supported, try a basic build test
            print("⚠️ --dry-run not supported, testing basic syntax...")
            
            # Check if Dockerfile has basic required elements
            with open('Dockerfile', 'r') as f:
                content = f.read()
            
            required_elements = [
                'FROM',
                'WORKDIR',
                'COPY',
                'CMD'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"❌ Dockerfile missing required elements: {', '.join(missing_elements)}")
                return False
            
            print("✅ Dockerfile has basic required elements")
            return True
            
    except Exception as e:
        print(f"❌ Could not test Dockerfile: {e}")
        return False

def test_docker_compose_syntax():
    """Test docker-compose.yml syntax"""
    print("\n🔍 Testing Docker Compose Syntax")
    print("=" * 50)
    
    try:
        result = subprocess.run(['docker-compose', 'config'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ docker-compose.yml syntax is valid")
            
            # Check for platform support in compose file
            with open('docker-compose.yml', 'r') as f:
                content = f.read()
            
            if 'linux/amd64' in content:
                print("✅ x86_64 platform support configured")
            else:
                print("⚠️ x86_64 platform support not found in compose file")
            
            return True
        else:
            print("❌ docker-compose.yml syntax errors:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not test docker-compose.yml: {e}")
        return False

def test_manage_py_docker():
    """Test manage.py Docker commands"""
    print("\n🔍 Testing manage.py Docker Commands")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'docker'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ manage.py docker commands available")
            print("Available operations:")
            for line in result.stdout.split('\n'):
                if line.strip() and 'Available Docker operations:' not in line:
                    print(f"  {line}")
            return True
        else:
            print("❌ manage.py docker commands failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not test manage.py docker: {e}")
        return False

def test_requirements():
    """Test that production requirements are included"""
    print("\n🔍 Testing Production Requirements")
    print("=" * 50)
    
    required_packages = ['gunicorn']
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        missing_packages = []
        for package in required_packages:
            if package in requirements:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - MISSING")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            return False
        
        print("\n✅ All production requirements present")
        return True
    except Exception as e:
        print(f"❌ Could not read requirements.txt: {e}")
        return False

def test_health_endpoint():
    """Test that health endpoint exists in app.py"""
    print("\n🔍 Testing Health Endpoint")
    print("=" * 50)
    
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        if '@app.route(\'/health\')' in app_content:
            print("✅ Health endpoint found in app.py")
            return True
        else:
            print("❌ Health endpoint not found in app.py")
            return False
    except Exception as e:
        print(f"❌ Could not read app.py: {e}")
        return False

def test_x86_64_support():
    """Test x86_64 platform support specifically"""
    print("\n🔍 Testing x86_64 Support")
    print("=" * 50)
    
    try:
        # Check Dockerfile for x86_64 support
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        if 'linux/amd64' in dockerfile_content or 'x86_64' in dockerfile_content:
            print("✅ Dockerfile includes x86_64 support")
        else:
            print("⚠️ Dockerfile may not explicitly mention x86_64")
        
        # Check docker-compose.yml for x86_64 support
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
        
        if 'linux/amd64' in compose_content:
            print("✅ docker-compose.yml includes x86_64 platform")
        else:
            print("❌ docker-compose.yml missing x86_64 platform")
            return False
        
        # Check manage.py for x86_64 defaults
        with open('manage.py', 'r') as f:
            manage_content = f.read()
        
        if 'linux/amd64' in manage_content:
            print("✅ manage.py includes x86_64 as default platform")
        else:
            print("⚠️ manage.py may not have x86_64 as default")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not test x86_64 support: {e}")
        return False

def test_docker_setup_script():
    """Test that Docker setup script exists and is executable."""
    print("Testing Docker setup script...")
    
    setup_docker_path = "setup_docker.py"
    
    # Check if file exists
    if not os.path.exists(setup_docker_path):
        print(f"❌ Docker setup script not found: {setup_docker_path}")
        return False
    
    # Check if file is executable
    if not os.access(setup_docker_path, os.X_OK):
        print(f"❌ Docker setup script not executable: {setup_docker_path}")
        return False
    
    # Check file content
    try:
        with open(setup_docker_path, 'r') as f:
            content = f.read()
            if 'Docker Setup script' in content and 'create_admin_user' in content:
                print(f"✅ Docker setup script is valid: {setup_docker_path}")
                return True
            else:
                print(f"❌ Docker setup script content seems invalid: {setup_docker_path}")
                return False
    except Exception as e:
        print(f"❌ Error reading Docker setup script: {e}")
        return False

def test_app_external_port_config():
    """Test that APP_EXTERNAL_PORT is properly configured in Docker Compose files."""
    print("Testing APP_EXTERNAL_PORT configuration...")
    
    compose_files = ["docker-compose.yml", "docker-compose.registry.yml"]
    
    for compose_file in compose_files:
        if not os.path.exists(compose_file):
            print(f"❌ Docker Compose file not found: {compose_file}")
            continue
            
        try:
            with open(compose_file, 'r') as f:
                content = f.read()
                
            # Check if APP_EXTERNAL_PORT is defined in environment
            if 'APP_EXTERNAL_PORT' in content:
                print(f"✅ APP_EXTERNAL_PORT configured in {compose_file}")
            else:
                print(f"❌ APP_EXTERNAL_PORT not found in {compose_file}")
                return False
                
            # Check if ports mapping uses the variable
            if '${APP_EXTERNAL_PORT' in content:
                print(f"✅ Ports mapping uses APP_EXTERNAL_PORT in {compose_file}")
            else:
                print(f"❌ Ports mapping doesn't use APP_EXTERNAL_PORT in {compose_file}")
                return False
                
        except Exception as e:
            print(f"❌ Error reading {compose_file}: {e}")
            return False
    
    return True

def main():
    """Run all Docker tests"""
    print("🐳 Docker Setup Test Suite")
    print("=" * 60)
    
    tests = [
        ("Docker Files", test_docker_files),
        ("Docker Commands", test_docker_commands),
        ("Platform Support", test_platform_support),
        ("Dockerfile Syntax", test_dockerfile_syntax),
        ("Docker Compose Syntax", test_docker_compose_syntax),
        ("manage.py Docker", test_manage_py_docker),
        ("Production Requirements", test_requirements),
        ("Health Endpoint", test_health_endpoint),
        ("x86_64 Support", test_x86_64_support),
        ("Docker Setup Script", test_docker_setup_script),
        ("APP_EXTERNAL_PORT Configuration", test_app_external_port_config)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Docker Setup Test Results")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All Docker tests passed! Ready for deployment.")
        print("✅ x86_64 support is configured and ready.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 