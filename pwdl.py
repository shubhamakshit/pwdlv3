import argparse
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


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='PhysicsWallah M3u8 parser.')
    parser.add_argument('--csv-file', type=str, help='Input csv file. Legacy Support too.')
    parser.add_argument('--id', type=str,
                        help='PhysicsWallh Video Id for single usage. Incompatible with --csv-file. Must be used with --name')
    parser.add_argument('--name', type=str,
                        help='Name for the output file. Incompatible with --csv-file. Must be used with --id')
    parser.add_argument('--dir', type=str, help='Output Directory')
    parser.add_argument('--verbose', action='store_true', help='Verbose Output')
    parser.add_argument('--shell', action='store_true', help='Start the shell')
    parser.add_argument('--webui', nargs='?', const=-1, type=int, help='Start the Webui')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--simulate', action='store_true',
                        help='Simulate the download process. No files will be downloaded.')
    return parser.parse_args()


def start_shell():
    """Start the shell if requested."""
    shell.main()


def check_dependencies(directory, verbose):
    """Check if all dependencies are installed."""
    global prefs
    state = CheckState().checkup(EXECUTABLES, directory=directory, verbose=verbose)
    prefs = state['prefs']
    return state


def start_webui(port, verbose):
    """Start the WebUI if requested."""
    from run import app
    if not prefs['webui']:
        Global.errprint("WebUI is not enabled in the preferences. Exiting ...")
        sys.exit(1)

    if 'webui-port' in prefs:
        port = prefs['webui-port']

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


def main():
    args = parse_arguments()

    if args.shell:
        start_shell()

    glv.vout = args.verbose

    state = check_dependencies(args.dir, glv.vout)

    if args.webui:
        start_webui(args.webui, glv.vout)

    if args.simulate:
        if args.csv_file:
            handle_csv_file(args.csv_file, state, glv.vout, simulate=True)
        elif args.id and args.name:
            download_process(args.id, args.name, state, glv.vout, simulate=True)
        sys.exit(0)

    if args.csv_file and (args.id or args.name):
        print("Both csv file and id (or name) is provided. Unable to decide. Aborting! ...")
        sys.exit(3)

    if args.csv_file:
        handle_csv_file(args.csv_file, state, glv.vout)
    elif args.id and args.name:
        download_process(args.id, args.name, state, glv.vout)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
