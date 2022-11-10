from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import  DataRequired, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    login = StringField("Enter your login", validators=[DataRequired(message='Login can not be empty')])
    password = StringField("Enter your password", validators=[DataRequired(message='Password can not be empty'), EqualTo('confirm', message='Password must match')])
    confirm = StringField("Confirm your password", validators=[DataRequired(message='Please confirm password')])
    submit = SubmitField("Register")
