#!/usr/bin/env python3
"""
Test script for health check functionality
"""

import requests
import json
import sys
from datetime import datetime

def test_health_endpoints():
    """Test all health check endpoints"""
    base_url = "http://localhost:5000"
    
    endpoints = [
        ('/health', 'Basic Health Check'),
        ('/health/detailed', 'Detailed Health Check'),
        ('/health/readiness', 'Readiness Check'),
        ('/health/liveness', 'Liveness Check'),
        ('/health/metrics', 'Health Metrics'),
        ('/api/version', 'Version Information'),
        ('/api/version/compatibility', 'Version Compatibility')
    ]
    
    print("🏥 Testing Health Check Endpoints")
    print("=" * 50)
    print(f"📍 Base URL: {base_url}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK (HTTP {response.status_code})")
                try:
                    data = response.json()
                    if 'status' in data:
                        print(f"   Status: {data['status']}")
                    if 'version' in data:
                        print(f"   Version: {data['version']}")
                except:
                    pass
            else:
                print(f"❌ {name}: FAILED (HTTP {response.status_code})")
            
            results.append({
                'name': name,
                'url': url,
                'status_code': response.status_code,
                'success': response.status_code == 200
            })
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: ERROR - {e}")
            results.append({
                'name': name,
                'url': url,
                'status_code': None,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 All health check endpoints are working!")
        return True
    else:
        print("⚠️ Some health check endpoints failed")
        return False

def test_health_check_script():
    """Test the health_check.py script"""
    print("\n🔍 Testing health_check.py script")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'health_check.py', '--url', 'http://localhost:5000'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ health_check.py script works correctly")
            print("Output:")
            print(result.stdout)
            return True
        else:
            print("❌ health_check.py script failed")
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing health_check.py script: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Health Check Test Suite")
    print("=" * 60)
    
    # Test 1: Direct endpoint testing
    test1_result = test_health_endpoints()
    
    # Test 2: Health check script testing
    test2_result = test_health_check_script()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 Final Test Results")
    print("=" * 60)
    
    print(f"✅ Endpoint Tests: {'PASS' if test1_result else 'FAIL'}")
    print(f"✅ Script Tests: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All health check tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some health check tests failed")
        sys.exit(1)

if __name__ == '__main__':
    main() 