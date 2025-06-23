#!/usr/bin/env python3
"""
Test script to verify Airbnb confirmation code parsing
"""

import re
import json

def parse_airbnb_guest_info(summary, description):
    """Parse guest information from Airbnb calendar event."""
    guest_info = {
        'name': '',
        'email': '',
        'count': 1,
        'confirm_code': ''
    }
    
    # Try to extract guest name from summary
    # Common patterns: "Guest Name - Airbnb" or "Guest Name (X guests)"
    name_patterns = [
        r'^(.+?)\s*-\s*Airbnb',
        r'^(.+?)\s*\(\d+\s*guests?\)',
        r'^(.+?)\s*-\s*\d+\s*guests?'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            guest_info['name'] = match.group(1).strip()
            break
    
    # Try to extract email from description
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, description)
    if email_match:
        guest_info['email'] = email_match.group(0)
    
    # Try to extract guest count
    count_patterns = [
        r'(\d+)\s*guests?',
        r'(\d+)\s*people'
    ]
    
    for pattern in count_patterns:
        match = re.search(pattern, summary + ' ' + description, re.IGNORECASE)
        if match:
            guest_info['count'] = int(match.group(1))
            break
    
    # Try to extract confirmation code from Airbnb reservation URL
    # Handle the case where URL is split across lines with \n
    confirm_patterns = [
        r'/de\s*\n\s*tails/([A-Z0-9]{10})',  # Handle split URL format
        r'/details/([A-Z0-9]{10})',  # Standard format
        r'tails/([A-Z0-9]{10})',  # Simple tails pattern
        r'confirmation\s+code:\s*([A-Z0-9]{6,})',
        r'code:\s*([A-Z0-9]{6,})',
        r'\b([A-Z0-9]{10})(?=\s|$|\\n)'  # 10-character code followed by space, end, or newline
    ]
    
    # Try patterns on the original description first (for split URLs)
    for pattern in confirm_patterns:
        match = re.search(pattern, summary + ' ' + description, re.IGNORECASE)
        if match:
            guest_info['confirm_code'] = match.group(1).upper()
            break
    
    # If no match found, try with normalized text
    if not guest_info['confirm_code']:
        normalized_text = summary + ' ' + description.replace('\n', ' ').replace('\\n', ' ')
        for pattern in confirm_patterns:
            match = re.search(pattern, normalized_text, re.IGNORECASE)
            if match:
                guest_info['confirm_code'] = match.group(1).upper()
                break
    
    return guest_info

def test_airbnb_parsing():
    """Test the parsing with sample Airbnb data."""
    
    # Load the comprehensive Airbnb data
    try:
        with open('airbnb_comprehensive_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ airbnb_comprehensive_data.json not found")
        return
    
    print("🧪 Testing Airbnb confirmation code parsing...")
    print("=" * 60)
    
    reservations = data.get('reservations', [])
    success_count = 0
    total_count = len(reservations)
    
    for i, reservation in enumerate(reservations, 1):
        summary = reservation.get('summary', '')
        description = reservation.get('description_raw', '')
        expected_code = reservation.get('confirmation_code', '')
        
        # Parse using our function
        parsed_info = parse_airbnb_guest_info(summary, description)
        parsed_code = parsed_info.get('confirm_code', '')
        
        # Check if parsing was successful
        if parsed_code == expected_code:
            print(f"✅ {i:2d}. Expected: {expected_code} | Parsed: {parsed_code}")
            success_count += 1
        else:
            print(f"❌ {i:2d}. Expected: {expected_code} | Parsed: {parsed_code}")
            print(f"    Summary: {summary}")
            print(f"    Description: {description[:100]}...")
            print()
    
    print("=" * 60)
    print(f"📊 Results: {success_count}/{total_count} confirmation codes parsed correctly")
    
    if success_count == total_count:
        print("🎉 All confirmation codes parsed successfully!")
    else:
        print(f"⚠️  {total_count - success_count} codes failed to parse")
    
    # Test with a few specific examples
    print("\n🔍 Detailed test examples:")
    print("-" * 40)
    
    test_cases = [
        {
            'summary': 'Reserved',
            'description': 'Reservation URL: https://www.airbnb.com/hosting/reservations/de\n tails/HMATZMHW8H\\nPhone Number (Last 4 Digits): 5900',
            'expected': 'HMATZMHW8H'
        },
        {
            'summary': 'Reserved',
            'description': 'Reservation URL: https://www.airbnb.com/hosting/reservations/de\n tails/HME3PXEKF8\\nPhone Number (Last 4 Digits): 8687',
            'expected': 'HME3PXEKF8'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        parsed = parse_airbnb_guest_info(test_case['summary'], test_case['description'])
        result = "✅" if parsed['confirm_code'] == test_case['expected'] else "❌"
        print(f"{result} Test {i}: Expected {test_case['expected']}, Got {parsed['confirm_code']}")

if __name__ == "__main__":
    test_airbnb_parsing() 