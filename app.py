from flask import *
from flask_socketio import SocketIO
import threading
import subprocess
import sys
import io
import os
from utils.basicUtils import BasicUtils
import logger

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

def buildUrl(uuid, name, dlId):
        return f'/download/{uuid}*{name}*{dlId}'

def checkIfDownloadExists(uuid):
    global clients
    if uuid in clients:
        for downloadName in clients[uuid]['downloads']:
            if clients[uuid]['downloads'][downloadName]['status'] == 'downloading':
                return clients[uuid]['downloads'][downloadName]['dlId']
    return False

def downloadVideo(data):
    uuid = data['uuid']
    dlId = data['dlId']
    downloads = data['data']
    for download in downloads:

       

        # name of and id of the video to download
        name, id = download[0], download[1]

         # emit out the name of the file video being processed
        socketio.emit(f'file_being_processed-{uuid}', {"name": f'{name}'})
        
        # check if download already exists
        if name in clients[uuid]['downloads']:

            # if the video is already downloading, skip
            if clients[uuid]['downloads'][name]['status'] == 'downloading':
                print('Download already in progress for uuid: {uuid} name: {name} id: {id}\nSkipping!')
                return
            
            if clients[uuid]['downloads'][name]['id'] == id and clients[uuid]['downloads'][name]['dlId'] == dlId:
                print(f'Download already in progress for uuid: {uuid} name: {name} id: {id}\nSkipping!')
                return
                
            # if the video is already downloaded, redo 
            if clients[uuid]['downloads'][name]['status'] == 'done':
                print(f'Download already completed for uuid: {uuid} name: {name} id: {id}\nRedoing!')
        
        # add download to client's downloads
        clients[uuid]['downloads'][name] = {
            'name': name,
            'id': id,
            'status': 'downloading',
            'dlId': dlId
        }

        p = subprocess.Popen(['python','pwdl.py','--id',id,'--name',f'{name}-{dlId}','--dir',f'{DL_DIR}/{uuid}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        for line in iter(p.stdout.readline, b''):
            decoded_line = line.decode().strip()
            decoded_line = replace_ansi_with_html(decoded_line)
            socketio.emit(f'stdout-{uuid}', {'output': decoded_line})
        p.communicate()
     
    socketio.emit(f'dl_done-{uuid}', {
        "uuid": uuid,
        "dlId": dlId
    })
    for downloadName in clients[uuid]['downloads']:
        clients[uuid]['downloads'][downloadName]['status'] = 'done'
    
            
            
    print('Download complete')
    
@app.route('/download/<uuid>*<dlId>')
def completedDownload(uuid, dlId):
    global clients

    list_of_downloads = []
    logger.log(f'Client {uuid} completed download with dlId {dlId}')
    logger.log(f'Client: {clients}')
    for download_name in clients[uuid]['downloads']:
        if clients[uuid]['downloads'][download_name]['dlId'] == dlId:
            list_of_downloads.append([download_name,buildUrl(uuid, download_name, dlId)])

    return render_template('downloadCompletedFiles.html',list_of_downloads = list_of_downloads)

@app.route('/')
def index():
    return render_template('index.html', active_page = 'home')

@app.route('/download')
def download():
    return render_template('dl.html',active_page = 'downloader')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join')
def handle_join(data):
    global clients
    print('Client joined the server: ' + data['uuid'])

    uuid = data['uuid']

    if uuid not in clients:
        logger.log(f'New client {uuid} connected')
        clients[uuid] = {'socket': request.sid, 'downloads': {}}
        if os.path.exists(f'{DL_DIR}/{uuid}'):
            os.rmdir(f'{DL_DIR}/{uuid}')
        os.mkdir(f'{DL_DIR}/{uuid}')
    else:
        # client already has appeared before 
        # may have unfinished downloads
        dlId = checkIfDownloadExists(uuid)
        if dlId:
            print('Download exists')
            socketio.emit(f'dl_status-{uuid}', {'dlId':dlId})
        else:
            print('Download does not exist')
            socketio.emit(f'message-{uuid}', {"message": "No downloads in progress, Client Ready to download", 'uuid': uuid})

@socketio.on('download')
def handle_download(data):
    thread = threading.Thread(target=downloadVideo, args=(data,))
    thread.start()


@app.route('/download/<uuid>*<name>*<dlId>')
def download_video(uuid, name, dlId):
    base_path = DL_DIR
    filepath =  f'/{uuid}/{name}-{dlId}.mp4'
    return send_file(base_path + filepath,download_name=f'{name}.mp4', as_attachment=True)

@app.route('/check/video/<id>',methods=['GET'])
def checkStatus(id):
    from mainUtils.key import getKey
    if getKey(id):
        return "True"
    return "False"

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
