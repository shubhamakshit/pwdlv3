import re
import subprocess
import sys

from mainLogic.utils.os2 import SysFunc
from mainLogic.error import errorList
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
from mainLogic.utils.process import to_list
from mainLogic.utils.glv_var import vars

defaults = [
    "defaults.json",
    "defaults.linux.json"
]

unindex_defaults = f'git update-index --skip-worktree {" ".join(defaults)}'
UPDATE_CHECK_CODE = 'git fetch --dry-run --verbose'





def check_for_updates():
    """Check for updates."""
    Global.sprint("Checking for updates...")
    code, out = shell(to_list(UPDATE_CHECK_CODE),return_out=True)
    out = "\n".join(out)

    pattern = r"\s*=\s*\[up to date\]\s*main\s*->\s*origin/main\s*"
    match = re.search(pattern, out, re.MULTILINE)

    if match:
        return False
    else:
        return True


def pull():
    """Pull the latest changes from the remote repository."""
    Global.sprint("Pulling the latest changes from the remote repository...")
    code, out = shell(["git", "pull"], return_out=True)
    out = "\n".join(out)
    Global.sprint(out)
    return code, out


def main():
    if check_for_updates():
        code, out = pull()
        if code == 0:
            Global.sprint("Please restart the script.")
        else:
            Global.errprint("Error occurred while pulling the latest changes. Exiting...")
            sys.exit(errorList["unknownError"]["code"])
    else:
        Global.sprint("No updates found.")
        sys.exit(errorList["noError"]["code"])


