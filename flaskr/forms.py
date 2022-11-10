from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import  DataRequired, EqualTo, ValidationError
from wtforms import validators


class RegistrationForm(FlaskForm):
    login = StringField("Enter your login", validators=[DataRequired(message='Login can not be empty')])
    password = StringField("Enter your password", validators=[DataRequired(message='Password can not be empty')])
    confirm = StringField("Confirm your password", validators=[DataRequired(message='Please confirm password'), EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Register")
