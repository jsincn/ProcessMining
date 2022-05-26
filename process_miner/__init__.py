from flask import Flask
from process_miner.api import api
from process_miner.views import views


def create_app():
    """
    Entry Point into our Flask App. Called when starting the webserver.
    :return: Flask App Object
    """
    # Create app and configure
    app = Flask(__name__, instance_relative_config=True)

    # TODO: PPM-7 Setup SQLite Database for further use

    # Register Blueprints (separate files) for the API and Frontend Routes
    app.register_blueprint(views)
    app.register_blueprint(api)
    return app
