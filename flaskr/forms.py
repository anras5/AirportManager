from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from flaskr import pool


# Custom validators
def user_exists(form, field):
    db = pool.acquire()
    cr = db.cursor()
    cr.execute("SELECT LOGIN FROM Pasazer")
    x = cr.fetchall()
    for user in x:
        if user[0] == field.data:
            raise ValidationError("User Already Exists")


def pesel_incorrect(form, field):
    for c in field.data:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            raise ValidationError("Wrong pesel")


# ------------------------------------------------------------------------------------------------------------------- #
# AUTHENTICATION FORMS #

class RegistrationForm(FlaskForm):
    login = StringField("Enter your login",
                        validators=[DataRequired(message='Login can not be empty'),
                                    user_exists,
                                    Length(max=25, message='Must be shorter than 25 characters')])
    password = StringField("Enter your password", validators=[DataRequired(message='Password can not be empty'),
                                                              Length(max=25,
                                                                     message='Must be shorter than 25 characters')])
    confirm = StringField("Confirm your password",
                          validators=[DataRequired(message='Please confirm password'),
                                      EqualTo('password', message='Passwords must match')])
    imie = StringField("Enter your first name",
                       validators=[DataRequired(),
                                   Length(max=25, message='Must be shorter than 25 characters')])
    nazwisko = StringField("Enter your last name",
                           validators=[DataRequired(),
                                       Length(max=25, message='Must be shorter than 25 characters')])
    pesel = StringField("Enter your pesel",
                        validators=[pesel_incorrect, Length(min=11, max=11, message='Must be 11 characters long')])
    dataurodzenia = DateField("Enter your birth date",
                              format='%Y-%m-%d',
                              validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    login = StringField("Enter your login", validators=[DataRequired()])
    password = StringField("Enter your password", validators=[DataRequired()])
    # stay_loggedin = BooleanField('stay logged-in')
    submit = SubmitField('LogIn')


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.AIRPORTS FORMS

class NewAirportForm(FlaskForm):
    nazwa = StringField("Enter airport's name")
    miasto = StringField("Enter airport's city")
    kraj = StringField("Enter airport's country")
    iatacode = StringField("Enter IATA code")
    icaocode = StringField("Enter ICAO code")
    longitude = FloatField("Enter airport's longitude")
    latitude = FloatField("Enter airport's latitude")
    submit = SubmitField("Add",)
