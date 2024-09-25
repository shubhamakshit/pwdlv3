import sys
import os
from mainLogic.error import errorList
from mainLogic.utils.glv import Global
from mainLogic.utils.os2 import SysFunc
from mainLogic.main import Main
from beta.shellLogic import shell
from mainLogic.startup.checkup import CheckState
from mainLogic.utils.gen_utils import generate_safe_folder_name
from mainLogic.utils import glv_var

# global variables
prefs = {}
glv = Global()

# hardcoding the list of executables required for the script to run
EXECUTABLES = glv_var.EXECUTABLES

def check_dependencies(directory, verbose):
    """Check if all dependencies are installed."""
    global prefs
    state = CheckState().checkup(EXECUTABLES, directory=directory, verbose=verbose)
    prefs = state['prefs']
    return state

def start_shell():
    """Start the shell if requested."""
    shell.main()

def start_webui(port, verbose):

    """Start the WebUI if requested."""
    from run import app
    if not prefs['webui']:
        Global.errprint("WebUI is not enabled in the preferences. Exiting ...")
        sys.exit(1)



    if 'webui-port' in prefs and not port == -1:
        port = prefs['webui-port']

    if port == -1:
        port = 5000



    if verbose:
        Global.hr()
        Global.dprint(f"Starting WebUI on port {port}")

    app.run(host="0.0.0.0", debug=True, port=port)

def download_process(id, name, state, verbose, simulate=False):
    """Process a single download or simulate the download."""
    if simulate:
        print("Simulating the download process. No files will be downloaded.")
        print(f"Id to be processed: {id}")
        print(f"Name to be processed: {name}")
        return

    try:
        Main(
            id=id,
            name=generate_safe_folder_name(name),
            directory=prefs['dir'],
            ffmpeg=state['ffmpeg'],
            vsdPath=state['vsd'],
            token=prefs['token'],
            random_id=prefs['random_id'],
            mp4d=state['mp4decrypt'],
            tmpDir=prefs['tmpDir'],
            verbose=verbose
        ).process()
    except Exception as e:
        if verbose:
            Global.hr()
            glv.errprint(f"Error: {e}")
        errorList['downloadFailed']['func'](name, id)
        sys.exit(errorList['downloadFailed']['code'])

def handle_csv_file(csv_file, state, verbose, simulate=False):
    """Handle processing of CSV file."""
    if not os.path.exists(csv_file):
        errorList['csvFileNotFound']['func'](csv_file)
        sys.exit(errorList['csvFileNotFound']['code'])

    if simulate:
        print("Simulating the download csv process. No files will be downloaded.")
        print(f"File to be processed: {csv_file}")
        return

    with open(csv_file, 'r') as f:
        for line in f:
            name, id = line.strip().split(',')
            name = generate_safe_folder_name(name)
            download_process(id, name, state, verbose)

def main(csv_file=None, id=None, name=None, directory=None, verbose=False, shell=False, webui_port=None, simulate=False):
    if shell:
        start_shell()

    glv.vout = verbose

    state = check_dependencies(directory, glv.vout)

    glv_var.vars['prefs'] = state['prefs']

    if webui_port is not None:
        start_webui(webui_port, glv.vout)

    if simulate:
        if csv_file:
            handle_csv_file(csv_file, state, glv.vout, simulate=True)
        elif id and name:
            download_process(id, name, state, glv.vout, simulate=True)
        return

    if csv_file and (id or name):
        print("Both csv file and id (or name) is provided. Unable to decide. Aborting! ...")
        sys.exit(3)

    if csv_file:
        handle_csv_file(csv_file, state, glv.vout)
    elif id and name:
        download_process(id, name, state, glv.vout)
    else:
        sys.exit(1)
