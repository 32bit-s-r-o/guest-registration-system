from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import tempfile
import os

invoices = Blueprint('invoices', __name__)

from database import db, User, Invoice, InvoiceItem, Registration, Trip
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

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

@invoices.route('/admin/invoices')
@login_required
@role_required('admin')
def admin_invoices():
    """Admin invoices list page."""
    invoices_list = Invoice.query.filter_by(admin_id=current_user.id).order_by(Invoice.created_at.desc()).all()
    return render_template('admin/invoices.html', invoices=invoices_list)

@invoices.route('/admin/invoices/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_invoice():
    """Create a new invoice."""
    if request.method == 'POST':
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{Invoice.query.filter_by(admin_id=current_user.id).count() + 1:03d}"
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            admin_id=current_user.id,
            registration_id=request.form.get('registration_id'),
            client_name=request.form.get('client_name'),
            client_email=request.form.get('client_email'),
            client_vat_number=request.form.get('client_vat_number'),
            client_address=request.form.get('client_address'),
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date(),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
            currency=request.form.get('currency', 'EUR'),
            notes=request.form.get('notes')
        )
        
        db.session.add(invoice)
        db.session.flush()  # Get the invoice ID
        
        # Process invoice items
        item_count = int(request.form.get('item_count', 0))
        for i in range(item_count):
            description = request.form.get(f'item_description_{i}')
            quantity = float(request.form.get(f'item_quantity_{i}', 1))
            unit_price = float(request.form.get(f'item_unit_price_{i}', 0))
            vat_rate = float(request.form.get(f'item_vat_rate_{i}', 0))
            
            if description and unit_price > 0:
                line_total = quantity * unit_price
                vat_amount = line_total * (vat_rate / 100)
                total_with_vat = line_total + vat_amount
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=vat_rate,
                    line_total=line_total,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat
                )
                db.session.add(item)
        
        # Calculate totals
        invoice.subtotal = sum(item.line_total for item in invoice.items)
        invoice.vat_total = sum(item.vat_amount for item in invoice.items)
        invoice.total_amount = invoice.subtotal + invoice.vat_total
        
        db.session.commit()
        flash(_('Invoice created successfully!'), 'success')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/new_invoice.html', today=today)

@invoices.route('/admin/invoices/<int:invoice_id>')
@login_required
@role_required('admin')
def view_invoice(invoice_id):
    """View a specific invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    return render_template('admin/view_invoice.html', invoice=invoice)

@invoices.route('/admin/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(invoice_id):
    """Edit an existing invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Update invoice details
        invoice.client_name = request.form.get('client_name')
        invoice.client_email = request.form.get('client_email')
        invoice.client_vat_number = request.form.get('client_vat_number')
        invoice.client_address = request.form.get('client_address')
        invoice.issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date()
        invoice.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None
        invoice.currency = request.form.get('currency', 'EUR')
        invoice.notes = request.form.get('notes')
        
        # Clear existing items
        for item in invoice.items:
            db.session.delete(item)
        
        # Add new items
        item_count = int(request.form.get('item_count', 0))
        for i in range(item_count):
            description = request.form.get(f'item_description_{i}')
            quantity = float(request.form.get(f'item_quantity_{i}', 1))
            unit_price = float(request.form.get(f'item_unit_price_{i}', 0))
            vat_rate = float(request.form.get(f'item_vat_rate_{i}', 0))
            
            if description and unit_price > 0:
                line_total = quantity * unit_price
                vat_amount = line_total * (vat_rate / 100)
                total_with_vat = line_total + vat_amount
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=vat_rate,
                    line_total=line_total,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat
                )
                db.session.add(item)
        
        # Recalculate totals
        invoice.subtotal = sum(item.line_total for item in invoice.items)
        invoice.vat_total = sum(item.vat_amount for item in invoice.items)
        invoice.total_amount = invoice.subtotal + invoice.vat_total
        
        db.session.commit()
        flash(_('Invoice updated successfully!'), 'success')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))
    
    # Convert invoice items to dictionaries for JSON serialization
    items_data = []
    for item in invoice.items:
        items_data.append({
            'description': item.description,
            'quantity': float(item.quantity),
            'unit_price': float(item.unit_price),
            'vat_rate': float(item.vat_rate)
        })
    
    return render_template('admin/edit_invoice.html', invoice=invoice, items_data=items_data)

