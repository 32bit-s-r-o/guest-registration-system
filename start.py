#!/usr/bin/env python3
"""
Startup script for Guest Registration System
Helps users choose between development and production modes
"""

import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='Start Guest Registration System')
    parser.add_argument('--mode', choices=['dev', 'prod', 'auto'], default='auto',
                       help='Startup mode: dev (Flask), prod (Gunicorn), auto (detect)')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--workers', type=int, default=4, help='Number of Gunicorn workers')
    parser.add_argument('--timeout', type=int, default=120, help='Gunicorn timeout')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.mode == 'auto':
        mode = 'prod' if os.getenv('FLASK_ENV') == 'production' else 'dev'
    else:
        mode = args.mode
    
    print(f"🚀 Starting Guest Registration System in {mode.upper()} mode")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    
    if mode == 'prod':
        print("🐳 Using Gunicorn production server")
        print(f"👥 Workers: {args.workers}")
        print(f"⏱️  Timeout: {args.timeout}")
        
        # Set environment variables
        os.environ['FLASK_ENV'] = 'production'
        os.environ['GUNICORN_WORKERS'] = str(args.workers)
        os.environ['GUNICORN_TIMEOUT'] = str(args.timeout)
        os.environ['APP_PORT'] = str(args.port)
        
        # Check if Gunicorn is available
        try:
            subprocess.run(['gunicorn', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Gunicorn not found. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'], check=True)
        
        # Start with Gunicorn
        cmd = [
            'gunicorn',
            '--bind', f'{args.host}:{args.port}',
            '--workers', str(args.workers),
            '--timeout', str(args.timeout),
            '--access-logfile', '-',
            '--error-logfile', '-',
            '--log-level', 'info',
            'app:app'
        ]
        
    else:  # dev mode
        print("🔧 Using Flask development server")
        cmd = [
            sys.executable, 'app.py',
            '--host', args.host,
            '--port', str(args.port),
            '--debug',
            '--reload'
        ]
    
    print(f"🎯 Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 