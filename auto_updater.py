# auto_updater.py
import sys
from pathlib import Path

# Adjust this import based on your actual file structure
# If git_updater.py is in the same directory as auto_updater.py:
from updater import GitUpdater 

# If git_updater.py is in a subdirectory like 'utils' and auto_updater.py is in parent:
# sys.path.append(str(Path(__file__).parent / 'utils')) 
# from git_updater import GitUpdater

# --- Configuration ---
REPO_PATH = "."  # Or specify your repository path: "/path/to/your/git/repo"
ALLOW_POST_OP_SCRIPTS = True # Set to True if you have post-update scripts and trust the repo
POST_OP_SCRIPT_NAME = "post-update.py" # Name of your post-operation script

def run_auto_update():
    print(f"--- Auto Git Update Check Started ({datetime.now()}) ---")
    
    try:
        updater = GitUpdater(
            repo_path=REPO_PATH,
            allow_remote_scripts=ALLOW_POST_OP_SCRIPTS,
            post_op_script_name=POST_OP_SCRIPT_NAME
        )
        
        # Check if there are updates first
        has_updates, commits_behind = updater.check_for_updates()

        if has_updates:
            print(f"Found {commits_behind} new commit(s). Initiating update...")
            success = updater.update(
                remote="origin",      # Or your desired remote
                branch=None,          # Uses current branch, or specify "main", "dev"
                force=False,          # Set to True for hard reset (DANGEROUS if you have uncommitted changes!)
                stash_changes=True    # Recommended: automatically stash local changes
            )
            
            if success:
                print("Repository updated successfully!")
            else:
                print("Repository update failed.")
        else:
            print("Repository is already up to date. No update needed.")
            
        print("--- Auto Git Update Check Finished ---")

    except ValueError as ve:
        print(f"ERROR: {ve}", file=sys.stderr)
        print("Please ensure the specified path is a valid Git repository.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during update: {e}", file=sys.stderr)
    
    finally:
        # This block ensures any cleanup or final reporting happens
        # The post-operation script in GitUpdater itself is handled by its finally block
        pass

if __name__ == "__main__":
    from datetime import datetime # Import here if only used in this file's main execution
    run_auto_update()
