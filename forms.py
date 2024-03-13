"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Optional, Email, URL, Length


class AddEditCafeForm(FlaskForm):

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
