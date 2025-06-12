import sys

from beta.shellLogic.Plugin import Plugin
from mainLogic.utils.os2 import SysFunc

os2 = SysFunc()

class HandleBasicCMDUtils(Plugin):
    def __init__(self):
        super().__init__()
        self.add_command(
            "dpp",
            "Handle DPP download (highly customised for mr tshonq)",
            regex="dpp",
            
        )
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
