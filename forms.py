"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, EmailField
from wtforms.validators import InputRequired, Optional, Email, URL, Length


class AddEditCafeForm(FlaskForm):
    """Form for adding/editing cafes"""

    name = StringField(
        'Name',
        validators=[InputRequired(), Length(max=80)]
    )

    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )

    url = StringField(
        'URL',
        validators=[Optional(), URL()]
    )

    address = StringField(
        'Address',
        validators=[InputRequired()]
    )

    city_code = SelectField('City',)

    image_url = StringField(
        'Image',
        validators=[Optional(), URL()]
    )

class SignUpForm(FlaskForm):
    """Form for signing users up"""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)]
    )

    first_name = StringField(
        'First Name',
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        'Last Name',
        validators=[InputRequired(), Length(max=30)]
    )

    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )

    email = EmailField(
        'Email',
        validators=[Email(), InputRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=5,max=40)]
    )

    image_url= StringField(
        'Profile Image',
        validators=[Optional(), URL()]
    )

class LoginForm(FlaskForm):
    """Form for user login"""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)]
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=5,max=40)]
    )

class ProfileEditForm(FlaskForm):
    """Form for editing user profile"""
    first_name = StringField(
        'First Name',
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        'Last Name',
        validators=[InputRequired(), Length(max=30)]
    )

    description = TextAreaField(
        'Description',
        validators=[Optional()]
    )

    email = EmailField(
        'Email',
        validators=[Email(), InputRequired()]
    )

    image_url= StringField(
        'Profile Image',
        validators=[Optional(), URL()]
    )



class CSRFProtectForm(FlaskForm):
    """ Form for CSRF protection """