# main.py

import sys
import os
import csv # Added import

from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global
from mainLogic.utils.gen_utils import generate_safe_folder_name
from mainLogic.main import Main
from beta.shellLogic import shell
from mainLogic.utils import glv_var
from mainLogic.error import errorList, CsvFileNotFound
from mainLogic.utils.glv_var import debugger

# Global variables
glv = Global()

# hardcoding the list of executables required for the script to run
EXECUTABLES = glv_var.EXECUTABLES


def start_shell():
    """Start the shell if requested."""
    shell.main()


def start_webui(port, verbose, no_reloader=False, ssl=False, ssl_cert=None, ssl_key=None, ssl_password=None):
    """Start the WebUI if requested."""
    from run import app

    if 'webui-port' in prefs and port == -1 and port <= glv_var.MINIMUM_PORT:
        port = prefs['webui-port']

    if port == -1:
        port = 5000

    # SSL Configuration
    ssl_context = None
    if ssl:
        try:
            import ssl as ssl_module
            
            # Default cert and key paths
            if not ssl_cert:
                ssl_cert = 'cert.pem'
            if not ssl_key:
                ssl_key = 'key.pem'
            
            # Check if cert files exist
            if not os.path.exists(ssl_cert):
                debugger.error(f"SSL certificate file not found: {ssl_cert}")
                debugger.info("You can generate a self-signed certificate with:")
                debugger.info(f"openssl req -x509 -newkey rsa:4096 -nodes -out {ssl_cert} -keyout {ssl_key} -days 365")
                sys.exit(1)
            
            if not os.path.exists(ssl_key):
                debugger.error(f"SSL private key file not found: {ssl_key}")
                sys.exit(1)
            
            # Create SSL context
            if ssl_password:
                # Load encrypted key with password
                ssl_context = ssl_module.SSLContext(ssl_module.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(ssl_cert, ssl_key, ssl_password)
            else:
                # Simple context for unencrypted keys
                ssl_context = (ssl_cert, ssl_key)
            
            if verbose:
                debugger.success(f"SSL enabled with cert: {ssl_cert}, key: {ssl_key}")
                
        except ImportError:
            debugger.error("SSL module not available. Cannot enable HTTPS.")
            sys.exit(1)
        except Exception as e:
            debugger.error(f"SSL configuration error: {e}")
            sys.exit(1)

    protocol = "HTTPS" if ssl else "HTTP"
    if verbose:
        Global.hr()
        debugger.debug(f"Starting WebUI on {protocol}://0.0.0.0:{port}")

    debug_mode = True if verbose else False
    use_reloader = not no_reloader if debug_mode else False
    
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=debug_mode, 
        use_reloader=use_reloader,
        threaded=True,
        ssl_context=ssl_context
    )


def download_process(
        id, name,batch_name,topic_name,lecture_url,
        state, verbose, simulate=False
):
    """Process a single download or simulate the download."""
    if simulate:
        print("Simulating the download process. No files will be downloaded.")
        print(f"Id to be processed: {id}")
        print(f"Name to be processed: {name}")
        return

    try:
        Main(
            id=id,
            name=generate_safe_folder_name(name), # Name is already made safe before this call in the new handle_csv_file
            batch_name=batch_name,
            topic_name=topic_name,
            lecture_url=lecture_url,
            directory=prefs['dir'],
            ffmpeg=state['ffmpeg'],
            token=prefs['token'],
            random_id=prefs['random_id'],
            mp4d=state['mp4decrypt'],
            tmpDir= state['tmpDir'] if 'tmpDir' in state else prefs['tmpDir'],
            verbose=verbose
        ).process()
    except Exception as e:
        if verbose:
            Global.hr()
            glv.errprint(f"Error: {e}")
        errorList['downloadFailed']['func'](name, id)
        sys.exit(errorList['downloadFailed']['code'])


