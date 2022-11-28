from flask import Blueprint, render_template, redirect, url_for, request
from flaskr import pool

ps_bp = Blueprint('passengers', __name__, url_prefix='/passengers')


@ps_bp.route('/')
def main():
    return render_template('passengers-index.page.html')
