from beta.shellLogic.Plugin import Plugin
from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher
from mainLogic.utils import glv_var
from mainLogic.startup.checkup import CheckState

class HandleKeyAndAvailability(Plugin):
    def __init__(self):
        super().__init__()
        ch = CheckState()
        self.prefs = ch.checkup(glv_var.EXECUTABLES, verbose=False)['prefs']
        self.token = self.prefs['token']
        self.random_id = self.prefs['random_id']
        self.lkf = LicenseKeyFetcher(self.token, self.random_id)
        self.commandList = {
            "get_key": {
                "desc": "Retrieve a license key",
                "regex": r"(get_key|key)",
                "func": self.get_key,
            },
            "check": {
                "desc": "Check availability of the license key",
                "regex": r"check",
                "func": self.check
            }
        }
        self.register_commands()

    def get_key(self, args=[]):
        if args:
            self.lkf.get_key(args[0])
        else:
            print("Please provide a key to get")

    def check(self, args=[]):
        print("Checking the availability of the key...")
        if args:
            if self.lkf.get_key(args[0], verbose=False):
                print("Key is available")
            else:
                print("Key is not available")
        else:
            print("Please provide a key to check")
