import os

class BasicUtils:

    @staticmethod
    def delete_old_files(directory, minutes):
        """
        Delete files in the given directory which are older than the given number of minutes.
        """
        import time

        current_time = time.time()

        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)

            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)

                if current_time - file_time >= minutes * 60:
                    os.remove(file_path)

    @staticmethod
    def abspath(path):
        return str(os.path.abspath(os.path.expandvars(path))).replace("\\", "/")
