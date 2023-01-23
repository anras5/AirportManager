import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from wtforms import IntegerField
from wtforms.validators import NumberRange, InputRequired

from flaskr.internal.helpers.forms import AirportForm, AirlinesForm, ManufacturersForm, ModelsForm, ArrivalForm, \
    ReservationForm, DepartureForm, AirportFormUpdate, AirlinesFormUpdate, ManufacturersFormUpdate, ModelsFormUpdate, \
    ArrivalFormUpdate, DepartureFormUpdate, ArrivalFormUpdateWithoutRunway, DepartureFormUpdateWithoutRunway
from flaskr.internal.helpers.models import Lotnisko
from flaskr import oracle_db
from flaskr.internal.helpers import constants as c

import os
import json

import requests

flights_bp = Blueprint('flights', __name__, url_prefix='/flights')


def get_airport_from_api(iatacode: str) -> Lotnisko:
    """
    get_airport_from_api returns data about an airport from RapidApi
    :param iatacode:
    :return: Lotnisko
    """
    # get data from https://airport-info.p.rapidapi.com/airport into api_data dictionary
    api_key = os.environ.get('RAPID_API_AIRPORT_INFO_KEY')
    # prepare headers for request
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "airport-info.p.rapidapi.com"
    }
    # prepare query dictionary
    querystring = {"iata": iatacode}

    # send request
    response = requests.get(f'https://airport-info.p.rapidapi.com/airport',
                            headers=headers,
                            params=querystring).text
    api_data = json.loads(response)
    # handle case when wrong iatacode is provided in the url parameter
    if 'error' in api_data:
        if api_data['error'] == "No airport found":
            flash("Nie znaleziono takiego lotniska. Uzupełnij pola samodzielnie.", category='warning')
        else:
            error = api_data.get('error').get('text')
            flash(error, category='error')
        return Lotnisko()
    return Lotnisko(nazwa=api_data.get('name', ''),
                    miasto=api_data.get('city', ''),
                    kraj=api_data.get('country', ''),
                    iatacode=api_data.get('iata', ''),
                    icaocode=api_data.get('icao', ''),
                    longitude=round(api_data.get('longitude', 1000.0), 4),
                    latitude=round(api_data.get('latitude', 1000.0), 4))


@flights_bp.route('/')
def main():
    return render_template('flights-index.page.html')


@flights_bp.route('/map')
def world_map():
    arrivals = oracle_db.select_arrivals_for_map()
    departures = oracle_db.select_departures_for_map()
    coordinates = {}
    with open('airport.json', 'r') as file:
        coordinates = json.load(file)
    if not coordinates:
        flash("Ustaw współrzędne lotniska w panelu sterowania", c.ERROR)
        return redirect(url_for('flights.main'))
    else:
        return render_template('flights-worldmap.page.html',
                               arrivals=arrivals,
                               departures=departures,
                               coordinates=coordinates)


# -------------------------------------------------------------------------------------------------------------------- #
# AIRPORTS

@flights_bp.route('/airports')
def airports():
    headers, airports_list = oracle_db.select_airports()

    return render_template('flights-airports/flights-airports.page.html',
                           airports_data=airports_list,
                           airports_headers=headers)


@flights_bp.route('/airports/new', methods=['GET', 'POST'])
def new_airport():
    form = AirportForm()
    if form.validate_on_submit():
        # POST

        flash_message, flash_category, flash_type = oracle_db.insert_airport(form.nazwa.data,
                                                                             form.miasto.data,
                                                                             form.kraj.data,
                                                                             form.iatacode.data,
                                                                             form.icaocode.data,
                                                                             form.longitude.data,
                                                                             form.latitude.data)
        flash(flash_message, flash_category)
        if flash_type == c.LOTNISKO_UN_IATA:
            form.iatacode.data = ""
            return render_template('flights-airports/flights-airports-new.page.html', form=form)
        if flash_type == c.LOTNISKO_UN_NAZWA:
            form.nazwa.data = ""
            return render_template('flights-airports/flights-airports-new.page.html', form=form)
        if flash_type == c.LOTNISKO_UN_ICAO:
            form.icaocode.data = ""
            return render_template('flights-airports/flights-airports-new.page.html', form=form)
        if flash_type == c.LOTNISKO_UN_GEO:
            form.longitude.data = ""
            form.latitude.data = ""
            return render_template('flights-airports/flights-airports-new.page.html', form=form)
        elif flash_category == c.ERROR:
            return redirect(url_for('flights.airports'))
        else:
            return redirect(url_for('flights.airports'))

    iatacode = request.args.get('iatacode')
    if iatacode:
        lotnisko = get_airport_from_api(iatacode)
    else:
        lotnisko = Lotnisko()

    # set default values on the form
    form.nazwa.data = lotnisko.nazwa
    form.miasto.data = lotnisko.miasto
    form.kraj.data = lotnisko.kraj
    form.iatacode.data = lotnisko.iatacode
    form.icaocode.data = lotnisko.icaocode
    form.longitude.data = lotnisko.longitude
    form.latitude.data = lotnisko.latitude

    return render_template('flights-airports/flights-airports-new.page.html',
                           form=form)


