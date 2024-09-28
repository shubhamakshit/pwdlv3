import os

from flask import Blueprint, request, jsonify

from mainLogic.utils import glv_var
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import PREFS_FILE

api_prefs = Blueprint('api_prefs', __name__)

@api_prefs.route('/api/prefs/defaults.json', methods=['GET'])
@api_prefs.route('/prefs/defaults.json', methods=['GET'])
def get_prefs():
    import json as js
    file_path = PREFS_FILE
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404
    with open(file_path, 'r') as file:
        data = js.load(file)
    return jsonify(data), 200


@api_prefs.route('/api/update/defaults.json', methods=['POST'])
@api_prefs.route('/update/defaults.json', methods=['POST'])
def update_prefs():
    import json as js
    file_path = PREFS_FILE
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404
    try:
        data = request.json
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    with open(file_path, 'r') as file:
        data = js.load(file)
    data.update(request.json)
    with open(file_path, 'w') as file:
        js.dump(data, file, indent=4)

    ## recheck dependencies
    from mainLogic.utils.dependency_checker import re_check_dependencies
    re_check_dependencies()


    return jsonify(data), 200

