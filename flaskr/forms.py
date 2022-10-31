from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class RegistrationForm(FlaskForm):
    login = StringField("Enter your login")
    password = StringField("Enter your password")
    submit = SubmitField("Register")