@flights_bp.route('/airports/update/<int:airport_id>', methods=['GET', 'POST'])
def update_airport(airport_id: int):
    form = AirportFormUpdate()

    # get lotnisko from db
    lotnisko = oracle_db.select_airport(airport_id)

    if form.validate_on_submit():
        # POST

        flash_message, flash_category, flash_type = oracle_db.update_airport(airport_id=airport_id,
                                                                             nazwa=form.nazwa.data,
                                                                             miasto=form.miasto.data,
                                                                             kraj=form.kraj.data,
                                                                             iatacode=form.iatacode.data,
                                                                             icaocode=form.icaocode.data,
                                                                             longitude=form.longitude.data,
                                                                             latitude=form.latitude.data)

        flash(flash_message, flash_category)
        if flash_type == c.LOTNISKO_UN_IATA:
            form.iatacode.data = ""
            return render_template('flights-airports/flights-airports-update.page.html', form=form, lotnisko=lotnisko)
        if flash_type == c.LOTNISKO_UN_NAZWA:
            form.nazwa.data = ""
            return render_template('flights-airports/flights-airports-update.page.html', form=form, lotnisko=lotnisko)
        if flash_type == c.LOTNISKO_UN_ICAO:
            form.icaocode.data = ""
            return render_template('flights-airports/flights-airports-update.page.html', form=form, lotnisko=lotnisko)
        if flash_type == c.LOTNISKO_UN_GEO:
            form.longitude.data = ""
            form.latitude.data = ""
            return render_template('flights-airports/flights-airports-update.page.html', form=form, lotnisko=lotnisko)
        elif flash_category == c.ERROR:
            return redirect(url_for('flights.airports'))
        else:
            return redirect(url_for('flights.airports'))

    # set default values on the form
    form.nazwa.data = lotnisko.nazwa
    form.miasto.data = lotnisko.miasto
    form.kraj.data = lotnisko.kraj
    form.iatacode.data = lotnisko.iatacode
    form.icaocode.data = lotnisko.icaocode
    form.longitude.data = lotnisko.longitude
    form.latitude.data = lotnisko.latitude

    return render_template('flights-airports/flights-airports-update.page.html',
                           form=form,
                           lotnisko=lotnisko)


@flights_bp.route('/airports/delete', methods=['POST'])
def delete_airport():
    # get airport id from parameters
    parameters = request.form
    airport_id = parameters.get('airport_id', '')
    if not airport_id:
        flash("Błąd - nie podano lotniska do usunięcia", category=c.ERROR)
        return redirect(url_for('flights.airports'))

    # delete record from database
    flash_message, flash_category = oracle_db.delete_airport(airport_id)

    # flash and redirect to airlines page
    flash(flash_message, flash_category)
    return redirect(url_for('flights.airports'))


# -------------------------------------------------------------------------------------------------------------------- #
# AIRLINES

@flights_bp.route('/airlines')
def airlines():
    headers, airlines_list = oracle_db.select_airlines()

    return render_template('flights-airlines/flights-airlines.page.html',
                           airlines_data=airlines_list,
                           airlines_headers=headers)


@flights_bp.route('/airlines/new', methods=['GET', 'POST'])
def new_airline():
    form = AirlinesForm()
    if form.validate_on_submit():
        # POST
        flash_message, flash_category, flash_type = oracle_db.insert_airline(form.nazwa.data,
                                                                             form.kraj.data)

        flash(flash_message, flash_category)
        if flash_type == c.LINIALOTNICZA_UN_NAZWA:
            # duplicated nazwa in db
            form.nazwa.data = ""
            return render_template('flights-airlines/flights-airlines-new.page.html',
                                   form=form)
        elif flash_category == c.ERROR:
            return redirect(url_for('flights.airlines'))
        else:
            return redirect(url_for('flights.airlines'))

    return render_template('flights-airlines/flights-airlines-new.page.html',
                           form=form)


@flights_bp.route('/airlines/update/<int:airline_id>', methods=['GET', 'POST'])
def update_airline(airline_id: int):
    form = AirlinesFormUpdate()

    # get linia lotnicza from db
    linialotnicza = oracle_db.select_airline(airline_id)

    if form.validate_on_submit():
        # update airline
        flash_message, flash_category, flash_type = oracle_db.update_airline(airline_id,
                                                                             form.nazwa.data,
                                                                             form.kraj.data)

        flash(flash_message, flash_category)
        if flash_type == c.LINIALOTNICZA_UN_NAZWA:
            # duplicated nazwa in db
            form.nazwa.data = ""
            return render_template('flights-airlines/flights-airlines-update.page.html',
                                   form=form,
                                   linialotnicza=linialotnicza)
        elif flash_category == c.ERROR:
            # some other error occurred
            return redirect(url_for('flights.airlines'))
        else:
            # success
            return redirect(url_for('flights.airlines'))

    # set default values on the form
    form.nazwa.data = linialotnicza.nazwa
    form.kraj.data = linialotnicza.kraj

    return render_template('flights-airlines/flights-airlines-update.page.html',
                           form=form,
                           linialotnicza=linialotnicza)


