import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for

from flaskr import oracle_db
from flaskr.internal.helpers import constants as c

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        date_range = request.form['date']
        if " to " in date_range:
            # filter arrivals by dates
            sd, ed = date_range.split(" to ")
            start_date = datetime.datetime.strptime(sd, "%Y-%m-%d %H:%M")
            end_date = datetime.datetime.strptime(ed, "%Y-%m-%d %H:%M")

            return render_template('dashboard-index.page.html',
                                   passengers_count=oracle_db.call_obsluzeni(start_date, end_date),
                                   date=f"od {sd} do {ed}")

        else:
            flash("Niepoprawny format daty", category=c.ERROR)

    return render_template('dashboard-index.page.html')


@dashboard_bp.route('/change', methods=['POST'])
def change():
    value = request.form.get('value')
    type = request.form.get('type')
    oracle_db.call_zmianaceny(value, type)
    flash("Pomyślna aktualizacja cen", c.SUCCESS)
    return redirect(url_for('dashboard.dashboard'))
