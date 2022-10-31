import os
from flask import Flask
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    load_dotenv('./../.env')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    bootstrap.init_app(app)  # initialize bootstrap

    from . import flights  # import blueprint
    app.register_blueprint(flights.bp)  # register blueprint

    from flaskr.auth import authentication  # import blueprint
    app.register_blueprint(authentication)  # register blueprint



    return app