@flights_bp.route('/airlines/delete', methods=['POST'])
def delete_airline():
    # get airline id from parameters
    parameters = request.form
    airline_id = parameters.get('airline_id', '')
    if not airline_id:
        flash("Błąd - nie podano linii lotniczej do usunięcia", category=c.ERROR)
        return redirect(url_for('flights.airlines'))

    # delete record from database
    flash_message, flash_category = oracle_db.delete_airline(airline_id)

    # flash and redirect to airlines page
    flash(flash_message, flash_category)
    return redirect(url_for('flights.airlines'))


# -------------------------------------------------------------------------------------------------------------------- #
# MANUFACTURERS

@flights_bp.route('/manufacturers')
def manufacturers():
    headers, manufacturers_list = oracle_db.select_manufacturers()

    return render_template('flights-manufacturers/flights-manufacturers.page.html',
                           manufacturers_data=manufacturers_list,
                           manufacturers_headers=headers)


@flights_bp.route('/manufacturers/new', methods=['GET', 'POST'])
def new_manufacturer():
    form = ManufacturersForm()
    if form.validate_on_submit():
        # POST

        flash_message, flash_category, flash_type = oracle_db.insert_manufacturer(form.nazwa.data, form.kraj.data)

        flash(flash_message, flash_category)
        if flash_type == c.PRODUCENT__UN:
            form.nazwa.data = ""
            return render_template("flights-manufacturers/flights-manufacturers-new.page.html",
                                   form=form)
        elif flash_category == c.ERROR:
            return redirect(url_for('flights.manufacturers'))
        else:
            return redirect(url_for('flights.manufacturers'))

    return render_template('flights-manufacturers/flights-manufacturers-new.page.html',
                           form=form)


@flights_bp.route('/manufacturers/update/<int:manufacturer_id>', methods=['GET', 'POST'])
def update_manufacturer(manufacturer_id: int):
    form = ManufacturersFormUpdate()

    # get producent from db
    producent = oracle_db.select_manufacturer(manufacturer_id)

    if form.validate_on_submit():
        # update manufacturer
        flash_message, flash_category, flash_type = oracle_db.update_manufacturer(manufacturer_id,
                                                                                  form.nazwa.data,
                                                                                  form.kraj.data)

        flash(flash_message, flash_category)
        if flash_type == c.PRODUCENT__UN:
            # duplicated nazwa in db
            form.nazwa.data = ""
            return render_template("flights-manufacturers/flights-manufacturers-update.page.html",
                                   form=form,
                                   producent=producent)
        elif flash_category == c.ERROR:
            return redirect(url_for('flights.manufacturers'))
        else:
            # success
            return redirect(url_for('flights.manufacturers'))

    # set default values on the form
    form.nazwa.data = producent.nazwa
    form.kraj.data = producent.kraj

    return render_template('flights-manufacturers/flights-manufacturers-update.page.html',
                           form=form,
                           producent=producent)


@flights_bp.route('/manufacturers/delete', methods=['POST'])
def delete_manufacturer():
    # get manufacturer id from parameters
    parameters = request.form
    man_id = parameters.get('manufacturer_id', '')
    if not man_id:
        flash("Błąd - nie podano producenta do usunięcia", category=c.ERROR)
        return redirect(url_for('flights.manufacturers'))

    flash_messsage, flash_category = oracle_db.delete_manufacturer(man_id)

    flash(flash_messsage, category=flash_category)
    return redirect(url_for('flights.manufacturers'))


# -------------------------------------------------------------------------------------------------------------------- #
# MODELS

@flights_bp.route('/models')
def models():
    headers, models_list = oracle_db.select_models_manufacturers()

    return render_template('flights-models/flights-models.page.html',
                           models_data=models_list,
                           headers=headers)


@flights_bp.route('/models/new', methods=['GET', 'POST'])
def new_model():
    form = ModelsForm()

    # get all manufacturers from database
    _, manufacturers_list = oracle_db.select_manufacturers(order=True)
    # insert manufacturers into form.producent.choices
    form.producent.choices = [(m.id, m.nazwa) for m in manufacturers_list]

    if form.validate_on_submit():
        # insert model
        flash_message, flash_category, flash_type = oracle_db.insert_model(form.nazwa.data,
                                                                           form.liczba_miejsc.data,
                                                                           form.predkosc.data,
                                                                           form.producent.data)

        flash(flash_message, flash_category)
        if flash_type == c.MODEL_UN_NAZWA:
            form.nazwa.data = ""
            return render_template('flights-models/flights-models-new.page.html',
                                   form=form)
        elif flash_category == c.ERROR:
            return redirect(url_for('flights.models'))
        else:
            return redirect(url_for('flights.models'))

    return render_template('flights-models/flights-models-new.page.html',
                           form=form)


