#!/usr/bin/env python3
"""
Health Check Script for Guest Registration System
Tests all health endpoints and provides detailed system status
"""

import requests
import json
import sys
import time
import argparse
from datetime import datetime
from urllib.parse import urljoin
from config import Config

class HealthChecker:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
    def check_endpoint(self, endpoint, name):
        """Check a specific health endpoint"""
        url = urljoin(self.base_url, endpoint)
        try:
            start_time = time.time()
            response = self.session.get(url)
            response_time = (time.time() - start_time) * 1000
            
            return {
                'name': name,
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code < 400,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
                'error': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'name': name,
                'url': url,
                'status_code': None,
                'response_time_ms': None,
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def run_all_checks(self):
        """Run all health checks"""
        print(f"🏥 Health Check for Guest Registration System")
        print(f"📍 Base URL: {self.base_url}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        endpoints = [
            ('/health', 'Basic Health Check'),
            ('/health/detailed', 'Detailed Health Check'),
            ('/health/readiness', 'Readiness Check'),
            ('/health/liveness', 'Liveness Check'),
            ('/health/metrics', 'Health Metrics'),
            ('/api/version', 'Version Information'),
            ('/api/version/compatibility', 'Version Compatibility')
        ]
        
        results = []
        for endpoint, name in endpoints:
            print(f"🔍 Checking {name}...")
            result = self.check_endpoint(endpoint, name)
            results.append(result)
            
            if result['success']:
                print(f"✅ {name}: OK ({result['response_time_ms']}ms)")
            else:
                print(f"❌ {name}: FAILED - {result['error'] or f'HTTP {result['status_code']}'}")
        
        return results
    
    def print_summary(self, results):
        """Print a summary of all health check results"""
        print("\n" + "=" * 60)
        print("📊 Health Check Summary")
        print("=" * 60)
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        print(f"✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {total - successful}/{total}")
        
        if successful == total:
            print("🎉 All health checks passed!")
            overall_status = "HEALTHY"
        elif successful > 0:
            print("⚠️  Some health checks failed")
            overall_status = "DEGRADED"
        else:
            print("💀 All health checks failed")
            overall_status = "UNHEALTHY"
        
        print(f"🏥 Overall Status: {overall_status}")
        
        # Show detailed results
        print("\n📋 Detailed Results:")
        for result in results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"  {status_icon} {result['name']}")
            if result['response_time_ms']:
                print(f"     Response Time: {result['response_time_ms']}ms")
            if result['data'] and 'status' in result['data']:
                print(f"     Status: {result['data']['status']}")
            if result['error']:
                print(f"     Error: {result['error']}")
        
        return overall_status
    
    def print_detailed_health(self, results):
        """Print detailed health information"""
        detailed_result = next((r for r in results if r['name'] == 'Detailed Health Check' and r['success']), None)
        if not detailed_result or not detailed_result['data']:
            print("\n❌ Could not retrieve detailed health information")
            return
        
        data = detailed_result['data']
        print("\n" + "=" * 60)
        print("🔬 Detailed System Health")
        print("=" * 60)
        
        print(f"📊 Overall Status: {data.get('overall_status', 'unknown')}")
        print(f"🕒 Timestamp: {data.get('timestamp', 'unknown')}")
        print(f"📦 Version: {data.get('version', 'unknown')}")
        
        checks = data.get('checks', {})
        for check_name, check_data in checks.items():
            status_icon = "✅" if check_data.get('status') == 'healthy' else "⚠️" if check_data.get('status') == 'warning' else "❌"
            print(f"\n{status_icon} {check_name.title()}: {check_data.get('status', 'unknown')}")
            
            for key, value in check_data.items():
                if key != 'status':
                    if isinstance(value, dict):
                        print(f"    {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"      {sub_key}: {sub_value}")
                    else:
                        print(f"    {key}: {value}")
    
    def print_metrics(self, results):
        """Print system metrics"""
        metrics_result = next((r for r in results if r['name'] == 'Health Metrics' and r['success']), None)
        if not metrics_result or not metrics_result['data']:
            print("\n❌ Could not retrieve metrics information")
            return
        
        data = metrics_result['data']
        print("\n" + "=" * 60)
        print("📈 System Metrics")
        print("=" * 60)
        
        print(f"🕒 Timestamp: {data.get('timestamp', 'unknown')}")
        print(f"📦 Version: {data.get('version', 'unknown')}")
        
        metrics = data.get('metrics', {})
        for metric_name, metric_data in metrics.items():
            print(f"\n📊 {metric_name.title()}:")
            if isinstance(metric_data, dict):
                for key, value in metric_data.items():
                    print(f"    {key}: {value}")
            else:
                print(f"    {metric_data}")

def main():
    parser = argparse.ArgumentParser(description='Health Check for Guest Registration System')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL of the application')
    parser.add_argument('--detailed', action='store_true', help='Show detailed health information')
    parser.add_argument('--metrics', action='store_true', help='Show system metrics')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Create health checker
    checker = HealthChecker(args.url)
    checker.session.timeout = args.timeout
    
    # Run health checks
    results = checker.run_all_checks()
    
    if args.json:
        # Output JSON format
        output = {
            'timestamp': datetime.now().isoformat(),
            'base_url': args.url,
            'results': results,
            'summary': {
                'total': len(results),
                'successful': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success'])
            }
        }
        print(json.dumps(output, indent=2))
    else:
        # Print summary
        overall_status = checker.print_summary(results)
        
        # Print detailed information if requested
        if args.detailed:
            checker.print_detailed_health(results)
        
        if args.metrics:
            checker.print_metrics(results)
        
        # Exit with appropriate code
        if overall_status == "HEALTHY":
            sys.exit(0)
        elif overall_status == "DEGRADED":
            sys.exit(1)
        else:
            sys.exit(2)

if __name__ == '__main__':
    main() 