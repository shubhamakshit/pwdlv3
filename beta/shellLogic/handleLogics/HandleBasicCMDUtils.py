import sys

from beta.shellLogic.Plugin import Plugin
from mainLogic.utils.os2 import SysFunc

os2 = SysFunc()

class HandleBasicCMDUtils(Plugin):
    def __init__(self):
        super().__init__()
        self.commandList = {
            "cls": {
                "desc": "Clear the screen",
                "regex": r"cls",
                "func": self.cls
            },
            "cd": {
                "desc": "Change directory",
                "regex": r"cd",
                "func": self.cd
            },
            "cmd": {
                "desc": "Run a command",
                "regex": r"cmd",
                "func": self.cmd
            },
            "exit": {
                "desc": "Exit the shell",
                "regex": r"exit",
                "func": self.exit_shell
            }
        }
        self.register_commands()

    def cls(self, args=[]):
        os2.clear()
        if args:
            print(args)

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
