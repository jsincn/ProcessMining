from flask import (
    Blueprint, request
)

from process_miner.miners.miningHandler import MiningHandler

api = Blueprint('api', __name__, template_folder='templates', url_prefix="/api")


@api.route('/')
def show():
    return "Should not be accessed!"


@api.route('upload', methods=['POST'])
def upload_xes():
    print("Received Request on /api/upload")
    if 'file' not in request.files:
        return "File not attached", 400
    file = request.files['file']
    algorithm = request.values['algorithm']
    lifecycleTransition = request.values['lifecycleTransition']
    mining_handler = MiningHandler(algorithm, file, lifecycleTransition)
    mining_handler.run()
    if mining_handler.success:
        response = mining_handler.prepare_response()
        print("Successfully completed request")
    else:
        response = mining_handler.logger.get_logs(), 500
        print("Failed to complete request")
        print("CAUSE")
        print(response)
        print("ENDCAUSE")
    return response
