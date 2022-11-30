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
    login = StringField("Podaj login",
                        validators=[DataRequired(message='Login can not be empty'),
                                    user_exists,
                                    Length(max=25, message='Must be shorter than 25 characters')])
    password = StringField("Podaj hasło", validators=[DataRequired(message='Password can not be empty'),
                                                              Length(max=25,
                                                                     message='Must be shorter than 25 characters')])
    confirm = StringField("Potwierdź hasło",
                          validators=[DataRequired(message='Please confirm password'),
                                      EqualTo('password', message='Passwords must match')])
    imie = StringField("Podaj swoje imię",
                       validators=[DataRequired(),
                                   Length(max=25, message='Must be shorter than 25 characters')])
    nazwisko = StringField("Podaj swoje nazwisko",
                           validators=[DataRequired(),
                                       Length(max=25, message='Must be shorter than 25 characters')])
    pesel = StringField("Podaj swój numer PESEL",
                        validators=[pesel_incorrect, Length(min=11, max=11, message='Must be 11 characters long')])
    dataurodzenia = DateField("Podaj datę urodzin",
                              format='%Y-%m-%d',
                              validators=[DataRequired()])
    submit = SubmitField("Załóż konto")


class LoginForm(FlaskForm):
    login = StringField("Podaj login", validators=[DataRequired()])
    password = StringField("Podaj hasło", validators=[DataRequired()])
    # stay_loggedin = BooleanField('stay logged-in')
    submit = SubmitField('Zaloguj się')


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.AIRPORTS FORMS

class AirportForm(FlaskForm):
    nazwa = StringField("Podaj nazwę lotniska", validators=[DataRequired()])
    miasto = StringField("Podaj miasto lotniska", validators=[DataRequired()])
    kraj = StringField("Podaj kraj lotniska", validators=[DataRequired()])
    iatacode = StringField("Podaj kod IATA", validators=[DataRequired(), Length(min=3, max=3, message="Kody IATA mają 3 cyfry")])
    icaocode = StringField("Podaj kod ICAO", validators=[DataRequired(), Length(min=4, max=4, message="Kody ICAO mają 4 cyfry")])
    longitude = FloatField("Podaj długość geograficzną", validators=[DataRequired()])
    latitude = FloatField("Podaj szerokość geograficzną", validators=[DataRequired()])
    submit = SubmitField("Dodaj lotnisko")