@flights_bp.route('/models/update/<int:model_id>', methods=['GET', 'POST'])
def update_model(model_id):
    form = ModelsFormUpdate()

    # get model from db
    model = oracle_db.select_model_manufacturer(model_id)

    # get all manufacturers from database
    _, manufacturers_list = oracle_db.select_models_manufacturers(order=True)
    # insert manufacturers into form.producent.choices
    form.producent.choices = [(m.id, m.nazwa) for m in manufacturers_list]

    if form.validate_on_submit():
        # update model
        flash_message, flash_category, flash_type = oracle_db.update_model(model_id,
                                                                           form.nazwa.data,
                                                                           form.liczba_miejsc.data,
                                                                           form.predkosc.data,
                                                                           form.producent.data)

        flash(flash_message, flash_type)
        if flash_type == c.MODEL_UN_NAZWA:
            form.nazwa.data = ""
            return render_template("flights-models/flights-models-update.page.html",
                                   form=form,
                                   model=model)
        if flash_type == c.ERROR:
            return redirect(url_for('flights.models'))
        else:
            return redirect(url_for('flights.models'))

    # set default data on the form
    form.producent.default = model.producent.id
    form.process()
    form.nazwa.data = model.nazwa
    form.liczba_miejsc.data = model.liczba_miejsc
    form.predkosc.data = model.predkosc

    return render_template('flights-models/flights-models-update.page.html',
                           form=form,
                           model=model)


@flights_bp.route('/models/delete', methods=['POST'])
def delete_model():
    # get model id from parameters
    parameters = request.form
    model_id = parameters.get('model_id', '')
    if not model_id:
        flash("Błąd - nie podano modelu do usunięcia", category=c.ERROR)
        return redirect(url_for('flights.models'))

    # delete model from database
    flash_messsage, flash_category = oracle_db.delete_model(model_id)

    flash(flash_messsage, flash_category)
    return redirect(url_for('flights.models'))


@flights_bp.route('/arrivals', methods=['GET', 'POST'])
def arrivals():
    if request.method == 'POST':
        date_range = request.form['date']
        if " to " in date_range:
            # filter arrivals by dates
            sd, ed = date_range.split(" to ")
            start_date = datetime.datetime.strptime(sd, "%Y-%m-%d %H:%M")
            end_date = datetime.datetime.strptime(ed, "%Y-%m-%d %H:%M")
            headers, arrivals_list = oracle_db.select_arrivals_by_dates(start_date, end_date)
            return render_template('flights-arrivals/flights-arrivals.page.html',
                                   arrivals_data=arrivals_list,
                                   headers=headers,
                                   date=f"Od {sd} do {ed}")

        else:
            flash("Niepoprawny format daty", category=c.ERROR)

    # load all arrivals
    headers, arrivals_list = oracle_db.select_arrivals()
    return render_template('flights-arrivals/flights-arrivals.page.html',
                           arrivals_data=arrivals_list,
                           headers=headers)


@flights_bp.route('/flights/check-availability/<redirect_type>', methods=['POST'])
def check_availability_runway(redirect_type: str):
    # redirect type can be 'new' or 'update'

    # get timestamp
    parameters = request.form
    timestamp = parameters.get('timestamp', '')
    if not timestamp:
        flash("Błąd - nie podano daty odlotu", category="error")

    # parse datetime
    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    # check what runways are available on the given date
    runway_list = oracle_db.select_available_runways(timestamp, timestamp + datetime.timedelta(minutes=10))
    if runway_list:
        # store available runways and flight timestamp in session so other endpoints can use it
        session['available_runways'] = [runway.id for runway in runway_list]
        session['flight_timestamp'] = datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M")

        if redirect_type == 'new_arrival':
            return redirect(url_for('flights.new_arrival'))
        if redirect_type == 'update_arrival':
            arrival_id = request.args.get('arrival_id')
            if not arrival_id:
                flash("Brak podanego ID przylotu", c.ERROR)
                return redirect(url_for('flights.arrivals'))
            else:
                return redirect(url_for('flights.update_arrival', arrival_id=arrival_id))
        if redirect_type == 'new_departure':
            return redirect(url_for('flights.new_departure'))
        if redirect_type == 'update_departure':
            departure_id = request.args.get('departure_id')
            if not departure_id:
                flash("Brak podanego ID odlotu", c.ERROR)
                return redirect(url_for('flights.departure'))
            else:
                return redirect(url_for('flights.update_departure', departure_id=departure_id))
    else:
        flash("Brak dostępnych pasów startowych w tym terminie", c.WARNING)
        if 'arrival' in redirect_type:
            return redirect(url_for('flights.arrivals'))
        if 'departures' in redirect_type:
            return redirect(url_for('flights.departures'))
        return redirect(url_for('flights.main'))


