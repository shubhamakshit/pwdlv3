import os

from flask import Blueprint, jsonify, send_file, render_template
from beta.api.mr_manager.boss_manager import Boss
from mainLogic.error import debugger
from mainLogic.utils.glv_var import ENDPOINTS_NAME

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
    task_info = client_manager.get_progress(task_id)

    if not task_info or task_info['status'] == 'not found':
        debugger.error(f"File not found:")
        return render_template("error.html",task_id=task_id,reason="not_found"), 404

    client_session_dir = os.path.join(OUT_DIR, task_info['client_id'], task_info['session_id'])

    file_path = os.path.join(client_session_dir, f"{name}-{task_id}.mp4")

    def dict_to_tuple(d):
        return tuple(d.values())

    if not os.path.exists(file_path):
        debugger.error(f"File not found: {file_path}")
        return render_template("error.html",task_id=task_id,video_details=client_manager.get_task(task_id),reason='deleted'), 404

    return send_file(file_path, as_attachment=True,download_name=f"{name}.mp4")

@dl_and_post_dl.route(ENDPOINTS_NAME.GET_PVT_FILE_FOR_A_CLIENT(), methods=['GET'])
@dl_and_post_dl.route('/get-private-file/<client_id>/<name>', methods=['GET'])
def get_private_file(client_id, name):
    client_session_dir = os.path.join(OUT_DIR, client_id)

    file_path = os.path.join(str(client_session_dir), name)
    if not os.path.exists(file_path):
        debugger.error(f"File not found: {file_path}")
        return render_template("error.html",reason='deleted'), 404

    return send_file(file_path, as_attachment=True,download_name=name)
