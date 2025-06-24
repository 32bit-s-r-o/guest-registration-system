#!/usr/bin/env python3
"""
Test script to verify the format_date filter works correctly.
"""

from app import app, db, User
from datetime import date
from flask import render_template_string
from config import Config

def test_format_date_in_template():
    """Test the format_date filter in a template context."""
    with app.app_context():
        # Test with default format user
        default_user = User.query.filter_by(username='admin').first()
        if default_user:
            print(f"Testing with user: {default_user.username} (format: {default_user.date_format})")
            
            # Test direct strftime first
            test_date = date(2025, 3, 26)
            print(f"  Test date type: {type(test_date)}, value: {test_date}")
            direct_result = test_date.strftime(default_user.date_format)
            print(f"  Direct strftime: {test_date} -> {direct_result}")
            
            # Test in template context
            template_string = "{{ test_date|format_date }}"
            
            with app.test_request_context():
                from flask_login import login_user
                login_user(default_user)
                result = render_template_string(template_string, test_date=test_date)
                print(f"  Template result: {test_date} -> {result}")
        
        # Test with custom format user
        custom_user = User.query.filter_by(username='test_admin_date_format').first()
        if custom_user:
            print(f"Testing with user: {custom_user.username} (format: {custom_user.date_format})")
            
            # Test direct strftime first
            test_date = date(2025, 3, 26)
            print(f"  Test date type: {type(test_date)}, value: {test_date}")
            direct_result = test_date.strftime(custom_user.date_format)
            print(f"  Direct strftime: {test_date} -> {direct_result}")
            
            # Test in template context
            template_string = "{{ test_date|format_date }}"
            
            with app.test_request_context():
                from flask_login import login_user
                login_user(custom_user)
                result = render_template_string(template_string, test_date=test_date)
                print(f"  Template result: {test_date} -> {result}")

if __name__ == "__main__":
    test_format_date_in_template() 