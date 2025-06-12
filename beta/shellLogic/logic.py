from beta.shellLogic.Plugin import Plugin
from beta.shellLogic.TokenUpdate import TokenUpdate
from beta.shellLogic.handleLogics.HandleBasicCMDUtils import HandleBasicCMDUtils

from beta.shellLogic.handleLogics.HandleHell import HandleHell
from beta.shellLogic.handleLogics.HandleKeyAndAvailiblity import HandleKeyAndAvailability
#from beta.shellLogic.handleLogics.HandleQuestions import HandleQuestions
from beta.shellLogic.handleLogics.HandleShellDL import HandleShellDL
from beta.shellLogic.handleLogics.HandleWEB import HandleWEB

# Instantiate the command handlers (automatically registers commands)
basic_cmd_utils = HandleBasicCMDUtils()
key_utils = HandleKeyAndAvailability()
dl_utils = HandleShellDL()
token_update = TokenUpdate()
#k_batch = KhazanaHandler()
webui = HandleWEB()
#ques = HandleQuestions()
hell = HandleHell()

def execute_help(command, args=[]):
    Plugin().help(command)

def execute(command, args=[]):
    Plugin().parseAndRun(command, args)