@flights_bp.route('/arrivals/new', methods=['GET', 'POST'])
def new_arrival():
    form = ArrivalForm()

    # get all airports from database
    _, airports_list = oracle_db.select_airports(order=True)
    form.lotnisko.choices = [(airport.id, airport.nazwa) for airport in airports_list]

    # get all models from database
    _, models_list = oracle_db.select_models_manufacturers(order=True)
    form.model.choices = [(model.id, f"{model.producent.nazwa} {model.nazwa}") for model in models_list]

    # get all airline
    _, airline_list = oracle_db.select_airlines(order=True)
    form.linia_lotnicza.choices = [(airline.id, airline.nazwa) for airline in airline_list]

    # get available runways list from session
    runways_ids_list = session.get('available_runways', '')

    # get timestamp from session
    timestamp = session.get('flight_timestamp', '')

    if not runways_ids_list or not timestamp:
        flash("Wystąpił błąd. Do dodania przylotu użyj przeznaczonego do tego przycisku!", c.WARNING)
        return redirect(url_for('flights.arrivals'))
    else:
        # load runways from database using ids from session
        runways = oracle_db.select_runways_by_ids(runways_ids_list)
        form.pas.choices = [(runway.id, runway.nazwa) for runway in runways]
        # parse timestamp to datetime.datetime object
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    if form.validate_on_submit():
        flash_message, flash_category, _ = oracle_db.insert_arrival(form.linia_lotnicza.data,
                                                                    form.lotnisko.data,
                                                                    form.model.data,
                                                                    timestamp,
                                                                    form.liczba_pasazerow.data,
                                                                    form.pas.data)

        flash(flash_message, flash_category)
        if flash_category == c.ERROR:
            return render_template('flights-arrivals/flights-arrivals-new.page.html',
                                   form=form,
                                   timestamp=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                                   models=models_list)
        else:
            # if no error in inserting the data to the database - pop values from session and display arrivals table
            session.pop('available_runways')
            session.pop('flight_timestamp')
            return redirect(url_for('flights.arrivals'))

    return render_template('flights-arrivals/flights-arrivals-new.page.html',
                           form=form,
                           timestamp=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                           models=models_list)


@flights_bp.route('/arrivals/update/<int:arrival_id>', methods=['GET', 'POST'])
def update_arrival(arrival_id: int):
    # get available runways list from session
    runways_ids_list = session.get('available_runways', '')

    # get timestamp from session
    timestamp = session.get('flight_timestamp', '')

    if not runways_ids_list or not timestamp:
        flash("Błąd. Do aktualizacji przylotu użyj przeznaczonego do tego przycisku!", c.WARNING)
        return redirect(url_for('flights.arrivals'))

    # get arrival from db
    arrival = oracle_db.select_arrival(arrival_id)

    # parse timestamp to datetime.datetime object
    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    # check if arrival date is changed
    is_date_changed = arrival.data_przylotu > timestamp or arrival.data_przylotu < timestamp
    if not is_date_changed:
        form = ArrivalFormUpdateWithoutRunway()
    else:
        form = ArrivalFormUpdate()
        # load runways from database using ids from session
        runways = oracle_db.select_runways_by_ids(runways_ids_list)
        form.pas.choices = [(runway.id, runway.nazwa) for runway in runways]

    # get all airports from database
    _, airports_list = oracle_db.select_airports(order=True)
    form.lotnisko.choices = [(airport.id, airport.nazwa) for airport in airports_list]

    # get all models from database
    _, models_list = oracle_db.select_models_manufacturers(order=True)
    form.model.choices = [(model.id, f"{model.producent.nazwa} {model.nazwa}") for model in models_list]

    # get all airline
    _, airline_list = oracle_db.select_airlines(order=True)
    form.linia_lotnicza.choices = [(airline.id, airline.nazwa) for airline in airline_list]

    if form.validate_on_submit():
        # update arrival
        if is_date_changed:
            flash_message, flash_category, flash_type = oracle_db.update_arrival_and_reservations(arrival_id,
                                                                                                  form.linia_lotnicza.data,
                                                                                                  form.lotnisko.data,
                                                                                                  form.model.data,
                                                                                                  timestamp,
                                                                                                  form.liczba_pasazerow.data,
                                                                                                  form.pas.data)
        else:
            flash_message, flash_category, flash_type = oracle_db.update_arrival(arrival_id,
                                                                                 form.linia_lotnicza.data,
                                                                                 form.lotnisko.data,
                                                                                 form.model.data,
                                                                                 form.liczba_pasazerow.data)

        flash(flash_message, flash_category)
        if flash_category == c.ERROR:
            return render_template("flights-arrivals/flights-arrivals-update.page.html",
                                   form=form,
                                   arrival=arrival,
                                   models=models_list,
                                   timestamp_old=datetime.datetime.strftime(arrival.data_przylotu, "%Y-%m-%d %H:%M"),
                                   timestamp_new=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                                   is_date_changed=is_date_changed)
        else:
            # if no error in updating the data - pop values from session and display arrivals table
            session.pop('available_runways')
            session.pop('flight_timestamp')
            return redirect(url_for('flights.arrivals'))

    # set default data on the form
    form.lotnisko.default = arrival.lotnisko.id
    form.model.default = arrival.model.id
    form.linia_lotnicza.default = arrival.linia_lotnicza.id
    form.process()
    form.liczba_pasazerow.data = arrival.liczba_pasazerow

    return render_template('flights-arrivals/flights-arrivals-update.page.html',
                           form=form,
                           arrival=arrival,
                           models=models_list,
                           timestamp_old=datetime.datetime.strftime(arrival.data_przylotu, "%Y-%m-%d %H:%M"),
                           timestamp_new=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                           is_date_changed=is_date_changed)


