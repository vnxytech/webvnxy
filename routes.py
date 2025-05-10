import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app
from models import User, Image
from forms import LoginForm, CreateUserForm, EditUserForm, RegenerateKeyForm, UploadImageForm, EditImageForm
from functools import wraps

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
        user = User.get_by_access_key(form.access_key.data)
        
        if user:
            if not user.get_account_status():
                flash('Your account is disabled. Please contact an administrator.', 'danger')
                return redirect(url_for('login'))
                
            login_user(user, remember=form.remember_me.data)
            # Record the login time
            User.record_login(user.id)
            next_page = request.args.get('next')
            
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid access key', 'danger')
    
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
    images = Image.get_images()
    return render_template('dashboard.html', images=images)

@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join('data', 'uploads'), filename)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_image():
    form = UploadImageForm()
    
    if form.validate_on_submit():
        image = form.image.data
        if image:
            # Create uploads directory if it doesn't exist
            os.makedirs(os.path.join('data', 'uploads'), exist_ok=True)
            
            # Generate unique filename
            filename = str(uuid.uuid4()) + secure_filename(image.filename)
            file_path = os.path.join('data', 'uploads', filename)
            
            # Save the image file
            image.save(file_path)
            
            # Create image record
            image_data = {
                "id": str(uuid.uuid4()),
                "title": form.title.data,
                "description": form.description.data,
                "filename": filename,
                "uploaded_by": current_user.id,
                "uploaded_by_name": current_user.name,
                "uploaded_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(file_path)
            }
            
            Image.save_image_data(image_data)
            
            flash(f'Image "{form.title.data}" uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('upload.html', form=form)

@app.route('/image/<image_id>')
@login_required
def view_image(image_id):
    image = Image.get_image(image_id)
    
    if not image:
        flash('Image not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('view_image.html', image=image)

@app.route('/image/edit/<image_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_image(image_id):
    image = Image.get_image(image_id)
    
    if not image:
        flash('Image not found!', 'danger')
        return redirect(url_for('dashboard'))
    
    form = EditImageForm(obj=image)
    
    if form.validate_on_submit():
        data = {
            'title': form.title.data,
            'description': form.description.data
        }
        
        success = Image.update_image(image_id, data)
        
        if success:
            flash(f'Image "{form.title.data}" updated successfully!', 'success')
            return redirect(url_for('view_image', image_id=image_id))
        else:
            flash('Error updating image', 'danger')
    
    # Pre-fill form data
    form.title.data = image['title']
    form.description.data = image['description']
    
    return render_template('edit_image.html', form=form, image=image)

@app.route('/image/delete/<image_id>', methods=['POST'])
@login_required
@admin_required
def delete_image(image_id):
    success = Image.delete_image(image_id)
    
    if success:
        flash('Image deleted successfully', 'success')
    else:
        flash('Image not found or could not be deleted', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.get_users()
    
    # Get recent logins (users with last_login value, sorted by last_login)
    recent_logins = [user for user in users if user.get('last_login')]
    recent_logins.sort(key=lambda x: x.get('last_login', ''), reverse=True)
    recent_logins = recent_logins[:5]  # Get only 5 most recent
    
    # Create forms needed for the admin panel
    create_form = CreateUserForm()
    
    return render_template('admin.html', users=users, recent_logins=recent_logins, 
                          create_form=create_form)

@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    
    if form.validate_on_submit():
        success, user_id, access_key = User.create(
            name=form.name.data,
            role=form.role.data,
            active=form.active.data
        )
        
        if success:
            flash(f'User {form.name.data} created successfully with access key: {access_key}', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Error creating user', 'danger')
    
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
            'name': form.name.data,
            'role': form.role.data,
            'active': form.active.data
        }
            
        success = User.update(user_id, data)
        
        if success:
            flash(f'User {form.name.data} updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Error updating user', 'danger')
    
    # Pre-fill form data
    form.name.data = user_obj.name
    form.role.data = user_obj.role
    form.active.data = user_obj.is_account_active
    
    return render_template('admin.html', edit_form=form, user=user_obj, active_tab='edit')

@app.route('/admin/regenerate-key/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def regenerate_key(user_id):
    user_obj = User.get(user_id)
    
    if not user_obj:
        flash('User not found', 'danger')
        return redirect(url_for('admin_panel'))
    
    form = RegenerateKeyForm()
    
    if form.validate_on_submit():
        success, new_key = User.regenerate_key(user_id)
        
        if success:
            flash(f'New access key generated for {user_obj.name}: {new_key}', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Error generating new access key', 'danger')
    
    return render_template('admin.html', regenerate_form=form, user=user_obj, active_tab='regenerate')

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Prevent admin from deleting themselves
    if int(user_id) == int(current_user.id):
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
