import os

class BasicUtils:

    @staticmethod
    def abspath(path):
        return str(os.path.abspath(os.path.expandvars(path))).replace("\\", "/")
