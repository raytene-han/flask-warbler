from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, URL, Optional
from wtforms_alchemy import model_form_factory
from models import db, DirectMessage

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL', validators=[Optional(), URL()])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""

class EditProfileForm(FlaskForm):
    """Form for editing user profile."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Image URL')
    bio = StringField('(Optional) Bio')
    password = PasswordField('Password', validators=[Length(min=6)])

class DirectMessageForm(ModelForm):
    class Meta:
        model = DirectMessage
        include = ['user_id_to']

    user_id_to = SelectField(validators=[DataRequired()])