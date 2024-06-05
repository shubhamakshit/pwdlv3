from mainLogic.utils.os2 import SysFunc
from beta.shellLogic.HandleBasicCMDUtils import HandleBasicCMDUtils
from beta.shellLogic.HandleKeyAndAvailiblity import HandleKeyAndAvailiblity
from beta.shellLogic.HandleShellDL import HandleShellDL

os2 = SysFunc()
f1 = HandleBasicCMDUtils()
key_utils =  HandleKeyAndAvailiblity()
dl_utils = HandleShellDL()

commands_available={
    # command: [location_of_function,help_class]
    "exit": [f1.parseAndRun,""],
    "cls" : [f1.parseAndRun,""],
    "get_key":[key_utils.parseAndRun,""],
    "check": [key_utils.parseAndRun,""],
    "edl": [dl_utils.parseAndRun,""],
    "dl":[dl_utils.parseAndRun,""]

}

def execute(command,args=[]):
    if command in commands_available:
        commands_available[command][0](command,args)