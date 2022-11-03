from flask import Blueprint, render_template
from flaskr.db import get_db

flights_bp = Blueprint('flights', __name__, url_prefix='/flights')


@flights_bp.route('/')
def world_map():
    return render_template('flights-worldmap.page.html')


@flights_bp.route('/sql-check')
def sql_check():
    db = get_db()
    cr = db.cursor()
    cr.execute("SELECT * FROM PRODUCENT")
    x = cr.fetchall()
    return f"{x}"
