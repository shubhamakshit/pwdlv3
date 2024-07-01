from mainLogic.utils.os2 import SysFunc
from beta.shellLogic.HandleBasicCMDUtils import HandleBasicCMDUtils
from beta.shellLogic.HandleKeyAndAvailiblity import HandleKeyAndAvailiblity
from beta.shellLogic.HandleShellDL import HandleShellDL
from beta.shellLogic.TokenUpdate import TokenUpdate

os2 = SysFunc()
f1 = HandleBasicCMDUtils()
key_utils =  HandleKeyAndAvailiblity()
dl_utils = HandleShellDL()
token_update = TokenUpdate()

commands_available={
    # command: [location_of_function,help_class]
    "exit": [f1.parseAndRun,""],
    "cls" : [f1.parseAndRun,""],
    "cd"  : [f1.parseAndRun,""],
    "cmd" : [f1.parseAndRun,""],
    "get_key":[key_utils.parseAndRun,""],
    "check": [key_utils.parseAndRun,""],
    "edl": [dl_utils.parseAndRun,""],
    "dl":[dl_utils.parseAndRun,""],
    "tkn-up":[token_update.parseAndRun,""],


}

def execute(command,args=[]):
    if command in commands_available:
        commands_available[command][0](command,args)