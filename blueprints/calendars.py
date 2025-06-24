from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime

calendars = Blueprint('calendars', __name__)

from app import app, db, User, Calendar, Amenity, Trip

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

@calendars.route('/admin/calendars')
@login_required
@role_required('admin')
def admin_calendars():
    """Manage calendars."""
    # Get all amenities owned by this admin
    amenities = Amenity.query.filter_by(admin_id=current_user.id).all()
    calendars_by_amenity = {}
    
    for amenity in amenities:
        calendars_by_amenity[amenity] = amenity.calendars
    
    return render_template('admin/calendars.html', calendars_by_amenity=calendars_by_amenity)

@calendars.route('/admin/calendars/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_calendar():
    """Create a new calendar."""
    if request.method == 'POST':
        amenity_id = request.form.get('amenity_id')
        amenity = Amenity.query.get(amenity_id)
        
        if not amenity or amenity.admin_id != current_user.id:
            flash(_('Invalid amenity selected'), 'error')
            return redirect(url_for('calendars.new_calendar'))
        
        calendar = Calendar(
            name=request.form.get('name'),
            description=request.form.get('description'),
            calendar_url=request.form.get('calendar_url'),
            calendar_type=request.form.get('calendar_type', 'airbnb'),
            sync_enabled=request.form.get('sync_enabled') == 'on',
            sync_frequency=request.form.get('sync_frequency', 'daily'),
            is_active=request.form.get('is_active') == 'on',
            amenity_id=amenity_id
        )
        db.session.add(calendar)
        db.session.commit()
        flash(_('Calendar created successfully!'), 'success')
        return redirect(url_for('calendars.admin_calendars'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/new_calendar.html', amenities=amenities)

@calendars.route('/admin/calendars/<int:calendar_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_calendar(calendar_id):
    """Edit a calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('calendars.admin_calendars'))
    
    if request.method == 'POST':
        amenity_id = request.form.get('amenity_id')
        amenity = Amenity.query.get(amenity_id)
        
        if not amenity or amenity.admin_id != current_user.id:
            flash(_('Invalid amenity selected'), 'error')
            return redirect(url_for('calendars.edit_calendar', calendar_id=calendar_id))
        
        calendar.name = request.form.get('name')
        calendar.description = request.form.get('description')
        calendar.calendar_url = request.form.get('calendar_url')
        calendar.calendar_type = request.form.get('calendar_type', 'airbnb')
        calendar.sync_enabled = request.form.get('sync_enabled') == 'on'
        calendar.sync_frequency = request.form.get('sync_frequency', 'daily')
        calendar.is_active = request.form.get('is_active') == 'on'
        calendar.amenity_id = amenity_id
        
        db.session.commit()
        flash(_('Calendar updated successfully!'), 'success')
        return redirect(url_for('calendars.admin_calendars'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/edit_calendar.html', calendar=calendar, amenities=amenities)

@calendars.route('/admin/calendars/<int:calendar_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_calendar(calendar_id):
    """Delete a calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('calendars.admin_calendars'))
    
    # Check if calendar has trips
    if calendar.trips:
        flash(_('Cannot delete calendar with existing trips'), 'error')
        return redirect(url_for('calendars.admin_calendars'))
    
    db.session.delete(calendar)
    db.session.commit()
    flash(_('Calendar deleted successfully!'), 'success')
    return redirect(url_for('calendars.admin_calendars'))

@calendars.route('/admin/sync-airbnb', methods=['POST'])
@login_required
def sync_airbnb():
    """Sync with all calendars for the current admin."""
    from app import sync_all_calendars_for_admin
    result = sync_all_calendars_for_admin(current_user.id)
    
    if result['success']:
        flash(_('Calendar sync successful: %(message)s', message=result['message']), 'success')
    else:
        flash(_('Calendar sync failed: %(message)s', message=result['message']), 'error')
    
    return redirect(url_for('trips.admin_trips'))

@calendars.route('/admin/sync-calendar/<int:calendar_id>', methods=['POST'])
@login_required
def sync_calendar(calendar_id):
    """Sync with a specific calendar."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    from app import sync_calendar_reservations
    result = sync_calendar_reservations(calendar_id)
    
    if result['success']:
        flash(_('Calendar sync successful for %(calendar)s: %(message)s', 
                calendar=calendar.name, message=result['message']), 'success')
    else:
        flash(_('Calendar sync failed for %(calendar)s: %(message)s', 
                calendar=calendar.name, message=result['message']), 'error')
    
    return redirect(url_for('amenities.admin_amenities'))

@calendars.route('/admin/amenities/<int:amenity_id>/sync', methods=['POST'])
@login_required
@role_required('admin')
def sync_amenity_calendars(amenity_id):
    """Sync all calendars for a specific amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    calendars = amenity.calendars
    total_synced = 0
    total_updated = 0
    failed = []
    for calendar in calendars:
        if calendar.sync_enabled and calendar.is_active:
            from app import sync_calendar_reservations
            result = sync_calendar_reservations(calendar.id)
            if result['success']:
                total_synced += result.get('synced', 0)
                total_updated += result.get('updated', 0)
            else:
                failed.append(f"{calendar.name}: {result['message']}")
    if failed:
        message = f"Synced {total_synced} new, updated {total_updated} existing. Failed: {'; '.join(failed)}"
        flash(_('Calendar sync completed with some errors: %(message)s', message=message), 'warning')
    else:
        message = f"Successfully synced {total_synced} new and updated {total_updated} existing reservations."
        flash(_('Calendar sync successful: %(message)s', message=message), 'success')
    return redirect(url_for('amenities.admin_amenities')) 