@flights_bp.route('/arrivals/delete', methods=['POST'])
def delete_arrival():
    # get arrival id from parameters
    parameters = request.form
    arrival_id = parameters.get('arrival_id', '')
    if not arrival_id:
        flash("Błąd - nie podano przylotu do usunięcia", category=c.ERROR)
        return redirect(url_for('flights.arrivals'))

    # delete arrival from database
    flash_messsage, flash_category = oracle_db.delete_arrival(arrival_id)

    flash(flash_messsage, flash_category)
    return redirect(url_for('flights.arrivals'))


@flights_bp.route('/departures', methods=['GET', 'POST'])
def departures():
    if request.method == 'POST':
        date_range = request.form['date']
        if " to " in date_range:
            # filter arrivals by dates
            sd, ed = date_range.split(" to ")
            start_date = datetime.datetime.strptime(sd, "%Y-%m-%d %H:%M")
            end_date = datetime.datetime.strptime(ed, "%Y-%m-%d %H:%M")
            headers, departures_list = oracle_db.select_departures_by_dates(start_date, end_date)
            return render_template('flights-departures/flights-departures.page.html',
                                   departures_data=departures_list,
                                   headers=headers,
                                   date=f"Od {sd} do {ed}")

        else:
            flash("Niepoprawny format daty", category=c.ERROR)

    # load all arrivals
    headers, departures_list = oracle_db.select_departures()
    return render_template('flights-departures/flights-departures.page.html',
                           departures_data=departures_list,
                           headers=headers)


@flights_bp.route('/departures/new', methods=['GET', 'POST'])
def new_departure():
    class DFormPools(DepartureForm):
        pass

    # get all classes
    _, class_list = oracle_db.select_classes(order=True)
    for class_ in class_list:
        setattr(DFormPools,
                class_.nazwa,
                IntegerField(f'Podaj liczbę biletów w klasie {class_.nazwa}',
                             validators=[NumberRange(min=0, max=c.MAX_NUMBER_9)]))

    form = DFormPools()

    # get all airports from database
    _, airports_list = oracle_db.select_airports(order=True)
    form.lotnisko.choices = [(airport.id, airport.nazwa) for airport in airports_list]

    # get all models from database
    _, models_list = oracle_db.select_models_manufacturers(order=True)
    form.model.choices = [(model.id, f"{model.producent.nazwa} {model.nazwa}") for model in models_list]

    # get all airline
    _, airline_list = oracle_db.select_airlines(order=True)
    form.linia_lotnicza.choices = [(airline.id, airline.nazwa) for airline in airline_list]

    # get available runways list from session
    runways_ids_list = session.get('available_runways', '')

    # get timestamp from session
    timestamp = session.get('flight_timestamp', '')

    if not runways_ids_list or not timestamp:
        flash("Wystąpił błąd. Do dodania odlotu użyj przeznaczonego do tego przycisku!", c.WARNING)
        return redirect(url_for('flights.departures'))
    else:
        # load runways from database using ids from session
        runways = oracle_db.select_runways_by_ids(runways_ids_list)
        form.pas.choices = [(runway.id, runway.nazwa) for runway in runways]
        # parse timestamp to datetime.datetime object
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    if form.validate_on_submit():
        # check if provided number of seats is lesser than sum of number of tickets
        # if it is - render the template again with a warning
        available_seats = form.liczba_miejsc.data
        ticket_pools = {
            (class_.id, class_.nazwa): getattr(form, class_.nazwa).data if getattr(form, class_.nazwa).data > 0 else 0
            for class_ in class_list
        }
        if available_seats < sum(ticket_pools.values()):
            flash("Suma liczby biletów nie może przekraczać liczby dostępnych miejsc", c.WARNING)
            return render_template('flights-departures/flights-departures-new.page.html',
                                   form=form,
                                   timestamp=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                                   models=models_list,
                                   class_list=class_list)

        # insert data to db
        flash_message, flash_category, _ = oracle_db.insert_departure_and_ticket_pools(form.linia_lotnicza.data,
                                                                                       form.lotnisko.data,
                                                                                       form.model.data,
                                                                                       timestamp,
                                                                                       form.liczba_miejsc.data,
                                                                                       form.pas.data,
                                                                                       ticket_pools)

        flash(flash_message, flash_category)
        if flash_category == c.ERROR:
            return render_template('flights-departures/flights-departures-new.page.html',
                                   form=form,
                                   timestamp=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                                   models=models_list,
                                   class_list=class_list)
        else:
            # if no error in inserting the data to the database - pop values from session and display arrivals table
            session.pop('available_runways')
            session.pop('flight_timestamp')
            return redirect(url_for('flights.departures'))

    return render_template('flights-departures/flights-departures-new.page.html',
                           form=form,
                           timestamp=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                           models=models_list,
                           class_list=class_list)


