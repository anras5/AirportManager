import cx_Oracle
from flask import Blueprint, render_template

runways_bp = Blueprint('runways', __name__, url_prefix='/runways')


@runways_bp.route('/')
def main():
    return render_template('runways-index.page.html')
