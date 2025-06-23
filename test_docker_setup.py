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
        'docker-compose': 'Docker Compose',
        'docker buildx': 'Docker Buildx'
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
    
    if missing_commands:
        print(f"\n❌ Missing commands: {', '.join(missing_commands)}")
        return False
    
    print("\n✅ All Docker commands available")
    return True

def test_dockerfile_syntax():
    """Test Dockerfile syntax"""
    print("\n🔍 Testing Dockerfile Syntax")
    print("=" * 50)
    
    try:
        result = subprocess.run(['docker', 'buildx', 'build', '--dry-run', '.'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dockerfile syntax is valid")
            return True
        else:
            print("❌ Dockerfile syntax errors:")
            print(result.stderr)
            return False
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
    
    required_packages = ['gunicorn', 'redis']
    
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

def main():
    """Run all Docker tests"""
    print("🐳 Docker Setup Test Suite")
    print("=" * 60)
    
    tests = [
        ("Docker Files", test_docker_files),
        ("Docker Commands", test_docker_commands),
        ("Dockerfile Syntax", test_dockerfile_syntax),
        ("Docker Compose Syntax", test_docker_compose_syntax),
        ("manage.py Docker", test_manage_py_docker),
        ("Production Requirements", test_requirements),
        ("Health Endpoint", test_health_endpoint)
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
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 