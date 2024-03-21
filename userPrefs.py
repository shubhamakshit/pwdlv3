import json
import error

class PreferencesLoader:
    def __init__(self, file_name='defaults.json', verbose=True):
        self.file_name = file_name
        self.prefs = {}
        self.load_preferences()

        if verbose:
            self.print_preferences()


    def load_preferences(self):
        try:
            with open(self.file_name, 'r') as json_file:
                self.prefs = json.loads(json_file.read())
        except FileNotFoundError:
            error.errorList["cantLoadFile"]["func"](self.file_name)
            exit(error.errorList["cantLoadFile"]["code"])

    def print_preferences(self):
        for key in self.prefs:
            print(f'{key} : {self.prefs[key]}')