@flights_bp.route('/departures/update/<int:departure_id>', methods=['GET', 'POST'])
def update_departure(departure_id: int):
    # get all classes and create inputs for them
    _, class_list = oracle_db.select_classes(order=True)

    # get available runways list from session
    runways_ids_list = session.get('available_runways', '')

    # get timestamp from session
    timestamp = session.get('flight_timestamp', '')

    if not runways_ids_list or not timestamp:
        flash("Błąd. Do aktualizacji odlotu użyj przeznaczonego do tego przycisku!", c.WARNING)
        return redirect(url_for('flights.departures'))

    # get departure from db
    departure = oracle_db.select_departure(departure_id)
    # parse timestamp to datetime.datetime object
    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    # check if departure date is changed
    is_date_changed = departure.data_odlotu > timestamp or departure.data_odlotu < timestamp
    if not is_date_changed:
        class DFormPools(DepartureFormUpdateWithoutRunway):
            pass
    else:
        class DFormPools(DepartureFormUpdate):
            pass

    # get all ticket pools for this departure
    _, ticket_pools_list = oracle_db.select_pools_by_departure(departure_id)
    for class_ in class_list:
        # if pool of this class already exists for this departure
        if class_.nazwa in [pool.klasa.nazwa for pool in ticket_pools_list]:
            for pool in ticket_pools_list:
                if class_.nazwa == pool.klasa.nazwa:
                    number_of_tickets = oracle_db.count_tickets_for_pool(pool.id)
                    setattr(DFormPools,
                            class_.nazwa,
                            IntegerField(f'Podaj liczbę biletów w klasie {class_.nazwa}',
                                         validators=[NumberRange(min=number_of_tickets, max=c.MAX_NUMBER_9),
                                                     InputRequired()]))
        # if pool of this class does not exist for this departure
        else:
            setattr(DFormPools,
                    class_.nazwa,
                    IntegerField(f'Podaj liczbę biletów w klasie {class_.nazwa}',
                                 validators=[NumberRange(min=0, max=c.MAX_NUMBER_9), InputRequired()]))

    form = DFormPools()
    if is_date_changed:
        # load runways from database using ids from session
        runways = oracle_db.select_runways_by_ids(runways_ids_list)
        form.pas.choices = [(runway.id, runway.nazwa) for runway in runways]

    # get all airports from database
    _, airports_list = oracle_db.select_airports(order=True)
    form.lotnisko.choices = [(airport.id, airport.nazwa) for airport in airports_list]

    # get all models from database
    _, models_list = oracle_db.select_models_manufacturers(order=True)
    form.model.choices = [(model.id, f"{model.producent.nazwa} {model.nazwa}") for model in models_list]

    # get all airline
    _, airline_list = oracle_db.select_airlines(order=True)
    form.linia_lotnicza.choices = [(airline.id, airline.nazwa) for airline in airline_list]

    if form.validate_on_submit():

        # check if provided number of seats is lesser than sum of number of tickets
        # if it is - render the template again with a warning
        available_seats = form.liczba_miejsc.data
        ticket_pools = {
            (class_.id, class_.nazwa): getattr(form, class_.nazwa).data if getattr(form, class_.nazwa).data > 0 else 0
            for class_ in class_list
        }
        if available_seats < sum(ticket_pools.values()):
            flash("Suma liczby biletów nie może przekraczać liczby dostępnych miejsc", c.WARNING)
            return render_template('flights-departures/flights-departures-update.page.html',
                                   form=form,
                                   departure=departure,
                                   models=models_list,
                                   class_list=class_list,
                                   timestamp_old=datetime.datetime.strftime(departure.data_odlotu, "%Y-%m-%d %H:%M"),
                                   timestamp_new=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                                   is_date_changed=is_date_changed)

        if is_date_changed:
            # update departure
            flash_message, flash_category, flash_type = oracle_db.update_departure_and_reservations(departure_id,
                                                                                                    form.linia_lotnicza.data,
                                                                                                    form.lotnisko.data,
                                                                                                    form.model.data,
                                                                                                    timestamp,
                                                                                                    form.liczba_miejsc.data,
                                                                                                    form.pas.data,
                                                                                                    ticket_pools)
        else:
            flash_message, flash_category, flash_type = oracle_db.update_departure(departure_id,
                                                                                   form.linia_lotnicza.data,
                                                                                   form.lotnisko.data,
                                                                                   form.model.data,
                                                                                   form.liczba_miejsc.data,
                                                                                   ticket_pools)

        flash(flash_message, flash_category)
        if flash_category == c.ERROR:
            return render_template("flights-departures/flights-departures-update.page.html",
                                   form=form,
                                   departure=departure,
                                   models=models_list,
                                   class_list=class_list,
                                   timestamp_old=datetime.datetime.strftime(departure.data_odlotu, "%Y-%m-%d %H:%M"),
                                   timestamp_new=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                                   is_date_changed=is_date_changed)
        else:
            # if no error in updating the data - pop values from session and display departures table
            session.pop('available_runways')
            session.pop('flight_timestamp')
            return redirect(url_for('flights.departures'))

    # set default data on the form
    form.lotnisko.default = departure.lotnisko.id
    form.model.default = departure.model.id
    form.linia_lotnicza.default = departure.linia_lotnicza.id
    form.process()
    form.liczba_miejsc.data = departure.liczba_miejsc
    for class_ in class_list:
        if class_.nazwa in [pool.klasa.nazwa for pool in ticket_pools_list]:
            for pool in ticket_pools_list:
                if class_.nazwa == pool.klasa.nazwa:
                    getattr(form, class_.nazwa).data = pool.ile_wszystkich_miejsc
        else:
            getattr(form, class_.nazwa).data = 0

    return render_template('flights-departures/flights-departures-update.page.html',
                           form=form,
                           departure=departure,
                           models=models_list,
                           class_list=class_list,
                           timestamp_old=datetime.datetime.strftime(departure.data_odlotu, "%Y-%m-%d %H:%M"),
                           timestamp_new=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                           is_date_changed=is_date_changed)


