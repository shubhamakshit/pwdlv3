from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import PREFS_FILE
from beta.update import UpdateJSONFile
class TokenUpdate:

    def __init__(self):

        self.file_path = PREFS_FILE
        # hard coding 'defaults.json' as to ../../defaults.json
        #Global.errprint("Warning! This is a beta feature. Use at your own risk.")
        #Global.errprint("Hard Coded to use 'defaults.json' as to ../../defaults.json (in Global.PREFERENCES_FILE)")
        self.commandList = {
            "tkn-up":{
                "func": self.update
            }
        }

    def update(self,args=[]):
        if args:
            u = UpdateJSONFile(self.file_path)
            u.update('token',args[0])
            Global.sprint("Token updated successfully.")
        else:
            Global.errprint("Please provide a token to update.")

    def parseAndRun(self,command,args=[]):
        # simpleParser.parseAndRun(self.commandList, command, args)
        if command in self.commandList:
            self.commandList[command]["func"](args)
        else:
            Global.errprint("Command not found.")



