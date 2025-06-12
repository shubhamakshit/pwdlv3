import json
from mainLogic import error
import os

from mainLogic.error import CantLoadFile
from mainLogic.utils.glv_var import vars, PREFS_FILE as pf,debugger

PREFS_FILE = pf

class PreferencesLoader:

    def __init__(self, file_name=None, verbose=True):
        global PREFS_FILE
        self.file_name = file_name
        self.prefs = {}

        if file_name:
            if os.path.exists(file_name):
                PREFS_FILE = file_name


        if verbose:
            print(f"Warning! Hard Coded '$script' location to {vars['$script']}")
            print(f"goes to userPrefs.py/..(mainLogic)/..(pwdlv3)/pwdl.py")

        self.file_name = PREFS_FILE


        self.load_preferences()

        # if verbose is true, print the preferences
        if verbose:
            self.print_preferences()

    def load_preferences(self):
        try:

            with open(self.file_name, 'r') as json_file:

                # read the contents of the file (so that we can replace the variables with their values)
                contents = json_file.read()

                # replace the variables with their values
                for var in vars:
                    contents = contents.replace(var, str(vars[var]))

                # replace the backslashes with forward slashes
                contents.replace('\\', '/')

                self.prefs = json.loads(contents)

        # if the file is not found, print an error message and exit
        except FileNotFoundError:
            CantLoadFile(self.file_name).exit()

    # print the preferences (internal function)
    def print_preferences(self):
        debugger.var(self.prefs)

