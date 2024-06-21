import os
import time
from flask import Flask, jsonify, request, send_from_directory, send_file, render_template
from beta.api.task_manager import TaskManager  # Assuming the TaskManager class is in task_manager.py
from mainLogic.big4.decrypt.key import LicenseKeyFetcher
from mainLogic.main import Main
from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global
from mainLogic.utils.basicUtils import BasicUtils
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

task_manager = TaskManager()

OUT_DIR = Global.api_webdl_directory

try:
    if not os.path.exists(OUT_DIR): os.makedirs(OUT_DIR)
except Exception as e:
    Global.errprint(f"Could not create output directory {OUT_DIR}")
    Global.sprint(f"Defaulting to './' ")
    Global.errprint(f"Error: {e}")
    OUT_DIR = './'

def setup_directory():
    pass
def download_pw_video(task_id, name, id, out_dir, progress_callback):

    print(f"Downloading {name} with id {id} to {out_dir}")

    ch = CheckState()
    state = ch.checkup(Global.EXECUTABLES, directory="./", verbose=True)
    prefs = state['prefs']
    vsd = state['vsd']
    ffmpeg = state['ffmpeg']
    mp4d = state['mp4decrypt']
    verbose = True
    Main(id=id,
         name=f"{name}-{task_id}",
         token=prefs['token'],
         directory=out_dir, tmpDir="/*auto*/", vsdPath=vsd, ffmpeg=ffmpeg, mp4d=mp4d, verbose=verbose, progress_callback=progress_callback).process()


@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    id = data.get('id')
    name = data.get('name')

    if not id or not name:
        return jsonify({'error': 'id and name are required'}), 400

    args ={
        'name' : name,
        'id' : id,
        'out_dir' : OUT_DIR
    }

    task_id = task_manager.create_task(download_pw_video, args)
    return jsonify({'task_id': task_id}), 202

@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    progress = task_manager.get_progress(task_id)
    return jsonify(progress), 200

@app.route('/get-file/<task_id>/<name>', methods=['GET'])
def get_file(task_id,name):
    file = BasicUtils.abspath(f"{OUT_DIR}/{name}-{task_id}.mp4")
    if not os.path.exists(file):
        return jsonify({'error': 'file not found'}), 404
    return send_file( f"{file}",download_name=name+"."+os.path.basename(file).split('.')[-1] ,as_attachment=True), 200

@app.route('/key/vid_id', methods=['GET'])
def get_key():
    vid_id = request.args.get('vid_id')
    token = request.args.get('token')
    if not vid_id or not token:
        return jsonify({'error': 'vid_id and token are required'}), 400
    fetcher = LicenseKeyFetcher(token)
    key = fetcher.get_key(vid_id)
    return jsonify({'key': key}), 200

@app.route('/util')
def json():
    return render_template('util.html')
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
    return jsonify({'message': 'Hello, World!'}), 200

if __name__ == '__main__':app.run(debug=True,port=7680)
