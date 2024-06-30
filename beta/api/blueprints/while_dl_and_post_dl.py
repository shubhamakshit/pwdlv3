import os

from flask import Blueprint, jsonify, send_file
from beta.api.mr_manager.boss_manager import Boss

client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR

dl_and_post_dl = Blueprint('dl_and_post_dl', __name__)



@dl_and_post_dl.route('/api/progress/<task_id>', methods=['GET'])
@dl_and_post_dl.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    progress = task_manager.get_progress(task_id)
    return jsonify(progress), 200


@dl_and_post_dl.route('/api/get-file/<task_id>/<name>', methods=['GET'])
@dl_and_post_dl.route('/get-file/<task_id>/<name>', methods=['GET'])
def get_file(task_id, name):
    task_info = task_manager.get_progress(task_id)

    if task_info['status'] == 'not found':
        return jsonify({'error': 'file not found'}), 404

    client_session_dir = os.path.join(OUT_DIR, task_info['client_id'], task_info['session_id'])

    file_path = os.path.join(client_session_dir, f"{name}-{task_id}.mp4")
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404

    return send_file(file_path, as_attachment=True,download_name=f"{name}.mp4")