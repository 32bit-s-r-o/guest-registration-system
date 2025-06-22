#!/usr/bin/env python3
"""
Migration script to add invoice and invoice_item tables to the database.
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Invoice, InvoiceItem

def migrate_invoice_tables():
    """Create invoice and invoice_item tables."""
    with app.app_context():
        print("Creating invoice tables...")
        
        # Create tables
        db.create_all()
        
        print("✅ Invoice tables created successfully!")
        print("\nTables created:")
        print("- invoice")
        print("- invoice_item")
        
        # Check if tables exist
        try:
            # Test query to verify tables exist
            invoice_count = Invoice.query.count()
            item_count = InvoiceItem.query.count()
            print(f"\n✅ Tables verified:")
            print(f"- invoice table: {invoice_count} records")
            print(f"- invoice_item table: {item_count} records")
            
        except Exception as e:
            print(f"❌ Error verifying tables: {e}")
            return False
        
        return True

if __name__ == "__main__":
    print("🚀 Starting invoice tables migration...")
    print("=" * 50)
    
    success = migrate_invoice_tables()
    
    print("=" * 50)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1) 