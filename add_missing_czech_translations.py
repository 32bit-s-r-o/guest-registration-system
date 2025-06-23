#!/usr/bin/env python3
"""
Script to add missing Czech translations for important strings.
"""

def add_missing_translations():
    """Add Czech translations for missing strings."""
    
    po_file = 'translations/cs/LC_MESSAGES/messages.po'
    
    # Read the file
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dictionary of important translations to add
    translations = {
        # About page
        'msgid "Mobile-responsive design"\nmsgstr ""': 'msgid "Mobile-responsive design"\nmsgstr "Responzivní design pro mobilní zařízení"',
        'msgid "User Experience"\nmsgstr ""': 'msgid "User Experience"\nmsgstr "Uživatelská zkušenost"',
        'msgid "Intuitive interface design"\nmsgstr ""': 'msgid "Intuitive interface design"\nmsgstr "Intuitivní návrh rozhraní"',
        'msgid "Clear progress indicators"\nmsgstr ""': 'msgid "Clear progress indicators"\nmsgstr "Jasné indikátory průběhu"',
        'msgid "Helpful validation messages"\nmsgstr ""': 'msgid "Helpful validation messages"\nmsgstr "Užitečné validační zprávy"',
        'msgid "Accessible for all users"\nmsgstr ""': 'msgid "Accessible for all users"\nmsgstr "Přístupné pro všechny uživatele"',
        'msgid "Flexibility"\nmsgstr ""': 'msgid "Flexibility"\nmsgstr "Flexibilita"',
        'msgid "Customizable trip settings"\nmsgstr ""': 'msgid "Customizable trip settings"\nmsgstr "Přizpůsobitelná nastavení výletů"',
        'msgid "Multiple document types supported"\nmsgstr ""': 'msgid "Multiple document types supported"\nmsgstr "Podporovány různé typy dokumentů"',
        'msgid "Scalable for any group size"\nmsgstr ""': 'msgid "Scalable for any group size"\nmsgstr "Škálovatelné pro jakoukoliv velikost skupiny"',
        'msgid "Easy admin management"\nmsgstr ""': 'msgid "Easy admin management"\nmsgstr "Snadná správa administrátora"',
        'msgid "Our Team"\nmsgstr ""': 'msgid "Our Team"\nmsgstr "Náš tým"',
        
        # Contact page
        'msgid "Website"\nmsgstr ""': 'msgid "Website"\nmsgstr "Webové stránky"',
        'msgid "Subject"\nmsgstr ""': 'msgid "Subject"\nmsgstr "Předmět"',
        'msgid "Message"\nmsgstr ""': 'msgid "Message"\nmsgstr "Zpráva"',
        'msgid "Please check back later or contact\\n                the administrator."\nmsgstr ""': 'msgid "Please check back later or contact\\n                the administrator."\nmsgstr "Prosím zkuste to později nebo kontaktujte administrátora."',
        
        # GDPR page
        'msgid "This privacy policy explains how we collect, use, and protect your personal data in accordance\\n                with the General Data Protection Regulation (GDPR) and other applicable data protection laws."\nmsgstr ""': 'msgid "This privacy policy explains how we collect, use, and protect your personal data in accordance\\n                with the General Data Protection Regulation (GDPR) and other applicable data protection laws."\nmsgstr "Tato zásady ochrany osobních údajů vysvětlují, jak shromažďujeme, používáme a chráníme vaše osobní údaje v souladu s Obecným nařízením o ochraně osobních údajů (GDPR) a dalšími platnými zákony o ochraně údajů."',
        'msgid "Photos of identification documents\\n                        (temporarily stored)"\nmsgstr ""': 'msgid "Photos of identification documents\\n                        (temporarily stored)"\nmsgstr "Fotografie identifikačních dokladů (dočasně uložené)"',
        
        # Admin pages
        'msgid "Back to Invoices"\nmsgstr ""': 'msgid "Back to Invoices"\nmsgstr "Zpět na faktury"',
        'msgid "Invoice Details"\nmsgstr ""': 'msgid "Invoice Details"\nmsgstr "Detaily faktury"',
        'msgid "Invoice Number"\nmsgstr ""': 'msgid "Invoice Number"\nmsgstr "Číslo faktury"',
        'msgid "Invoice Date"\nmsgstr ""': 'msgid "Invoice Date"\nmsgstr "Datum faktury"',
        'msgid "Due Date"\nmsgstr ""': 'msgid "Due Date"\nmsgstr "Datum splatnosti"',
        'msgid "Status"\nmsgstr ""': 'msgid "Status"\nmsgstr "Stav"',
        'msgid "Total Amount"\nmsgstr ""': 'msgid "Total Amount"\nmsgstr "Celková částka"',
        'msgid "VAT Amount"\nmsgstr ""': 'msgid "VAT Amount"\nmsgstr "Částka DPH"',
        'msgid "Net Amount"\nmsgstr ""': 'msgid "Net Amount"\nmsgstr "Čistá částka"',
        'msgid "Description"\nmsgstr ""': 'msgid "Description"\nmsgstr "Popis"',
        'msgid "Quantity"\nmsgstr ""': 'msgid "Quantity"\nmsgstr "Množství"',
        'msgid "Unit Price"\nmsgstr ""': 'msgid "Unit Price"\nmsgstr "Jednotková cena"',
        'msgid "Line Total"\nmsgstr ""': 'msgid "Line Total"\nmsgstr "Celkem řádek"',
        'msgid "Subtotal"\nmsgstr ""': 'msgid "Subtotal"\nmsgstr "Mezisoučet"',
        'msgid "VAT"\nmsgstr ""': 'msgid "VAT"\nmsgstr "DPH"',
        'msgid "Total"\nmsgstr ""': 'msgid "Total"\nmsgstr "Celkem"',
        'msgid "Print Invoice"\nmsgstr ""': 'msgid "Print Invoice"\nmsgstr "Vytisknout fakturu"',
        'msgid "Download PDF"\nmsgstr ""': 'msgid "Download PDF"\nmsgstr "Stáhnout PDF"',
        'msgid "Edit Invoice"\nmsgstr ""': 'msgid "Edit Invoice"\nmsgstr "Upravit fakturu"',
        'msgid "Delete Invoice"\nmsgstr ""': 'msgid "Delete Invoice"\nmsgstr "Smazat fakturu"',
        'msgid "New Invoice"\nmsgstr ""': 'msgid "New Invoice"\nmsgstr "Nová faktura"',
        'msgid "Create Invoice"\nmsgstr ""': 'msgid "Create Invoice"\nmsgstr "Vytvořit fakturu"',
        'msgid "Invoice Items"\nmsgstr ""': 'msgid "Invoice Items"\nmsgstr "Položky faktury"',
        'msgid "Add Item"\nmsgstr ""': 'msgid "Add Item"\nmsgstr "Přidat položku"',
        'msgid "Remove Item"\nmsgstr ""': 'msgid "Remove Item"\nmsgstr "Odebrat položku"',
        'msgid "Save Invoice"\nmsgstr ""': 'msgid "Save Invoice"\nmsgstr "Uložit fakturu"',
        'msgid "Cancel"\nmsgstr ""': 'msgid "Cancel"\nmsgstr "Zrušit"',
        'msgid "Update"\nmsgstr ""': 'msgid "Update"\nmsgstr "Aktualizovat"',
        'msgid "Delete"\nmsgstr ""': 'msgid "Delete"\nmsgstr "Smazat"',
        'msgid "Edit"\nmsgstr ""': 'msgid "Edit"\nmsgstr "Upravit"',
        'msgid "View"\nmsgstr ""': 'msgid "View"\nmsgstr "Zobrazit"',
        'msgid "Actions"\nmsgstr ""': 'msgid "Actions"\nmsgstr "Akce"',
        'msgid "No invoices found"\nmsgstr ""': 'msgid "No invoices found"\nmsgstr "Nebyly nalezeny žádné faktury"',
        'msgid "No registrations found"\nmsgstr ""': 'msgid "No registrations found"\nmsgstr "Nebyly nalezeny žádné registrace"',
        'msgid "No trips found"\nmsgstr ""': 'msgid "No trips found"\nmsgstr "Nebyly nalezeny žádné výlety"',
        
        # Registration form
        'msgid "Age Category"\nmsgstr ""': 'msgid "Age Category"\nmsgstr "Věková kategorie"',
        'msgid "Adult"\nmsgstr ""': 'msgid "Adult"\nmsgstr "Dospělý"',
        'msgid "Child"\nmsgstr ""': 'msgid "Child"\nmsgstr "Dítě"',
        'msgid "Photo Upload Required"\nmsgstr ""': 'msgid "Photo Upload Required"\nmsgstr "Nahrání fotografie je povinné"',
        'msgid "Photo upload is required for this age category"\nmsgstr ""': 'msgid "Photo upload is required for this age category"\nmsgstr "Nahrání fotografie je povinné pro tuto věkovou kategorii"',
        'msgid "Photo upload is not required for this age category"\nmsgstr ""': 'msgid "Photo upload is not required for this age category"\nmsgstr "Nahrání fotografie není povinné pro tuto věkovou kategorii"',
        
        # Settings
        'msgid "Photo Upload Settings"\nmsgstr ""': 'msgid "Photo Upload Settings"\nmsgstr "Nastavení nahrávání fotografií"',
        'msgid "Require photo upload for adults"\nmsgstr ""': 'msgid "Require photo upload for adults"\nmsgstr "Vyžadovat nahrání fotografie pro dospělé"',
        'msgid "Require photo upload for children"\nmsgstr ""': 'msgid "Require photo upload for children"\nmsgstr "Vyžadovat nahrání fotografie pro děti"',
        'msgid "Language Settings"\nmsgstr ""': 'msgid "Language Settings"\nmsgstr "Nastavení jazyka"',
        'msgid "Enable language picker"\nmsgstr ""': 'msgid "Enable language picker"\nmsgstr "Povolit výběr jazyka"',
        'msgid "Default language"\nmsgstr ""': 'msgid "Default language"\nmsgstr "Výchozí jazyk"',
        'msgid "English"\nmsgstr ""': 'msgid "English"\nmsgstr "Angličtina"',
        'msgid "Czech"\nmsgstr ""': 'msgid "Czech"\nmsgstr "Čeština"',
    }
    
    # Apply translations
    for old, new in translations.items():
        content = content.replace(old, new)
    
    # Write back to file
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added Czech translations for important missing strings")
    print("📝 You can now compile translations with: python extract_translations.py")

if __name__ == '__main__':
    add_missing_translations() 