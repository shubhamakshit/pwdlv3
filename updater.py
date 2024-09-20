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
UNTRACK_DEFAULTS = f'git update-index --no-skip-worktree {" ".join(defaults)}'

def check_git_availability():
    """Check if Git is available."""
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        Global.errprint("Git is not available. Please install Git to use this script.")
        sys.exit(errorList["gitNotAvailable"]["code"])

def check_for_updates():
    """Check for updates."""
    Global.sprint("Checking for updates...")
    check_git_availability()
    code, output = shell(UPDATE_CHECK_CODE.split(), return_out=True, cwd=vars["$script"])
    output = "\n".join(output)

    # Simplify pattern for detecting "up to date" status
    if re.search(r"up to date", output, re.MULTILINE):
        return False
    return True

def run_git_command(args):
    """Helper function to run Git commands and return output."""
    code, output = shell(args, return_out=True, cwd=vars["$script"])
    output = "\n".join(output)
    return code, output

def pull_latest_changes():
    """Pull the latest changes from the remote repository."""
    Global.sprint("Pulling the latest changes from the remote repository...")
    code, output = run_git_command(["git", "pull"])
    Global.sprint(output)
    return code

def untrack_defaults():
    """Untrack the default files."""
    Global.sprint("Untracking defaults...")
    return run_git_command(UNTRACK_DEFAULTS.split())

def stash_and_pull():
    """Stash local changes and pull the latest changes."""
    Global.sprint("Stashing local changes...")
    code, output = run_git_command(["git", "stash"])
    if code == 0:
        Global.sprint("Successfully stashed changes. Pulling latest changes...")
        return pull_latest_changes()
    else:
        Global.errprint("Failed to stash changes. Exiting...")
        sys.exit(errorList["gitStashError"]["code"])

def main():
    if check_for_updates():
        untrack_defaults()
        code = pull_latest_changes()

        if code == 0:
            Global.sprint("Please restart the script.")
        else:
            Global.errprint(f"Error occurred while pulling the latest changes (exit code {code}).")
            answer = input("Do you want to stash your changes and try pulling again? (y/n): ").strip().lower()
            if answer == 'y':
                stash_code = stash_and_pull()
                if stash_code == 0:
                    Global.sprint("Please restart the script.")
                else:
                    Global.errprint("Failed to pull after stashing. Exiting...")
                    sys.exit(errorList["gitPullError"]["code"])
            else:
                Global.errprint("User opted not to stash changes. Exiting...")
                sys.exit(errorList["gitPullError"]["code"])
    else:
        Global.sprint("No updates found.")
        sys.exit(errorList["noError"]["code"])

def get_latest_origin_hash():
    """Get the latest origin commit hash."""
    Global.sprint("Getting the latest origin hash...")
    code, output = run_git_command(["git", "ls-remote", "origin", "HEAD"])
    commit_hash = output.split()[0]
    Global.sprint(f"Latest origin hash: {commit_hash}")
    return commit_hash

def parse_git_log(log_data):
    """Parse Git log output."""
    commit_info = {}
    lines = log_data.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith('commit'):
            commit_info['commit'] = line.split(' ')[1].strip()
        elif line.startswith('Author'):
            commit_info['author'] = line.split('Author: ')[1].strip()
        elif line.startswith('Date'):
            commit_info['date'] = line.split('Date:   ')[1].strip()
        elif line and not line.startswith(('commit', 'Author', 'Date')):
            commit_info['message'] = line.strip()

    return commit_info

def get_info_by_commit_hash(commit_hash):
    """Get information for a specific commit."""
    Global.sprint(f"Getting information for commit: {commit_hash}")
    code, output = run_git_command(["git", "log", "-1", commit_hash])
    commit_info = parse_git_log(output)
    Global.sprint(commit_info)
    return commit_info

if __name__ == "__main__":
    main()
