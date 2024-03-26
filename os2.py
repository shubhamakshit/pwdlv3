import platform
import os
import error
from process import shell
# 0 - linux
# 1 - windows
# 2 - mac (currently not supported)
 
class SysFunc:
    def __init__(self,os=1 if "Windows" in platform.system() else 0 if "Linux" in platform.system() else -1):
        if os == -1:
            raise Exception("UnsupportedOS")
        self.os = os

    
    def clear(self):
        if self.os == 0:
            os.system("clear")
        elif self.os == 1:
            os.system("cls")
        else:
            raise Exception("UnsupportedOS")
    

    def which(self,program):

        if self.os == 0:
            if shell('which',stderr="",stdout="") != 256 or shell('which',stderr="",stdout="") != 1:
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
        