import subprocess
from mainLogic.utils.glv_var import vars
import sys

# Defaults
defaults = [
    "defaults.json",
    "defaults.linux.json"
]

# Commands
unindex_defaults = f'git update-index --skip-worktree {" ".join(defaults)}'
UPDATE_CHECK_CODE = 'git fetch --dry-run --verbose'
CHECK_UP_TO_DATE = 'git status -uno'

# Functions to run shell commands
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True,cwd=vars['$script'])
    return result

def is_branch_up_to_date():
    result = run_command(CHECK_UP_TO_DATE)
    return "Your branch is up to date" in result.stdout

def update_branch():
    result = run_command('git pull')
    return result

def stash_changes():
    result = run_command('git stash')
    return result

def ask_user_overwrite():
    while True:
        choice = input("Branch is not up to date. Overwrite? (y/n): ").lower()
        if choice in ['y', 'n']:
            return choice == 'y'

def main():
    # Unindex default files
    run_command(unindex_defaults)

    # Check for updates
    print("Checking if branch is up to date...")
    if not is_branch_up_to_date():
        if ask_user_overwrite():
            print("Stashing changes...")
            stash_changes()
            print("Updating branch...")
            result = update_branch()
            if result.returncode == 0:
                print("Branch updated successfully.")
            else:
                print("Error updating branch:", result.stderr)
        else:
            print("Branch not updated.")
    else:
        print("Branch is up to date.")

if __name__ == "__main__":
    main()
