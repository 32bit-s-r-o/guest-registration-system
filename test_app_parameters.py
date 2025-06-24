#!/usr/bin/env python3
"""
Test script to demonstrate Flask app parameter functionality
"""

import subprocess
import time
import requests
import sys
from config import Config

def test_app_parameters():
    """Test different parameter combinations for the Flask app"""
    
    print("Testing Flask App Parameter Functionality")
    print("=" * 50)
    
    # Test cases with different parameter combinations
    test_cases = [
        {
            'name': 'Default parameters',
            'args': [],
            'expected_port': 5000,
            'expected_host': '127.0.0.1'
        },
        {
            'name': 'Custom port',
            'args': ['--port', '8080'],
            'expected_port': 8080,
            'expected_host': '127.0.0.1'
        },
        {
            'name': 'Custom host and port',
            'args': ['--host', '0.0.0.0', '--port', '9000'],
            'expected_port': 9000,
            'expected_host': '0.0.0.0'
        },
        {
            'name': 'Production mode (no debug)',
            'args': ['--no-debug', '--port', '7000'],
            'expected_port': 7000,
            'expected_host': '127.0.0.1'
        },
        {
            'name': 'Development mode with reload',
            'args': ['--debug', '--reload', '--port', '6000'],
            'expected_port': 6000,
            'expected_host': '127.0.0.1'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Args: {' '.join(test_case['args'])}")
        
        # Start the app with the given parameters
        try:
            process = subprocess.Popen(
                ['python', 'app.py'] + test_case['args'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"   ✓ App started successfully on {test_case['expected_host']}:{test_case['expected_port']}")
                
                # Try to make a request to verify it's working
                try:
                    response = requests.get(f"http://127.0.0.1:{test_case['expected_port']}/", timeout=5)
                    if response.status_code == 200:
                        print(f"   ✓ App responding correctly (HTTP {response.status_code})")
                    else:
                        print(f"   ⚠ App responding but with status {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"   ⚠ Could not connect to app: {e}")
                
                # Stop the process
                process.terminate()
                process.wait(timeout=5)
                print(f"   ✓ App stopped cleanly")
                
            else:
                stdout, stderr = process.communicate()
                print(f"   ✗ App failed to start")
                if stderr:
                    print(f"   Error: {stderr.strip()}")
                    
        except Exception as e:
            print(f"   ✗ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Parameter Testing Complete!")
    print("\nAvailable parameters:")
    print("  --host HOST           Host to bind to (default: 127.0.0.1)")
    print("  --port PORT           Port to bind to (default: 5000)")
    print("  --debug               Enable debug mode")
    print("  --no-debug            Disable debug mode")
    print("  --reload              Enable auto-reload on code changes")
    print("  --threaded            Enable threading")
    print("  --ssl-context SSL     SSL context for HTTPS (e.g., 'adhoc')")
    print("\nExample usage:")
    print("  python app.py --port 8080 --host 0.0.0.0 --threaded")
    print("  python app.py --debug --reload --port 5000")
    print("  python app.py --no-debug --port 80 --ssl-context adhoc")

if __name__ == '__main__':
    test_app_parameters() 