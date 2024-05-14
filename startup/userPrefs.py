import json
import error
import os
from utils.basicUtils import BasicUtils

class PreferencesLoader:
    def __init__(self, file_name='defaults.json', verbose=True):
        self.file_name = file_name
        self.prefs = {}

        # defining some variables that can be used in the preferences file 
        self.vars = {
            "$script" : BasicUtils.abspath(os.path.dirname(__file__)),
            "$home"   : os.path.expanduser("~"),
        }

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
                for var in self.vars:
                    contents = contents.replace(var,self.vars[var])

                # replace the backslashes with forward slashes
                contents.replace('\\','/')

                self.prefs = json.loads(contents)

        # if the file is not found, print an error message and exit
        except FileNotFoundError:
            error.errorList["cantLoadFile"]["func"](self.file_name)
            exit(error.errorList["cantLoadFile"]["code"])


    # print the preferences (internal function)
    def print_preferences(self):
        for key in self.prefs:
            print(f'{key} : {self.prefs[key]}')