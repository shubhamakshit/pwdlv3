import os
from mainLogic.utils.gen_utils import delete_old_files
from mainLogic.main import Main
from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global
from mainLogic.utils import glv_var


def download_pw_video(task_id, name, id, out_dir, client_id, session_id, progress_callback):
    # Create directories for client_id and session_id if they don't exist
    client_session_dir = os.path.join(out_dir, client_id, session_id)
    os.makedirs(client_session_dir, exist_ok=True)

    print(f"Downloading {name} with id {id} to {client_session_dir}")

    ch = CheckState()
    state = ch.checkup(glv_var.EXECUTABLES, directory="./", verbose=False,do_raise=True)
    prefs = state['prefs']

    if 'webui-del-time' in prefs:
        del_time = int(prefs['webui-del-time'])
    else:
        del_time = 45

    delete_old_files(glv_var.api_webdl_directory, del_time)

    vsd = state['vsd']
    ffmpeg = state['ffmpeg']

    mp4d = state['mp4decrypt']

    try:
        Main(id=id,
             name=f"{name}-{task_id}",
             token=prefs['token'],
             directory=client_session_dir, tmpDir="/*auto*/", vsdPath=vsd, ffmpeg=ffmpeg, mp4d=mp4d, verbose=False,
             progress_callback=progress_callback).process()
    except Exception as e:
        Global.errprint(f"Download failed for {name} with id {id}. (Main.process exited)")
        Global.errprint(f"Error: {e}")
        return False
