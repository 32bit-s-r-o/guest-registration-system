#!/usr/bin/env python3
"""
Fix Invoice Totals Script
Recalculates totals for all existing invoices in the database
"""

import os
import sys
from decimal import Decimal

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import Invoice, InvoiceItem

def fix_invoice_totals():
    """Fix totals for all invoices in the database"""
    print("🔧 Fixing Invoice Totals")
    print("=" * 50)
    
    with app.app_context():
        # Get all invoices
        invoices = Invoice.query.all()
        
        if not invoices:
            print("❌ No invoices found in database")
            return
        
        print(f"📄 Found {len(invoices)} invoices to fix")
        print()
        
        fixed_count = 0
        error_count = 0
        
        for invoice in invoices:
            try:
                print(f"🔍 Processing Invoice {invoice.invoice_number} (ID: {invoice.id})")
                
                # Calculate correct totals from items
                subtotal = sum(Decimal(str(item.line_total)) for item in invoice.items)
                vat_total = sum(Decimal(str(item.vat_amount)) for item in invoice.items)
                total_amount = subtotal + vat_total
                
                # Check if totals need fixing
                current_subtotal = Decimal(str(invoice.subtotal or 0))
                current_vat_total = Decimal(str(invoice.vat_total or 0))
                current_total = Decimal(str(invoice.total_amount or 0))
                
                if (current_subtotal != subtotal or 
                    current_vat_total != vat_total or 
                    current_total != total_amount):
                    
                    print(f"   ❌ Totals incorrect:")
                    print(f"      Subtotal: {current_subtotal} → {subtotal}")
                    print(f"      VAT Total: {current_vat_total} → {vat_total}")
                    print(f"      Total: {current_total} → {total_amount}")
                    
                    # Update the invoice totals
                    invoice.subtotal = float(subtotal)
                    invoice.vat_total = float(vat_total)
                    invoice.total_amount = float(total_amount)
                    
                    fixed_count += 1
                    print(f"   ✅ Fixed")
                else:
                    print(f"   ✅ Totals already correct")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error processing invoice {invoice.id}: {e}")
                error_count += 1
                print()
        
        # Commit all changes
        try:
            db.session.commit()
            print("💾 All changes committed to database")
        except Exception as e:
            print(f"❌ Error committing changes: {e}")
            db.session.rollback()
            return False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Fix Summary")
        print("=" * 50)
        print(f"Total Invoices: {len(invoices)}")
        print(f"✅ Fixed: {fixed_count}")
        print(f"❌ Errors: {error_count}")
        print(f"✅ Already Correct: {len(invoices) - fixed_count - error_count}")
        
        if fixed_count > 0:
            print(f"\n🎉 Successfully fixed {fixed_count} invoices!")
        else:
            print(f"\n✅ All invoices already have correct totals!")
        
        return True

if __name__ == '__main__':
    success = fix_invoice_totals()
    sys.exit(0 if success else 1) 