import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, session

from flaskr.internal.helpers.forms import AirportForm, AirlinesForm, ManufacturersForm, ModelsForm, ArrivalForm
from flaskr.internal.helpers.models import Lotnisko
from flaskr import oracle_db
from flaskr.internal.helpers import constants as c
from flaskr.internal.helpers.constants import ERROR

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
    # try:
    #     if not session["user"] or not session["admin"]:
    #         return redirect(url_for('authentication.do_login_user'))
    # except:
    #     pass
    return render_template('flights-worldmap.page.html')


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
        # TODO: catching unique keys exceptions
        if flash_category == c.ERROR:
            return render_template('flights-airports/flights-airports-new.page.html',
                                   form=form)
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
    form = AirportForm()

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
        # TODO: catching unique keys exceptions
        if flash_category == c.ERROR:
            return render_template('flights-airports/flights-airports-update.page.html',
                                   form=form,
                                   lotnisko=lotnisko)
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
        flash("Błąd - nie podano lotniska do usunięcia", category='error')
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
    form = AirlinesForm()

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
        elif flash_category == ERROR:
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
        flash("Błąd - nie podano linii lotniczej do usunięcia", category='error')
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

        if flash_category == c.ERROR:
            flash(flash_message, category=flash_category)
            return render_template("flights-manufacturers/flights-manufacturers-new.page.html",
                                   form=form)
        else:
            flash(flash_message, category=flash_category)
            return redirect(url_for('flights.manufacturers'))

    return render_template('flights-manufacturers/flights-manufacturers-new.page.html',
                           form=form)


@flights_bp.route('/manufacturers/update/<int:manufacturer_id>', methods=['GET', 'POST'])
def update_manufacturer(manufacturer_id: int):
    form = ManufacturersForm()

    # get producent from db
    producent = oracle_db.select_manufacturer(manufacturer_id)

    if form.validate_on_submit():
        # update manufacturer
        flash_message, flash_category, flash_type = oracle_db.update_manufacturer(manufacturer_id,
                                                                                  form.nazwa.data,
                                                                                  form.kraj.data)

        flash(flash_message, flash_category)
        # TODO: catching unique keys error
        if flash_category == ERROR:
            return render_template("flights-manufacturers/flights-manufacturers-update.page.html",
                                   form=form,
                                   producent=producent)
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
        flash("Błąd - nie podano producenta do usunięcia", category='error')
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
        # TODO catching unique keys error
        if flash_category == c.ERROR:
            return render_template('flights-models/flights-models-new.page.html',
                                   form=form)
        else:
            return redirect(url_for('flights.models'))

    return render_template('flights-models/flights-models-new.page.html',
                           form=form)


@flights_bp.route('/models/update/<int:model_id>', methods=['GET', 'POST'])
def update_model(model_id):
    form = ModelsForm()

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
        if flash_type == c.ERROR:
            return render_template("flights-models/flights-models-update.page.html",
                                   form=form,
                                   model=model)
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
        flash("Błąd - nie podano modelu do usunięcia", category='error')
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


@flights_bp.route('/arrivals/check-availability', methods=['POST'])
def check_availability_runway():
    # get timestamp
    parameters = request.form
    timestamp = parameters.get('timestamp', '')
    if not timestamp:
        flash("Błąd - nie podano daty odlotu", category="error")

    # parse datetime
    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

    # check what runways are available on the given date
    runway_list = oracle_db.select_available_runways(timestamp)
    if runway_list:
        session['available_runways'] = [runway.id for runway in runway_list]
        session['arrival_timestamp'] = datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M")
        return redirect(url_for('flights.new_arrival'))
    else:
        flash("Brak dostępnych pasów startowych w tym terminie", c.WARNING)
        return redirect(url_for('flights.arrivals'))


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
    timestamp = session.get('arrival_timestamp', '')

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
            session.pop('arrival_timestamp')
            return redirect(url_for('flights.arrivals'))

    return render_template('flights-arrivals/flights-arrivals-new.page.html',
                           form=form,
                           timestamp=datetime.datetime.strftime(timestamp, "%Y-%m-%d %H:%M"),
                           models=models_list)


@flights_bp.route('/arrivals/update/<int:arrival_id>', methods=['GET', 'POST'])
def update_arrival(arrival_id: int):
    return redirect(url_for('flights.arrivals'))


@flights_bp.route('/arrivals/delete', methods=['POST'])
def delete_arrival():
    return redirect(url_for('flights.arrivals'))
