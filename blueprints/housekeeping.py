from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user, login_user
from flask_babel import gettext as _
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os

housekeeping = Blueprint('housekeeping', __name__)

from database import db, User, Housekeeping, HousekeepingPhoto, Trip, Amenity, AmenityHousekeeper, Calendar, create_missing_housekeeping_tasks_for_calendar
from utils import role_required, allowed_file

@housekeeping.route('/housekeeper')
def housekeeper_landing():
    """Housekeeper landing page."""
    return render_template('housekeeper/landing.html')

@housekeeping.route('/housekeeper/login', methods=['GET', 'POST'])
def housekeeper_login():
    """Housekeeper login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_deleted=False).first()
        if user and user.check_password(password) and user.role == 'housekeeper':
            login_user(user)
            return redirect(url_for('housekeeping.housekeeper_dashboard'))
        else:
            flash(_('Invalid username or password'), 'error')
    
    return render_template('housekeeper/login.html')

@housekeeping.route('/housekeeper/dashboard')
@login_required
@role_required('housekeeper')
def housekeeper_dashboard():
    # Show assigned housekeeping tasks (for now, all tasks)
    tasks = Housekeeping.query.filter_by(housekeeper_id=current_user.id).all()
    return render_template('housekeeper/dashboard.html', tasks=tasks)

@housekeeping.route('/housekeeper/calendar')
@login_required
@role_required('housekeeper')
def housekeeper_calendar():
    return render_template('housekeeper/calendar.html')

@housekeeping.route('/api/housekeeping_events')
@login_required
@role_required('housekeeper')
def housekeeping_events_api():
    # Return housekeeping tasks as JSON for the calendar
    tasks = Housekeeping.query.filter_by(housekeeper_id=current_user.id).all()
    events = []
    for task in tasks:
        # Use the trip's end date for the title if available
        trip_end_date = task.trip.end_date if task.trip and task.trip.end_date else task.date
        
        # Format the date using the user's preferred format
        try:
            date_format = current_user.date_format or 'd.m.Y'
            # Convert PHP/JS style to Python strftime
            format_map = [
                ('d', '%d'),
                ('j', '%-d'),
                ('m', '%m'),
                ('n', '%-m'),
                ('Y', '%Y'),
                ('y', '%y'),
            ]
            py_format = date_format
            for php, py in format_map:
                py_format = py_format.replace(php, py)
            formatted_date = trip_end_date.strftime(py_format)
        except (ValueError, TypeError):
            formatted_date = trip_end_date.strftime('%d.%m.%Y')
        
        events.append({
            'id': task.id,
            'title': f'Housekeeping - {formatted_date}',
            'start': task.date.isoformat(),
            'end': task.date.isoformat(),
            'status': task.status,
            'pay_amount': float(task.pay_amount),
            'paid': task.paid,
        })
    return jsonify(events)

@housekeeping.route('/housekeeper/upload_photo/<int:task_id>', methods=['POST'])
@login_required
@role_required('housekeeper')
def upload_amenity_photo(task_id):
    """Upload amenity photo for a housekeeping task (multiple supported)."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Verify the task belongs to the current housekeeper
    if task.housekeeper_id != current_user.id:
        from flask import abort
        abort(403)
    
    if 'photo' not in request.files:
        flash(_('No photo selected'), 'error')
        return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task_id))
    
    file = request.files['photo']
    if file.filename == '':
        flash(_('No photo selected'), 'error')
        return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task_id))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(f"amenity_{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Add new photo record
        photo = HousekeepingPhoto(task_id=task_id, file_path=filename)
        db.session.add(photo)
        task.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Photo uploaded successfully'), 'success')
    else:
        flash(_('Invalid file type. Please upload JPG or PNG files only.'), 'error')
    
    return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task_id))

