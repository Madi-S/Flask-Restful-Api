from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

    @property
    def visible_fields(self):
        return self.username, self.password


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(4, 30)])
    password = PasswordField(label='Password', validators=[
        Length(6, 50),
        EqualTo('password_confirm', message='Passwords must match')
    ])
    password_confirm = StringField(label='Password confirm', validators=[
        Length(6, 50)
    ])
    submit = SubmitField('Sign Up')

    @property
    def visible_fields(self):
        return self.username, self.password, self.password_confirm
