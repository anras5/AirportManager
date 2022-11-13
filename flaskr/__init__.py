import os
from flask import Flask, render_template, session, url_for, redirect
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    bootstrap.init_app(app)

    load_dotenv('./../.env')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from . import authentication
    app.register_blueprint(authentication.at_bp)

    from . import flights
    app.register_blueprint(flights.flights_bp)

    @app.route('/')
    def home():
        print('XDDD')
        try:
            if not session["user"] or not session["admin"]:
                return redirect(url_for('authentication.do_login_user'))
        except:
            pass
        return render_template('index.page.html')

    return app
