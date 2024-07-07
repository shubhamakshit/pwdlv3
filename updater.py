import re
import subprocess
import sys

from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
from mainLogic.error import errorList

defaults = [
    "defaults.json",
    "defaults.linux.json"
]

UPDATE_CHECK_CODE = 'git fetch --dry-run --verbose'


def check_git_availability():
    """Check if Git is available."""
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        Global.errprint("Git is not available. Please install Git to use this script.")
        sys.exit(errorList["gitNotAvailable"]["code"])


def check_for_updates():
    """Check for updates."""
    Global.sprint("Checking for updates...")
    check_git_availability()
    code, out = shell(UPDATE_CHECK_CODE.split(), return_out=True)
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
            Global.errprint(f"Error occurred while pulling the latest changes (exit code {code}).")
            answer = input("Do you want to stash your changes and try pulling again? (y/n): ").strip().lower()
            if answer == 'y':
                stash_code, stash_out = shell(["git", "stash"])
                if stash_code == 0:
                    pull_code, pull_out = pull()
                    if pull_code == 0:
                        Global.sprint("Please restart the script.")
                    else:
                        Global.errprint(f"Failed to pull after stashing (exit code {pull_code}). Exiting...")
                        sys.exit(errorList["gitPullError"]["code"])
                else:
                    Global.errprint("Failed to stash changes. Exiting...")
                    sys.exit(errorList["gitStashError"]["code"])
            else:
                Global.errprint("User opted not to stash changes. Exiting...")
                sys.exit(errorList["gitPullError"]["code"])
    else:
        Global.sprint("No updates found.")
        sys.exit(errorList["noError"]["code"])


if __name__ == "__main__":
    main()
