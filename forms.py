from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.utils import secure_filename
import os

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Create User')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('New Password', validators=[
        Length(min=0, max=64),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm New Password')
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Update User')

class UploadFileForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')

    def validate_file(self, field):
        if field.data:
            filename = secure_filename(field.data.filename)
            if not filename.endswith(('.json', '.csv')):
                raise ValidationError('Only JSON and CSV files are allowed')
