from flask import Flask, render_template, url_for, redirect, flash
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from flaskr.internal.db.OracleDB import OracleDB

bootstrap = Bootstrap()
oracle_db = OracleDB()


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    bootstrap.init_app(app)

    # dotenv file
    load_dotenv('./../.env')

    # test config
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from flaskr.internal.modules import flights
    app.register_blueprint(flights.flights_bp)

    from flaskr.internal.modules import tickets
    app.register_blueprint(tickets.tickets_bp)

    from flaskr.internal.modules import runways
    app.register_blueprint(runways.runways_bp)

    # general routes
    @app.route('/')
    def home():
        return render_template('index.page.html')

    @app.errorhandler(404)
    def page_not_found(error):
        flash("Taka strona nie istnieje!", "error")
        return redirect(url_for('home'))

    return app
