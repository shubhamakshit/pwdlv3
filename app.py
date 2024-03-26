from flask import *
from flask_socketio import SocketIO
import threading
import subprocess
import sys
import io
import os
from basicUtils import BasicUtils

# Set PYTHONUNBUFFERED environment variable
os.environ['PYTHONUNBUFFERED'] = '1'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DEBUG'] = True  # Add this line to enable debug mode
socketio = SocketIO(app)
out_orig = sys.stdout
out = io.StringIO()
DL_DIR = f'{BasicUtils.abspath(os.path.dirname(__file__))}/webdl'
clients = {}

def replace_ansi_with_html(text):
    # replace ansi formatting with html (colorama uses)
    text = text.replace('\x1b[0m', '</span>')
    text = text.replace('\x1b[31m', '<span style="color: red;">')
    text = text.replace('\x1b[32m', '<span style="color: green;">')
    text = text.replace('\x1b[33m', '<span style="color: yellow;">')
    text = text.replace('\x1b[34m', '<span style="color: blue;">')
    text = text.replace('\x1b[35m', '<span style="color: magenta;">')
    text = text.replace('\x1b[36m', '<span style="color: cyan;">')
    text = text.replace('\x1b[37m', '<span style="color: white;">')
    return text

def checkIfDownloadExists(uuid):
    global clients
    if uuid in clients:
        for dl in clients[uuid]['downloads']:
            if dl['status'] == 'downloading':
                return dl
    return False

def downloadVideo(data):
    uuid = data.get('uuid')
    id = data.get('id')
    name = data.get('name')
    dlId = data.get('dlId')
    p = subprocess.Popen(['python','pwdl.py','--id',id,'--name',f'{name}-{dlId}','--dir',f'{DL_DIR}/{uuid}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in iter(p.stdout.readline, b''):
        decoded_line = line.decode().strip()
        decoded_line = replace_ansi_with_html(decoded_line)
        socketio.emit(f'stdout-{uuid}', {'output': decoded_line})
    p.communicate()
    socketio.emit(f'dl_done-{uuid}', checkIfDownloadExists(uuid))
    for downloads in clients[uuid]['downloads']:
        if downloads['dlId'] == dlId:
            clients[uuid]['downloads'].remove(downloads)
    print('Download complete')
    


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/download')
def download():
    return render_template('dl.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join')
def handle_join(data):
    global clients
    print('Client joined the server: ' + data['uuid'])

    uuid = data['uuid']

    if uuid not in clients:
        clients[uuid] = {'socket': request.sid, 'downloads': []}
        if os.path.exists(f'{DL_DIR}/{uuid}'):
            os.rmdir(f'{DL_DIR}/{uuid}')
        os.mkdir(f'{DL_DIR}/{uuid}')
    else:
        # client already has appeared before 
        # may have unfinished downloads
        print(clients[uuid])
        unfinished = checkIfDownloadExists(uuid)
        if unfinished:
            print('Download exists')
            socketio.emit(f'dl_status-{uuid}', unfinished)
        else:
            print('Download does not exist')
            socketio.emit(f'message-{uuid}', {"message": "No downloads in progress, Client Ready to download", 'uuid': uuid})

@socketio.on('download')
def handle_download(data):
    uuid = data['uuid']
    if checkIfDownloadExists(uuid):
        print('Download exists')
        socketio.emit(f'dl_status-{uuid}', {'uuid': uuid})
        return
    clients[uuid]['downloads'].append({'status': 'downloading',
                                        'id': data['id'],
                                        'name': data['name'],
                                        'dlId': data['dlId']
                                       })
    threading.Thread(target=downloadVideo, args=(data,)).start()

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/download/<uuid>*<name>*<dlId>')
def download_video(uuid, name, dlId):
    base_path = DL_DIR
    filepath =  f'/{uuid}/{name}-{dlId}.mp4'
    return send_file(base_path + filepath,download_name=f'{name}.mp4', as_attachment=True)

if __name__ == '__main__':
    socketio.run(app)
