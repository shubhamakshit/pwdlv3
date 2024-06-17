from mainLogic.big4.decrypt.key import LicenseKeyFetcher
from beta.shellLogic import simpleParser
from mainLogic.utils.glv import Global

class HandleKeyAndAvailiblity:

    def __init__(self):
        from mainLogic.startup.checkup import CheckState
        ch = CheckState()
        self.token = ch.checkup(Global.EXECUTABLES,verbose=False)['prefs']['token']
        self.lkf = LicenseKeyFetcher(self.token)
        self.commandList = {
            "get_key":{
                "regex": r"(get_key|key)",
                "func": self.get_key,
            },
            "check":{
                "func": self.check
            }

        }

    def get_key(self,args=[]):
        if args:
            self.lkf.get_key(args[0])

    def check(self,args=[]):
        print("Checking the availiblity of the key...")
        if args:
            if self.lkf.get_key(args[0],verbose=False):
                print("Key is available")
            else:
                print("Key is not available")
        else:
            print("Please provide a key to check")

    def parseAndRun(self,command,args=[]):
        simpleParser.parseAndRun(self.commandList, command, args)
