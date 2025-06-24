from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from functools import wraps
from datetime import datetime

users = Blueprint('users', __name__)

from database import db, User

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                login_manager = current_app.extensions.get('login_manager')
                return login_manager.unauthorized()
            if current_user.role != role:
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@users.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Admin users list page."""
    users_list = User.query.filter_by(is_deleted=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)

@users.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_user():
    """Create a new user."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'admin')
        
        # Check if username or email already exists (not deleted)
        if User.query.filter_by(username=username, is_deleted=False).first():
            flash(_('Username already exists'), 'error')
            return render_template('admin/new_user.html')
        
        if User.query.filter_by(email=email, is_deleted=False).first():
            flash(_('Email already exists'), 'error')
            return render_template('admin/new_user.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('User created successfully!'), 'success')
        return redirect(url_for('users.admin_users'))
    
    # Get role from query parameter for pre-filling
    default_role = request.args.get('role', 'admin')
    return render_template('admin/new_user.html', default_role=default_role)

@users.route('/admin/users/<int:user_id>')
@login_required
@role_required('admin')
def view_user(user_id):
    """View a specific user."""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    return render_template('admin/view_user.html', user=user)

@users.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    """Edit an existing user."""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'admin')
        new_password = request.form.get('new_password')
        
        # Check if username or email already exists (excluding current user, not deleted)
        existing_user = User.query.filter_by(username=username, is_deleted=False).first()
        if existing_user and existing_user.id != user.id:
            flash(_('Username already exists'), 'error')
            return render_template('admin/edit_user.html', user=user)
        
        existing_user = User.query.filter_by(email=email, is_deleted=False).first()
        if existing_user and existing_user.id != user.id:
            flash(_('Email already exists'), 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Update user
        user.username = username
        user.email = email
        user.role = role
        
        # Update password if provided
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        
        flash(_('User updated successfully!'), 'success')
        return redirect(url_for('users.view_user', user_id=user.id))
    
    return render_template('admin/edit_user.html', user=user)

@users.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Soft delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current user
    if user.id == current_user.id:
        flash(_('You cannot delete your own account'), 'error')
        return redirect(url_for('users.admin_users'))
    
    # Check if user is already deleted
    if user.is_deleted:
        flash(_('User is already deleted.'), 'info')
        return redirect(url_for('users.admin_users'))
    try:
        user.is_deleted = True
        db.session.commit()
        flash(_('User deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to soft delete user {user_id}: {e}")
        flash(_('Error deleting user: %(error)s', error=str(e)), 'error')
    return redirect(url_for('users.admin_users')) 