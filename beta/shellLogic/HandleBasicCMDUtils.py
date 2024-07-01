import sys
from beta.shellLogic import simpleParser
from mainLogic.utils.os2 import SysFunc

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

            "cd":
                {
                    "desc": "Change directory",
                    "regex": r"cd",
                    "func": self.cd
                },
            "cmd":
                {
                    "desc": "Run a command",
                    "regex": r"cmd",
                    "func": self.cmd
                },
            "exit":
                {
                    "desc": "Exit the shell",
                    "regex": r"exit",
                    "func": self.exit_shell
                },
        }

    def cls(self, args=[]):
        os2.clear()
        if args: print(args)

    def exit_shell(self, args=[]):
        sys.exit(0)

    def cd(self, args=[]):
        if args:
            os2.cd(args[0])
        else:
            os2.cd()

    def cmd(self, args=[]):
        import os
        os.system(" ".join(args))

    def parseAndRun(self, command, args=[]):
        # for key in self.commandList:
        #     if re.match(self.commandList[key]["regex"], command):
        #         self.commandList[key]["func"]()
        #         return
        # raise logicError.commandNotFound(command)
        simpleParser.parseAndRun(self.commandList, command, args)
