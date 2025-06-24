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