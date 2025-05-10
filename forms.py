from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from werkzeug.utils import secure_filename
import os

class LoginForm(FlaskForm):
    access_key = StringField('Access Key', validators=[DataRequired(), Length(min=16, max=16)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=64)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Create User')

class EditUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=64)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Update User')

class RegenerateKeyForm(FlaskForm):
    confirm = BooleanField('I understand this will invalidate the current access key', validators=[DataRequired()])
    submit = SubmitField('Regenerate Access Key')

class UploadImageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload')

class EditImageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Update')
