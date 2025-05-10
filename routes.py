import os
import json
import csv
import io
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app
from models import User, UserData
from forms import LoginForm, CreateUserForm, EditUserForm, UploadFileForm
from functools import wraps
from utils import parse_csv, parse_json

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        
        if user and user.check_password(form.password.data):
            if not user.is_active():
                flash('Your account is disabled. Please contact an administrator.', 'danger')
                return redirect(url_for('login'))
                
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    uploads = UserData.get_user_uploads(current_user.id)
    return render_template('dashboard.html', uploads=uploads)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadFileForm()
    
    if form.validate_on_submit():
        uploaded_file = form.file.data
        if uploaded_file:
            # Create user directory if it doesn't exist
            user_dir = os.path.join('data', 'uploads', str(current_user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Save the file
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(user_dir, filename)
            
            uploaded_file.save(file_path)
            flash(f'File {filename} uploaded successfully!', 'success')
            return redirect(url_for('view_data', file_id=filename))
    
    return render_template('upload.html', form=form)

@app.route('/view/<file_id>')
@login_required
def view_data(file_id):
    file_path = os.path.join('data', 'uploads', str(current_user.id), file_id)
    
    if not os.path.exists(file_path):
        flash('File not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    data = None
    columns = []
    rows = []
    
    try:
        if file_id.endswith('.json'):
            data = parse_json(file_path)
        elif file_id.endswith('.csv'):
            columns, rows = parse_csv(file_path)
    except Exception as e:
        flash(f'Error parsing file: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('view_data.html', 
                          file_id=file_id, 
                          data=data, 
                          columns=columns, 
                          rows=rows,
                          file_type=file_id.split('.')[-1])

@app.route('/delete/<file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    success = UserData.delete_upload(current_user.id, file_id)
    
    if success:
        flash(f'File {file_id} deleted successfully', 'success')
    else:
        flash('File not found or could not be deleted', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.get_users()
    return render_template('admin.html', users=users)

@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    
    if form.validate_on_submit():
        success, result = User.create(
            username=form.username.data,
            password=form.password.data,
            role=form.role.data,
            active=form.active.data
        )
        
        if success:
            flash(f'User {form.username.data} created successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash(f'Error creating user: {result}', 'danger')
    
    return render_template('admin.html', create_form=form, active_tab='create')

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user_obj = User.get(user_id)
    
    if not user_obj:
        flash('User not found', 'danger')
        return redirect(url_for('admin_panel'))
    
    form = EditUserForm(obj=user_obj)
    
    if form.validate_on_submit():
        data = {
            'username': form.username.data,
            'role': form.role.data,
            'active': form.active.data
        }
        
        # Only update password if provided
        if form.password.data:
            data['password'] = form.password.data
            
        success = User.update(user_id, data)
        
        if success:
            flash(f'User {form.username.data} updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Error updating user', 'danger')
    
    # Pre-fill form data
    form.username.data = user_obj.username
    form.role.data = user_obj.role
    form.active.data = user_obj.active
    
    return render_template('admin.html', edit_form=form, user=user_obj, active_tab='edit')

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Prevent admin from deleting themselves
    if int(user_id) == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin_panel'))
    
    success = User.delete(user_id)
    
    if success:
        flash('User deleted successfully', 'success')
    else:
        flash('Error deleting user', 'danger')
        
    return redirect(url_for('admin_panel'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message='Page not found'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, message='Forbidden'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message='Internal server error'), 500
