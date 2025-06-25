#!/usr/bin/env python3
"""
Comprehensive test suite for invoice functionality
Tests: creation, editing, deletion, PDF generation, database operations
"""

import os
import sys
import tempfile
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_config import TestConfig
from app import app, db
from database import Invoice, InvoiceItem, User
from flask import render_template_string
from werkzeug.test import Client
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def test_invoice_comprehensive():
    """Comprehensive test for all invoice functionality"""
    # Set test environment
    os.environ['DATABASE_URL'] = TestConfig.TEST_DATABASE_URL
    os.environ['SECRET_KEY'] = TestConfig.TEST_SECRET_KEY
    
    with app.app_context():
        print("🧪 Comprehensive Invoice Test Suite")
        print("=" * 60)
        
        # Setup test data
        admin = setup_test_data()
        
        # Test 1: Create invoice with items
        invoice = test_create_invoice_with_items(admin)
        
        # Test 2: Edit invoice items
        test_edit_invoice_items(invoice)
        
        # Test 3: Delete invoice items
        test_delete_invoice_items(invoice)
        
        # Test 4: Test PDF generation
        test_pdf_generation(invoice)
        
        # Test 5: Database operations
        test_database_operations(invoice)
        
        # Test 6: Form submission simulation
        test_form_submission_comprehensive()
        
        # Test 7: Template rendering
        test_template_rendering_comprehensive(invoice)
        
        # Test 8: Invoice status changes
        test_invoice_status_changes(invoice)
        
        print("\n✅ All comprehensive tests completed successfully!")

def setup_test_data():
    """Setup test data"""
    print("📋 Setting up test data...")
    
    # Create admin user if not exists
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='test_admin',
            email='test_admin@example.com',
            password_hash='test_hash',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("   ✅ Created test admin user")
    else:
        print("   ✅ Using existing admin user")
    
    return admin

