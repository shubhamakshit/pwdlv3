import re
import os
import time
import json
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

def generate_safe_folder_name(folder_name: str) -> str:
    """
    Generate a safe folder name by replacing spaces with underscores and removing special characters.
    
    Parameters:
    folder_name (str): The original folder name.
    
    Returns:
    str: The safe folder name.
    """
    # Replace spaces with underscores
    safe_name = folder_name.replace(' ', '_')
    
    # Remove any characters that are not alphanumeric or underscores
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', safe_name)
    
    return safe_name

def download_pw_video(task_id, name, id, out_dir, progress_callback):

    name = generate_safe_folder_name(name)
    

    print(f"Downloading {name} with id {id} to {out_dir}")

    ch = CheckState()
    state = ch.checkup(Global.EXECUTABLES, directory="./", verbose=True)
    prefs = state['prefs']

    if 'webui-del-time' in prefs:
        del_time = prefs['webui-del-time']
    else:
        del_time = 45

    print(f"Deleting files older than {del_time} minutes in {OUT_DIR}")

    # delete all files in webdl directory which are older than 45 mins
    try:
        BasicUtils.delete_old_files(OUT_DIR, int(del_time))
    except Exception as e:
        Global.errprint(f"Could not delete files in {OUT_DIR}")
        Global.errprint(f"Error: {e}")

    vsd = state['vsd']
    ffmpeg = state['ffmpeg']
    mp4d = state['mp4decrypt']
    verbose = True
    Main(id=id,
         name=f"{name}-{task_id}",
         token=prefs['token'],
         directory=out_dir, tmpDir="/*auto*/", vsdPath=vsd, ffmpeg=ffmpeg, mp4d=mp4d, verbose=verbose, progress_callback=progress_callback).process()

@app.route('/api/create_task',methods=['POST'])
@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    id = data.get('id')
    name = data.get('name')

    # if name contains space etc replace it with _ (and no consequetive _)
    name = "_".join(name.split())

    if not id or not name:
        return jsonify({'error': 'id and name are required'}), 400

    args ={
        'name' : name,
        'id' : id,
        'out_dir' : OUT_DIR
    }

    task_id = task_manager.create_task(download_pw_video, args)
    return jsonify({'task_id': task_id}), 202

@app.route('/api/progress/<task_id>', methods=['GET'])
@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    progress = task_manager.get_progress(task_id)
    return jsonify(progress), 200

@app.route('/api/get-file/<task_id>/<name>', methods=['GET'])
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

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/util')
def json():
    return render_template('util.html')
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
    return jsonify({'message': 'Hello, World!'}), 200

@app.route('/api/prefs/defaults.json', methods=['GET'])
@app.route('/prefs/defaults.json', methods=['GET'])
def get_prefs():
    file_path = Global.PREFERENCES_FILE
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404
    data = None
    with open(file_path, 'r') as file:
        import json as js_on
        data = js_on.loads(file.read())
    return jsonify(data), 200

@app.route('/api/update/defaults.json', methods=['POST'])
@app.route('/update/defaults.json', methods=['POST'])
def update_prefs():
    file_path = Global.PREFERENCES_FILE
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404
    try:
        data = request.json
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    with open(file_path, 'r') as file:
        import json as js_on
        data = js_on.loads(file.read())
    data.update(request.json)
    with open(file_path, 'w') as file:
        import json as js_on
        js_on.dump(data, file, indent=4)
    return jsonify(data), 200

@app.route('/prefs')
def prefs():
    return render_template('prefs.html')

if __name__ == '__main__':app.run(debug=True,port=7680)
