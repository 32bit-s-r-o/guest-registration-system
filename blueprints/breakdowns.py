from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict

breakdowns = Blueprint('breakdowns', __name__)

from app import app, db, User, Registration, Guest, Trip, Invoice

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

@breakdowns.route('/admin/breakdowns')
@login_required
@role_required('admin')
def admin_breakdowns():
    """Main breakdowns/analytics page."""
    return render_template('admin/breakdowns.html')

@breakdowns.route('/admin/breakdowns/registrations')
@login_required
@role_required('admin')
def registration_breakdown():
    """Registration statistics and breakdowns."""
    # Get all registrations for the current admin
    registrations = Registration.query.join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Status breakdown
    status_counts = defaultdict(int)
    for reg in registrations:
        status_counts[reg.status] += 1
    
    # Monthly breakdown
    monthly_counts = defaultdict(int)
    for reg in registrations:
        month_key = reg.created_at.strftime('%Y-%m')
        monthly_counts[month_key] += 1
    
    # Trip breakdown
    trip_counts = defaultdict(int)
    for reg in registrations:
        trip_counts[reg.trip.title] += 1
    
    # Language breakdown
    language_counts = defaultdict(int)
    for reg in registrations:
        language_counts[reg.language] += 1
    
    # Guest count distribution
    guest_count_distribution = defaultdict(int)
    for reg in registrations:
        guest_count_distribution[len(reg.guests)] += 1
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_registrations = [reg for reg in registrations if reg.created_at >= thirty_days_ago]
    
    stats = {
        'total_registrations': len(registrations),
        'pending_count': status_counts['pending'],
        'approved_count': status_counts['approved'],
        'rejected_count': status_counts['rejected'],
        'recent_count': len(recent_registrations),
        'status_breakdown': dict(status_counts),
        'monthly_breakdown': dict(monthly_counts),
        'trip_breakdown': dict(trip_counts),
        'language_breakdown': dict(language_counts),
        'guest_count_distribution': dict(guest_count_distribution)
    }
    
    return render_template('admin/registration_breakdown.html', stats=stats, registrations=registrations)

@breakdowns.route('/admin/breakdowns/guests')
@login_required
@role_required('admin')
def guest_breakdown():
    """Guest statistics and breakdowns."""
    # Get all guests for registrations belonging to the current admin
    guests = Guest.query.join(Registration).join(Trip).filter(Trip.admin_id == current_user.id).all()
    
    # Age category breakdown
    age_category_counts = defaultdict(int)
    for guest in guests:
        age_category_counts[guest.age_category] += 1
    
    # Document type breakdown
    document_type_counts = defaultdict(int)
    for guest in guests:
        document_type_counts[guest.document_type] += 1
    
    # GDPR consent breakdown
    gdpr_consent_count = sum(1 for guest in guests if guest.gdpr_consent)
    gdpr_no_consent_count = len(guests) - gdpr_consent_count
    
    # Monthly guest registration
    monthly_guest_counts = defaultdict(int)
    for guest in guests:
        month_key = guest.created_at.strftime('%Y-%m')
        monthly_guest_counts[month_key] += 1
    
    # Trip breakdown for guests
    trip_guest_counts = defaultdict(int)
    for guest in guests:
        trip_guest_counts[guest.registration.trip.title] += 1
    
    stats = {
        'total_guests': len(guests),
        'adult_count': age_category_counts['adult'],
        'child_count': age_category_counts['child'],
        'gdpr_consent_count': gdpr_consent_count,
        'gdpr_no_consent_count': gdpr_no_consent_count,
        'age_category_breakdown': dict(age_category_counts),
        'document_type_breakdown': dict(document_type_counts),
        'monthly_guest_counts': dict(monthly_guest_counts),
        'trip_guest_counts': dict(trip_guest_counts)
    }
    
    return render_template('admin/guest_breakdown.html', stats=stats, guests=guests)

