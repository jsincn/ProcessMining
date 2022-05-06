import os

from flask import Flask

from process_miner.api import api
from process_miner.views import views


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(views)
    app.register_blueprint(api)
    return app
