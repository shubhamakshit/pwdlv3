from flask import Blueprint, request, jsonify
from beta.api.mr_manager.boss_manager import Boss
from mainLogic.big4.decrypt.key import LicenseKeyFetcher

client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR

client_info = Blueprint('client_info', __name__)

@client_info.route('/api/session/<client_id>/<session_id>', methods=['GET'])
@client_info.route('/session/<client_id>/<session_id>', methods=['GET'])
def get_session(client_id, session_id):
    # if client_id == 'anonymous' or session_id == 'anonymous':
    #     return jsonify({'error': 'Access to anonymous sessions is not allowed'}), 403

    client_info = client_manager.get_client_info(client_id)
    if client_info and session_id in client_info['sessions']:
        session_info = client_info['sessions'][session_id]
        return jsonify(session_info), 200
    else:
        return jsonify({'error': 'Session not found'}), 404


@client_info.route('/api/client/<client_id>', methods=['GET'])
@client_info.route('/client/<client_id>', methods=['GET'])
def get_client(client_id):

    client_info = client_manager.get_client_info(client_id)
    if client_info:
        return jsonify(client_info), 200
    else:
        return jsonify({'error': 'Client not found'}), 404


@client_info.route('/api/session/<client_id>/<session_id>/active', methods=['GET'])
@client_info.route('/session/<client_id>/<session_id>/active', methods=['GET'])
def check_session_active(client_id, session_id):
    if client_id == 'anonymous' or session_id == 'anonymous':
        return jsonify({'error': 'Access to anonymous sessions is not allowed'}), 403

    client_info = client_manager.get_client_info(client_id)
    if client_info and session_id in client_info['sessions']:
        session_info = client_info['sessions'][session_id]
        tasks = session_info['tasks']
        for task_id in tasks:
            status = tasks[task_id]['status']
            if status == 'running':
                return jsonify({'active': True}), 200
        return jsonify({'active': False}), 200
    else:
        return jsonify({'error': 'Session not found'}), 404


def is_session_active(client_id, session_id):
    if client_id == 'anonymous' or session_id == 'anonymous':
        return {'error': 'Access to anonymous sessions is not allowed'}, 403

    client_info = client_manager.get_client_info(client_id)
    if client_info and session_id in client_info['sessions']:
        session_info = client_info['sessions'][session_id]
        tasks = session_info['tasks']
        for task_id, task in tasks.items():
            if task['status'] == 'running':
                return {'active': True}, 200
        return {'active': False}, 200
    else:
        return {'error': 'Session not found'}, 404


@client_info.route('/api/client/<client_id>/active_sessions', methods=['GET'])
@client_info.route('/client/<client_id>/active_sessions', methods=['GET'])
def get_active_sessions(client_id):
    if client_id == 'anonymous':
        return jsonify({'error': 'Access to anonymous client is not allowed'}), 403

    client_info = client_manager.get_client_info(client_id)

    if client_info:
        active_sessions = []
        for session_id in client_info['sessions']:
            session_data = is_session_active(client_id, session_id)
            if session_data[1] != 200:
                return jsonify(session_data[0]), session_data[1]
            active = session_data[0].get('active', False)

            if active:
                active_sessions.append(session_id)
        return jsonify({"active_sessions": active_sessions}), 200
    return jsonify({'error': 'Client not found'}), 404



@client_info.route('/api/key/vid_id', methods=['GET'])
@client_info.route('/key/vid_id', methods=['GET'])
def get_key():
    vid_id = request.args.get('vid_id')
    token = request.args.get('token')
    if not vid_id or not token:
        return jsonify({'error': 'vid_id and token are required'}), 400
    fetcher = LicenseKeyFetcher(token)
    key = fetcher.get_key(vid_id)
    return jsonify({'key': key}), 200
