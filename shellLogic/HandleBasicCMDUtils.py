import re
import sys
from shellLogic import logicError

from utils.os2 import SysFunc

os2 = SysFunc()


class HandleBasicCMDUtils:
    # basic class for handling basic commands
    # every such class must have a method to parse command (regex based) a help for each command handled by the class

    def __init__(self):
        self.commandList = {
            "cls":
                {
                    "desc": "Clear the screen",
                    "regex": r"cls",
                    "func": self.cls
                },
            "exit":
                {
                    "desc": "Exit the shell",
                    "regex": r"exit",
                    "func": self.exit_shell
                },
        }

    def cls(self):
        os2.clear()

    def exit_shell(self):
        sys.exit(10)

    def parseAndRun(self, command):
        for key in self.commandList:
            if re.match(self.commandList[key]["regex"], command):
                self.commandList[key]["func"]()
                return
        raise logicError.commandNotFound(command)


test = HandleBasicCMDUtils()
test.parseAndRun("23")
