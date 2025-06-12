# auto_updater.py
import sys
from pathlib import Path
from datetime import datetime # Keep this import at the top

# Adjust this import based on your actual file structure
# If updater.py is in the same directory as auto_updater.py:
from updater import GitUpdater 

# If updater.py is in a subdirectory like 'utils' and auto_updater.py is in parent:
# sys.path.append(str(Path(__file__).parent / 'utils')) 
# from updater import GitUpdater

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
        
        # --- THE CRUCIAL CHANGE IS HERE ---
        # ALWAYS call updater.update(). 
        # The update method itself handles checking for updates (fetch, rev-list)
        # and running the post-op script in its internal 'finally' block,
        # whether an actual merge occurs or not.
        success = updater.update(
            remote="origin",      # Or your desired remote
            branch=None,          # Uses current branch, or specify "main", "dev"
            force=False,          # Set to True for hard reset (DANGEROUS if you have uncommitted changes!)
            stash_changes=True    # Recommended: automatically stash local changes
        )
        # --- END OF CRUCIAL CHANGE ---
        
        if success:
            print("Auto update process completed successfully!")
        else:
            print("Auto update process failed.")
            
        print("--- Auto Git Update Check Finished ---")

    except ValueError as ve:
        print(f"ERROR: {ve}", file=sys.stderr)
        print("Please ensure the specified path is a valid Git repository.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during update: {e}", file=sys.stderr)
    
    finally:
        # This finally block is for run_auto_update(), not GitUpdater.update()
        pass 

if __name__ == "__main__":
    run_auto_update()
