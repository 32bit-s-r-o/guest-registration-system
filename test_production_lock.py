#!/usr/bin/env python3
"""
Test script to verify production lock functionality
"""

import os
import sys
from utils import is_production_environment, check_production_lock, is_production_seed_allowed

def test_production_detection():
    """Test production environment detection"""
    print("🧪 Testing Production Environment Detection")
    print("=" * 50)
    
    # Test 1: Development environment
    print("\n1. Testing development environment...")
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['SERVER_HOST'] = 'localhost'
    
    is_prod = is_production_environment()
    print(f"   FLASK_ENV=development, DATABASE_URL=sqlite:///test.db")
    print(f"   Is production: {is_prod}")
    assert not is_prod, "Development environment should not be detected as production"
    print("   ✅ PASS")
    
    # Test 2: Production environment via FLASK_ENV
    print("\n2. Testing production environment via FLASK_ENV...")
    os.environ['FLASK_ENV'] = 'production'
    
    is_prod = is_production_environment()
    print(f"   FLASK_ENV=production")
    print(f"   Is production: {is_prod}")
    assert is_prod, "Production environment should be detected"
    print("   ✅ PASS")
    
    # Test 3: Production environment via Docker
    print("\n3. Testing production environment via Docker...")
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DOCKER_ENV'] = 'true'
    
    is_prod = is_production_environment()
    print(f"   DOCKER_ENV=true")
    print(f"   Is production: {is_prod}")
    assert is_prod, "Docker environment should be detected as production"
    print("   ✅ PASS")
    
    # Test 4: Production environment via database URL
    print("\n4. Testing production environment via database URL...")
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DOCKER_ENV'] = 'false'
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@prod-server.com:5432/prod_db'
    
    is_prod = is_production_environment()
    print(f"   DATABASE_URL=postgresql://user:pass@prod-server.com:5432/prod_db")
    print(f"   Is production: {is_prod}")
    assert is_prod, "Production database URL should be detected"
    print("   ✅ PASS")
    
    # Test 5: Production environment via server URL
    print("\n5. Testing production environment via server URL...")
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['SERVER_URL'] = 'https://www.myapp.com'
    
    is_prod = is_production_environment()
    print(f"   SERVER_URL=https://www.myapp.com")
    print(f"   Is production: {is_prod}")
    assert is_prod, "HTTPS server URL should be detected as production"
    print("   ✅ PASS")
    
    # Test 6: Production environment via server host
    print("\n6. Testing production environment via server host...")
    os.environ['SERVER_URL'] = ''
    os.environ['SERVER_HOST'] = 'myapp.com'
    
    is_prod = is_production_environment()
    print(f"   SERVER_HOST=myapp.com")
    print(f"   Is production: {is_prod}")
    assert is_prod, "Non-localhost server host should be detected as production"
    print("   ✅ PASS")
    
    print("\n✅ All production detection tests passed!")

def test_production_lock():
    """Test production lock functionality"""
    print("\n🔒 Testing Production Lock Functionality")
    print("=" * 50)
    
    # Test 1: Development environment should allow operations
    print("\n1. Testing development environment (should allow)...")
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['SERVER_HOST'] = 'localhost'
    os.environ['ALLOW_PRODUCTION_SEED'] = 'false'
    
    try:
        check_production_lock("Test operation")
        print("   ✅ PASS - Operation allowed in development")
    except RuntimeError as e:
        print(f"   ❌ FAIL - Operation blocked in development: {e}")
        return False
    
    # Test 2: Production environment should block operations
    print("\n2. Testing production environment (should block)...")
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        check_production_lock("Test operation")
        print("   ❌ FAIL - Operation allowed in production")
        return False
    except RuntimeError as e:
        print("   ✅ PASS - Operation blocked in production")
        print(f"   Error message: {str(e)[:100]}...")
    
    # Test 3: Production environment with override should allow operations
    print("\n3. Testing production environment with override (should allow)...")
    os.environ['ALLOW_PRODUCTION_SEED'] = 'true'
    
    try:
        check_production_lock("Test operation")
        print("   ✅ PASS - Operation allowed in production with override")
    except RuntimeError as e:
        print(f"   ❌ FAIL - Operation blocked despite override: {e}")
        return False
    
    # Test 4: Test override detection
    print("\n4. Testing override detection...")
    assert is_production_seed_allowed(), "Override should be detected"
    print("   ✅ PASS - Override correctly detected")
    
    os.environ['ALLOW_PRODUCTION_SEED'] = 'false'
    assert not is_production_seed_allowed(), "Override should not be detected"
    print("   ✅ PASS - Override correctly not detected")
    
    print("\n✅ All production lock tests passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Production Lock Test Suite")
    print("=" * 60)
    
    try:
        test_production_detection()
        if test_production_lock():
            print("\n🎉 All tests passed! Production lock is working correctly.")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 