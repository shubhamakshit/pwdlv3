import time
from flask import Flask, jsonify, request
from beta.api.task_manager import TaskManager  # Assuming the TaskManager class is in task_manager.py
from mainLogic.main import Main
from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global

app = Flask(__name__)
task_manager = TaskManager()

def example_task(id, name, progress_callback):

    ch = CheckState()
    prefs = ch.checkup(Global.EXECUTABLES, directory="./", verbose=True)
    nm3 = prefs['nm3']
    ffmpeg = prefs['ffmpeg']
    mp4d = prefs['mp4decrypt']
    verbose = True
    Main(id=id, name=name, directory="./", tmpDir="/*auto*/", nm3Path=nm3, ffmpeg=ffmpeg, mp4d=mp4d, verbose=verbose, progress_callback=progress_callback).process()


@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    id = data.get('id')
    name = data.get('name')

    if not id or not name:
        return jsonify({'error': 'id and name are required'}), 400


    task_id = task_manager.create_task(example_task,id, name )
    return jsonify({'task_id': task_id}), 202

@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    progress = task_manager.get_progress(task_id)
    return jsonify(progress), 200

if __name__ == '__main__':
    app.run(debug=True)
