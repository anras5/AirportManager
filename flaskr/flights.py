from flask import Blueprint, render_template, redirect, url_for, request
from flaskr.forms import NewAirportForm
from flaskr import pool
import requests
import os
import json

flights_bp = Blueprint('flights', __name__, url_prefix='/flights')


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
    airports_cursor.execute("SELECT * FROM LOTNISKO")
    headers = [header[0] for header in airports_cursor.description]
    data = airports_cursor.fetchall()
    airports_cursor.close()

    return render_template('flights-airports.page.html', airports_data=data, airports_headers=headers)


@flights_bp.route('/airports/new', methods=['GET', 'POST'])
def new_airport():
    form = NewAirportForm()
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
        return redirect(url_for('flights.airports'))
    else:
        # GET

        # get data from https://airport-info.p.rapidapi.com/airport into api_data dictionary
        api_key = os.environ.get('RAPID_API_AIRPORT_INFO_KEY')

        # prepare headers for request
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "airport-info.p.rapidapi.com"
        }

        # get iatacode from url parameter
        iatacode = request.args.get('iatacode')
        querystring = {"iata": iatacode}

        # send request only if iatacode provided in url parameter
        if iatacode:
            # send request
            response = requests.get(f'https://airport-info.p.rapidapi.com/airport', headers=headers, params=querystring).text
            api_data = json.loads(response)
            print(api_data)

            # handle case when wrong iatacode is provided in the url parameter
            if 'error' in api_data:
                error = api_data.get('error').get('text')
                if error == 'No airport found':
                    api_data = {}

        else:
            api_data = {}
        return render_template('flights-airports-new.page.html',
                               form=form,
                               api_data=api_data)


@flights_bp.route('/airports/delete/<int:airport_id>')
def delete_airport(airport_id):
    db = pool.acquire()
    airports_delete_cursor = db.cursor()
    airports_delete_cursor.execute("DELETE FROM LOTNISKO WHERE LOTNISKO_ID = :id", id=airport_id)
    db.commit()
    airports_delete_cursor.close()
    return redirect(url_for('flights.airports'))
