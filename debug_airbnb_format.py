#!/usr/bin/env python3
"""
Debug script to examine Airbnb description format
"""

import json
from config import Config

def debug_airbnb_format():
    """Debug the Airbnb data format to understand parsing issues."""
    
    try:
        with open('airbnb_comprehensive_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ airbnb_comprehensive_data.json not found")
        return
    
    print("🔍 Debugging Airbnb data format...")
    print("=" * 60)
    
    reservations = data.get('reservations', [])
    
    for i, reservation in enumerate(reservations[:3], 1):  # Look at first 3
        print(f"\n📋 Reservation {i}:")
        print(f"Summary: '{reservation.get('summary', '')}'")
        print(f"Expected Code: '{reservation.get('confirmation_code', '')}'")
        
        description = reservation.get('description_raw', '')
        print(f"Description (raw): {repr(description)}")
        print(f"Description (display): {description}")
        
        # Check for the confirmation code in the description
        expected_code = reservation.get('confirmation_code', '')
        if expected_code in description:
            print(f"✅ Code '{expected_code}' found in description")
        else:
            print(f"❌ Code '{expected_code}' NOT found in description")
        
        # Try different patterns
        import re
        
        patterns = [
            r'/details/([A-Z0-9]{9})',
            r'confirmation\s+code:\s*([A-Z0-9]{6,})',
            r'code:\s*([A-Z0-9]{6,})',
            r'\b([A-Z0-9]{9})\b'
        ]
        
        normalized_text = description.replace('\n', ' ').replace('\\n', ' ')
        print(f"Normalized text: {repr(normalized_text)}")
        
        for j, pattern in enumerate(patterns, 1):
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                print(f"  Pattern {j} matched: {match.group(1)}")
            else:
                print(f"  Pattern {j} failed")

if __name__ == "__main__":
    debug_airbnb_format() 