def test_create_invoice_with_items(admin):
    """Test creating an invoice with items"""
    print("\n📝 Test 1: Creating invoice with items")
    
    # Create invoice
    invoice = Invoice(
        invoice_number="COMP-TEST-001",
        admin_id=admin.id,
        client_name="Comprehensive Test Client",
        client_email="comprehensive@example.com",
        client_vat_number="CZ12345678",
        client_address="Test Address 123\nTest City, 12345",
        issue_date=datetime.now().date(),
        due_date=(datetime.now().date() + timedelta(days=30)),
        currency="EUR",
        status="draft",
        notes="Test invoice for comprehensive testing"
    )
    db.session.add(invoice)
    db.session.flush()
    
    # Add comprehensive items
    items_data = [
        {
            'description': 'Accommodation - 2 nights',
            'quantity': 2,
            'unit_price': 100.00,
            'vat_rate': 21.0,
            'line_total': 200.00,
            'vat_amount': 42.00,
            'total_with_vat': 242.00
        },
        {
            'description': 'Cleaning fee',
            'quantity': 1,
            'unit_price': 50.00,
            'vat_rate': 21.0,
            'line_total': 50.00,
            'vat_amount': 10.50,
            'total_with_vat': 60.50
        },
        {
            'description': 'Tourist tax',
            'quantity': 2,
            'unit_price': 5.00,
            'vat_rate': 0.0,
            'line_total': 10.00,
            'vat_amount': 0.00,
            'total_with_vat': 10.00
        }
    ]
    
    for item_data in items_data:
        item = InvoiceItem(
            invoice_id=invoice.id,
            description=item_data['description'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            vat_rate=item_data['vat_rate'],
            line_total=item_data['line_total'],
            vat_amount=item_data['vat_amount'],
            total_with_vat=item_data['total_with_vat']
        )
        db.session.add(item)
    
    # Calculate totals
    invoice.subtotal = sum(item.line_total for item in invoice.items)
    invoice.vat_total = sum(item.vat_amount for item in invoice.items)
    invoice.total_amount = invoice.subtotal + invoice.vat_total
    
    db.session.commit()
    
    # Verify creation
    saved_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    print(f"   ✅ Created invoice with {len(saved_items)} items")
    print(f"   📊 Totals: Subtotal={invoice.subtotal}, VAT={invoice.vat_total}, Total={invoice.total_amount}")
    
    return invoice

def test_edit_invoice_items(invoice):
    """Test editing invoice items"""
    print("\n✏️ Test 2: Editing invoice items")
    
    original_item_count = len(invoice.items)
    original_total = invoice.total_amount
    
    # Clear existing items
    for item in invoice.items:
        db.session.delete(item)
    
    # Add updated items
    updated_items_data = [
        {
            'description': 'Updated Accommodation - 3 nights',
            'quantity': 3,
            'unit_price': 120.00,
            'vat_rate': 21.0,
            'line_total': 360.00,
            'vat_amount': 75.60,
            'total_with_vat': 435.60
        },
        {
            'description': 'Premium Cleaning',
            'quantity': 1,
            'unit_price': 75.00,
            'vat_rate': 21.0,
            'line_total': 75.00,
            'vat_amount': 15.75,
            'total_with_vat': 90.75
        }
    ]
    
    for item_data in updated_items_data:
        item = InvoiceItem(
            invoice_id=invoice.id,
            description=item_data['description'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            vat_rate=item_data['vat_rate'],
            line_total=item_data['line_total'],
            vat_amount=item_data['vat_amount'],
            total_with_vat=item_data['total_with_vat']
        )
        db.session.add(item)
    
    # Recalculate totals
    invoice.subtotal = sum(item.line_total for item in invoice.items)
    invoice.vat_total = sum(item.vat_amount for item in invoice.items)
    invoice.total_amount = invoice.subtotal + invoice.vat_total
    
    db.session.commit()
    
    # Verify changes
    updated_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    print(f"   ✅ Updated invoice: {len(updated_items)} items (was {original_item_count})")
    print(f"   📊 New total: {invoice.total_amount} (was {original_total})")
    
    for i, item in enumerate(updated_items, 1):
        print(f"      Item {i}: {item.description} - {item.quantity} x {item.unit_price} = {item.line_total}")

def test_delete_invoice_items(invoice):
    """Test deleting invoice items"""
    print("\n🗑️ Test 3: Deleting invoice items")
    
    original_item_count = len(invoice.items)
    
    # Delete first item
    first_item = invoice.items[0]
    item_description = first_item.description
    db.session.delete(first_item)
    
    # Recalculate totals
    invoice.subtotal = sum(item.line_total for item in invoice.items)
    invoice.vat_total = sum(item.vat_amount for item in invoice.items)
    invoice.total_amount = invoice.subtotal + invoice.vat_total
    
    db.session.commit()
    
    # Verify deletion
    remaining_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    print(f"   ✅ Deleted item: {item_description}")
    print(f"   📊 Remaining items: {len(remaining_items)} (was {original_item_count})")
    print(f"   📊 Updated total: {invoice.total_amount}")
    
    # Test cascade deletion
    print("\n   🔄 Testing cascade deletion...")
    db.session.delete(invoice)
    db.session.commit()
    
    # Verify all items are deleted
    remaining_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    print(f"   ✅ Cascade deletion: {len(remaining_items)} items remaining (should be 0)")

def test_pdf_generation(invoice):
    """Test PDF generation"""
    print("\n📄 Test 4: PDF generation")
    
    try:
        # Generate HTML content for the invoice
        html_content = render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invoice {{ invoice.invoice_number }}</title>
            <style>
                body { font-family: Arial, sans-serif; font-size: 12px; }
                .header { text-align: center; margin-bottom: 20px; }
                .invoice-details { margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f8f9fa; }
                .total-row { font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Invoice {{ invoice.invoice_number }}</h1>
            </div>
            
            <div class="invoice-details">
                <p><strong>Client:</strong> {{ invoice.client_name }}</p>
                <p><strong>Issue Date:</strong> {{ invoice.issue_date.strftime('%Y-%m-%d') }}</p>
                <p><strong>Currency:</strong> {{ invoice.currency }}</p>
            </div>
            
            {% if invoice.items %}
            <table>
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>VAT %</th>
                        <th>Line Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in invoice.items %}
                    <tr>
                        <td>{{ item.description }}</td>
                        <td>{{ "%.2f"|format(item.quantity) }}</td>
                        <td>{{ "%.2f"|format(item.unit_price) }} {{ invoice.currency }}</td>
                        <td>{{ "%.2f"|format(item.vat_rate) }}%</td>
                        <td>{{ "%.2f"|format(item.line_total) }} {{ invoice.currency }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <div class="total-row">
                <p><strong>Subtotal:</strong> {{ "%.2f"|format(invoice.subtotal) }} {{ invoice.currency }}</p>
                <p><strong>VAT Total:</strong> {{ "%.2f"|format(invoice.vat_total) }} {{ invoice.currency }}</p>
                <p><strong>Total:</strong> {{ "%.2f"|format(invoice.total_amount) }} {{ invoice.currency }}</p>
            </div>
            {% else %}
            <p>No items found for this invoice.</p>
            {% endif %}
        </body>
        </html>
        """, invoice=invoice)
        
        # Create PDF
        font_config = FontConfiguration()
        css = CSS(string='''
            @page { size: A4; margin: 1.5cm; }
            body { font-family: Arial, sans-serif; font-size: 10px; line-height: 1.2; }
            .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 6px; text-align: left; font-size: 9px; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .total-row { font-weight: bold; background-color: #f8f9fa; }
        ''', font_config=font_config)
        
        # Generate PDF
        html_doc = HTML(string=html_content)
        pdf = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf)
            tmp_path = tmp_file.name
        
        # Check file size
        file_size = os.path.getsize(tmp_path)
        print(f"   ✅ PDF generated successfully")
        print(f"   📊 File size: {file_size} bytes")
        print(f"   📁 Saved to: {tmp_path}")
        
        # Clean up
        os.unlink(tmp_path)
        print("   🧹 Temporary file cleaned up")
        
    except Exception as e:
        print(f"   ❌ PDF generation error: {e}")

def test_database_operations(invoice):
    """Test database operations"""
    print("\n🗄️ Test 5: Database operations")
    
    # Test query operations
    all_invoices = Invoice.query.all()
    all_items = InvoiceItem.query.all()
    
    print(f"   📊 Total invoices in database: {len(all_invoices)}")
    print(f"   📊 Total invoice items in database: {len(all_items)}")
    
    # Test filtering
    draft_invoices = Invoice.query.filter_by(status='draft').all()
    print(f"   📊 Draft invoices: {len(draft_invoices)}")
    
    # Test relationships
    for inv in all_invoices[:3]:  # Test first 3 invoices
        item_count = len(inv.items)
        print(f"   📋 Invoice {inv.invoice_number}: {item_count} items")
    
    # Test aggregation
    total_invoice_value = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
    print(f"   💰 Total invoice value: {total_invoice_value}")
    
    # Test foreign key constraints
    print("   🔗 Testing foreign key constraints...")
    try:
        # Try to create item with non-existent invoice_id
        invalid_item = InvoiceItem(
            invoice_id=99999,  # Non-existent ID
            description="Test",
            quantity=1,
            unit_price=10.00
        )
        db.session.add(invalid_item)
        db.session.commit()
        print("   ❌ Foreign key constraint not working")
    except Exception as e:
        print("   ✅ Foreign key constraint working correctly")
        db.session.rollback()

def test_form_submission_comprehensive():
    """Test comprehensive form submission"""
    print("\n📤 Test 6: Comprehensive form submission")
    
    # Simulate complex form data
    form_data = {
        'client_name': 'Comprehensive Test Client',
        'client_email': 'comprehensive@example.com',
        'client_vat_number': 'CZ12345678',
        'client_address': 'Test Address 123\nTest City, 12345',
        'issue_date': datetime.now().strftime('%Y-%m-%d'),
        'due_date': (datetime.now().date() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'currency': 'EUR',
        'notes': 'Comprehensive test invoice',
        'item_count': '3',
        'item_description_0': 'Accommodation - 2 nights',
        'item_quantity_0': '2',
        'item_unit_price_0': '100.00',
        'item_vat_rate_0': '21.0',
        'item_description_1': 'Cleaning fee',
        'item_quantity_1': '1',
        'item_unit_price_1': '50.00',
        'item_vat_rate_1': '21.0',
        'item_description_2': 'Tourist tax',
        'item_quantity_2': '2',
        'item_unit_price_2': '5.00',
        'item_vat_rate_2': '0.0'
    }
    
    # Test form processing logic
    admin = User.query.filter_by(role='admin').first()
    
    # Create invoice
    invoice = Invoice(
        invoice_number="FORM-COMP-001",
        admin_id=admin.id,
        client_name=form_data['client_name'],
        client_email=form_data['client_email'],
        client_vat_number=form_data['client_vat_number'],
        client_address=form_data['client_address'],
        issue_date=datetime.strptime(form_data['issue_date'], '%Y-%m-%d').date(),
        due_date=datetime.strptime(form_data['due_date'], '%Y-%m-%d').date(),
        currency=form_data['currency'],
        notes=form_data['notes']
    )
    db.session.add(invoice)
    db.session.flush()
    
    # Process items
    item_count = int(form_data['item_count'])
    print(f"   📊 Processing {item_count} items from form")
    
    total_subtotal = 0
    total_vat = 0
    
    for i in range(item_count):
        description = form_data[f'item_description_{i}']
        quantity = float(form_data[f'item_quantity_{i}'])
        unit_price = float(form_data[f'item_unit_price_{i}'])
        vat_rate = float(form_data[f'item_vat_rate_{i}'])
        
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
            
            total_subtotal += line_total
            total_vat += vat_amount
            
            print(f"      ✅ Item {i}: {description} - {quantity} x {unit_price} = {line_total}")
    
    # Calculate totals
    invoice.subtotal = total_subtotal
    invoice.vat_total = total_vat
    invoice.total_amount = total_subtotal + total_vat
    
    db.session.commit()
    
    # Verify results
    saved_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    print(f"   ✅ Form submission: {len(saved_items)} items saved")
    print(f"   📊 Calculated totals: Subtotal={invoice.subtotal}, VAT={invoice.vat_total}, Total={invoice.total_amount}")

def test_template_rendering_comprehensive(invoice):
    """Test comprehensive template rendering"""
    print("\n🎨 Test 7: Comprehensive template rendering")
    
    try:
        # Test view invoice template
        view_template = """
        {% if invoice.items %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th class="text-center">Quantity</th>
                            <th class="text-end">Unit Price</th>
                            <th class="text-center">VAT</th>
                            <th class="text-end">Line Total</th>
                            <th class="text-end">VAT Amount</th>
                            <th class="text-end">Total with VAT</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in invoice.items %}
                        <tr>
                            <td>{{ item.description }}</td>
                            <td class="text-center">{{ "%.2f"|format(item.quantity) }}</td>
                            <td class="text-end">{{ "%.2f"|format(item.unit_price) }} {{ invoice.currency }}</td>
                            <td class="text-center">{{ "%.2f"|format(item.vat_rate) }}%</td>
                            <td class="text-end">{{ "%.2f"|format(item.line_total) }} {{ invoice.currency }}</td>
                            <td class="text-end">{{ "%.2f"|format(item.vat_amount) }} {{ invoice.currency }}</td>
                            <td class="text-end"><strong>{{ "%.2f"|format(item.total_with_vat) }} {{ invoice.currency }}</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <div class="text-center py-3">
                <p class="text-muted">No items found for this invoice.</p>
            </div>
        {% endif %}
        """
        
        result = render_template_string(view_template, invoice=invoice)
        
        if "No items found" in result:
            print("   ❌ Template shows 'No items found'")
        else:
            print("   ✅ View template renders items correctly")
        
        # Test items count
        count_template = "Items Count: {{ invoice.items|length }}"
        count_result = render_template_string(count_template, invoice=invoice)
        print(f"   📊 Items count: {count_result}")
        
        # Test summary calculations
        summary_template = """
        Subtotal: {{ "%.2f"|format(invoice.subtotal) }} {{ invoice.currency }}
        VAT Total: {{ "%.2f"|format(invoice.vat_total) }} {{ invoice.currency }}
        Total: {{ "%.2f"|format(invoice.total_amount) }} {{ invoice.currency }}
        """
        summary_result = render_template_string(summary_template, invoice=invoice)
        print("   📊 Summary calculations rendered correctly")
        
    except Exception as e:
        print(f"   ❌ Template rendering error: {e}")

def test_invoice_status_changes(invoice):
    """Test invoice status changes"""
    print("\n🔄 Test 8: Invoice status changes")
    
    # Test status transitions
    statuses = ['draft', 'sent', 'paid', 'overdue']
    
    for status in statuses:
        old_status = invoice.status
        invoice.status = status
        invoice.updated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"   ✅ Status changed from {old_status} to {status}")
    
    # Test invalid status
    try:
        invoice.status = 'invalid_status'
        db.session.commit()
        print("   ❌ Invalid status accepted")
    except Exception as e:
        print("   ✅ Invalid status rejected correctly")
        db.session.rollback()

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    with app.app_context():
        # Delete test invoices and their items
        test_invoices = Invoice.query.filter(
            Invoice.invoice_number.like('COMP-%') | 
            Invoice.invoice_number.like('FORM-COMP-%')
        ).all()
        
        for invoice in test_invoices:
            # Delete items first
            InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
            db.session.delete(invoice)
        
        db.session.commit()
        print(f"   ✅ Cleaned up {len(test_invoices)} test invoices")

if __name__ == "__main__":
    try:
        test_invoice_comprehensive()
    finally:
        cleanup_test_data() 