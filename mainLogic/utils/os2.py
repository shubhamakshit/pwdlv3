import platform
import os
from mainLogic import error
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
# 0 - linux
# 1 - windows
# 2 - mac (currently not supported)
 
class SysFunc:
    def __init__(self,os=1 if "Windows" in platform.system() else 0 if "Linux" in platform.system() else -1):
        if os == -1:
            raise Exception("UnsupportedOS")
        self.os = os

    def create_dir(self,dirName,verbose=False):
        try:
            if not os.path.exists(dirName):
                if verbose: Global.dprint(f"Creating directory {dirName}")
                os.makedirs(dirName)
        except:
            if verbose: Global.errprint(f"Could not make directory {dirName}. Exiting...")
            error.errorList["couldNotMakeDir"]["func"](dirName)
            exit(error.errorList["couldNotMakeDir"]["code"])

        if verbose: Global.dprint(f"Directory {dirName} created")
    def clear(self):
        if self.os == 0:
            os.system("clear")
        elif self.os == 1:
            os.system("cls")
        else:
            raise Exception("UnsupportedOS")
    

    def which(self,program):

        if self.os == 0:
            if shell('which',stderr="",stdout="") != 1 and shell('which',stderr="",stdout="") != 255:
                error.errorList["dependencyNotFound"]["func"]('which')
                exit(error.errorList["dependencyNotFound"]["code"])
            else:
                self.whichPresent = True

            return shell(f"which {program}",stderr="",stdout="")
        
        elif self.os == 1:

            if shell('where',stderr="",stdout="") != 2:
                error.errorList["dependencyNotFound"]["func"]('where')
                exit(error.errorList["dependencyNotFound"]["code"])
            else:
                self.whichPresent = True
            return shell(f"where {program}" , stderr="",stdout="")
        else:
            raise Exception("UnsupportedOS")

    @staticmethod
    def modify_path(path):
        expanded_path = os.path.expandvars(path)
        absolute_path = os.path.abspath(expanded_path)
        modified_path = absolute_path.replace(os.sep, '/')
        return modified_path
        