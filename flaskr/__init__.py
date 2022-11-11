import os
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = 'authentication.do_login_user'

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    bootstrap.init_app(app)
    login_manager.init_app(app)


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
        return render_template('index.page.html')

    return app
