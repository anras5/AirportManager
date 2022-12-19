from flask import Blueprint, render_template, redirect, url_for, request
from flaskr.models import Pas
from flaskr import oracle_db


runways_bp = Blueprint('runways', __name__, url_prefix='/runways')


@runways_bp.route('/')
def main():
    return render_template('runways-index.page.html')


# -------------------------------------------------------------------------------------------------------------------- #
# RUNWAYS

@runways_bp.route('/runways')
def runways():
    headers, runways_list = oracle_db.select_runways()

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
