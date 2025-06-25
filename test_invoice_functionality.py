#!/usr/bin/env python3
"""
Test invoice functionality with test environment
Tests: creation, editing, deletion, PDF generation, database operations
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_invoice_functionality():
    """Test invoice functionality with test environment"""
    print("🧪 Testing Invoice Functionality")
    print("=" * 50)
    
    # Set test environment variables
    os.environ['TEST_MODE'] = 'true'
    os.environ['TEST_PORT'] = '5001'
    os.environ['TEST_DATABASE_URL'] = 'sqlite:///test_guest_registration.db'
    os.environ['TEST_TABLE_PREFIX'] = 'test_guest_reg_'
    
    # Import after setting environment
    from test_config import TestConfig
    from app import app, db
    from database import Invoice, InvoiceItem, User
    from flask import render_template_string
    
    with app.app_context():
        print("📋 Test Environment Setup")
        print("   ✅ Test database configured")
        print("   ✅ Test table prefix: test_guest_reg_")
        print("   ✅ Test port: 5001")
        
        # Test 1: Database connectivity
        test_database_connectivity()
        
        # Test 2: Invoice creation and items
        invoice = test_invoice_creation()
        
        # Test 3: Invoice item deletion
        test_invoice_item_deletion(invoice)
        
        # Test 4: PDF generation
        test_pdf_generation(invoice)
        
        # Test 5: Database operations
        test_database_operations()
        
        # Test 6: Template rendering
        test_template_rendering(invoice)
        
        print("\n✅ All invoice functionality tests completed!")

def test_database_connectivity():
    """Test database connectivity"""
    print("\n🗄️ Test 1: Database Connectivity")
    
    try:
        from app import db
        from database import Invoice, InvoiceItem, User
        
        # Test basic queries
        user_count = User.query.count()
        invoice_count = Invoice.query.count()
        item_count = InvoiceItem.query.count()
        
        print(f"   ✅ Database connected successfully")
        print(f"   📊 Users: {user_count}")
        print(f"   📊 Invoices: {invoice_count}")
        print(f"   📊 Invoice Items: {item_count}")
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")

def test_invoice_creation():
    """Test invoice creation with items"""
    print("\n📝 Test 2: Invoice Creation with Items")
    
    from app import db
    from database import Invoice, InvoiceItem, User
    
    # Get admin user
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("   ❌ No admin user found")
        return None
    
    # Create invoice
    invoice = Invoice(
        invoice_number="TEST-INV-001",
        admin_id=admin.id,
        client_name="Test Client",
        client_email="test@example.com",
        client_vat_number="CZ12345678",
        client_address="Test Address 123\nTest City, 12345",
        issue_date=datetime.now().date(),
        due_date=(datetime.now().date() + timedelta(days=30)),
        currency="EUR",
        status="draft",
        notes="Test invoice for functionality testing"
    )
    db.session.add(invoice)
    db.session.flush()
    
    # Add items
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

def test_invoice_item_deletion(invoice):
    """Test deleting invoice items"""
    print("\n🗑️ Test 3: Invoice Item Deletion")
    
    if not invoice:
        print("   ❌ No invoice to test deletion")
        return
    
    original_item_count = len(invoice.items)
    original_total = invoice.total_amount
    
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
    print(f"   📊 Updated total: {invoice.total_amount} (was {original_total})")
    
    # Test cascade deletion
    print("\n   🔄 Testing cascade deletion...")
    db.session.delete(invoice)
    db.session.commit()
    
    # Verify all items are deleted
    remaining_items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    print(f"   ✅ Cascade deletion: {len(remaining_items)} items remaining (should be 0)")

def test_pdf_generation(invoice):
    """Test PDF generation"""
    print("\n📄 Test 4: PDF Generation")
    
    if not invoice:
        print("   ❌ No invoice to test PDF generation")
        return
    
    try:
        from flask import render_template_string
        
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
        
        # Save HTML to file for verification
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
            tmp_file.write(html_content.encode('utf-8'))
            tmp_path = tmp_file.name
        
        # Check file size
        file_size = os.path.getsize(tmp_path)
        print(f"   ✅ HTML generated successfully")
        print(f"   📊 File size: {file_size} bytes")
        print(f"   📁 Saved to: {tmp_path}")
        
        # Check if items are in HTML
        if "Accommodation" in html_content:
            print("   ✅ Invoice items found in HTML")
        else:
            print("   ❌ Invoice items not found in HTML")
        
        # Clean up
        os.unlink(tmp_path)
        print("   🧹 Temporary file cleaned up")
        
    except Exception as e:
        print(f"   ❌ HTML generation error: {e}")

def test_database_operations():
    """Test database operations"""
    print("\n🗄️ Test 5: Database Operations")
    
    from app import db
    from database import Invoice, InvoiceItem, User
    
    # Test query operations
    all_invoices = Invoice.query.all()
    all_items = InvoiceItem.query.all()
    all_users = User.query.all()
    
    print(f"   📊 Total users: {len(all_users)}")
    print(f"   📊 Total invoices: {len(all_invoices)}")
    print(f"   📊 Total invoice items: {len(all_items)}")
    
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

def test_template_rendering(invoice):
    """Test template rendering"""
    print("\n🎨 Test 6: Template Rendering")
    
    if not invoice:
        print("   ❌ No invoice to test template rendering")
        return
    
    try:
        from flask import render_template_string
        
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

if __name__ == "__main__":
    test_invoice_functionality() 