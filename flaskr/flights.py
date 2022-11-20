from flask import Blueprint, render_template, session, redirect, url_for, request
from flaskr.db import get_db
from flaskr.forms import NewAirportForm

flights_bp = Blueprint('flights', __name__, url_prefix='/flights')


@flights_bp.route('/')
def main():
    return render_template('flights-index.page.html')


@flights_bp.route('/map')
def world_map():
    try:
        if not session["user"] or not session["admin"]:
            return redirect(url_for('authentication.do_login_user'))
    except:
        pass
    return render_template('flights-worldmap.page.html')


@flights_bp.route('/airports')
def airports():
    db = get_db()
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
        pass
    return render_template('flights-airports-new.page.html', form=form)


@flights_bp.route('/airports/delete/<int:airport_id>')
def delete_airport(airport_id):
    db = get_db()
    airports_delete_cursor = db.cursor()
    airports_delete_cursor.execute("DELETE FROM LOTNISKO WHERE LOTNISKO_ID = :id", id=airport_id)
    db.commit()
    airports_delete_cursor.close()
    return redirect(url_for('flights.airports'))
