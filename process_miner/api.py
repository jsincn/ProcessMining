from datetime import datetime

from flask import (
    Blueprint, request
)
from werkzeug.utils import secure_filename
import timeit
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
    # print(file.read())
    response = {}
    start = timeit.default_timer()
    parser = XESParser()
    if parser.read_xes(file.read()):
        traces_df = parser.get_parsed_logs()
        miner = AlphaMiner()
        miner.run(traces_df)
        stop = timeit.default_timer()
        response['locations'] = miner.get_location_csv()
        response['transitions'] = miner.get_transition_csv()
        response['filename'] = secure_filename(file.filename)
        response['runtime'] = stop - start
        response['algorithm'] = "Alpha Miner"
        response['cache'] = False
        response['timestamp'] = datetime.now()
        response['meta'] = miner.get_meta()
        print(miner.get_location_csv())
        print(miner.get_transition_csv())
    return response
