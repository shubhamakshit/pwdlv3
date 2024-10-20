import platform
import os
from mainLogic import error
from mainLogic.error import CouldNotMakeDir, DependencyNotFound
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global


# 0 - linux
# 1 - windows
# 2 - mac (currently not supported)

class SysFunc:
    def __init__(self, os=1 if "Windows" in platform.system() else 0 if "Linux" in platform.system() else -1):
        if os == -1:
            raise Exception("UnsupportedOS")
        self.os = os

    def create_dir(self, dirName, verbose=False):
        try:
            if not os.path.exists(dirName):
                if verbose: Global.dprint(f"Creating directory {dirName}")
                os.makedirs(dirName)
        except:
            if verbose: Global.errprint(f"Could not make directory {dirName}. Exiting...")
            CouldNotMakeDir(dirName).exit()

        if verbose: Global.dprint(f"Directory {dirName} created")

    def clear(self):
        if self.os == 0:
            os.system("clear")
        elif self.os == 1:
            os.system("cls")
        else:
            raise Exception("UnsupportedOS")

    def which(self, program):

        if self.os == 0:
            if shell('which', stderr="", stdout="") != 1 and shell('which', stderr="", stdout="") != 255:
                DependencyNotFound("which").exit()
            else:
                self.whichPresent = True

            return shell(f"which {program}", stderr="", stdout="")

        elif self.os == 1:

            if shell('where', stderr="", stdout="") != 2:
                DependencyNotFound("where").exit()
            else:
                self.whichPresent = True
            return shell(f"where {program}", stderr="", stdout="")
        else:
            raise Exception("UnsupportedOS")

    @staticmethod
    def modify_path(path):
        expanded_path = os.path.expandvars(path)
        absolute_path = os.path.abspath(expanded_path)
        modified_path = absolute_path.replace(os.sep, '/')
        return modified_path

    @staticmethod
    def list_files_and_folders(directory):

        import os
        import json

        try:
            # Dictionaries to store the files and folders
            result = {
                "folders": [],
                "files": []
            }

            # Walk through the directory
            for entry in os.scandir(directory):
                if entry.is_dir():
                    result["folders"].append(entry.name)
                elif entry.is_file():
                    result["files"].append(entry.name)

            return result

        except FileNotFoundError:
            return json.dumps({"error": f"The directory '{directory}' does not exist."}, indent=4)
        except PermissionError:
            return json.dumps({"error": f"Permission denied for accessing the directory '{directory}'."}, indent=4)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_file_or_folder(path):
        import shutil
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):

                shutil.rmtree(path)

    @staticmethod
    def get_size_in_mB(path):
        import os
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)

    def cd(self, dir=None):
        try:
            if dir:
                os.chdir(dir)
            else:
                os.chdir(os.path.expanduser("~"))
        except Exception as e:
            Global.errprint(f"Could not change directory : {e}")


