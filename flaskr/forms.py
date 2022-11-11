from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import  DataRequired, EqualTo, ValidationError
from flaskr.db import get_db

# Custom validator
def user_exists(form, field):
    db = get_db()
    cr = db.cursor()
    cr.execute("SELECT LOGIN FROM USERS")
    x = cr.fetchall()
    for user in x:
        print("Field data: ", field.data)
        print('user: ', user[0])
        if user[0] == field.data:
            raise ValidationError("User Already Exists")


class RegistrationForm(FlaskForm):
    login = StringField("Enter your login", validators=[DataRequired(message='Login can not be empty'), user_exists])
    password = StringField("Enter your password", validators=[DataRequired(message='Password can not be empty')])
    confirm = StringField("Confirm your password", validators=[DataRequired(message='Please confirm password'), EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    login = StringField("Enter your login", validators=[DataRequired()])
    password = StringField("Enter your password", validators=[DataRequired()])
    stay_loggedin = BooleanField('stay logged-in')
    submit = SubmitField('LogIn')
