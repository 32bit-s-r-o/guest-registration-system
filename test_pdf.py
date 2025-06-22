#!/usr/bin/env python3

import os
import sys
from app import app, db, Admin, Invoice, InvoiceItem
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def test_pdf_generation():
    with app.app_context():
        # Check if admin exists
        admin = Admin.query.first()
        if not admin:
            print("No admin found. Creating test admin...")
            admin = Admin(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                company_name='Test Company',
                contact_name='Test Contact',
                contact_email='contact@test.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("Test admin created.")
        
        # Check if invoices exist
        invoices = Invoice.query.all()
        print(f"Found {len(invoices)} invoices in database")
        
        if not invoices:
            print("No invoices found. Creating test invoice...")
            
            # Create test invoice
            invoice = Invoice(
                invoice_number='INV-2024-001',
                admin_id=admin.id,
                client_name='Test Client',
                client_email='client@test.com',
                client_vat_number='CZ12345678',
                client_address='Test Address\nTest City, 12345',
                issue_date=date.today(),
                due_date=date.today().replace(day=date.today().day + 30),
                subtotal=100.00,
                vat_total=21.00,
                total_amount=121.00,
                currency='EUR',
                notes='Test invoice for PDF generation',
                status='draft'
            )
            db.session.add(invoice)
            db.session.flush()
            
            # Create test invoice items
            item1 = InvoiceItem(
                invoice_id=invoice.id,
                description='Test Service 1',
                quantity=1,
                unit_price=50.00,
                vat_rate=21.00,
                line_total=50.00,
                vat_amount=10.50,
                total_with_vat=60.50
            )
            
            item2 = InvoiceItem(
                invoice_id=invoice.id,
                description='Test Service 2',
                quantity=1,
                unit_price=50.00,
                vat_rate=21.00,
                line_total=50.00,
                vat_amount=10.50,
                total_with_vat=60.50
            )
            
            db.session.add(item1)
            db.session.add(item2)
            db.session.commit()
            
            print(f"Test invoice created with ID: {invoice.id}")
            print(f"Invoice number: {invoice.invoice_number}")
        else:
            invoice = invoices[0]
            print(f"Using existing invoice: {invoice.invoice_number} (ID: {invoice.id})")
        
        # Test PDF generation
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Generate HTML content
            html_content = f"""
            <html>
            <head>
                <title>Invoice {invoice.invoice_number}</title>
            </head>
            <body>
                <h1>Invoice {invoice.invoice_number}</h1>
                <p>Client: {invoice.client_name}</p>
                <p>Total: {invoice.total_amount} {invoice.currency}</p>
            </body>
            </html>
            """
            
            # Create PDF
            font_config = FontConfiguration()
            css = CSS(string='''
                body { font-family: Arial, sans-serif; }
                h1 { color: #333; }
            ''', font_config=font_config)
            
            html_doc = HTML(string=html_content)
            pdf = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
            
            print("✅ PDF generation successful!")
            print(f"Generated PDF size: {len(pdf)} bytes")
            
            # Save test PDF
            with open('test_invoice.pdf', 'wb') as f:
                f.write(pdf)
            print("Test PDF saved as 'test_invoice.pdf'")
            
        except Exception as e:
            print(f"❌ PDF generation failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_pdf_generation() 