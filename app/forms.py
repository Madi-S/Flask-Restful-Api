from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.widgets import PasswordInput

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

    @property
    def visible_fields(self):
        return self.username, self.password


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(4, 30)])
    password = StringField(label='Password', widget=PasswordInput(), validators=[DataRequired(), Length(6, 50), EqualTo('password_confirm', message='Passwords do not match')])
    password_confirm = StringField(label='Password confirm', widget=PasswordInput(), validators=[DataRequired(), Length(6, 50)])
    submit = SubmitField('Sign Up')

    @property
    def visible_fields(self):
        return self.username, self.password, self.password_confirm