@housekeeping.route('/admin/housekeeping', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_housekeeping():
    # Filtering
    housekeeper_id = request.args.get('housekeeper_id', type=int)
    status = request.args.get('status')
    amenity_id = request.args.get('amenity_id', type=int)
    query = Housekeeping.query.join(Trip)
    
    if housekeeper_id:
        query = query.filter_by(housekeeper_id=housekeeper_id)
    if status:
        query = query.filter_by(status=status)
    if amenity_id:
        query = query.filter(Trip.amenity_id == amenity_id)
    
    tasks = query.order_by(Housekeeping.date.desc()).all()
    housekeepers = User.query.filter_by(role='housekeeper').all()
    
    # Get amenities for filtering
    amenities = Amenity.query.filter_by(admin_id=current_user.id).order_by(Amenity.name).all()

    # Pay summaries
    pay_summary = {}
    for hk in housekeepers:
        hk_tasks = [t for t in tasks if t.housekeeper_id == hk.id]
        # Only count completed tasks for payment
        completed_tasks = [t for t in hk_tasks if t.status == 'completed']
        pay_summary[hk.id] = {
            'username': hk.username,
            'total': sum(float(t.pay_amount) for t in completed_tasks),
            'paid': sum(float(t.pay_amount) for t in completed_tasks if t.paid),
            'pending': sum(float(t.pay_amount) for t in completed_tasks if not t.paid),
        }
    
    # Grand totals - only count completed tasks
    completed_tasks = [t for t in tasks if t.status == 'completed']
    grand_total = sum(float(t.pay_amount) for t in completed_tasks)
    grand_paid = sum(float(t.pay_amount) for t in completed_tasks if t.paid)
    grand_pending = sum(float(t.pay_amount) for t in completed_tasks if not t.paid)

    # Handle pay status/amount update
    if request.method == 'POST':
        task_id = request.form.get('task_id', type=int)
        pay_amount = request.form.get('pay_amount', type=float)
        paid = request.form.get('paid') == 'on'
        task = Housekeeping.query.get_or_404(task_id)
        task.pay_amount = pay_amount
        task.paid = paid
        if paid:
            task.paid_date = datetime.utcnow()
        db.session.commit()
        flash(_('Housekeeping pay updated.'), 'success')
        return redirect(url_for('housekeeping.admin_housekeeping', housekeeper_id=housekeeper_id, status=status, amenity_id=amenity_id))

    return render_template('admin/housekeeping.html', tasks=tasks, housekeepers=housekeepers, amenities=amenities, selected_housekeeper=housekeeper_id, selected_status=status, selected_amenity=amenity_id, pay_summary=pay_summary, grand_total=grand_total, grand_paid=grand_paid, grand_pending=grand_pending)

@housekeeping.route('/housekeeper/task/<int:task_id>')
@login_required
def housekeeper_task_detail(task_id):
    """Display detailed view of a housekeeping task."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Check access: either the housekeeper assigned to the task or admin who owns the amenity
    if current_user.role == 'housekeeper':
        if task.housekeeper_id != current_user.id:
            flash(_('Access denied'), 'error')
            return redirect(url_for('housekeeping.housekeeper_dashboard'))
    elif current_user.role == 'admin':
        if task.trip.amenity.admin_id != current_user.id:
            flash(_('Access denied'), 'error')
            return redirect(url_for('housekeeping.admin_housekeeping'))
    else:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('housekeeper/task_detail.html', task=task, today=datetime.utcnow().date())

@housekeeping.route('/housekeeper/task/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(task_id):
    """Update the status of a housekeeping task."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Check access: either the housekeeper assigned to the task or admin who owns the amenity
    if current_user.role == 'housekeeper':
        if task.housekeeper_id != current_user.id:
            flash(_('Access denied'), 'error')
            return redirect(url_for('housekeeping.housekeeper_dashboard'))
    elif current_user.role == 'admin':
        if task.trip.amenity.admin_id != current_user.id:
            flash(_('Access denied'), 'error')
            return redirect(url_for('housekeeping.admin_housekeeping'))
    else:
        flash(_('Access denied'), 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    new_status = request.form.get('status')
    if new_status in ['pending', 'in_progress', 'completed']:
        # Check if trying to mark as completed - only apply date restriction to housekeepers
        if new_status == 'completed' and current_user.role == 'housekeeper':
            today = datetime.utcnow().date()
            if task.date != today:
                # Convert PHP/JS style to Python strftime format
                format_map = [
                    ('d', '%d'),
                    ('j', '%-d'),
                    ('m', '%m'),
                    ('n', '%-m'),
                    ('Y', '%Y'),
                    ('y', '%y'),
                ]
                
                date_format = current_user.date_format or 'd.m.Y'
                py_format = date_format
                for php, py in format_map:
                    py_format = py_format.replace(php, py)
                
                flash(_('Tasks can only be marked as completed on the task date (%(task_date)s). Today is %(today)s.', 
                       task_date=task.date.strftime(py_format),
                       today=today.strftime(py_format)), 'error')
                return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task_id))
        
        task.status = new_status
        task.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Task status updated successfully'), 'success')
    else:
        flash(_('Invalid status'), 'error')
    
    # Redirect based on user role
    if current_user.role == 'admin':
        return redirect(url_for('housekeeping.admin_housekeeping_task_detail', task_id=task_id))
    else:
        return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task_id))

