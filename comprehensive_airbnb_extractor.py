#!/usr/bin/env python3
"""
Comprehensive Airbnb iCalendar Data Extractor
Extracts maximum possible data from Airbnb hosting calendar
"""

import re
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from urllib.parse import urlparse, parse_qs

def parse_date(date_str):
    """Parse YYYYMMDD format to datetime object"""
    return datetime.strptime(date_str, "%Y%m%d")

def format_date(date_obj):
    """Format datetime to readable string"""
    return date_obj.strftime("%Y-%m-%d (%A)")

def calculate_duration(start_date, end_date):
    """Calculate stay duration in nights"""
    return (end_date - start_date).days

def extract_comprehensive_data(ical_path):
    """Extract all possible data from Airbnb iCalendar"""
    
    with open(ical_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse calendar metadata
    calendar_info = {
        "prodid": re.search(r"PRODID:(.*)", content),
        "version": re.search(r"VERSION:(.*)", content),
        "calscale": re.search(r"CALSCALE:(.*)", content)
    }
    
    # Find all VEVENT blocks
    events = content.split("BEGIN:VEVENT")[1:]
    
    reservations = []
    phone_numbers = []
    all_dates = []
    
    for i, event in enumerate(events, 1):
        # Handle iCal line folding
        cleaned_event = re.sub(r'\n ', '', event)
        
        reservation = {
            "event_number": i,
            "raw_event": event.strip()
        }
        
        # Extract basic event data
        dtstamp = re.search(r"DTSTAMP:(\d{8}T\d{6}Z)", event)
        dtstart = re.search(r"DTSTART;VALUE=DATE:(\d{8})", event)
        dtend = re.search(r"DTEND;VALUE=DATE:(\d{8})", event)
        summary = re.search(r"SUMMARY:(.*)", event)
        uid = re.search(r"UID:(.*)", event)
        description = re.search(r"DESCRIPTION:(.*?)(?=\nEND:VEVENT|\nBEGIN:|\Z)", event, re.DOTALL)
        
        # Parse timestamps
        if dtstamp:
            reservation["timestamp"] = dtstamp.group(1)
            reservation["timestamp_parsed"] = datetime.strptime(dtstamp.group(1), "%Y%m%dT%H%M%SZ")
        
        # Parse dates
        if dtstart and dtend:
            start_date = parse_date(dtstart.group(1))
            end_date = parse_date(dtend.group(1))
            
            reservation.update({
                "check_in_date": dtstart.group(1),
                "check_out_date": dtend.group(1),
                "check_in_formatted": format_date(start_date),
                "check_out_formatted": format_date(end_date),
                "duration_nights": calculate_duration(start_date, end_date),
                "month": start_date.strftime("%B %Y"),
                "day_of_week_checkin": start_date.strftime("%A"),
                "day_of_week_checkout": end_date.strftime("%A"),
                "is_weekend_checkin": start_date.weekday() >= 5,
                "is_weekend_checkout": end_date.weekday() >= 5
            })
            
            all_dates.extend([start_date, end_date])
        
        # Parse summary
        if summary:
            reservation["summary"] = summary.group(1).strip()
            reservation["is_reserved"] = "reserved" in summary.group(1).lower()
        
        # Parse UID
        if uid:
            reservation["uid"] = uid.group(1).strip()
            # Extract property ID from UID if possible
            uid_parts = uid.group(1).split('-')
            if len(uid_parts) > 1:
                reservation["property_id"] = uid_parts[0]
        
        # Parse description for detailed info
        if description:
            desc_text = description.group(1).strip()
            reservation["description_raw"] = desc_text
            
            # Extract reservation URL and code
            url_match = re.search(r"https://www\.airbnb\.com/hosting/reservations/details/([A-Z0-9]{10})", cleaned_event)
            if url_match:
                reservation["confirmation_code"] = url_match.group(1)
                reservation["reservation_url"] = f"https://www.airbnb.com/hosting/reservations/details/{url_match.group(1)}"
            
            # Extract phone number
            phone_match = re.search(r"Phone Number \(Last 4 Digits\): (\d{4})", desc_text)
            if phone_match:
                phone_last4 = phone_match.group(1)
                reservation["phone_last_4"] = phone_last4
                phone_numbers.append(phone_last4)
            
            # Look for additional data patterns
            # Guest name (if present)
            name_patterns = [
                r"Guest: ([^\n]+)",
                r"Name: ([^\n]+)",
                r"Booked by: ([^\n]+)"
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, desc_text, re.IGNORECASE)
                if name_match:
                    reservation["guest_name"] = name_match.group(1).strip()
                    break
            
            # Price information (if present)
            price_patterns = [
                r"\$(\d+(?:\.\d{2})?)",
                r"(\d+(?:\.\d{2})?) USD",
                r"Total: \$?(\d+(?:\.\d{2})?)"
            ]
            for pattern in price_patterns:
                price_match = re.search(pattern, desc_text)
                if price_match:
                    reservation["price"] = float(price_match.group(1))
                    break
        
        reservations.append(reservation)
    
    # Calculate analytics
    analytics = calculate_analytics(reservations, all_dates)
    
    return {
        "calendar_info": calendar_info,
        "reservations": reservations,
        "analytics": analytics,
        "extraction_timestamp": datetime.now().isoformat()
    }

def calculate_analytics(reservations, all_dates):
    """Calculate comprehensive analytics"""
    
    valid_reservations = [r for r in reservations if r.get("confirmation_code")]
    
    analytics = {
        "total_events": len(reservations),
        "total_reservations": len(valid_reservations),
        "extraction_success_rate": len(valid_reservations) / len(reservations) * 100 if reservations else 0
    }
    
    if not valid_reservations:
        return analytics
    
    # Date analytics
    check_in_dates = [datetime.strptime(r["check_in_date"], "%Y%m%d") for r in valid_reservations]
    check_out_dates = [datetime.strptime(r["check_out_date"], "%Y%m%d") for r in valid_reservations]
    
    analytics.update({
        "date_range": {
            "first_checkin": min(check_in_dates).strftime("%Y-%m-%d"),
            "last_checkout": max(check_out_dates).strftime("%Y-%m-%d"),
            "total_span_days": (max(check_out_dates) - min(check_in_dates)).days
        }
    })
    
    # Duration analytics
    durations = [r["duration_nights"] for r in valid_reservations if "duration_nights" in r]
    if durations:
        analytics["stay_duration"] = {
            "average_nights": sum(durations) / len(durations),
            "min_nights": min(durations),
            "max_nights": max(durations),
            "total_booked_nights": sum(durations),
            "duration_distribution": dict(Counter(durations))
        }
    
    # Monthly distribution
    months = [r["month"] for r in valid_reservations if "month" in r]
    analytics["monthly_distribution"] = dict(Counter(months))
    
    # Day of week patterns
    checkin_days = [r["day_of_week_checkin"] for r in valid_reservations if "day_of_week_checkin" in r]
    checkout_days = [r["day_of_week_checkout"] for r in valid_reservations if "day_of_week_checkout" in r]
    
    analytics["day_patterns"] = {
        "checkin_days": dict(Counter(checkin_days)),
        "checkout_days": dict(Counter(checkout_days)),
        "weekend_checkins": sum(1 for r in valid_reservations if r.get("is_weekend_checkin")),
        "weekend_checkouts": sum(1 for r in valid_reservations if r.get("is_weekend_checkout"))
    }
    
    # Phone number analytics
    phone_numbers = [r["phone_last_4"] for r in valid_reservations if "phone_last_4" in r]
    if phone_numbers:
        phone_counter = Counter(phone_numbers)
        analytics["phone_analytics"] = {
            "unique_phone_numbers": len(set(phone_numbers)),
            "total_phone_numbers": len(phone_numbers),
            "repeat_guests": {phone: count for phone, count in phone_counter.items() if count > 1},
            "phone_distribution": dict(phone_counter)
        }
    
    # Booking gaps analysis
    if len(valid_reservations) > 1:
        sorted_reservations = sorted(valid_reservations, key=lambda x: x["check_in_date"])
        gaps = []
        
        for i in range(len(sorted_reservations) - 1):
            current_checkout = datetime.strptime(sorted_reservations[i]["check_out_date"], "%Y%m%d")
            next_checkin = datetime.strptime(sorted_reservations[i+1]["check_in_date"], "%Y%m%d")
            gap_days = (next_checkin - current_checkout).days
            gaps.append(gap_days)
        
        analytics["booking_gaps"] = {
            "average_gap_days": sum(gaps) / len(gaps) if gaps else 0,
            "min_gap_days": min(gaps) if gaps else 0,
            "max_gap_days": max(gaps) if gaps else 0,
            "back_to_back_bookings": sum(1 for gap in gaps if gap == 0),
            "gap_distribution": dict(Counter(gaps))
        }
    
    # Revenue potential (if price data available)
    prices = [r["price"] for r in valid_reservations if "price" in r]
    if prices:
        analytics["revenue_data"] = {
            "total_revenue": sum(prices),
            "average_booking_value": sum(prices) / len(prices),
            "min_booking_value": min(prices),
            "max_booking_value": max(prices)
        }
    
    return analytics

def generate_report(data):
    """Generate a comprehensive text report"""
    
    report = []
    report.append("=" * 80)
    report.append("🏠 COMPREHENSIVE AIRBNB CALENDAR ANALYSIS REPORT")
    report.append("=" * 80)
    
    # Calendar info
    report.append(f"\n📅 CALENDAR INFORMATION:")
    report.append(f"   Extraction Time: {data['extraction_timestamp']}")
    report.append(f"   Total Events: {data['analytics']['total_events']}")
    report.append(f"   Valid Reservations: {data['analytics']['total_reservations']}")
    report.append(f"   Success Rate: {data['analytics']['extraction_success_rate']:.1f}%")
    
    # Date range
    if 'date_range' in data['analytics']:
        dr = data['analytics']['date_range']
        report.append(f"\n📊 DATE RANGE ANALYSIS:")
        report.append(f"   First Check-in: {dr['first_checkin']}")
        report.append(f"   Last Check-out: {dr['last_checkout']}")
        report.append(f"   Total Span: {dr['total_span_days']} days")
    
    # Stay duration
    if 'stay_duration' in data['analytics']:
        sd = data['analytics']['stay_duration']
        report.append(f"\n🛏️  STAY DURATION ANALYSIS:")
        report.append(f"   Average Stay: {sd['average_nights']:.1f} nights")
        report.append(f"   Shortest Stay: {sd['min_nights']} nights")
        report.append(f"   Longest Stay: {sd['max_nights']} nights")
        report.append(f"   Total Booked Nights: {sd['total_booked_nights']}")
        report.append(f"   Duration Distribution: {sd['duration_distribution']}")
    
    # Monthly distribution
    if 'monthly_distribution' in data['analytics']:
        report.append(f"\n📅 MONTHLY BOOKING DISTRIBUTION:")
        for month, count in data['analytics']['monthly_distribution'].items():
            report.append(f"   {month}: {count} bookings")
    
    # Day patterns
    if 'day_patterns' in data['analytics']:
        dp = data['analytics']['day_patterns']
        report.append(f"\n📆 DAY OF WEEK PATTERNS:")
        report.append(f"   Check-in Days: {dp['checkin_days']}")
        report.append(f"   Check-out Days: {dp['checkout_days']}")
        report.append(f"   Weekend Check-ins: {dp['weekend_checkins']}")
        report.append(f"   Weekend Check-outs: {dp['weekend_checkouts']}")
    
    # Phone analytics
    if 'phone_analytics' in data['analytics']:
        pa = data['analytics']['phone_analytics']
        report.append(f"\n📞 GUEST PHONE ANALYSIS:")
        report.append(f"   Unique Phone Numbers: {pa['unique_phone_numbers']}")
        report.append(f"   Total Bookings with Phone: {pa['total_phone_numbers']}")
        if pa['repeat_guests']:
            report.append(f"   Repeat Guests: {pa['repeat_guests']}")
    
    # Booking gaps
    if 'booking_gaps' in data['analytics']:
        bg = data['analytics']['booking_gaps']
        report.append(f"\n⏰ BOOKING GAP ANALYSIS:")
        report.append(f"   Average Gap: {bg['average_gap_days']:.1f} days")
        report.append(f"   Min Gap: {bg['min_gap_days']} days")
        report.append(f"   Max Gap: {bg['max_gap_days']} days")
        report.append(f"   Back-to-back Bookings: {bg['back_to_back_bookings']}")
        report.append(f"   Gap Distribution: {bg['gap_distribution']}")
    
    # Revenue data
    if 'revenue_data' in data['analytics']:
        rd = data['analytics']['revenue_data']
        report.append(f"\n💰 REVENUE ANALYSIS:")
        report.append(f"   Total Revenue: ${rd['total_revenue']:.2f}")
        report.append(f"   Average Booking Value: ${rd['average_booking_value']:.2f}")
        report.append(f"   Min Booking Value: ${rd['min_booking_value']:.2f}")
        report.append(f"   Max Booking Value: ${rd['max_booking_value']:.2f}")
    
    # Detailed reservations
    report.append(f"\n📋 DETAILED RESERVATION LIST:")
    for i, res in enumerate([r for r in data['reservations'] if r.get('confirmation_code')], 1):
        report.append(f"\n   {i:2d}. {res['confirmation_code']}")
        report.append(f"       Dates: {res.get('check_in_formatted', 'N/A')} → {res.get('check_out_formatted', 'N/A')}")
        report.append(f"       Duration: {res.get('duration_nights', 'N/A')} nights")
        if 'phone_last_4' in res:
            report.append(f"       Phone: ***-***-{res['phone_last_4']}")
        if 'guest_name' in res:
            report.append(f"       Guest: {res['guest_name']}")
        if 'price' in res:
            report.append(f"       Price: ${res['price']:.2f}")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)

