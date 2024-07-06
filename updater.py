def build_update_index_command(script_dir):
    command = f"git update-index --skip-worktree defaults.json defaults.linux.json"

def pull_latest_changes():
    command = "git pull"

def main():
    from mainLogic.utils.process import shell
    shell(build_update_index_command(),filter=r'.*')
    shell(pull_latest_changes(),r'.*')