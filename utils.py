from functools import wraps
from flask import abort, current_app
from flask_login import current_user
import os

def role_required(role):
    """Decorator to require a specific role for access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Let Flask-Login handle the redirect
                from flask_login import login_manager
                return login_manager.unauthorized()
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_server_url():
    """Get the server URL for external access (Docker, reverse proxy, etc.)"""
    # First check if SERVER_URL is set (complete override)
    server_url = os.environ.get('SERVER_URL')
    if server_url:
        return server_url.rstrip('/')
    
    # Otherwise build from components
    protocol = os.environ.get('SERVER_PROTOCOL', 'http')
    host = os.environ.get('SERVER_HOST', 'localhost')
    port = os.environ.get('SERVER_PORT', '5000')
    
    # Don't include port for standard ports
    if (protocol == 'http' and port == '80') or (protocol == 'https' and port == '443'):
        return f"{protocol}://{host}"
    else:
        return f"{protocol}://{host}:{port}"

def register_url_utils(app):
    """Register URL utility functions with the Flask app."""
    
    @app.context_processor
    def inject_server_url():
        """Inject server URL into template context."""
        try:
            return {
                'server_url': get_server_url()
            }
        except Exception:
            # Fallback to localhost if there's any error
            return {
                'server_url': 'http://localhost:5000'
            }
    
    @app.template_filter('absolute_url')
    def absolute_url_filter(path):
        """Convert relative path to absolute URL."""
        try:
            if path.startswith('http'):
                return path
            return f"{get_server_url()}{path}"
        except Exception:
            # Fallback to localhost if there's any error
            if path.startswith('http'):
                return path
            return f"http://localhost:5000{path}"

def load_dynamic_server_config(app):
    """Load dynamic server config from environment into app.config."""
    app.config['SERVER_URL'] = os.environ.get('SERVER_URL')
    app.config['SERVER_PROTOCOL'] = os.environ.get('SERVER_PROTOCOL', 'http')
    app.config['SERVER_HOST'] = os.environ.get('SERVER_HOST', 'localhost')
    app.config['SERVER_PORT'] = os.environ.get('SERVER_PORT', '5000')

def is_production_environment():
    """
    Check if the current environment is production.
    
    Returns:
        bool: True if running in production, False otherwise
    """
    # Check for explicit production environment variables
    flask_env = os.environ.get('FLASK_ENV', '').lower()
    if flask_env == 'production':
        return True
    
    # Check for Docker environment (usually production)
    if os.environ.get('DOCKER_ENV', '').lower() == 'true':
        return True
    
    # Check for production database URLs (common patterns)
    database_url = os.environ.get('DATABASE_URL', '').lower()
    production_indicators = [
        'prod',
        'production',
        'live',
        'staging'
    ]
    
    for indicator in production_indicators:
        if indicator in database_url:
            return True
    
    # Check for production server URLs
    server_url = os.environ.get('SERVER_URL', '').lower()
    if server_url and ('https://' in server_url or 'www.' in server_url):
        return True
    
    # Check for production hostnames
    server_host = os.environ.get('SERVER_HOST', '').lower()
    if server_host and server_host not in ['localhost', '127.0.0.1', '0.0.0.0']:
        return True
    
    return False

def check_production_lock(operation_name="this operation"):
    """
    Check if the current operation is allowed in the current environment.
    
    Args:
        operation_name (str): Name of the operation for error messages
        
    Raises:
        RuntimeError: If the operation is not allowed in production
        
    Returns:
        bool: True if operation is allowed
    """
    if is_production_environment():
        # Check if production seeding is explicitly allowed
        if is_production_seed_allowed():
            print(f"⚠️  WARNING: {operation_name} is being executed in production environment")
            print("   This is allowed because ALLOW_PRODUCTION_SEED=true is set")
            print("   Please ensure this is intentional and safe!")
            return True
        
        error_msg = f"""
🚫 PRODUCTION LOCK ACTIVATED 🚫

{operation_name} is not allowed in production environment.

Environment detected as production due to:
- FLASK_ENV=production
- DOCKER_ENV=true
- Production database URL
- Production server URL
- Non-localhost server host

To override this lock (NOT RECOMMENDED):
1. Set environment variable: ALLOW_PRODUCTION_SEED=true
2. Or set environment variable: FLASK_ENV=development

⚠️  WARNING: Seeding production databases can:
- Overwrite real customer data
- Disrupt business operations
- Cause data loss
- Impact system performance

If you need to reset production data, use proper backup/restore procedures.
"""
        raise RuntimeError(error_msg)
    
    return True

def is_production_seed_allowed():
    """
    Check if production seeding is explicitly allowed via environment variable.
    
    Returns:
        bool: True if production seeding is allowed, False otherwise
    """
    import os
    return os.environ.get('ALLOW_PRODUCTION_SEED', '').lower() == 'true' 