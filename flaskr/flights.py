from flask import Blueprint, render_template, redirect, url_for, request, flash
from flaskr.forms import AirportForm, AirlinesForm, ManufacturersForm
from flaskr.models import Lotnisko, LiniaLotnicza, Producent
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


# -------------------------------------------------------------------------------------------------------------------- #
# AIRPORTS

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

    return render_template('flights-airports/flights-airports.page.html',
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
        flash("Pomyślna aktualizacja lotniska", category='success')
        return redirect(url_for('flights.airports'))

    db = pool.acquire()
    airports_update_cursor = db.cursor()
    airports_update_cursor.execute("""SELECT NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE
                                      FROM LOTNISKO
                                      WHERE LOTNISKO_ID = :id""",
                                   id=airport_id)
    data = airports_update_cursor.fetchone()
    lotnisko = Lotnisko(nazwa=data[0],
                        miasto=data[1],
                        kraj=data[2],
                        iatacode=data[3],
                        icaocode=data[4],
                        longitude=data[5],
                        latitude=data[6])
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
    db = pool.acquire()
    airports_delete_cursor = db.cursor()
    airports_delete_cursor.execute("DELETE FROM LOTNISKO WHERE LOTNISKO_ID = :id", id=airport_id)
    db.commit()
    airports_delete_cursor.close()
    flash("Pomyślnie usunięto lotnisko", category='success')
    return redirect(url_for('flights.airports'))


# -------------------------------------------------------------------------------------------------------------------- #
# AIRLINES

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
    form = AirlinesForm()
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
                           form=form)


@flights_bp.route('/airlines/update/<int:airlines_id>', methods=['GET', 'POST'])
def update_airline(airlines_id: int):
    form = AirlinesForm()
    if form.validate_on_submit():
        # POST
        db = pool.acquire()
        cr = db.cursor()
        cr.execute("""UPDATE LINIALOTNICZA
                      SET NAZWA = :nazwa,
                          KRAJ = :kraj
                      WHERE LINIALOTNICZA_ID = :id""",
                   nazwa=form.nazwa.data,
                   kraj=form.kraj.data,
                   id=airlines_id)
        db.commit()
        cr.close()
        flash("Pomyślna aktualizacja linii lotniczej", category='success')
        return redirect(url_for('flights.airlines'))

    db = pool.acquire()
    airports_update_cursor = db.cursor()
    airports_update_cursor.execute("""SELECT NAZWA, KRAJ
                                      FROM LINIALOTNICZA
                                      WHERE LINIALOTNICZA_ID = :id""",
                                   id=airlines_id)
    data = airports_update_cursor.fetchone()
    linialotnicza = LiniaLotnicza(nazwa=data[0],
                                  kraj=data[1])
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
    db = pool.acquire()
    airlines_delete_cursor = db.cursor()
    airlines_delete_cursor.execute("DELETE FROM LINIALOTNICZA WHERE LINIALOTNICZA_ID = :id", id=airline_id)
    db.commit()
    airlines_delete_cursor.close()

    # flash and redirect to airlines page
    flash("Pomyślnie usunięto linię lotniczą", category='success')
    return redirect(url_for('flights.airlines'))


# -------------------------------------------------------------------------------------------------------------------- #
# AIRLINES

@flights_bp.route('/manufacturers')
def manufacturers():
    db = pool.acquire()
    manufacturers_cursor = db.cursor()
    manufacturers_cursor.execute("SELECT PRODUCENT_ID, NAZWA, KRAJ FROM PRODUCENT")
    headers = [header[0] for header in manufacturers_cursor.description]
    manufacturers_list = []
    for manufacturer in manufacturers_cursor:
        manufacturers_list.append(
            Producent(
                _id=manufacturer[0],
                nazwa=manufacturer[1],
                kraj=manufacturer[2]
            )
        )
    manufacturers_cursor.close()

    return render_template('flights-manufacturers/flights-manufacturers.page.html',
                           manufacturers_data=manufacturers_list,
                           manufacturers_headers=headers)


@flights_bp.route('/manufacturers/new', methods=['GET', 'POST'])
def new_manufacturer():
    form = ManufacturersForm()
    if form.validate_on_submit():
        # POST
        db = pool.acquire()
        cr = db.cursor()
        cr.execute("""INSERT INTO PRODUCENT
                           VALUES ((SELECT MAX(PRODUCENT_ID) FROM PRODUCENT)+1,
                                   :nazwa,
                                   :kraj)""",
                   nazwa=form.nazwa.data,
                   kraj=form.kraj.data)
        db.commit()
        cr.close()
        flash("Pomyślnie dodano nowego producenta", category='success')
        return redirect(url_for('flights.manufacturers'))

    return render_template('flights-manufacturers/flights-manufacturers-new.page.html',
                           form=form)


@flights_bp.route('/manufacturers/update/<int:manufacturer_id>', methods=['GET', 'POST'])
def update_manufacturer(manufacturer_id: int):
    form = ManufacturersForm()
    if form.validate_on_submit():
        # POST
        db = pool.acquire()
        cr = db.cursor()
        cr.execute("""UPDATE PRODUCENT
                      SET NAZWA = :nazwa,
                          KRAJ = :kraj
                      WHERE PRODUCENT_ID = :id""",
                   nazwa=form.nazwa.data,
                   kraj=form.kraj.data,
                   id=manufacturer_id)
        db.commit()
        cr.close()
        flash("Pomyślna aktualizacja producenta", category='success')
        return redirect(url_for('flights.manufacturers'))

    db = pool.acquire()
    cr = db.cursor()
    cr.execute("""SELECT NAZWA, KRAJ
                    FROM PRODUCENT
                   WHERE PRODUCENT_ID = :id""",
               id=manufacturer_id)
    data = cr.fetchone()
    producent = Producent(nazwa=data[0],
                          kraj=data[1])
    return render_template('flights-manufacturers/flights-manufacturers-update.page.html',
                           form=form,
                           producent=producent)
