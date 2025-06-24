from functools import wraps
from flask import abort
from flask_login import current_user

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