def handle_csv_file(csv_file, state, batch_name_param, verbose, simulate=False):
    """Handle processing of CSV file with or without headers, including new arguments."""
    try:
        if not os.path.exists(csv_file):
            raise CsvFileNotFound(csv_file)
    except CsvFileNotFound as e:
        debugger.error(e)
        e.exit()

    if simulate:
        print("Simulating the download csv process. No files will be downloaded.")
        print(f"File to be processed: {csv_file}")
        return

    with open(csv_file, 'r', newline='', encoding='utf-8') as f: # Added encoding
        sniffer = csv.Sniffer()
        try:
            sample = f.read(2048)  # Read a sample to detect header
            has_header = sniffer.has_header(sample)
        except csv.Error: # Handles cases like empty file or unparseable sample
            has_header = False
        f.seek(0)  # Rewind to start of file

        reader = None
        if has_header:
            reader = csv.DictReader(f)
        else:
            reader = csv.reader(f)

        # Define a mapping for flexible header names (lowercase) if DictReader is used.
        header_aliases = {
            'id': ['id', 'lecture id', 'video id'],
            'name': ['name', 'lecture_name', 'lecture name', 'title'],
            'batch_name': ['batch_name', 'batch name', 'batch'],
            'topic_name': ['topic_name', 'topic name', 'topic'],
            'lecture_url': ['lecture_url', 'lecture url', 'url', 'video_url']
        }

        for i, row_data in enumerate(reader):
            csv_id = None
            csv_name = None
            # Default to batch_name_param, can be overridden by CSV
            csv_batch_name = batch_name_param
            csv_topic_name = None
            csv_lecture_url = None

            current_line_num = reader.line_num if hasattr(reader, 'line_num') else i + 1

            if has_header:  # row_data is a dict from DictReader
                # Helper to get value from possible header names, case-insensitively
                def get_val_from_dict(r_dict, key_aliases_list, default_val=None):
                    r_dict_lower_keys = {str(k).lower().strip(): v for k, v in r_dict.items()}
                    for alias in key_aliases_list: # alias is already lowercase
                        if alias in r_dict_lower_keys:
                            val = r_dict_lower_keys[alias]
                            return val.strip() if isinstance(val, str) else val
                    return default_val

                csv_id = get_val_from_dict(row_data, header_aliases['id'])
                csv_name = get_val_from_dict(row_data, header_aliases['name'])
                
                val_batch_name_csv = get_val_from_dict(row_data, header_aliases['batch_name'])
                if val_batch_name_csv is not None and val_batch_name_csv != '':
                     csv_batch_name = val_batch_name_csv # Override with CSV value if present and non-empty
                
                csv_topic_name = get_val_from_dict(row_data, header_aliases['topic_name'])
                csv_lecture_url = get_val_from_dict(row_data, header_aliases['lecture_url'])

            else:  # row_data is a list from csv.reader
                num_cols = len(row_data)
                if num_cols < 2:  # Need at least id and name
                    if verbose:
                        debugger.warning(f"Skipping line {current_line_num} in CSV: not enough columns (ID and Name are required). Line: {row_data}")
                    continue
                
                csv_id = row_data[0].strip() if row_data[0] else None
                csv_name = row_data[1].strip() if row_data[1] else None
                
                # Optional fields by position; use batch_name_param if CSV field is missing or empty
                val_batch_name_csv_list = row_data[2].strip() if num_cols > 2 and row_data[2] and row_data[2].strip() else None
                if val_batch_name_csv_list is not None:
                    csv_batch_name = val_batch_name_csv_list # Override with CSV value if present and non-empty
                
                csv_topic_name = row_data[3].strip() if num_cols > 3 and row_data[3] and row_data[3].strip() else None
                csv_lecture_url = row_data[4].strip() if num_cols > 4 and row_data[4] and row_data[4].strip() else None

            # --- Post-extraction Validation and Processing ---
            if not csv_id or not csv_name:
                if verbose:
                    debugger.warning(f"Skipping line {current_line_num} in CSV: 'id' or 'name' is missing or empty. Parsed values: ID='{csv_id}', Name='{csv_name}'")
                continue
            
            # Ensure optional fields that are empty strings become None
            if csv_topic_name == '': csv_topic_name = None
            if csv_lecture_url == '': csv_lecture_url = None
            if csv_batch_name == '': csv_batch_name = batch_name_param # If CSV gives empty batch, revert to param
            if csv_batch_name is None and batch_name_param is not None and batch_name_param != '': # Ensure param is used if csv_batch_name ended up None
                csv_batch_name = batch_name_param


            final_safe_name = generate_safe_folder_name(csv_name)

            if verbose:
                debugger.info(f"Preparing from CSV line {current_line_num}: ID='{csv_id}', Name='{csv_name}' (Folder: '{final_safe_name}'), Batch='{csv_batch_name}', Topic='{csv_topic_name}', URL='{csv_lecture_url}'")

            download_process(
                id=csv_id,
                name=final_safe_name, # Already safe
                batch_name=csv_batch_name,
                topic_name=csv_topic_name,
                lecture_url=csv_lecture_url,
                state=state,
                verbose=verbose
            )


