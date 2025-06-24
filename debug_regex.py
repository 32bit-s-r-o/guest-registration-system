#!/usr/bin/env python3
"""
Debug regex pattern for Airbnb confirmation codes
"""

import re
from config import Config

def test_regex_patterns():
    """Test different regex patterns with the actual data format."""
    
    # Sample data from the debug output
    test_data = 'Reservation URL: https://www.airbnb.com/hosting/reservations/de\n tails/HMATZMHW8H\\nPhone Number (Last 4 Digits): 5900'
    expected_code = 'HMATZMHW8H'
    
    print("🔍 Testing regex patterns with actual data format")
    print("=" * 60)
    print(f"Test data: {repr(test_data)}")
    print(f"Expected code: {expected_code}")
    print()
    
    # Test different patterns
    patterns = [
        (r'/de\s*\n\s*tails/([A-Z0-9]{10})', "Split URL pattern"),
        (r'/details/([A-Z0-9]{10})', "Standard URL pattern"),
        (r'tails/([A-Z0-9]{10})', "Simple tails pattern"),
        (r'confirmation\s+code:\s*([A-Z0-9]{6,})', "Confirmation code pattern"),
        (r'code:\s*([A-Z0-9]{6,})', "Code pattern"),
        (r'\b([A-Z0-9]{10})(?=\s|$|\\n)', "10-character code with lookahead"),
        (r'\b([A-Z0-9]{10})\b', "10-character code with word boundaries"),
        (r'([A-Z0-9]{10})', "Any 10-character code")
    ]
    
    for pattern, pattern_desc in patterns:
        match = re.search(pattern, test_data, re.IGNORECASE)
        if match:
            print(f"✅ {pattern_desc}: {match.group(1)} (length: {len(match.group(1))})")
        else:
            print(f"❌ {pattern_desc}: No match")
    
    print("\n🔍 Testing with normalized text:")
    normalized_text = test_data.replace('\n', ' ').replace('\\n', ' ')
    print(f"Normalized: {repr(normalized_text)}")
    
    for pattern, pattern_desc in patterns:
        match = re.search(pattern, normalized_text, re.IGNORECASE)
        if match:
            print(f"✅ {pattern_desc}: {match.group(1)} (length: {len(match.group(1))})")
        else:
            print(f"❌ {pattern_desc}: No match")

if __name__ == "__main__":
    test_regex_patterns() 