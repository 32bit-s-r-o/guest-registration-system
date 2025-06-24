from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_babel import gettext as _
import os
import uuid
from datetime import datetime

registration = Blueprint('registration', __name__)

from app import app, User, Trip, Registration, Guest, Invoice, InvoiceItem, db

@registration.route('/register')
def register_landing():
    """Landing page for registration with confirmation code form."""
    return render_template('register_landing.html')

@registration.route('/register', methods=['POST'])
def submit_confirm_code():
    """Handle confirmation code submission and redirect to registration form."""
    confirm_code = request.form.get('confirm_code', '').strip().upper()
    
    if not confirm_code:
        flash(_('Please enter a confirmation code'), 'error')
        return redirect(url_for('registration.register_landing'))
    
    # Check if confirmation code exists
    trip = Trip.query.filter_by(external_confirm_code=confirm_code).first()
    if not trip:
        flash(_('Invalid confirmation code. Please check your code and try again.'), 'error')
        return redirect(url_for('registration.register_landing'))
    
    return redirect(url_for('registration.register', trip_id=trip.id))

@registration.route('/register/id/<int:trip_id>')
def register(trip_id):
    """Registration form for a specific trip."""
    trip = Trip.query.get_or_404(trip_id)
    admin = User.query.get(trip.admin_id)
    return render_template('register.html', trip=trip, admin=admin)

@registration.route('/register/<confirm_code>')
def register_by_code(confirm_code):
    """Registration form using confirmation code."""
    trip = Trip.query.filter_by(external_confirm_code=confirm_code).first()
    if not trip:
        flash(_('Invalid confirmation code. Please check your code and try again.'), 'error')
        return redirect(url_for('registration.register_landing'))
    
    admin = User.query.get(trip.admin_id)
    return render_template('register.html', trip=trip, admin=admin)

