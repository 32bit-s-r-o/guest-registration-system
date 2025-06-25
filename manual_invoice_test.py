#!/usr/bin/env python3
"""
Manual test script to verify invoice items functionality in production
Run this after deploying the fix to verify it works
"""

import os
import sys
from datetime import datetime

def manual_invoice_test():
    """Manual test instructions for invoice items functionality"""
    print("🧪 Manual Invoice Items Test")
    print("=" * 50)
    print()
    print("📋 Test Instructions:")
    print("1. Go to your production site: https://airbnb.rlt.sk")
    print("2. Login as admin")
    print("3. Navigate to Invoices")
    print("4. Create a new invoice or edit an existing one")
    print("5. Add invoice items using the 'Add Item' button")
    print("6. Fill in the item details (description, quantity, price, VAT)")
    print("7. Save the invoice")
    print("8. View the invoice to verify items are displayed")
    print()
    print("✅ Expected Results:")
    print("- Items should be saved when you submit the form")
    print("- Items should be displayed in the invoice view")
    print("- Item count should be correct")
    print("- Totals should be calculated properly")
    print()
    print("🔍 What to Check:")
    print("- Form submission doesn't show errors")
    print("- Invoice view shows all added items")
    print("- Item descriptions, quantities, and prices are correct")
    print("- VAT calculations are accurate")
    print("- Total amounts are correct")
    print()
    print("📝 Test Data to Use:")
    print("Item 1: Accommodation - 2 nights x €100.00 (21% VAT)")
    print("Item 2: Cleaning fee - 1 x €50.00 (21% VAT)")
    print("Item 3: Tourist tax - 2 x €5.00 (0% VAT)")
    print()
    print("🔧 Technical Details:")
    print("- Hidden 'item_count' field should be present in form")
    print("- JavaScript should update item_count when adding/removing items")
    print("- Backend should process item_count > 0")
    print("- Database should store invoice items correctly")
    print()
    print("📞 If Issues Found:")
    print("1. Check browser console for JavaScript errors")
    print("2. Check server logs for backend errors")
    print("3. Verify database tables exist and are accessible")
    print("4. Confirm the fix was deployed correctly")
    print()
    print("✅ Success Criteria:")
    print("- Can add multiple invoice items")
    print("- Items persist after form submission")
    print("- Items display correctly in invoice view")
    print("- No JavaScript or server errors")
    print("- All calculations are accurate")

def check_fix_implementation():
    """Check if the fix is properly implemented"""
    print("\n🔍 Checking Fix Implementation:")
    print("=" * 40)
    
    # Check template files
    templates_to_check = [
        "templates/admin/edit_invoice.html",
        "templates/admin/new_invoice.html"
    ]
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            print(f"\n📄 {template_path}:")
            
            if 'name="item_count"' in content:
                print("   ✅ Hidden input field present")
            else:
                print("   ❌ Hidden input field missing")
            
            if 'function updateItemCount()' in content:
                print("   ✅ updateItemCount function present")
            else:
                print("   ❌ updateItemCount function missing")
            
            if 'updateItemCount();' in content:
                print("   ✅ Function calls present")
            else:
                print("   ❌ Function calls missing")
        else:
            print(f"   ❌ Template file not found: {template_path}")
    
    # Check backend code
    backend_path = "blueprints/invoices.py"
    if os.path.exists(backend_path):
        with open(backend_path, 'r') as f:
            content = f.read()
        
        print(f"\n🔧 {backend_path}:")
        
        if 'item_count = int(request.form.get(\'item_count\', 0))' in content:
            print("   ✅ item_count processing present")
        else:
            print("   ❌ item_count processing missing")
        
        if 'for i in range(item_count):' in content:
            print("   ✅ Item processing loop present")
        else:
            print("   ❌ Item processing loop missing")
    else:
        print(f"   ❌ Backend file not found: {backend_path}")

if __name__ == "__main__":
    check_fix_implementation()
    manual_invoice_test() 