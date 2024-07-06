from mainLogic.utils.process import shell

def stash_files(files):
    files_str = ' '.join(files)
    stash_command = f"git stash push -m 'Stash local changes for {files_str}' {files_str}"
    result = shell(stash_command)
    if result.returncode != 0:
        print(f"Command '{stash_command}' failed with error:\n{result.stderr}")
    else:
        print(f"Command '{stash_command}' succeeded with output:\n{result.stdout}")

def pull_changes(branch='main'):
    pull_command = f"git pull origin {branch}"
    result = shell(pull_command)
    if result.returncode != 0:
        print(f"Command '{pull_command}' failed with error:\n{result.stderr}")
    else:
        print(f"Command '{pull_command}' succeeded with output:\n{result.stdout}")

def apply_stash():
    apply_command = "git stash pop"
    result = shell(apply_command)
    if result.returncode != 0:
        print(f"Command '{apply_command}' failed with error:\n{result.stderr}")
    else:
        print(f"Command '{apply_command}' succeeded with output:\n{result.stdout}")

def update_repo(files_to_stash, branch='main'):
    stash_files(files_to_stash)
    pull_changes(branch)
    apply_stash()

if __name__ == "__main__":
    files_to_stash = ['defaults.json', 'default.linux.json']
    update_repo(files_to_stash)
