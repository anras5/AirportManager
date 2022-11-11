from flask import Blueprint, render_template
from flaskr.authentication import isLoggedIn

from flaskr.db import get_db

flights_bp = Blueprint('flights', __name__, url_prefix='/flights')


@flights_bp.route('/')
def world_map():
    return render_template('flights-worldmap.page.html')


@flights_bp.route('/sql-check')
def sql_check():
    db = get_db()
    cr = db.cursor()
    cr.execute("SELECT * FROM LOTNISKO")
    x = cr.fetchall()
    return f"{x}"


@flights_bp.route('/airports')
def airports():
    db = get_db()
    airports_cursor = db.cursor()
    airports_cursor.execute("SELECT * FROM LOTNISKO")
    headers = [header[0] for header in airports_cursor.description]
    data = airports_cursor.fetchall()
    print(headers)
    print(data)
    print(isLoggedIn)
    return render_template('flights-airports.page.html', airports_data=data, airports_headers=headers)