def main(csv_file=None,
         id=None, name=None,batch_name=None,topic_name=None,lecture_url=None,
         directory=None, verbose=False, shell=False, webui_port=None, no_reloader=False, tmp_dir=None,
         new_downloader=False,
         simulate=False, ssl=False, ssl_cert=None, ssl_key=None, ssl_password=None):
    global prefs  # Use global keyword to modify global prefs

    if shell:
        start_shell()

    glv.vout = verbose

    ch = CheckState()
    state = ch.checkup(EXECUTABLES, directory=directory,tmp_dir=tmp_dir, verbose=verbose, do_raise=False)
    prefs = state['prefs']

    glv_var.vars['prefs'] = prefs

    if webui_port is not None:
        start_webui(webui_port, glv.vout, no_reloader=no_reloader, ssl=ssl, ssl_cert=ssl_cert, ssl_key=ssl_key, ssl_password=ssl_password)

    if simulate:
        if csv_file:
            # Pass batch_name from main args to handle_csv_file for simulation context
            handle_csv_file(csv_file, state, batch_name, glv.vout, simulate=True)
        elif id and name:
            # For single simulated download, batch_name, topic_name, lecture_url from args are used
            download_process(id, name, batch_name, topic_name, lecture_url, state, glv.vout, simulate=True)
        return

    if csv_file and (id or name):
        print("Both csv file and id (or name) is provided. Unable to decide. Aborting! ...")
        sys.exit(3)

    if csv_file:
        # Pass batch_name from main args to handle_csv_file
        # This batch_name acts as a default if not specified in the CSV
        handle_csv_file(csv_file, state, batch_name, glv.vout, simulate=False) # simulate is False here
    elif id and name:
        download_process(
            id=id,
            name=name, # generate_safe_folder_name is called inside download_process if called directly, or handled if from csv
            batch_name=batch_name,
            topic_name=topic_name,
            lecture_url=lecture_url,
            state=state,
            verbose=glv.vout
        )
    else:
        # If not shell, not webui, not csv, and not id/name, it's an invalid invocation or just setup.
        # Depending on desired behavior, could exit or inform user.
        # Original code exited with 1 if no specific action was taken.
        # Let's refine this: if no action command like shell, webui, csv or id/name, then what?
        # If only setup was done (e.g. directory check) it might be okay.
        # But if user expected an action, this is an issue.
        # The original `sys.exit(1)` implies an action was expected but not specified.
        # For now, keeping behavior similar if no primary action is performed.
        if not shell and webui_port is None: # if no other primary action was triggered
             debugger.info("No specific action (shell, webui, csv, id/name download) requested. Setup may have completed if directory was specified.")
             # sys.exit(1) # Or choose to not exit if only setup is valid.
                           # The original code implied an exit if not csv and not id/name and not shell/webui.

# Example of how prefs would be defined if it's not set by checkup in some contexts
# This is just for completeness if the script is run in a way that bypasses full setup.
# prefs = {'dir': '.', 'token': None, 'random_id': None, 'tmpDir': 'tmp'}


if __name__ == '__main__':
    # This is a placeholder for how you might call main()
    # You would typically use argparse or similar to populate the arguments to main()
    # For example:
    # main(csv_file="input.csv", verbose=True, batch_name="Default Batch")
    # main(id="someid", name="Some Name", batch_name="My Batch", topic_name="My Topic", lecture_url="http://example.com/lecture", verbose=True)
    pass