@housekeeping.route('/admin/housekeeping/bulk-update-status', methods=['POST'])
@login_required
@role_required('admin')
def bulk_update_housekeeping_status():
    """Bulk update status for multiple housekeeping tasks."""
    task_ids = request.form.getlist('task_ids')
    new_status = request.form.get('status')
    
    if not task_ids:
        flash(_('No tasks selected'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    
    if new_status not in ['pending', 'in_progress', 'completed']:
        flash(_('Invalid status'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    
    updated_count = 0
    for task_id in task_ids:
        task = Housekeeping.query.get(task_id)
        if task and task.trip.amenity.admin_id == current_user.id:
            task.status = new_status
            task.updated_at = datetime.utcnow()
            updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
        flash(_('%(count)d tasks updated successfully', count=updated_count), 'success')
    else:
        flash(_('No tasks were updated'), 'error')
    
    return redirect(url_for('housekeeping.admin_housekeeping'))

@housekeeping.route('/housekeeper/task/<int:task_id>/add-notes', methods=['POST'])
@login_required
@role_required('housekeeper')
def add_task_notes(task_id):
    """Add or update notes for a housekeeping task."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Check if the current housekeeper has access to this task
    if task.housekeeper_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('housekeeping.housekeeper_dashboard'))
    
    notes = request.form.get('notes', '').strip()
    task.notes = notes
    task.updated_at = datetime.utcnow()
    db.session.commit()
    flash(_('Task notes updated successfully'), 'success')
    
    return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task_id))

@housekeeping.route('/housekeeper/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
@role_required('housekeeper')
def delete_housekeeping_photo(photo_id):
    photo = HousekeepingPhoto.query.get_or_404(photo_id)
    task = photo.task
    # Check if the current housekeeper has access to this task
    if task.housekeeper_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('housekeeping.housekeeper_dashboard'))
    # Delete the file from disk
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(photo)
    db.session.commit()
    flash(_('Photo deleted successfully'), 'success')
    return redirect(url_for('housekeeping.housekeeper_task_detail', task_id=task.id))

@housekeeping.route('/admin/housekeeping/task/<int:task_id>')
@login_required
@role_required('admin')
def admin_housekeeping_task_detail(task_id):
    """Admin view of housekeeping task details."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Check if admin has access to this task (through amenity ownership)
    if task.trip.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    
    # Get all users for the reassignment dropdown
    users = User.query.filter_by(is_deleted=False).all()
    
    return render_template('admin/housekeeping_task_detail.html', task=task, today=datetime.utcnow().date(), users=users)

@housekeeping.route('/admin/housekeeping/<int:task_id>/reassign', methods=['POST'])
@login_required
@role_required('admin')
def reassign_housekeeping_task(task_id):
    """Reassign a housekeeping task to a different housekeeper."""
    task = Housekeeping.query.get_or_404(task_id)
    
    # Check if admin has access to this task (through amenity ownership)
    if task.trip.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    
    new_housekeeper_id = request.form.get('housekeeper_id', type=int)
    
    if not new_housekeeper_id:
        flash(_('Please select a housekeeper'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    
    # Check if housekeeper exists and is actually a housekeeper
    housekeeper = User.query.filter_by(id=new_housekeeper_id, role='housekeeper').first()
    if not housekeeper:
        flash(_('Invalid housekeeper selected'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    
    # Update the task
    task.housekeeper_id = new_housekeeper_id
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(_('Housekeeping task reassigned successfully'), 'success')
    return redirect(url_for('housekeeping.admin_housekeeping'))

@housekeeping.route('/admin/housekeeping/<int:task_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_housekeeping_task(task_id):
    """Delete a housekeeping task."""
    task = Housekeeping.query.get_or_404(task_id)
    # Check if admin has access to this task (through amenity ownership)
    if task.trip.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('housekeeping.admin_housekeeping'))
    try:
        db.session.delete(task)
        db.session.commit()
        flash(_('Housekeeping task deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting housekeeping task: %(error)s', error=str(e)), 'error')
    return redirect(url_for('housekeeping.admin_housekeeping'))

@housekeeping.route('/admin/calendars/<int:calendar_id>/create-housekeeping-tasks', methods=['POST'])
@login_required
@role_required('admin')
def create_housekeeping_tasks_from_calendar(calendar_id):
    """Create housekeeping tasks for all trips in a calendar that don't already have one."""
    calendar = Calendar.query.get_or_404(calendar_id)
    if calendar.amenity.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('calendars.admin_calendars'))
    
    # Check if there's a default housekeeper assigned
    default_assignment = AmenityHousekeeper.query.filter_by(
        amenity_id=calendar.amenity_id, is_default=True).first()
    
    if not default_assignment and not calendar.amenity.default_housekeeper_id:
        flash(_('No default housekeeper assigned to this amenity. Please assign a default housekeeper first.'), 'error')
        return redirect(url_for('calendars.admin_calendars'))
    
    # Use the helper function to create missing tasks
    from app import create_missing_housekeeping_tasks_for_calendar
    created = create_missing_housekeeping_tasks_for_calendar(calendar_id)
    
    if created > 0:
        flash(_('%(num)d housekeeping tasks created from calendar.', num=created), 'success')
    else:
        flash(_('No new housekeeping tasks created. All trips already have housekeeping tasks.'), 'info')
    
    return redirect(url_for('calendars.admin_calendars'))

@housekeeping.route('/admin/amenities/<int:amenity_id>/housekeepers')
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

@housekeeping.route('/admin/amenities/<int:amenity_id>/housekeepers/assign', methods=['POST'])
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
        return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))
    
    # Check if housekeeper exists and is actually a housekeeper
    housekeeper = User.query.filter_by(id=housekeeper_id, role='housekeeper').first()
    if not housekeeper:
        flash(_('Invalid housekeeper selected'), 'error')
        return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))
    
    # Check if assignment already exists
    existing_assignment = AmenityHousekeeper.query.filter_by(
        amenity_id=amenity_id, 
        housekeeper_id=housekeeper_id
    ).first()
    
    if existing_assignment:
        flash(_('Housekeeper is already assigned to this amenity'), 'error')
        return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))
    
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
    return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))

@housekeeping.route('/admin/amenities/<int:amenity_id>/housekeepers/<int:assignment_id>/set-default', methods=['POST'])
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
        return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))
    
    # Unset all other defaults for this amenity
    AmenityHousekeeper.query.filter_by(
        amenity_id=amenity_id, 
        is_default=True
    ).update({'is_default': False})
    
    # Set this assignment as default
    assignment.is_default = True
    db.session.commit()
    
    flash(_('Default housekeeper updated successfully'), 'success')
    return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))

@housekeeping.route('/admin/amenities/<int:amenity_id>/housekeepers/<int:assignment_id>/remove', methods=['POST'])
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
        return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id))
    
    db.session.delete(assignment)
    db.session.commit()
    
    flash(_('Housekeeper removed from amenity successfully'), 'success')
    return redirect(url_for('housekeeping.amenity_housekeepers', amenity_id=amenity_id)) 