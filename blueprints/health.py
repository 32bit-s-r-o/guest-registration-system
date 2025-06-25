from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime
import os
import sys
import shutil
import subprocess
import tempfile
import zipfile

health = Blueprint('health', __name__)

from database import db, User, Trip, Registration, Guest, Invoice, Housekeeping
from version import version_manager
from migrations import MigrationManager
from sqlalchemy import text
from migrations import get_migration_manager

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                login_manager = current_app.extensions.get('login_manager')
                return login_manager.unauthorized()
            if current_user.role != role:
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@health.route('/health')
def health_check():
    """Basic health check endpoint for Docker and load balancers."""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': version_manager.get_current_version(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': version_manager.get_current_version(),
            'database': 'disconnected',
            'error': str(e)
        }), 503

@health.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with comprehensive system status."""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': version_manager.get_current_version(),
        'checks': {},
        'overall_status': 'healthy'
    }
    
    # Database health check
    try:
        db.session.execute(text('SELECT 1'))
        db_result = db.session.execute(text('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'public\''))
        table_count = db_result.scalar()
        
        health_status['checks']['database'] = {
            'status': 'healthy',
            'connected': True,
            'table_count': table_count,
            'response_time_ms': 0  # Could be enhanced with timing
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'connected': False,
            'error': str(e)
        }
        health_status['overall_status'] = 'unhealthy'
    
    # File system health check
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if os.path.exists(upload_folder):
            free_space = shutil.disk_usage(upload_folder).free
            free_space_mb = free_space / (1024 * 1024)
            
            health_status['checks']['filesystem'] = {
                'status': 'healthy',
                'upload_folder': upload_folder,
                'exists': True,
                'writable': os.access(upload_folder, os.W_OK),
                'free_space_mb': round(free_space_mb, 2)
            }
        else:
            health_status['checks']['filesystem'] = {
                'status': 'unhealthy',
                'upload_folder': upload_folder,
                'exists': False,
                'error': 'Upload folder does not exist'
            }
            health_status['overall_status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['filesystem'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['overall_status'] = 'unhealthy'
    
    # Application health check
    try:
        # Check if critical modules are available
        import PIL
        import cffi
        import weasyprint
        
        health_status['checks']['application'] = {
            'status': 'healthy',
            'flask_version': '2.3.3',  # Hardcoded for now
            'python_version': sys.version.split()[0],
            'critical_modules': {
                'PIL': PIL.__version__,
                'cffi': cffi.__version__,
                'weasyprint': weasyprint.__version__
            }
        }
    except Exception as e:
        health_status['checks']['application'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['overall_status'] = 'unhealthy'
    
    # Migration status check
    try:
        migration_manager = get_migration_manager()
        current_version = migration_manager.get_current_version()
        applied_migrations = migration_manager.get_applied_migrations()
        pending_migrations = migration_manager.get_pending_migrations()
        
        health_status['checks']['migrations'] = {
            'status': 'healthy' if not pending_migrations else 'warning',
            'current_version': current_version,
            'applied_count': len(applied_migrations),
            'pending_count': len(pending_migrations),
            'up_to_date': len(pending_migrations) == 0
        }
        
        if pending_migrations:
            health_status['overall_status'] = 'warning'
    except Exception as e:
        health_status['checks']['migrations'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['overall_status'] = 'unhealthy'
    
    # Memory usage check
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        
        health_status['checks']['memory'] = {
            'status': 'healthy',
            'memory_usage_mb': round(memory_mb, 2),
            'memory_percent': round(process.memory_percent(), 2)
        }
    except ImportError:
        health_status['checks']['memory'] = {
            'status': 'not_available',
            'message': 'psutil not installed'
        }
    except Exception as e:
        health_status['checks']['memory'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Determine HTTP status code
    if health_status['overall_status'] == 'healthy':
        status_code = 200
    elif health_status['overall_status'] == 'warning':
        status_code = 200  # Still return 200 for warnings
    else:
        status_code = 503
    
    return jsonify(health_status), status_code

@health.route('/health/readiness')
def readiness_check():
    """Readiness check for Kubernetes and orchestration systems."""
    try:
        # Check if application is ready to serve requests
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
        
        # Basic application readiness (no database dependency)
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat(),
            'version': version_manager.get_current_version()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'version': version_manager.get_current_version(),
            'error': str(e)
        }), 503

@health.route('/health/liveness')
def liveness_check():
    """Liveness check for Kubernetes and orchestration systems."""
    try:
        # Simple check to ensure the application is alive
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat(),
            'version': version_manager.get_current_version()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'dead',
            'timestamp': datetime.utcnow().isoformat(),
            'version': version_manager.get_current_version(),
            'error': str(e)
        }), 503

@health.route('/health/metrics')
def health_metrics():
    """Health metrics endpoint for monitoring."""
    try:
        # Basic metrics
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'version': current_app.config.get('VERSION', 'unknown'),
            'database': {
                'connected': True,
                'tables': {
                    'users': User.query.count(),
                    'amenities': 0,  # Will be imported from app
                    'trips': Trip.query.count(),
                    'registrations': Registration.query.count(),
                    'guests': Guest.query.count(),
                    'invoices': Invoice.query.count(),
                    'housekeeping': Housekeeping.query.count(),
                }
            },
            'system': {
                'uptime': 'unknown',  # Could be enhanced with process start time
                'memory_usage': 'unknown',  # Could be enhanced with psutil
                'cpu_usage': 'unknown',  # Could be enhanced with psutil
            }
        }
        
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500 