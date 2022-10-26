from flask import Blueprint, render_template
from flaskr.db import get_db

bp = Blueprint('flights', __name__, url_prefix='/flights')


@bp.route('/')
def world_map():
    return render_template('index.page.html')


@bp.route('/sql-check')
def sql_check():
    db = get_db()
    cr = db.cursor()
    cr.execute("SELECT * FROM PRODUCENT")
    x = cr.fetchall()
    return f"{x}"
