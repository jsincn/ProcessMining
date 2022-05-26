from datetime import datetime

from flask import (
    Blueprint, request
)
from werkzeug.utils import secure_filename
import timeit

from process_miner.miners.miningHandler import MiningHandler
from process_miner.miners.xesparser import XESParser
from process_miner.miners.alpha import AlphaMiner

api = Blueprint('api', __name__, template_folder='templates', url_prefix="/api")


@api.route('/')
def show():
    return "Should not be accessed!"


@api.route('upload', methods=['POST'])
def upload_xes():
    if 'file' not in request.files:
        return "File not attached", 400
    file = request.files['file']
    algorithm = request.values['algorithm']
    mining_handler = MiningHandler(algorithm, file)
    mining_handler.run()
    if mining_handler.success:
        response = mining_handler.prepare_response()
        print(response)
    else:
        response = {}
    return response
