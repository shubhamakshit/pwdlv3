import error 
from basicUtils import BasicUtils
import os
from os2 import SysFunc
from flareCheck import checkFlare
from glv import Global

class CheckState:

    def __init__(self) -> None:
        pass

    def checkup(self,executable,verbose=True):

        state = {}

        if verbose: Global.hr(); Global.dprint("Checking for Flare...")
        if checkFlare() == False:
            error.errorList["flareNotRunning"]["func"]()
            exit(error.errorList["flareNotRunning"]["code"])
        if verbose: Global.sprint("Flare is running."); Global.hr()
        

        if verbose: Global.dprint("Checking for default settings...")
        if not os.path.exists('defaults.json'):
            error.errorList["defaultsNotFound"]["func"]()
            exit(error.errorList["defaultsNotFound"]["code"])
        if verbose: Global.sprint("Default settings found."); 
        
        from userPrefs import PreferencesLoader
        prefs = PreferencesLoader(verbose=verbose).prefs

        os2 = SysFunc()

        
        notFound = []
        for exe in executable:
            if verbose: Global.hr(); Global.dprint(f"Checking for {exe}...")

            if os2.which(exe) == 1:
                error.errorList["dependencyNotFound"]["func"](exe)
                print(f"{exe} not found on path! Checking in default settings...")
                executable.remove(exe)
                notFound.append(exe)

            else: 
                if verbose: Global.sprint(f"{exe} found.")
                state[exe] = exe

        if len(notFound) > 0:

            if verbose: Global.dprint("Following dependencies were not found on path. Checking in default settings...")
            if verbose: Global.dprint(notFound); Global.hr()

            for exe in notFound:

                if verbose: Global.dprint(f"Checking for {exe} in default settings...")

                if exe in prefs:

                    if verbose: Global.sprint(f"{exe} found in default settings.")
                    if verbose: Global.sprint(f"Path: {prefs[exe]}")
                    if verbose: Global.dprint(f"Checking for {exe} at {prefs[exe].strip()}...")

                    if not os.path.exists(prefs[exe].strip()):
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


