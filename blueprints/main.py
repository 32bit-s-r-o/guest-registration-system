from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_login import login_required
from flask_babel import gettext as _

main = Blueprint('main', __name__)

from app import app, User

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with admin contact information."""
    from app import User
    admin_contact = User.query.filter_by(role='admin', is_deleted=False).first()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        flash(_('Thank you for your message, %(name)s! We will get back to you soon.', name=name), 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', admin_contact=admin_contact)

@main.route('/gdpr')
def gdpr():
    from app import User
    admin_contact = User.query.filter_by(role='admin', is_deleted=False).first()
    return render_template('gdpr.html', admin_contact=admin_contact)

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files (only accessible to admins)"""
    from app import app
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@main.route('/set_language/<lang_code>')
def set_language(lang_code):
    from app import app
    # If language picker is disabled, redirect back without changing language
    if not app.config['LANGUAGE_PICKER_ENABLED']:
        return redirect(request.referrer or url_for('main.index'))
    
    if lang_code in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.index')) 