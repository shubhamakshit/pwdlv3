import error
import os
from utils.os2 import SysFunc
from startup.flareCheck import checkFlare
from utils.glv import Global

class CheckState:

    def __init__(self) -> None:
        pass

    def checkup(self,executable,verbose=True):

        state = {}
        print(__file__)
        default_json = __file__.replace(__name__ + '.py', '') + 'defaults.json'
        # check if defaults.json exists
        # and if it does, load the preferences
        if verbose: Global.hr();Global.dprint("Checking for default settings...")

        if verbose: Global.hr();Global.dprint(f"Checking at {default_json}")
        if verbose: Global.errprint('Warning!\nHard Coded \'defaults.json\' location to $script/default.json ')

        if not os.path.exists(default_json):
            error.errorList["defaultsNotFound"]["func"]()
            exit(error.errorList["defaultsNotFound"]["code"])

        if verbose: Global.sprint("Default settings found."); Global.hr()
        
        # load the preferences
        from startup.userPrefs import PreferencesLoader
        prefs = PreferencesLoader(file_name=default_json,verbose=verbose).prefs

        # check if method is patched (currently via userPrefs.py)
        if 'patched' in prefs:
            if prefs['patched']:
                error.errorList["methodPatched"]["func"]()
                exit(error.errorList["methodPatched"]["code"])

        if verbose: Global.hr(); Global.dprint("Checking for Flare...")
        # default url is localhost:8191
        # however user can change it in the preferences file
        if verbose: Global.dprint(f"Checking at {prefs['flare_url'] if 'flare_url' in prefs else 'http://localhost:8191/v1'}")
        if not checkFlare(prefs['flare_url'] if 'flare_url' in prefs else 'http://localhost:8191/v1'):
            error.errorList["flareNotStarted"]["func"]()
            exit(error.errorList["flareNotStarted"]["code"])

        if verbose: Global.sprint("Flare is running."); Global.hr()

        os2 = SysFunc()

        found= []
        notFound = []

        for exe in executable:
            if verbose: Global.hr(); Global.dprint(f"Checking for {exe}...")

            if os2.which(exe) == 1:
                if verbose: error.errorList["dependencyNotFound"]["func"](exe)
                if verbose: print(f"{exe} not found on path! Checking in default settings...")

                # add exe's which are found to the found list
                found.append(exe)
                # add exe's which are not found to the notFound list
                notFound.append(exe)

            else: 
                if verbose: Global.sprint(f"{exe} found.")
                state[exe] = exe

        if len(notFound) > 0:

            if verbose: Global.hr();Global.dprint("Following dependencies were not found on path. Checking in default settings...")
            if verbose: Global.dprint(notFound); Global.hr()

            for exe in notFound:

                if verbose: Global.dprint(f"Checking for {exe} in default settings...")

                if exe in prefs:

                    if verbose: Global.sprint(f"Key for {exe} found in default settings.")
                    if verbose: Global.sprint(f"Value: {prefs[exe]}")
                    if verbose: Global.dprint(f"Checking for {exe} at '{prefs[exe].strip()}' ...")

                    if not os.path.exists(prefs[exe].strip()):
                        Global.errprint(f"{exe} not found at {prefs[exe].strip()}")
                        error.errorList["dependencyNotFoundInPrefs"]["func"](exe)
                        exit(error.errorList["dependencyNotFoundInPrefs"]["code"])

                    if verbose: Global.sprint(f"{exe} found at {prefs[exe].strip()}")
                    state[exe] = prefs[exe].strip()


                else:
                    error.errorList["dependencyNotFoundInPrefs"]["func"](exe)
                    exit(error.errorList["dependencyNotFoundInPrefs"]["code"])
                
                if verbose: Global.hr()
        
        state['prefs'] = prefs
        

        return state


