#!/usr/bin/env python3
"""
Script to fix fuzzy translations in the Czech PO file.
Removes fuzzy markers and fixes common translation issues.
"""

import re

def fix_fuzzy_translations():
    """Remove fuzzy markers and fix translations in the Czech PO file."""
    
    po_file = 'translations/cs/LC_MESSAGES/messages.po'
    
    # Read the file
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all fuzzy markers
    content = re.sub(r'#, fuzzy\n', '', content)
    
    # Fix specific translation issues
    fixes = {
        # Fix translations that don't match their msgid
        'msgid "Admin dashboard for easy management"\nmsgstr "Administrátorská nástěnka"': 
        'msgid "Admin dashboard for easy management"\nmsgstr "Administrátorská nástěnka pro snadnou správu"',
        
        'msgid "Contact Person"\nmsgstr "Kontaktní informace"': 
        'msgid "Contact Person"\nmsgstr "Kontaktní osoba"',
        
        'msgid "Phone"\nmsgstr "Domů"': 
        'msgid "Phone"\nmsgstr "Telefon"',
        
        'msgid "Send Message"\nmsgstr "Datum konce"': 
        'msgid "Send Message"\nmsgstr "Odeslat zprávu"',
        
        'msgid "Your Name"\nmsgstr "Uživatelské jméno"': 
        'msgid "Your Name"\nmsgstr "Vaše jméno"',
        
        'msgid "Your Email"\nmsgstr "Email"': 
        'msgid "Your Email"\nmsgstr "Váš email"',
        
        'msgid "Contact information not available."\nmsgstr "Kontaktní informace"': 
        'msgid "Contact information not available."\nmsgstr "Kontaktní informace nejsou k dispozici."',
        
        'msgid "Quick Links"\nmsgstr "Rychlé akce"': 
        'msgid "Quick Links"\nmsgstr "Rychlé odkazy"',
        
        'msgid "Company"\nmsgstr "Jméno klienta"': 
        'msgid "Company"\nmsgstr "Společnost"',
        
        'msgid "Your Company Address"\nmsgstr "Jméno klienta"': 
        'msgid "Your Company Address"\nmsgstr "Adresa vaší společnosti"',
        
        'msgid "Your Contact Email"\nmsgstr "Email"': 
        'msgid "Your Contact Email"\nmsgstr "Váš kontaktní email"',
        
        'msgid "Your Contact Phone"\nmsgstr "Kontaktní informace"': 
        'msgid "Your Contact Phone"\nmsgstr "Váš kontaktní telefon"',
    }
    
    # Apply fixes
    for old, new in fixes.items():
        content = content.replace(old, new)
    
    # Write back to file
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed all fuzzy markers and fixed translations")
    print("📝 You can now compile translations with: python extract_translations.py")

if __name__ == '__main__':
    fix_fuzzy_translations() 