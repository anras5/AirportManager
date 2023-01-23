from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange
from flaskr.internal.helpers.constants import MAX_NUMBER_9, MAX_NUMBER_12_6, MAX_NUMBER_6


def pesel_incorrect(form, field):
    for c in field.data:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            raise ValidationError("Wrong pesel")


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
    longitude = DecimalField("Podaj długość geograficzną",
                             validators=[DataRequired(), NumberRange(min=-180, max=180)])
    latitude = DecimalField("Podaj szerokość geograficzną",
                            validators=[DataRequired(), NumberRange(min=-90, max=90)])
    submit = SubmitField("Dodaj lotnisko")


class AirportFormUpdate(AirportForm):
    submit = SubmitField("Edytuj lotnisko")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.AIRLINES FORMS

class AirlinesForm(FlaskForm):
    nazwa = StringField("Podaj nazwę linii lotniczych",
                        validators=[DataRequired(),
                                    Length(min=1, max=100, message="Podaj od 1 do 100 znaków")])
    kraj = StringField("Podaj kraj lotniska", validators=[DataRequired(),
                                                          Length(min=1, max=25, message="Podaj od 1 do 25 znaków")])
    submit = SubmitField("Dodaj linię lotniczą")


class AirlinesFormUpdate(AirlinesForm):
    submit = SubmitField("Edytuj linię lotniczą")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.MANUFACTURERS FORMS

class ManufacturersForm(FlaskForm):
    nazwa = StringField("Podaj nazwę producenta",
                        validators=[DataRequired(), Length(min=1, max=100, message="Podaj od 1 do 100 znaków")])
    kraj = StringField("Podaj kraj lotniska",
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
                                 validators=[DataRequired(),
                                             NumberRange(min=0, max=MAX_NUMBER_9)])
    predkosc = IntegerField("Podaj maksymalną prędkość modelu",
                            validators=[DataRequired(),
                                        NumberRange(min=100, max=MAX_NUMBER_6)])
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
    dlugosc = DecimalField("Podaj długość pasa w metrach",
                           validators=[DataRequired(),
                                       NumberRange(min=1, max=MAX_NUMBER_6)])
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
                                    validators=[DataRequired(),
                                                NumberRange(min=0, max=MAX_NUMBER_9)])
    submit = SubmitField("Dodaj przylot")


class ArrivalFormUpdate(ArrivalForm):
    submit = SubmitField("Edytuj przylot")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.ARRIVALS FORMS

class ClassSeatsForm(FlaskForm):
    seats = IntegerField()


class DepartureForm(FlaskForm):
    pas = SelectField("Wybierz spośród dostępnych pasów startowych", validators=[DataRequired()])
    lotnisko = SelectField("Wybierz lotnisko docelowe", validators=[DataRequired()])
    model = SelectField("Wybierz model samolotu, który obsługuje połączenie", validators=[DataRequired()])
    linia_lotnicza = SelectField("Wybierz linię lotniczą, która obsługuje połączenie", validators=[DataRequired()])
    liczba_miejsc = IntegerField("Podaj liczbę dostępnych miejsc dla tego lotu",
                                 validators=[DataRequired(), NumberRange(min=0)])
    # pola z klasą dodawane dynamicznie #
    submit = SubmitField("Dodaj odlot")


# ------------------------------------------------------------------------------------------------------------------- #
# FLIGHTS.FLIGHTS FORMS

class ReservationForm(FlaskForm):
    pas = SelectField("Wybierz spośród dostępnych pasów startowych", validators=[DataRequired()])
    submit = SubmitField("Dodaj rezerwację")


# ------------------------------------------------------------------------------------------------------------------- #
# TICKETS.CLASSES FORMS

class ClassForm(FlaskForm):
    nazwa = StringField("Podaj nazwę klasy biletów", validators=[DataRequired()])
    obsluga = StringField("Podaj krótki opis obsługi", validators=[DataRequired()])
    komfort = StringField("Podaj jaki komfort oferuje klasa", validators=[DataRequired()])
    cena = DecimalField("Podaj cenę biletu w tej klasie", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Dodaj klasę")


# ------------------------------------------------------------------------------------------------------------------- #
# TICKETS.PASSENGERS FORMS

class PassengerForm(FlaskForm):
    login = StringField("Podaj login", validators=[DataRequired()])
    haslo = StringField("Podaj hasło", validators=[DataRequired()])
    imie = StringField("Podaj imię", validators=[DataRequired()])
    nazwisko = StringField("Podaj nazwisko", validators=[DataRequired()])
    pesel = StringField("Podaj pesel", validators=[DataRequired(), Length(min=11, max=11)])
    data_urodzenia = DateField("Podaj datę urodzin", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Dodaj pasażera")


class TicketForm(FlaskForm):
    czy_oplacony = IntegerField("Czy bilet został opłacony? Tak - 1, Nie - 0",
                                validators=[DataRequired(), NumberRange(min=0, max=1)])
    cena = IntegerField("Cena biletu", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Zatwierdź edycję")
