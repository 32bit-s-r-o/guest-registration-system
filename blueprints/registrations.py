from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime
import os

registrations = Blueprint('registrations', __name__)

from app import app, db, User, Registration, Trip

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                from app import login_manager
                return login_manager.unauthorized()
            if current_user.role != role:
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@registrations.route('/admin/registrations')
@login_required
@role_required('admin')
def admin_registrations():
    registrations_list = Registration.query.filter_by(status='pending').all()
    return render_template('admin/registrations.html', registrations=registrations_list)

@registrations.route('/admin/registration/<int:registration_id>')
@login_required
@role_required('admin')
def view_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    return render_template('admin/view_registration.html', registration=registration)

@registrations.route('/admin/registration/<int:registration_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    registration.status = 'approved'
    registration.updated_at = datetime.utcnow()
    
    # Delete document images after approval (GDPR compliance)
    for guest in registration.guests:
        if guest.document_image:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], guest.document_image))
                guest.document_image = None
            except:
                pass  # File might already be deleted
    
    db.session.commit()
    
    # Send approval email
    from app import send_approval_email
    send_approval_email(registration)
    
    flash(_('Registration approved and email sent to user'), 'success')
    return redirect(url_for('registrations.admin_registrations'))

@registrations.route('/admin/registration/<int:registration_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    registration.status = 'rejected'
    registration.admin_comment = request.form.get('comment')
    registration.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Send rejection email
    from app import send_rejection_email
    send_rejection_email(registration)
    
    flash(_('Registration rejected and email sent to user'), 'success')
    return redirect(url_for('registrations.admin_registrations')) 