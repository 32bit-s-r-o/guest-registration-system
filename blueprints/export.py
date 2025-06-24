from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime
from io import StringIO, BytesIO
import csv

export = Blueprint('export', __name__)

from database import db, User, Registration, Guest, Trip, Invoice

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

@export.route('/admin/export/registrations')
@login_required
@role_required('admin')
def export_registrations_csv():
    """Export registrations to CSV."""
    # Get all registrations for the current admin
    registrations = Registration.query.join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Registration ID'),
        _('Trip Title'),
        _('Email'),
        _('Status'),
        _('Language'),
        _('Created Date'),
        _('Updated Date'),
        _('Guest Count'),
        _('Admin Comment')
    ])
    
    # Write data
    for reg in registrations:
        writer.writerow([
            reg.id,
            reg.trip.title,
            reg.email,
            reg.status,
            reg.language,
            reg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            reg.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            len(reg.guests),
            reg.admin_comment or ''
        ])
    
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'registrations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@export.route('/admin/export/guests')
@login_required
@role_required('admin')
def export_guests_csv():
    """Export guests to CSV."""
    # Get all guests for registrations belonging to the current admin
    guests = Guest.query.join(Registration).join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Guest ID'),
        _('Registration ID'),
        _('Trip Title'),
        _('First Name'),
        _('Last Name'),
        _('Age Category'),
        _('Document Type'),
        _('Document Number'),
        _('GDPR Consent'),
        _('Created Date')
    ])
    
    # Write data
    for guest in guests:
        writer.writerow([
            guest.id,
            guest.registration_id,
            guest.registration.trip.title,
            guest.first_name,
            guest.last_name,
            guest.age_category,
            guest.document_type,
            guest.document_number,
            'Yes' if guest.gdpr_consent else 'No',
            guest.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'guests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@export.route('/admin/export/trips')
@login_required
@role_required('admin')
def export_trips_csv():
    """Export trips to CSV."""
    # Get all trips for the current admin
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Trip ID'),
        _('Title'),
        _('Start Date'),
        _('End Date'),
        _('Max Guests'),
        _('Created Date'),
        _('Amenity'),
        _('Calendar'),
        _('Externally Synced'),
        _('External Guest Name'),
        _('External Guest Email'),
        _('External Guest Count'),
        _('External Confirmation Code'),
        _('Registration Count'),
        _('Pending Count'),
        _('Approved Count'),
        _('Rejected Count')
    ])
    
    # Write data
    for trip in trips:
        registrations = trip.registrations
        pending_count = len([r for r in registrations if r.status == 'pending'])
        approved_count = len([r for r in registrations if r.status == 'approved'])
        rejected_count = len([r for r in registrations if r.status == 'rejected'])
        
        writer.writerow([
            trip.id,
            trip.title,
            trip.start_date.strftime('%Y-%m-%d'),
            trip.end_date.strftime('%Y-%m-%d'),
            trip.max_guests,
            trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            trip.amenity.name if trip.amenity else '',
            trip.calendar.name if trip.calendar else '',
            'Yes' if trip.is_externally_synced else 'No',
            trip.external_guest_name or '',
            trip.external_guest_email or '',
            trip.external_guest_count or '',
            trip.external_confirm_code or '',
            len(registrations),
            pending_count,
            approved_count,
            rejected_count
        ])
    
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'trips_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@export.route('/admin/export/invoices')
@login_required
@role_required('admin')
def export_invoices_csv():
    """Export invoices to CSV."""
    # Get all invoices for the current admin
    invoices = Invoice.query.filter_by(admin_id=current_user.id).all()
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Invoice ID'),
        _('Invoice Number'),
        _('Client Name'),
        _('Client Email'),
        _('Client VAT Number'),
        _('Issue Date'),
        _('Due Date'),
        _('Subtotal'),
        _('VAT Total'),
        _('Total Amount'),
        _('Currency'),
        _('Status'),
        _('Created Date'),
        _('Updated Date'),
        _('Registration ID'),
        _('Trip Title')
    ])
    
    # Write data
    for invoice in invoices:
        trip_title = invoice.registration.trip.title if invoice.registration else ''
        writer.writerow([
            invoice.id,
            invoice.invoice_number,
            invoice.client_name,
            invoice.client_email or '',
            invoice.client_vat_number or '',
            invoice.issue_date.strftime('%Y-%m-%d'),
            invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
            float(invoice.subtotal),
            float(invoice.vat_total),
            float(invoice.total_amount),
            invoice.currency,
            invoice.status,
            invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            invoice.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            invoice.registration_id or '',
            trip_title
        ])
    
    output.seek(0)
    # Convert to bytes and create BytesIO
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    
    return send_file(
        BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'invoices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    ) 