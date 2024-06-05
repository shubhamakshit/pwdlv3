from mainUtils.key import getKey
from shellLogic import simpleParser


class HandleKeyAndAvailiblity:

    def __init__(self):
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
            getKey(args[0])

    def check(self,args=[]):
        print("Checking the availiblity of the key...")
        if args:
            if getKey(args[0],verbose=False):
                print("Key is available")
            else:
                print("Key is not available")
        else:
            print("Please provide a key to check")

    def parseAndRun(self,command,args=[]):
        simpleParser.parseAndRun(self.commandList,command,args)
