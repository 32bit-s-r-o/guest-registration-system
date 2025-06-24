from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_babel import gettext as _

auth = Blueprint('auth', __name__)

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    from database import User
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = User.query.filter_by(username=username, is_deleted=False).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash(_('Invalid username or password'), 'error')
    
    return render_template('admin/login.html')

@auth.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login')) 