import cx_Oracle
from flask import Blueprint, render_template, redirect, url_for, request

from flaskr import pool
from flaskr.models import Pas

runways_bp = Blueprint('runways', __name__, url_prefix='/runways')


@runways_bp.route('/')
def main():
    return render_template('runways-index.page.html')


# -------------------------------------------------------------------------------------------------------------------- #
# RUNWAYS

@runways_bp.route('/runways')
def runways():
    db = pool.acquire()
    cr = db.cursor()
    cr.execute("SELECT PAS_ID, DLUGOSC, OPIS FROM PAS")
    headers = [header[0] for header in cr.description]
    runways_list = []
    for runway in cr:
        runways_list.append(
            Pas(runway[0],
                runway[1],
                runway[2])
        )
    cr.close()

    return render_template('runways-runways/runways-runways.page.html',
                           data=runways_list,
                           headers=headers)


@runways_bp.route('/runways/new', methods=['GET', 'POST'])
def new_runway():
    return redirect(url_for('runways.main'))


@runways_bp.route('/runways/update/<int:runway_id>', methods=['GET', 'POST'])
def update_runway(runway_id: int):
    return redirect(url_for('runways.main'))


@runways_bp.route('/runways/delete', methods=['POST'])
def delete_runway():
    print(request.form.get('runway_id'))
    return redirect(url_for('runways.main'))
