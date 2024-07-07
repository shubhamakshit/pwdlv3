import re
import subprocess
import sys

from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
from mainLogic.error import errorList
from mainLogic.utils.glv_var import vars

defaults = [
    "defaults.json",
    "defaults.linux.json"
]

UPDATE_CHECK_CODE = 'git fetch --dry-run --verbose'
UNTRACK__DEFAULTS = f'git update-index --no-skip-worktree {" ".join(defaults)}'

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
    code, out = shell(UPDATE_CHECK_CODE.split(), return_out=True, cwd=vars["$script"])
    out = "\n".join(out)

    pattern = r"\s*=\s*\[up to date\]\s*main\s*->\s*origin/main\s*"
    match = re.search(pattern, out, re.MULTILINE)

    if match:
        return False
    else:
        return True


def pull():
    """Pull the latest changes from the remote repository."""
    Global.sprint("untracking defaults...")
    code, out = shell(UNTRACK__DEFAULTS.split(), return_out=True, cwd=vars["$script"])
    """Move """
    Global.sprint("Pulling the latest changes from the remote repository...")
    code, out = shell(["git", "pull"], return_out=True, cwd=vars["$script"])
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
                stash_code, stash_out = shell(["git", "stash"], return_out=True, cwd=vars["$script"])
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


def get_latest_origin_hash():
    """Get the latest origin hash."""
    Global.sprint("Getting the latest origin hash...")
    code, out = shell(["git", "ls-remote", "origin", "HEAD"], return_out=True, cwd=vars["$script"])
    out = "\n".join(out)
    hash = out.split()[0]
    Global.sprint(f"Latest origin hash: {hash}")
    return hash


def parse_git_log(log_data):
    commit_info = {}
    lines = log_data.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith('commit'):
            commit_info['commit'] = line.split('commit ')[1].strip()
        elif line.startswith('Author'):
            commit_info['author'] = line.split('Author: ')[1].strip()
        elif line.startswith('Date'):
            commit_info['date'] = line.split('Date:   ')[1].strip()
        elif line and not line.startswith('commit') and not line.startswith('Author') and not line.startswith('Date'):
            commit_info['message'] = line.strip()

    return commit_info


def get_info_by_commit_hash(hash):
    """Get the information by commit hash."""
    Global.sprint(f"Getting the information by commit hash: {hash}")
    code, out = shell(["git", "log", "-1", hash], return_out=True, cwd=vars["$script"])
    out = "\n".join(out)
    info = {}
    info = parse_git_log(out)
    Global.sprint(info)
    return info


if __name__ == "__main__":
    main()

