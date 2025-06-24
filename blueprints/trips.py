from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime

trips = Blueprint('trips', __name__)

# Import database models from database.py
from database import db, User, Trip, Amenity

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                from flask_login import LoginManager
                # Get the login manager from current app
                login_manager = current_app.extensions.get('login_manager')
                if login_manager:
                    return login_manager.unauthorized()
                else:
                    from flask import abort
                    abort(401)
            if current_user.role != role:
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@trips.route('/admin/trips')
@login_required
@role_required('admin')
def admin_trips():
    # Get trips grouped by amenity
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    trips_by_amenity = {}
    
    for amenity in amenities:
        trips_by_amenity[amenity] = Trip.query.filter_by(amenity_id=amenity.id).order_by(Trip.start_date).all()
    
    # Flatten trips for the template
    trips_list = []
    for amenity_trips in trips_by_amenity.values():
        trips_list.extend(amenity_trips)
    
    return render_template('admin/trips.html', trips=trips_list, trips_by_amenity=trips_by_amenity, amenities=amenities)

@trips.route('/admin/trips/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_trip():
    if request.method == 'POST':
        amenity_id = request.form.get('amenity_id')
        amenity = Amenity.query.get(amenity_id)
        
        if not amenity or amenity.admin_id != current_user.id:
            flash(_('Invalid amenity selected'), 'error')
            return redirect(url_for('trips.new_trip'))
        
        # Get max_guests from form, fallback to amenity's max_guests
        try:
            max_guests = int(request.form.get('max_guests', '').strip())
            if max_guests < 1:
                raise ValueError
        except Exception:
            max_guests = amenity.max_guests
        
        trip = Trip(
            title=request.form.get('title'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            max_guests=max_guests,
            admin_id=current_user.id,
            amenity_id=amenity_id
        )
        db.session.add(trip)
        db.session.commit()
        flash(_('Trip created successfully!'), 'success')
        return redirect(url_for('trips.admin_trips'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/new_trip.html', amenities=amenities)

@trips.route('/admin/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_trip(trip_id):
    """Edit an existing trip."""
    trip = Trip.query.get_or_404(trip_id)
    if trip.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('trips.admin_trips'))
    
    if request.method == 'POST':
        amenity_id = request.form.get('amenity_id')
        amenity = Amenity.query.get(amenity_id)
        
        if not amenity or amenity.admin_id != current_user.id:
            flash(_('Invalid amenity selected'), 'error')
            return redirect(url_for('trips.edit_trip', trip_id=trip_id))
        
        # Get max_guests from form, fallback to amenity's max_guests
        try:
            max_guests = int(request.form.get('max_guests', '').strip())
            if max_guests < 1:
                raise ValueError
        except Exception:
            max_guests = amenity.max_guests
        
        trip.title = request.form.get('title')
        trip.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trip.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        trip.max_guests = max_guests
        trip.amenity_id = amenity_id
        
        db.session.commit()
        flash(_('Trip updated successfully!'), 'success')
        return redirect(url_for('trips.admin_trips'))
    
    amenities = Amenity.query.filter_by(admin_id=current_user.id, is_active=True).order_by(Amenity.name).all()
    return render_template('admin/edit_trip.html', trip=trip, amenities=amenities)

@trips.route('/admin/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_trip(trip_id):
    """Delete a trip."""
    trip = Trip.query.get_or_404(trip_id)
    if trip.admin_id != current_user.id:
        flash(_('Access denied'), 'error')
        return redirect(url_for('trips.admin_trips'))
    
    # Check if trip has registrations
    if trip.registrations:
        flash(_('Cannot delete trip with existing registrations'), 'error')
        return redirect(url_for('trips.admin_trips'))
    
    db.session.delete(trip)
    db.session.commit()
    flash(_('Trip deleted successfully!'), 'success')
    return redirect(url_for('trips.admin_trips')) 