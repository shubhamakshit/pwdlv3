import os
from mainLogic.utils.gen_utils import delete_old_files
from mainLogic.main import Main
from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global


def download_pw_video(task_id, name, id, out_dir, client_id, session_id, progress_callback):
    # Create directories for client_id and session_id if they don't exist
    client_session_dir = os.path.join(out_dir, client_id, session_id)
    os.makedirs(client_session_dir, exist_ok=True)

    print(f"Downloading {name} with id {id} to {client_session_dir}")

    ch = CheckState()
    state = ch.checkup(Global.EXECUTABLES, directory="./", verbose=False)
    prefs = state['prefs']

    if 'webui-del-time' in prefs:
        del_time = int(prefs['webui-del-time'])
    else:
        del_time = 45

    delete_old_files(Global.api_webdl_directory, del_time)

    vsd = state['vsd']
    ffmpeg = state['ffmpeg']
    mp4d = state['mp4decrypt']
    verbose = True
    Main(id=id,
         name=f"{name}-{task_id}",
         token=prefs['token'],
         directory=client_session_dir, tmpDir="/*auto*/", vsdPath=vsd, ffmpeg=ffmpeg, mp4d=mp4d, verbose=verbose,
         progress_callback=progress_callback).process()
