from flask import Blueprint, render_template, redirect, url_for, request, flash
from flaskr.forms import AirportForm, AirlineForm
from flaskr.models import Lotnisko, LiniaLotnicza
from flaskr import pool

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


@flights_bp.route('/airports')
def airports():
    db = pool.acquire()
    airports_cursor = db.cursor()
    airports_cursor.execute(
        "SELECT LOTNISKO_ID, NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE  FROM LOTNISKO")
    headers = [header[0] for header in airports_cursor.description]
    airports_list = []
    for airport in airports_cursor:
        airports_list.append(
            Lotnisko(
                _id=airport[0],
                nazwa=airport[1],
                miasto=airport[2],
                kraj=airport[3],
                iatacode=airport[4],
                icaocode=airport[5],
                longitude=airport[6],
                latitude=airport[7]
            )
        )
    airports_cursor.close()

    return render_template('flights-airports/flights-airports.html',
                           airports_data=airports_list,
                           airports_headers=headers)


@flights_bp.route('/airports/new', methods=['GET', 'POST'])
def new_airport():
    form = AirportForm()
    if form.validate_on_submit():
        # POST
        db = pool.acquire()
        cr = db.cursor()
        cr.execute("""INSERT INTO LOTNISKO
                      VALUES ((SELECT MAX(LOTNISKO_ID) FROM LOTNISKO)+1,
                              :nazwa,
                              :miasto,
                              :kraj,
                              :iatacode,
                              :icaocode,
                              :longitude,
                              :latitude)""",
                   nazwa=form.nazwa.data,
                   miasto=form.miasto.data,
                   kraj=form.kraj.data,
                   iatacode=form.iatacode.data,
                   icaocode=form.icaocode.data,
                   longitude=form.longitude.data,
                   latitude=form.latitude.data)
        db.commit()
        cr.close()
        flash("Pomyślnie dodano nowe lotnisko", category='success')
        return redirect(url_for('flights.airports'))
    else:
        # GET

        iatacode = request.args.get('iatacode')
        if iatacode:
            lotnisko = get_airport_from_api(iatacode)
        else:
            lotnisko = Lotnisko()

        return render_template('flights-airports/flights-airports-new.page.html',
                               form=form,
                               lotnisko=lotnisko)


@flights_bp.route('/airports/update/<int:airport_id>', methods=['GET', 'POST'])
def update_airport(airport_id: int):
    form = AirportForm()
    if form.validate_on_submit():
        # POST
        db = pool.acquire()
        cr = db.cursor()
        cr.execute("""UPDATE LOTNISKO
                      SET NAZWA = :nazwa,
                          MIASTO = :miasto,
                          KRAJ = :kraj,
                          IATACODE = :iatacode,
                          ICAOCODE = :icaocode,
                          LONGITUDE = :longitude,
                          LATITUDE = :latitude
                      WHERE LOTNISKO_ID = :id""",
                   nazwa=form.nazwa.data,
                   miasto=form.miasto.data,
                   kraj=form.kraj.data,
                   iatacode=form.iatacode.data,
                   icaocode=form.icaocode.data,
                   longitude=form.longitude.data,
                   latitude=form.latitude.data,
                   id=airport_id)
        db.commit()
        cr.close()
        flash("Pomyślna aktualizacja lotniska", category='neutral')
        return redirect(url_for('flights.airports'))

    db = pool.acquire()
    airports_update_cursor = db.cursor()
    airports_update_cursor.execute("""SELECT NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE
                                      FROM LOTNISKO
                                      WHERE LOTNISKO_ID = :id""",
                                   id=airport_id)
    data = airports_update_cursor.fetchone()
    airport_data = {
        'name': data[0],
        'city': data[1],
        'country': data[2],
        'iata': data[3],
        'icao': data[4],
        'longitude': data[5],
        'latitude': data[6]
    }
    return render_template('flights-airports/flights-airports-update.page.html',
                           form=form,
                           airport_data=airport_data)


@flights_bp.route('/airports/delete', methods=['POST'])
def delete_airport():
    # get airport id from parameters
    parameters = request.form
    airport_id = parameters.get('airport_id', '')
    if not airport_id:
        flash("Błąd - nie podano lotniska do usunięcia", category='error')
        return redirect(url_for('flights.airports'))
    db = pool.acquire()
    airports_delete_cursor = db.cursor()
    airports_delete_cursor.execute("DELETE FROM LOTNISKO WHERE LOTNISKO_ID = :id", id=airport_id)
    db.commit()
    airports_delete_cursor.close()
    flash("Pomyślnie usunięto lotnisko", category='success')
    return redirect(url_for('flights.airports'))


@flights_bp.route('/airlines')
def airlines():
    db = pool.acquire()
    airlines_cursor = db.cursor()
    airlines_cursor.execute("SELECT LINIALOTNICZA_ID, NAZWA, KRAJ FROM LINIALOTNICZA")
    headers = [header[0] for header in airlines_cursor.description]
    airlines_list = []
    for airline in airlines_cursor:
        airlines_list.append(
            LiniaLotnicza(
                _id=airline[0],
                nazwa=airline[1],
                kraj=airline[2]
            )
        )
    airlines_cursor.close()

    return render_template('flights-airlines/flights-airlines.page.html',
                           airlines_data=airlines_list,
                           airlines_headers=headers)


@flights_bp.route('/airlines/new', methods=['GET', 'POST'])
def new_airline():
    form = AirlineForm()
    if form.validate_on_submit():
        # POST
        db = pool.acquire()
        cr = db.cursor()
        cr.execute("""INSERT INTO LINIALOTNICZA
                           VALUES ((SELECT MAX(LINIALOTNICZA_ID) FROM LINIALOTNICZA)+1,
                                   :nazwa,
                                   :kraj)""",
                   nazwa=form.nazwa.data,
                   kraj=form.kraj.data)
        db.commit()
        cr.close()
        flash("Pomyślnie dodano nową linię lotniczą", category='success')
        return redirect(url_for('flights.airlines'))

    return render_template('flights-airlines/flights-airlines-new.page.html',
                           form=form, )
