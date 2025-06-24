from flask import current_app
from flask_login import current_user

def nl2br_filter(text):
    """Convert newlines to <br> tags."""
    if text:
        return text.replace('\n', '<br>')
    return ''

def format_date_filter(date_obj):
    """Format date according to user preference."""
    if not date_obj:
        return ''
    
    # Get user's preferred date format
    date_format = 'd.m.Y'  # Default
    if current_user.is_authenticated and hasattr(current_user, 'date_format') and current_user.date_format:
        date_format = current_user.date_format
    
    # Convert PHP/JS style to Python strftime format
    format_map = [
        ('d', '%d'),
        ('j', '%-d'),
        ('m', '%m'),
        ('n', '%-m'),
        ('Y', '%Y'),
        ('y', '%y'),
        ('M', '%b'),
        ('F', '%B'),
        ('D', '%a'),
        ('l', '%A'),
        ('/', '/'),
        ('.', '.'),
        ('-', '-'),
        (' ', ' ')
    ]
    
    py_format = date_format
    for php_char, py_char in format_map:
        py_format = py_format.replace(php_char, py_char)
    
    try:
        return date_obj.strftime(py_format)
    except:
        # Fallback to default format if conversion fails
        return date_obj.strftime('%d.%m.%Y')

def registration_name_filter(reg):
    """Get a display name for a registration."""
    if reg.guests:
        first_guest = reg.guests[0]
        return f"{first_guest.first_name} {first_guest.last_name}"
    return reg.email

def register_template_filters(app):
    """Register all template filters with the Flask app."""
    app.jinja_env.filters['nl2br'] = nl2br_filter
    app.jinja_env.filters['format_date'] = format_date_filter
    app.jinja_env.filters['registration_name'] = registration_name_filter 