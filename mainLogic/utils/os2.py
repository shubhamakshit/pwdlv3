import platform
import os
import re
import shutil
from re import Pattern

from Models.Files import Files
from mainLogic import error
from mainLogic.error import CouldNotMakeDir, DependencyNotFound
from mainLogic.utils.glv_var import debugger
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
                if verbose: debugger.debug(f"Creating directory {dirName}")
                os.makedirs(dirName)
        except:
            if verbose: debugger.error(f"Could not make directory {dirName}. Exiting...")
            CouldNotMakeDir(dirName).exit()

        if verbose: debugger.debug(f"Directory {dirName} created")

    def clear(self):
        if self.os == 0:
            os.system("clear")
        elif self.os == 1:
            os.system("cls")
        else:
            raise Exception("UnsupportedOS")

    def which(self, program):

        if shutil.which(program):
            return shutil.which(program)

        # if self.os == 0:
        #     if shell('which', stderr="", stdout="") != 1 and shell('which', stderr="", stdout="") != 255:
        #         DependencyNotFound("which").exit()
        #     else:
        #         self.whichPresent = True
        #
        #     return shell(f"which {program}", stderr="", stdout="")
        #
        # elif self.os == 1:
        #
        #     if shell('where', stderr="", stdout="") != 2:
        #         DependencyNotFound("where").exit()
        #     else:
        #         self.whichPresent = True
        #     return shell(f"where {program}", stderr="", stdout="")
        # else:
        #     raise Exception("UnsupportedOS")

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
            result = Files.WebdlFolderData()

            # Walk through the directory
            for entry in os.scandir(directory):
                if entry.is_dir():
                    result.folders.append(entry.name)
                elif entry.is_file():
                    result.files.append(entry.name)

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


    import os
    import re
    from typing import Pattern

    @staticmethod
    def concatenate_mp4_segments(
            directory: str,
            output_dir: str = None,
            output_filename: str = "output.mp4",
            init_regex: str = r"^init\.mp4$",
            segment_regex: str = r"^(\d+)\.mp4$",
            cleanup: bool = False
    ) -> None:
        """
        Concatenates init.mp4 followed by numbered .mp4 files in order.

        Args:
            directory (str): Path to directory containing video segments.
            output_dir (str): Directory to save the output file. If None, uses segments directory.
            output_filename (str): Name of the output file (default: "output.mp4").
            init_regex (str): Regex pattern to find init segment.
            segment_regex (str): Regex pattern to find numbered segments (must have a capture group for number).
            cleanup (bool): Whether to remove init and segment files after successful concatenation.
        """

        init_pattern: Pattern = re.compile(init_regex)
        segment_pattern: Pattern = re.compile(segment_regex)

        # Set output directory to segments directory if not specified
        if output_dir is None:
            output_dir = directory

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Combine output directory and filename
        output_file = os.path.join(output_dir, output_filename)

        init_path = None
        segments = []
        segment_files = []  # Store all files for potential cleanup

        for filename in os.listdir(directory):
            if init_pattern.match(filename):
                init_path = os.path.join(directory, filename)
                segment_files.append(init_path)
            else:
                match = segment_pattern.match(filename)
                if match:
                    segment_number = int(match.group(1))
                    file_path = os.path.join(directory, filename)
                    segments.append((segment_number, file_path))
                    segment_files.append(file_path)

        if not init_path:
            raise FileNotFoundError(f"No init segment found with pattern: {init_regex}")

        segments.sort()  # Sort by numeric order

        try:
            with open(output_file, "wb") as outfile:
                # Write init.mp4
                with open(init_path, "rb") as f:
                    outfile.write(f.read())

                # Write each segment in order
                for num, path in segments:
                    with open(path, "rb") as f:
                        outfile.write(f.read())

            print(f"Concatenation complete. Output saved to: {output_file}")
            return os.path.abspath(output_file)

            # Clean up files if requested
            if cleanup:
                for file_path in segment_files:
                    try:
                        os.remove(file_path)
                        #print(f"Removed: {file_path}")
                    except OSError as e:
                        print(f"Error removing {file_path}: {e}")
                print("Cleanup completed.")

        except Exception as e:
            print(f"Error during concatenation: {e}")
            raise