@registration.route('/register/id/<int:trip_id>', methods=['POST'])
def submit_registration(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    admin = User.query.get(trip.admin_id)
    
    # Get form data
    email = request.form.get('email')
    language = session.get('lang', 'en')  # Get current language from session
    guests_data = []
    
    # Collect guest data
    guest_index = 1
    while True:
        first_name = request.form.get(f'first_name_{guest_index}')
        last_name = request.form.get(f'last_name_{guest_index}')
        age_category = request.form.get(f'age_category_{guest_index}')
        document_type = request.form.get(f'document_type_{guest_index}')
        document_number = request.form.get(f'document_number_{guest_index}')
        gdpr_consent = request.form.get(f'gdpr_consent_{guest_index}') == 'on'
        
        if not first_name or not last_name:  # Stop if no more guest data
            break
            
        # Check photo requirement based on age category and admin settings
        photo_required = False
        if age_category == 'adult' and admin.photo_required_adults:
            photo_required = True
        elif age_category == 'child' and admin.photo_required_children:
            photo_required = True
        
        # Check if photo is uploaded when required
        document_image = request.files.get(f'document_image_{guest_index}')
        if photo_required and (not document_image or not document_image.filename):
            flash(_('Document photo is required for %(age_category)s guests', age_category=age_category), 'error')
            return redirect(request.url)
        
        guests_data.append({
            'first_name': first_name,
            'last_name': last_name,
            'age_category': age_category,
            'document_type': document_type,
            'document_number': document_number,
            'gdpr_consent': gdpr_consent,
            'photo_required': photo_required
        })
        
        guest_index += 1
    
    # Handle file uploads
    uploaded_files = []
    for i, guest_data in enumerate(guests_data):
        document_image = request.files.get(f'document_image_{i+1}')
        if document_image and document_image.filename:
            filename = secure_filename(f"{uuid.uuid4()}_{document_image.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            document_image.save(file_path)
            uploaded_files.append(filename)
        else:
            uploaded_files.append(None)
    
    # Handle invoice request
    invoice_request = request.form.get('invoice_request') == 'on'
    invoice_data = None
    
    if invoice_request:
        invoice_data = {
            'client_name': request.form.get('invoice_name'),
            'vat_number': request.form.get('invoice_vat'),
            'address': request.form.get('invoice_address')
        }
    
    # Store in session for confirmation
    session['registration_data'] = {
        'trip_id': trip_id,
        'email': email,
        'language': language,
        'guests': guests_data,
        'uploaded_files': uploaded_files,
        'invoice_request': invoice_request,
        'invoice_data': invoice_data
    }
    
    return redirect(url_for('registration.confirm_registration'))

@registration.route('/confirm')
def confirm_registration():
    if 'registration_data' not in session:
        return redirect(url_for('main.index'))
    
    data = session['registration_data']
    trip = Trip.query.get(data['trip_id'])
    
    return render_template('confirm.html', data=data, trip=trip)

@registration.route('/submit', methods=['POST'])
def submit_for_approval():
    if 'registration_data' not in session:
        return redirect(url_for('main.index'))
    
    data = session['registration_data']
    trip = Trip.query.get(data['trip_id'])
    
    # Create registration
    registration = Registration(
        trip_id=data['trip_id'],
        email=data['email'],
        language=data.get('language', 'en')
    )
    db.session.add(registration)
    db.session.flush()  # Get the registration ID
    
    # Create guests
    for i, guest_data in enumerate(data['guests']):
        guest = Guest(
            registration_id=registration.id,
            first_name=guest_data['first_name'],
            last_name=guest_data['last_name'],
            age_category=guest_data['age_category'],
            document_type=guest_data['document_type'],
            document_number=guest_data['document_number'],
            document_image=data['uploaded_files'][i] if i < len(data['uploaded_files']) else None,
            gdpr_consent=guest_data['gdpr_consent']
        )
        db.session.add(guest)
    
    # Create draft invoice if requested
    if data.get('invoice_request') and data.get('invoice_data'):
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{Invoice.query.filter_by(admin_id=trip.admin_id).count() + 1:03d}"
        
        # Determine client name
        client_name = data['invoice_data']['client_name'] if data['invoice_data']['client_name'] else f"{data['guests'][0]['first_name']} {data['guests'][0]['last_name']}"
        
        # Create draft invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            admin_id=trip.admin_id,
            registration_id=registration.id,
            client_name=client_name,
            client_email=data['email'],
            client_vat_number=data['invoice_data']['vat_number'],
            client_address=data['invoice_data']['address'],
            issue_date=datetime.utcnow().date(),
            currency=data['invoice_data']['currency'],
            notes=f"Registration: {trip.title}\nGuest Notes: {data['invoice_data']['notes']}\nVAT Number: {data['invoice_data']['vat_number']}" if data['invoice_data']['vat_number'] else f"Registration: {trip.title}\nGuest Notes: {data['invoice_data']['notes']}",
            status='draft'
        )
        db.session.add(invoice)
        
        # Add a placeholder item for the admin to complete
        placeholder_item = InvoiceItem(
            invoice_id=invoice.id,
            description=f"Registration for {trip.title} - {len(data['guests'])} guest(s)",
            quantity=1,
            unit_price=0,
            vat_rate=0,
            line_total=0,
            vat_amount=0,
            total_with_vat=0
        )
        db.session.add(placeholder_item)
    
    db.session.commit()
    
    # Clear session
    session.pop('registration_data', None)
    # Store last confirmation code registration link for sharing
    if trip.airbnb_confirm_code:
        session['last_confirm_code_url'] = url_for('register_by_code', confirm_code=trip.airbnb_confirm_code, _external=True)
    else:
        session['last_confirm_code_url'] = ''
    
    flash(_('Registration submitted successfully! You will receive an email once it is reviewed.'), 'success')
    return redirect(url_for('registration.registration_success'))

@registration.route('/success')
def registration_success():
    return render_template('success.html') 