@invoices.route('/admin/invoices/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    """Delete an invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    db.session.delete(invoice)
    db.session.commit()
    flash(_('Invoice deleted successfully!'), 'success')
    return redirect(url_for('invoices.admin_invoices'))

@invoices.route('/admin/invoices/<int:invoice_id>/change-status', methods=['POST'])
@login_required
def change_invoice_status(invoice_id):
    """Change invoice status."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    new_status = request.form.get('status')
    if new_status in ['draft', 'sent', 'paid', 'overdue']:
        old_status = invoice.status
        invoice.status = new_status
        invoice.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(_('Invoice status changed from %(old_status)s to %(new_status)s successfully!', old_status=old_status.title(), new_status=new_status.title()), 'success')
    else:
        flash(_('Invalid status provided.'), 'error')
    
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))

@invoices.route('/admin/invoices/<int:invoice_id>/pdf')
@login_required
def generate_invoice_pdf(invoice_id):
    """Generate PDF for an invoice."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    # Generate HTML content for the invoice
    html_content = render_template('admin/invoice_pdf.html', invoice=invoice)
    
    # Create PDF
    font_config = FontConfiguration()
    css = CSS(string='''
        @page { 
            size: A4; 
            margin: 1.5cm;
        }
        body { 
            font-family: Arial, sans-serif; 
            font-size: 10px;
            line-height: 1.2;
        }
        .header { 
            text-align: center; 
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }
        .invoice-details {
            margin-top: 10px;
            font-size: 9px;
            color: #666;
        }
        .invoice-details span {
            margin: 0 15px;
        }
        .row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .company-info {
            text-align: left;
            width: 48%;
        }
        .client-info {
            text-align: right;
            width: 48%;
        }
        .invoice-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .invoice-table th,
        .invoice-table td {
            border: 1px solid #ddd;
            padding: 6px;
            text-align: left;
            font-size: 9px;
        }
        .invoice-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .total-row {
            font-weight: bold;
            background-color: #f8f9fa;
        }
        .notes {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            font-size: 9px;
        }
    ''', font_config=font_config)
    
    # Generate PDF
    html_doc = HTML(string=html_content)
    pdf = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf)
        tmp_path = tmp_file.name
    
    # Send file and clean up
    try:
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f'invoice_{invoice.invoice_number}.pdf',
            mimetype='application/pdf'
        )
    finally:
        # Clean up temporary file after sending
        try:
            os.unlink(tmp_path)
        except:
            pass

@invoices.route('/admin/invoices/<int:invoice_id>/send-pdf', methods=['POST'])
@login_required
@role_required('admin')
def send_invoice_pdf(invoice_id):
    """Send the invoice PDF to the registration/client email."""
    invoice = Invoice.query.filter_by(id=invoice_id, admin_id=current_user.id).first_or_404()
    
    # Determine recipient and language
    recipient = invoice.client_email or (invoice.registration.email if invoice.registration else None)
    if not recipient:
        flash(_('No recipient email found for this invoice.'), 'error')
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))
    
    # Set language based on registration
    if invoice.registration and invoice.registration.language:
        # Temporarily set the language for this request
        from flask_babel import get_locale
        original_locale = get_locale()
        from flask import session
        session['lang'] = invoice.registration.language
    
    # Generate HTML content for the invoice
    html_content = render_template('admin/invoice_pdf.html', invoice=invoice)
    font_config = FontConfiguration()
    css = CSS(string='''
        @page { size: A4; margin: 1.5cm; }
        body { font-family: Arial, sans-serif; font-size: 10px; line-height: 1.2; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 15px; }
        .invoice-details { margin-top: 10px; font-size: 9px; color: #666; }
        .invoice-details span { margin: 0 15px; }
        .row { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .company-info { text-align: left; width: 48%; }
        .client-info { text-align: right; width: 48%; }
        .invoice-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .invoice-table th, .invoice-table td { border: 1px solid #ddd; padding: 6px; text-align: left; font-size: 9px; }
        .invoice-table th { background-color: #f8f9fa; font-weight: bold; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .total-row { font-weight: bold; background-color: #f8f9fa; }
        .notes { margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff; font-size: 9px; }
    ''', font_config=font_config)
    html_doc = HTML(string=html_content)
    pdf_bytes = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
    
    # Send email with PDF attachment
    try:
        msg = Message(
            subject=_('Your Invoice from %(company)s', company=invoice.admin.company_name or _('Our Company')),
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[recipient]
        )
        msg.body = _(
            """Dear %(client_name)s,

Please find attached your invoice %(invoice_number)s.

Thank you for your business!

Best regards,
%(company)s""",
            client_name=invoice.client_name,
            invoice_number=invoice.invoice_number,
            company=invoice.admin.company_name or _('Our Company')
        )
        msg.attach(
            filename=f"invoice_{invoice.invoice_number}.pdf",
            content_type="application/pdf",
            data=pdf_bytes
        )
        mail = Mail(current_app)
        mail.send(msg)
        flash(_('Invoice PDF sent to %(email)s', email=recipient), 'success')
    except Exception as e:
        print(f"Error sending invoice PDF: {e}")
        flash(_('Failed to send invoice PDF: %(error)s', error=str(e)), 'error')
    finally:
        # Restore original language if it was changed
        if invoice.registration and invoice.registration.language:
            from flask import session
            session['lang'] = original_locale.language if original_locale else 'en'
    
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id)) 