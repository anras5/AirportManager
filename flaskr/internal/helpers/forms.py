from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField, DecimalField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange, InputRequired
from flaskr.internal.helpers.constants import MAX_NUMBER_9, MAX_NUMBER_6


def pesel_incorrect(form, field):
    for c in field.data:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            raise ValidationError("Niepoprawny numer PESEL")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.AIRPORTS FORMS

class AirportForm(FlaskForm):
    nazwa = StringField("Podaj nazwę lotniska", validators=[DataRequired(),
                                                            Length(min=1, max=100, message="Podaj od 1 do 100 znaków")])
    miasto = StringField("Podaj miasto lotniska", validators=[DataRequired(),
                                                              Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    kraj = StringField("Podaj kraj lotniska", validators=[DataRequired(),
                                                          Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    iatacode = StringField("Podaj kod IATA",
                           validators=[DataRequired(),
                                       Length(min=3, max=3, message="Kody IATA mają 3 cyfry")])
    icaocode = StringField("Podaj kod ICAO",
                           validators=[DataRequired(),
                                       Length(min=4, max=4, message="Kody ICAO mają 4 cyfry")])
    longitude = DecimalField("Podaj długość geograficzną", places=3,
                             validators=[NumberRange(min=-180, max=180), InputRequired()])
    latitude = DecimalField("Podaj szerokość geograficzną", places=3,
                            validators=[NumberRange(min=-90, max=90), InputRequired()])
    submit = SubmitField("Dodaj lotnisko")


class AirportFormUpdate(AirportForm):
    submit = SubmitField("Edytuj lotnisko")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.AIRLINES FORMS

class AirlinesForm(FlaskForm):
    nazwa = StringField("Podaj nazwę linii lotniczych",
                        validators=[DataRequired(),
                                    Length(min=1, max=100, message="Podaj od 1 do 100 znaków")])
    kraj = StringField("Podaj kraj linii lotniczej", validators=[DataRequired(),
                                                                 Length(min=1, max=25,
                                                                        message="Podaj od 1 do 25 znaków")])
    submit = SubmitField("Dodaj linię lotniczą")


class AirlinesFormUpdate(AirlinesForm):
    submit = SubmitField("Edytuj linię lotniczą")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.MANUFACTURERS FORMS

class ManufacturersForm(FlaskForm):
    nazwa = StringField("Podaj nazwę producenta",
                        validators=[DataRequired(), Length(min=1, max=100, message="Podaj od 1 do 100 znaków")])
    kraj = StringField("Podaj kraj producenta",
                       validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    submit = SubmitField("Dodaj producenta")


class ManufacturersFormUpdate(ManufacturersForm):
    submit = SubmitField("Edytuj producenta")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.MODELS FORMS

class ModelsForm(FlaskForm):
    nazwa = StringField("Podaj nazwę modelu",
                        validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    liczba_miejsc = IntegerField("Podaj liczbę miejsc w samolocie",
                                 validators=[NumberRange(min=0, max=MAX_NUMBER_9), InputRequired()])
    predkosc = IntegerField("Podaj maksymalną prędkość modelu",
                            validators=[NumberRange(min=100, max=MAX_NUMBER_6), InputRequired()])
    producent = SelectField("Wybierz producenta samolotu", validators=[DataRequired()])
    submit = SubmitField("Dodaj model")


class ModelsFormUpdate(ModelsForm):
    submit = SubmitField("Edytuj model")


# ------------------------------------------------------------------------------------------------------------------- #
# RUNWAYS.RUNWAYS FORMS

class RunwaysForm(FlaskForm):
    nazwa = StringField("Podaj nazwę pasa startowego",
                        validators=[DataRequired(),
                                    Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    dlugosc = DecimalField("Podaj długość pasa w metrach", places=1,
                           validators=[NumberRange(min=1, max=MAX_NUMBER_6), InputRequired()])
    opis = StringField("Podaj dodatkowy opis pasa startowego", validators=[Length(max=100)])
    submit = SubmitField("Dodaj pas")


class RunwaysFormUpdate(RunwaysForm):
    submit = SubmitField("Edytuj pas")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.ARRIVALS FORMS

class ArrivalForm(FlaskForm):
    pas = SelectField("Wybierz spośród dostępnych pasów startowych", validators=[DataRequired()])
    lotnisko = SelectField("Wybierz lotnisko, z którego przyleci samolot", validators=[DataRequired()])
    model = SelectField("Wybierz model samolotu, który obsługuje połączenie", validators=[DataRequired()])
    linia_lotnicza = SelectField("Wybierz linię lotniczą, która obsługuje połączenie", validators=[DataRequired()])
    liczba_pasazerow = IntegerField("Podaj liczbę pasażerów, którzy przylecą tym lotem",
                                    validators=[NumberRange(min=0, max=MAX_NUMBER_9), InputRequired()])
    submit = SubmitField("Dodaj przylot")


class ArrivalFormUpdate(ArrivalForm):
    submit = SubmitField("Edytuj przylot")


class ArrivalFormUpdateWithoutRunway(FlaskForm):
    lotnisko = SelectField("Wybierz lotnisko, z którego przyleci samolot", validators=[DataRequired()])
    model = SelectField("Wybierz model samolotu, który obsługuje połączenie", validators=[DataRequired()])
    linia_lotnicza = SelectField("Wybierz linię lotniczą, która obsługuje połączenie", validators=[DataRequired()])
    liczba_pasazerow = IntegerField("Podaj liczbę pasażerów, którzy przylecą tym lotem",
                                    validators=[NumberRange(min=0, max=MAX_NUMBER_9), InputRequired()])
    submit = SubmitField("Edytuj przylot")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.ARRIVALS FORMS

class DepartureForm(FlaskForm):
    pas = SelectField("Wybierz spośród dostępnych pasów startowych", validators=[DataRequired()])
    lotnisko = SelectField("Wybierz lotnisko docelowe", validators=[DataRequired()])
    model = SelectField("Wybierz model samolotu, który obsługuje połączenie", validators=[DataRequired()])
    linia_lotnicza = SelectField("Wybierz linię lotniczą, która obsługuje połączenie", validators=[DataRequired()])
    liczba_miejsc = IntegerField("Podaj liczbę dostępnych miejsc dla tego lotu",
                                 validators=[NumberRange(min=0, max=MAX_NUMBER_9), InputRequired()])
    # pola z klasą dodawane dynamicznie #
    submit = SubmitField("Dodaj odlot")


class DepartureFormUpdate(DepartureForm):
    submit = SubmitField("Edytuj odlot")


class DepartureFormUpdateWithoutRunway(FlaskForm):
    lotnisko = SelectField("Wybierz lotnisko docelowe", validators=[DataRequired()])
    model = SelectField("Wybierz model samolotu, który obsługuje połączenie", validators=[DataRequired()])
    linia_lotnicza = SelectField("Wybierz linię lotniczą, która obsługuje połączenie", validators=[DataRequired()])
    liczba_miejsc = IntegerField("Podaj liczbę dostępnych miejsc dla tego lotu",
                                 validators=[NumberRange(min=0, max=MAX_NUMBER_9), InputRequired()])
    # pola z klasą dodawane dynamicznie #
    submit = SubmitField("Edytuj odlot")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.FLIGHTS FORMS

class ReservationForm(FlaskForm):
    pas = SelectField("Wybierz spośród dostępnych pasów startowych", validators=[DataRequired()])
    submit = SubmitField("Dodaj rezerwację")


# ------------------------------------------------------------------------------------------------------------------- #
# TICKETS.CLASSES FORMS

class ClassForm(FlaskForm):
    nazwa = StringField("Podaj nazwę klasy biletów",
                        validators=[DataRequired(), Length(min=1, max=15, message="Podaj od 1 do 15 znaków")])
    obsluga = StringField("Podaj krótki opis obsługi",
                          validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    komfort = StringField("Podaj jaki komfort oferuje klasa",
                          validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    cena = DecimalField("Podaj cenę biletu w tej klasie", places=2,
                        validators=[NumberRange(min=0, max=MAX_NUMBER_6), InputRequired()])
    submit = SubmitField("Dodaj klasę")


class ClassFormUpdate(ClassForm):
    submit = SubmitField("Edytuj klasę")


# ------------------------------------------------------------------------------------------------------------------- #
# TICKETS.PASSENGERS FORMS

class PassengerForm(FlaskForm):
    login = StringField("Podaj login",
                        validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    haslo = PasswordField("Podaj hasło",
                          validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    imie = StringField("Podaj imię",
                       validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    nazwisko = StringField("Podaj nazwisko",
                           validators=[DataRequired(), Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    pesel = StringField("Podaj pesel", validators=[DataRequired(), Length(min=11, max=11), pesel_incorrect])
    data_urodzenia = DateField("Podaj datę urodzin", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Dodaj pasażera")

    def validate_data_urodzenia(form, field):
        if field.data < datetime(year=1900, month=1, day=1).date():
            raise ValidationError("Data urodzenia musi być większa niż 01-01-1900")
        if field.data > datetime.now().date():
            raise ValidationError("Data urodzenia nie może być większa od dzisiejszej")


class PassengerFormUpdate(PassengerForm):
    submit = SubmitField("Edytuj pasażera")


class TicketForm(FlaskForm):
    czy_oplacony = IntegerField("Czy bilet został opłacony? Tak - 1, Nie - 0",
                                validators=[DataRequired(), NumberRange(min=0, max=1)])
    cena = IntegerField("Cena biletu", validators=[DataRequired(), NumberRange(min=0, max=MAX_NUMBER_6)])
    submit = SubmitField("Zatwierdź edycję")