def main():
    ical_path = "airbnb.ics"
    
    try:
        # Extract comprehensive data
        print("🔍 Extracting comprehensive data from Airbnb calendar...")
        data = extract_comprehensive_data(ical_path)
        
        # Generate and display report
        report = generate_report(data)
        print(report)
        
        # Save detailed JSON data
        with open("airbnb_comprehensive_data.json", "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n💾 Detailed data saved to 'airbnb_comprehensive_data.json'")
        
        # Save simple codes list
        codes = [r['confirmation_code'] for r in data['reservations'] if r.get('confirmation_code')]
        with open("airbnb_codes_simple.txt", "w") as f:
            for code in codes:
                f.write(f"{code}\n")
        print(f"💾 Simple codes list saved to 'airbnb_codes_simple.txt'")
        
        # Save CSV for spreadsheet analysis
        try:
            import csv
            with open("airbnb_reservations.csv", "w", newline='') as f:
                if codes:
                    writer = csv.DictWriter(f, fieldnames=[
                        'confirmation_code', 'check_in_date', 'check_out_date', 
                        'duration_nights', 'phone_last_4', 'day_of_week_checkin',
                        'is_weekend_checkin', 'month'
                    ])
                    writer.writeheader()
                    for res in data['reservations']:
                        if res.get('confirmation_code'):
                            writer.writerow({k: res.get(k, '') for k in writer.fieldnames})
            print(f"💾 CSV data saved to 'airbnb_reservations.csv'")
        except ImportError:
            pass
        
    except FileNotFoundError:
        print(f"❌ Error: File '{ical_path}' not found.")
        print("Please make sure the airbnb.ics file exists in the current directory.")
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 