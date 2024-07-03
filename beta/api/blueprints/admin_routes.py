import os.path

from flask import Blueprint, request, jsonify, send_file
from beta.api.mr_manager.boss_manager import Boss
from mainLogic.utils.os2 import SysFunc

client_manager = Boss.client_manager
task_manager = Boss.task_manager

admin = Blueprint('admin', __name__)

@admin.route('/api/webdl')
@admin.route('/webdl')
def webdl():
    return jsonify(SysFunc.list_files_and_folders(Boss.OUT_DIR)), 200

@admin.route('/api/webdl/webdl')
@admin.route('/webdl/webdl')
def webdl_copy():
    return webdl()

@admin.route('/api/webdl/<path:subpath>')
@admin.route('/webdl/<path:subpath>')
def webdl_subpath(subpath):
    return jsonify(SysFunc.list_files_and_folders(os.path.join(Boss.OUT_DIR, subpath))), 200

@admin.route('/api/delete/<path:subpath>')
@admin.route('/delete/<path:subpath>')
def delete_subpath(subpath):
    path_file_or_folder = os.path.join(Boss.OUT_DIR, subpath)

    if os.path.exists(path_file_or_folder):
        try:
            SysFunc.delete_file_or_folder(path_file_or_folder)
            return jsonify({'success': f'{subpath} deleted'}), 200
        except Exception as e:
            return jsonify({'error': f"Could not delete {e}"}), 404
    else:
        return jsonify({'error': 'file not found'}), 404

@admin.route('/api/get/<path:subpath>')
@admin.route('/get/<path:subpath>')
def get_subpath(subpath):
    path_to_file = os.path.join(Boss.OUT_DIR, subpath)
    if os.path.exists(path_to_file):
        return send_file(path_to_file, as_attachment=True, download_name=os.path.basename(path_to_file))
    else:
        return jsonify({'error': 'file not found'}), 404
