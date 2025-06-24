from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps

amenities = Blueprint('amenities', __name__)

from app import app, db, User, Amenity, AmenityHousekeeper

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

@amenities.route('/admin/amenities')
@login_required
@role_required('admin')
def admin_amenities():
    """Manage amenities."""
    amenities_list = Amenity.query.filter_by(admin_id=current_user.id).order_by(Amenity.name).all()
    return render_template('admin/amenities.html', amenities=amenities_list)

@amenities.route('/admin/amenities/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_amenity():
    """Create a new amenity."""
    if request.method == 'POST':
        amenity = Amenity(
            name=request.form.get('name'),
            description=request.form.get('description'),
            max_guests=int(request.form.get('max_guests', 1)),
            admin_id=current_user.id,
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(amenity)
        db.session.commit()
        flash(_('Amenity created successfully!'), 'success')
        return redirect(url_for('amenities.admin_amenities'))
    
    return render_template('admin/new_amenity.html')

@amenities.route('/admin/amenities/<int:amenity_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_amenity(amenity_id):
    """Edit an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    if request.method == 'POST':
        amenity.name = request.form.get('name')
        amenity.description = request.form.get('description')
        amenity.max_guests = int(request.form.get('max_guests', 1))
        amenity.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash(_('Amenity updated successfully!'), 'success')
        return redirect(url_for('amenities.admin_amenities'))
    
    return render_template('admin/edit_amenity.html', amenity=amenity)

@amenities.route('/admin/amenities/<int:amenity_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_amenity(amenity_id):
    """Delete an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    # Check if amenity has trips
    if amenity.trips:
        flash(_('Cannot delete amenity with existing trips'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    db.session.delete(amenity)
    db.session.commit()
    flash(_('Amenity deleted successfully!'), 'success')
    return redirect(url_for('amenities.admin_amenities'))

@amenities.route('/admin/amenities/<int:amenity_id>/housekeepers')
@login_required
@role_required('admin')
def amenity_housekeepers(amenity_id):
    """Manage housekeepers for a specific amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    # Get all housekeepers
    housekeepers = User.query.filter_by(role='housekeeper').all()
    
    # Get current assignments
    assignments = AmenityHousekeeper.query.filter_by(amenity_id=amenity_id).all()
    assigned_housekeeper_ids = [a.housekeeper_id for a in assignments]
    
    # Get default housekeeper
    default_assignment = next((a for a in assignments if a.is_default), None)
    
    return render_template('admin/amenity_housekeepers.html', 
                         amenity=amenity, 
                         housekeepers=housekeepers,
                         assignments=assignments,
                         assigned_housekeeper_ids=assigned_housekeeper_ids,
                         default_assignment=default_assignment)

@amenities.route('/admin/amenities/<int:amenity_id>/housekeepers/assign', methods=['POST'])
@login_required
@role_required('admin')
def assign_housekeeper_to_amenity(amenity_id):
    """Assign a housekeeper to an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    housekeeper_id = request.form.get('housekeeper_id', type=int)
    is_default = request.form.get('is_default') == 'on'
    
    if not housekeeper_id:
        flash(_('Please select a housekeeper'), 'error')
        return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))
    
    # Check if housekeeper exists and is actually a housekeeper
    housekeeper = User.query.filter_by(id=housekeeper_id, role='housekeeper').first()
    if not housekeeper:
        flash(_('Invalid housekeeper selected'), 'error')
        return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))
    
    # Check if assignment already exists
    existing_assignment = AmenityHousekeeper.query.filter_by(
        amenity_id=amenity_id, 
        housekeeper_id=housekeeper_id
    ).first()
    
    if existing_assignment:
        flash(_('Housekeeper is already assigned to this amenity'), 'error')
        return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))
    
    # Create new assignment
    assignment = AmenityHousekeeper(
        amenity_id=amenity_id,
        housekeeper_id=housekeeper_id,
        is_default=is_default
    )
    
    # If this is set as default, unset other defaults for this amenity
    if is_default:
        AmenityHousekeeper.query.filter_by(
            amenity_id=amenity_id, 
            is_default=True
        ).update({'is_default': False})
    
    db.session.add(assignment)
    db.session.commit()
    
    flash(_('Housekeeper assigned successfully'), 'success')
    return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))

@amenities.route('/admin/amenities/<int:amenity_id>/housekeepers/<int:assignment_id>/set-default', methods=['POST'])
@login_required
@role_required('admin')
def set_default_housekeeper(amenity_id, assignment_id):
    """Set a housekeeper as default for an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    assignment = AmenityHousekeeper.query.get_or_404(assignment_id)
    if assignment.amenity_id != amenity_id:
        flash(_('Invalid assignment'), 'error')
        return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))
    
    # Unset all other defaults for this amenity
    AmenityHousekeeper.query.filter_by(
        amenity_id=amenity_id, 
        is_default=True
    ).update({'is_default': False})
    
    # Set this assignment as default
    assignment.is_default = True
    db.session.commit()
    
    flash(_('Default housekeeper updated successfully'), 'success')
    return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))

@amenities.route('/admin/amenities/<int:amenity_id>/housekeepers/<int:assignment_id>/remove', methods=['POST'])
@login_required
@role_required('admin')
def remove_housekeeper_from_amenity(amenity_id, assignment_id):
    """Remove a housekeeper from an amenity."""
    amenity = Amenity.query.get_or_404(amenity_id)
    if amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('amenities.admin_amenities'))
    
    assignment = AmenityHousekeeper.query.get_or_404(assignment_id)
    if assignment.amenity_id != amenity_id:
        flash(_('Invalid assignment'), 'error')
        return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))
    
    db.session.delete(assignment)
    db.session.commit()
    
    flash(_('Housekeeper removed from amenity successfully'), 'success')
    return redirect(url_for('amenities.amenity_housekeepers', amenity_id=amenity_id))

@amenities.route('/admin/amenities/<int:amenity_id>/sync', methods=['POST'])
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
        else:
            failed.append(f"{calendar.name}: {result['message']}")
    if failed:
        message = f"Synced {total_synced} new, updated {total_updated} existing. Failed: {'; '.join(failed)}"
        flash(_('Calendar sync completed with some errors: %(message)s', message=message), 'warning')
    else:
        message = f"Successfully synced {total_synced} new and updated {total_updated} existing reservations."
        flash(_('Calendar sync successful: %(message)s', message=message), 'success')
    return redirect(url_for('amenities.admin_amenities')) 