from flask import Blueprint, request, jsonify
from beta.api.api_dl import download_pw_video
from beta.api.mr_manager.boss_manager import Boss
from mainLogic.utils.gen_utils import generate_safe_folder_name

legacy_create_task = Blueprint('legacy_create_task', __name__)

client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR

@legacy_create_task.route('/api/create_task', methods=['POST'])
@legacy_create_task.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    client_id = data.get('client_id', 'anonymous')
    session_id = data.get('session_id', 'anonymous')
    id = data.get('id')
    name = data.get('name')

    # Generate safe names
    name = generate_safe_folder_name(name)

    if not id or not name:
        return jsonify({'error': 'id and name are required'}), 400

    args = {
        'name': name,
        'id': id,
        'out_dir': OUT_DIR,
        'client_id': client_id,
        'session_id': session_id
    }

    client_manager.add_client(client_id)
    client_manager.add_session(client_id, session_id)

    task_id = task_manager.create_task(client_id, session_id, download_pw_video, args)
    return jsonify({'task_id': task_id}), 202

