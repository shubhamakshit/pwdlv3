import json
import error
import os
from basicUtils import BasicUtils
class PreferencesLoader:
    def __init__(self, file_name='defaults.json', verbose=True):
        self.file_name = file_name
        self.prefs = {}
        self.vars = {
            "$script" : BasicUtils.abspath(os.path.dirname(__file__)),
            "$home"   : os.path.expanduser("~"),
            "$user"   : os.getlogin()
        }
        self.load_preferences()

        if verbose:
            self.print_preferences()
        

    def load_preferences(self):
        try:
            with open(self.file_name, 'r') as json_file:
                contents = json_file.read()
                
                for var in self.vars:
                    contents = contents.replace(var,self.vars[var])

                contents.replace('\\','/')

                print(contents)
                self.prefs = json.loads(contents)


                

        except FileNotFoundError:
            error.errorList["cantLoadFile"]["func"](self.file_name)
            exit(error.errorList["cantLoadFile"]["code"])

    def print_preferences(self):
        for key in self.prefs:
            print(f'{key} : {self.prefs[key]}')