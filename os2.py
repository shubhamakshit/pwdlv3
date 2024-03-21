import platform
import os
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
            return os.system(f"which {program}")
        elif self.os == 1:
            return os.system(f"where {program}")
        else:
            raise Exception("UnsupportedOS")
        