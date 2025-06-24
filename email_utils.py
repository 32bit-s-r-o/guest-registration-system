from flask import session, url_for, current_app
from flask_mail import Message
from flask_babel import gettext as _
from utils import get_server_url

def send_approval_email(registration):
    """Send approval email to guest after registration is approved."""
    try:
        # Set language based on registration
        original_lang = session.get('language', 'en')
        if registration.language:
            session['language'] = registration.language
        
        msg = Message(
            _('Your registration has been approved!'),
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[registration.email]
        )
        msg.body = _("""
Dear Guest,

Your registration for %(trip_title)s has been approved!

Your personal data has been processed and all uploaded documents have been securely deleted in compliance with GDPR regulations.

Thank you for choosing our service.

Best regards,
The Admin Team
""", trip_title=registration.trip.title)
        current_app.extensions['mail'].send(msg)
        
        # Restore original language
        session['language'] = original_lang
        return True
    except Exception as e:
        print(f"Error sending approval email: {e}")
        return False

def send_rejection_email(registration):
    """Send rejection email to guest when registration is rejected."""
    try:
        # Set language based on registration
        original_lang = session.get('language', 'en')
        if registration.language:
            session['language'] = registration.language
        
        # Generate proper URL using server configuration
        server_url = get_server_url()
        update_link = f"{server_url}{url_for('registration.register', trip_id=registration.trip_id)}"
        
        msg = Message(
            _('Registration Update Required'),
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[registration.email]
        )
        msg.body = _("""
Dear Guest,

Your registration for %(trip_title)s requires updates.

Admin Comment: %(admin_comment)s

Please update your information using this link: %(update_link)s

Thank you for your understanding.

Best regards,
The Admin Team
""", trip_title=registration.trip.title, admin_comment=registration.admin_comment, update_link=update_link)
        current_app.extensions['mail'].send(msg)
        
        # Restore original language
        session['language'] = original_lang
        return True
    except Exception as e:
        print(f"Error sending rejection email: {e}")
        return False 