from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime
from io import StringIO, BytesIO
import csv

api = Blueprint('api', __name__)

from database import db, User, Guest, Registration, Trip, Invoice, InvoiceItem
from version import version_manager, check_version_compatibility, get_version_changelog
from app import get_migration_manager

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

@api.route('/api/backup/guests', methods=['GET'])
@login_required
@role_required('admin')
def api_backup_guests():
    """Export all registered guests for a given month (no photos, admin only)."""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    fmt = request.args.get('format', 'csv')
    if not year or not month:
        return jsonify({'error': 'Missing year or month parameter'}), 400

    # Get guests for the given month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    guests = Guest.query.join(Registration).filter(
        Registration.created_at >= start_date,
        Registration.created_at < end_date
    ).all()

    # Prepare data (no photos)
    guest_data = []
    for g in guests:
        guest_data.append({
            'id': g.id,
            'registration_id': g.registration_id,
            'first_name': g.first_name,
            'last_name': g.last_name,
            'age_category': g.age_category,
            'document_type': g.document_type,
            'document_number': g.document_number,
            'gdpr_consent': g.gdpr_consent,
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'trip_title': g.registration.trip.title if g.registration and g.registration.trip else '',
            'registration_email': g.registration.email if g.registration else '',
            'registration_language': g.registration.language if g.registration else '',
        })

    if fmt == 'json':
        return jsonify(guest_data)
    else:
        # CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=guest_data[0].keys() if guest_data else [
            'id','registration_id','first_name','last_name','age_category','document_type','document_number','gdpr_consent','created_at','trip_title','registration_email','registration_language'])
        writer.writeheader()
        for row in guest_data:
            writer.writerow(row)
        csv_data = output.getvalue().encode('utf-8')
        output.close()
        return send_file(
            BytesIO(csv_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'guests_{year}_{month:02d}.csv'
        )

@api.route('/api/version')
def api_version():
    """Get application version information"""
    return jsonify(version_manager.get_version_info())

@api.route('/api/version/compatibility')
def api_version_compatibility():
    """Check version compatibility"""
    migration_manager = get_migration_manager()
    current_db_version = migration_manager.get_current_version()
    app_version = version_manager.get_current_version()
    
    compatibility = check_version_compatibility(app_version, current_db_version)
    
    return jsonify({
        'app_version': app_version,
        'database_version': current_db_version,
        'compatible': compatibility['compatible'],
        'recommendation': compatibility['recommendation']
    })

@api.route('/api/version/changelog/<version>')
def api_version_changelog(version):
    """Get changelog for a specific version"""
    changelog = get_version_changelog(version)
    return jsonify(changelog) 