@breakdowns.route('/admin/breakdowns/trips')
@login_required
@role_required('admin')
def trip_breakdown():
    """Trip statistics and breakdowns."""
    # Get all trips for the current admin
    trips = Trip.query.filter_by(admin_id=current_user.id).all()
    
    # Registration count per trip
    trip_registration_counts = {}
    trip_guest_counts = {}
    trip_status_breakdowns = {}
    
    for trip in trips:
        registrations = trip.registrations
        trip_registration_counts[trip.title] = len(registrations)
        
        # Count guests per trip
        guest_count = sum(len(reg.guests) for reg in registrations)
        trip_guest_counts[trip.title] = guest_count
        
        # Status breakdown per trip
        status_counts = defaultdict(int)
        for reg in registrations:
            status_counts[reg.status] += 1
        trip_status_breakdowns[trip.title] = dict(status_counts)
    
    # Monthly trip creation
    monthly_trip_counts = defaultdict(int)
    for trip in trips:
        month_key = trip.created_at.strftime('%Y-%m')
        monthly_trip_counts[month_key] += 1
    
    # External sync statistics
    externally_synced_count = sum(1 for trip in trips if trip.is_externally_synced)
    externally_not_synced_count = len(trips) - externally_synced_count
    
    # Duration statistics
    trip_durations = []
    for trip in trips:
        duration = (trip.end_date - trip.start_date).days
        trip_durations.append(duration)
    
    avg_duration = sum(trip_durations) / len(trip_durations) if trip_durations else 0
    
    stats = {
        'total_trips': len(trips),
        'externally_synced_count': externally_synced_count,
        'externally_not_synced_count': externally_not_synced_count,
        'avg_duration_days': round(avg_duration, 1),
        'trip_registration_counts': trip_registration_counts,
        'trip_guest_counts': trip_guest_counts,
        'trip_status_breakdowns': trip_status_breakdowns,
        'monthly_trip_counts': dict(monthly_trip_counts)
    }
    
    return render_template('admin/trip_breakdown.html', stats=stats, trips=trips)

@breakdowns.route('/admin/breakdowns/invoices')
@login_required
@role_required('admin')
def invoice_breakdown():
    """Invoice statistics and breakdowns."""
    # Get all invoices for the current admin
    invoices = Invoice.query.filter_by(admin_id=current_user.id).all()
    
    # Status breakdown
    status_counts = defaultdict(int)
    for invoice in invoices:
        status_counts[invoice.status] += 1
    
    # Monthly invoice creation
    monthly_invoice_counts = defaultdict(int)
    for invoice in invoices:
        month_key = invoice.created_at.strftime('%Y-%m')
        monthly_invoice_counts[month_key] += 1
    
    # Amount statistics
    total_amount = sum(float(invoice.total_amount) for invoice in invoices)
    avg_amount = total_amount / len(invoices) if invoices else 0
    
    # Status-based amounts
    status_amounts = defaultdict(float)
    for invoice in invoices:
        status_amounts[invoice.status] += float(invoice.total_amount)
    
    # Currency breakdown
    currency_counts = defaultdict(int)
    for invoice in invoices:
        currency_counts[invoice.currency] += 1
    
    # Monthly revenue
    monthly_revenue = defaultdict(float)
    for invoice in invoices:
        month_key = invoice.created_at.strftime('%Y-%m')
        monthly_revenue[month_key] += float(invoice.total_amount)
    
    stats = {
        'total_invoices': len(invoices),
        'total_amount': total_amount,
        'avg_amount': round(avg_amount, 2),
        'status_counts': dict(status_counts),
        'status_amounts': dict(status_amounts),
        'currency_counts': dict(currency_counts),
        'monthly_invoice_counts': dict(monthly_invoice_counts),
        'monthly_revenue': dict(monthly_revenue)
    }
    
    return render_template('admin/invoice_breakdown.html', stats=stats, invoices=invoices) 