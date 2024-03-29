import datetime
import json

from flask import Blueprint, render_template, request, flash, redirect, url_for

from flaskr import oracle_db
from flaskr.internal.helpers import constants as c

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    with open('airport.json', 'r') as file:
        coordinates = json.load(file)
        if not coordinates:
            coordinates = {"lon": 0, "lat": 0}
            json.dump(coordinates, file)

    if request.method == 'POST':
        date_range = request.form['date']
        if " to " in date_range:
            # filter arrivals by dates
            sd, ed = date_range.split(" to ")
            start_date = datetime.datetime.strptime(sd, "%Y-%m-%d %H:%M")
            end_date = datetime.datetime.strptime(ed, "%Y-%m-%d %H:%M")

            return render_template('dashboard-index.page.html',
                                   passengers_count=oracle_db.call_obsluzeni(start_date, end_date),
                                   date=f"od {sd} do {ed}",
                                   coordinates=coordinates)

        else:
            flash("Niepoprawny format daty", category=c.ERROR)

    return render_template('dashboard-index.page.html', coordinates=coordinates)


@dashboard_bp.route('/change', methods=['POST'])
def change():
    value = request.form.get('value')
    type = request.form.get('type')

    min_value = oracle_db.select_min_price()
    if type == '-' and min_value - int(value) < 0:
        flash("Błąd - nie można ustawić ceny na ujemną", c.ERROR)
        return redirect(url_for('dashboard.dashboard'))

    oracle_db.call_zmianaceny(value, type)
    flash("Pomyślna aktualizacja cen", c.SUCCESS)
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/airport', methods=['POST'])
def airport():
    lon = request.form.get('lon')
    lat = request.form.get('lat')
    with open('airport.json', 'w') as file:
        json.dump({"lon": lon, "lat": lat}, file)
    flash("Pomyślna aktualizacja lokacji lotniska", c.SUCCESS)
    return redirect(url_for('dashboard.dashboard'))
