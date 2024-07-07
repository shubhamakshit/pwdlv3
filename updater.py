import re

from mainLogic.utils.os2 import SysFunc
from mainLogic.error import errorList
from mainLogic.utils.process import to_list
from mainLogic.utils.glv_var import vars
import subprocess
import os

defaults = [
    "defaults.json",
    "defaults.linux.json"
]

unindex_defaults = f'git update-index --skip-worktree {" ".join(defaults)}'
UPDATE_CHECK_CODE = 'git fetch --dry-run --verbose'


def cmd(command):
    """Run a command in the shell."""
    result = subprocess.run(command, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8'), result.returncode

def check_for_updates():
    """Check for updates."""
    print("Checking for updates...")
    out, code = cmd(UPDATE_CHECK_CODE)
    pattern = r'^\s*=\s*\[up to date\]\s+main\s+->\s+origin/main\s*$'

    # Check if the pattern is found in the git output
    match = re.search(pattern, out, re.MULTILINE)
    if match:
        print("No updates found.")
    else:
        print("Updates found. Please update your repository.")

check_for_updates()