@flights_bp.route('/departures/delete', methods=['POST'])
def delete_departure():
    # get departure_id from parameters
    parameters = request.form
    departure_id = parameters.get('departure_id', '')
    if not departure_id:
        flash("Błąd - nie podano odlotu do usunięcia", category=c.ERROR)
        return redirect(url_for('flights.departure'))

    # delete arrival from database
    flash_messsage, flash_category = oracle_db.delete_departure(departure_id)

    flash(flash_messsage, flash_category)
    return redirect(url_for('flights.departures'))


@flights_bp.route('/departures/<int:departure_id>/pools')
def departure_pools(departure_id: int):
    # get departure's pools
    headers, pools = oracle_db.select_pools_by_departure(departure_id)
    return render_template('flights-departures/flights-departures-pools.page.html',
                           departure_id=departure_id,
                           headers=headers,
                           data=pools)


@flights_bp.route('/flights/<int:flight_id>/reservations')
def flight_reservations(flight_id: int):
    # get flight's reservations
    headers, reservations = oracle_db.select_reservations_by_flight(flight_id)
    flight_date = oracle_db.select_flight_date(flight_id)

    return render_template('flights-flights/flights-flight-reservations.page.html',
                           flight_id=flight_id,
                           flight_date=flight_date,
                           headers=headers,
                           data=reservations)


@flights_bp.route('/flights/<int:flight_id>/check-reservation-dates', methods=['POST'])
def flight_reservations_check_dates(flight_id: int):
    # get timestamp
    parameters = request.form
    timestamp = parameters.get('timestamp', '')
    if not timestamp:
        flash("Błąd - nie podano odpowiednich dat", c.ERROR)
        return redirect(url_for('flights.main'))

    sd, ed = timestamp.split(" to ")
    start_date = datetime.datetime.strptime(sd, "%Y-%m-%d %H:%M")
    end_date = datetime.datetime.strptime(ed, "%Y-%m-%d %H:%M")

    runway_list = oracle_db.select_available_runways(start_date, end_date)
    if runway_list:
        session['available_runways_reservations'] = [runway.id for runway in runway_list]
        session['start_time_reservations'] = datetime.datetime.strftime(start_date, "%Y-%m-%d %H:%M")
        session['end_time_reservations'] = datetime.datetime.strftime(end_date, "%Y-%m-%d %H:%M")
        return redirect(url_for('flights.flight_reservations_new', flight_id=flight_id))
    else:
        flash("Brak dostępnych pasów startowych w tym terminie", c.WARNING)
        return redirect(url_for('flights.flight_reservations', flight_id=flight_id))


@flights_bp.route('/flights/<int:flight_id>/reservations/new', methods=['GET', 'POST'])
def flight_reservations_new(flight_id: int):
    form = ReservationForm()

    # get available runways list from session
    runways_ids_list = session.get('available_runways_reservations', '')
    # get timestamp from session
    start_time_str = session.get('start_time_reservations', '')
    end_time_str = session.get('end_time_reservations', '')

    if not runways_ids_list or not start_time_str or not end_time_str:
        flash("Wystąpił błąd. Do dodania rezerwacji użyj przeznaczonego do tego przycisku!", c.WARNING)
        return redirect(url_for('flights.flight_reservations', flight_id=flight_id))
    else:
        # load runways from database using ids from session
        runways = oracle_db.select_runways_by_ids(runways_ids_list)
        form.pas.choices = [(runway.id, runway.nazwa) for runway in runways]
        # parse start_time_str and end_time_str to datetime.datetime object
        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")

    if form.validate_on_submit():
        flash_message, flash_category, _ = oracle_db.insert_reservation(start_time,
                                                                        end_time,
                                                                        flight_id,
                                                                        form.pas.data)

        flash(flash_message, flash_category)
        # pop values from session
        session.pop('available_runways_reservations')
        session.pop('start_time_reservations')
        session.pop('end_time_reservations')
        return redirect(url_for('flights.flight_reservations', flight_id=flight_id))

    return render_template('flights-flights/flights-flight-reservations-new.page.html',
                           form=form,
                           sd=start_time_str,
                           ed=end_time_str,
                           flight_id=flight_id)


@flights_bp.route('/flights/reservations/delete', methods=['POST'])
def flight_reservations_delete():
    # get ids from parameters
    parameters = request.form
    flight_id = parameters.get('flight_id', '')
    reservation_id = parameters.get('reservation_id', '')
    if not flight_id or not reservation_id:
        flash("Błąd - nie podano wystarczających danych", category=c.ERROR)
        return redirect(url_for('flights.main'))

    # delete reservation from database
    flash_messsage, flash_category = oracle_db.delete_reservation(reservation_id, flight_id)

    flash(flash_messsage, flash_category)
    return redirect(url_for('flights.flight_reservations', flight_id=flight_id))
