from flask import (
    Blueprint, request
)
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
    parser = XESParser()
    if parser.read_xes(file.read()):
        traces_df = parser.get_parsed_logs()
        miner = AlphaMiner()
        miner.run(traces_df)
        print(miner.get_location_csv())
        print(miner.get_transition_csv())
    return "File Processing"