# auto_updater.py
import sys
from pathlib import Path
from datetime import datetime

# Adjust this import based on your actual file structure
# If updater.py is in the same directory as auto_updater.py:
from updater import GitUpdater 

# If updater.py is in a subdirectory like 'utils' and auto_updater.py is in parent:
# sys.path.append(str(Path(__file__).parent / 'utils')) 
# from updater import GitUpdater

# --- Configuration (Defaults) ---
DEFAULT_REPO_PATH = "."
DEFAULT_ALLOW_POST_OP_SCRIPTS = True # Whether GitUpdater itself is allowed to run remote scripts
DEFAULT_POST_OP_SCRIPT_NAME = "post-update.py"

def run_auto_update(
    repo_path: str = DEFAULT_REPO_PATH,
    allow_remote_scripts: bool = DEFAULT_ALLOW_POST_OP_SCRIPTS,
    post_op_script_name: str = DEFAULT_POST_OP_SCRIPT_NAME,
    run_post_install_script_force: bool = False, # NEW PARAMETER: Forces post-install script run
    force_update: bool = False # NEW PARAMETER: Forces Git update (hard reset)
):
    """
    Automates Git repository update checks and operations.

    Args:
        repo_path (str): Path to the Git repository.
        allow_remote_scripts (bool): If True, allows GitUpdater to run remote scripts.
                                     SECURITY RISK: Only enable if you trust the repository.
        post_op_script_name (str): The name of the script to execute after operations.
        run_post_install_script_force (bool): If True, the post-operation script will be
                                              executed even if no new updates are found.
                                              (This means GitUpdater.update() will be called unconditionally).
        force_update (bool): If True, forces the Git update operation (e.g., git reset --hard).
                             WARNING: This discards local uncommitted changes.
    """
    print(f"--- Auto Git Update Check Started ({datetime.now()}) ---")
    
    # Flag to track if updates were found AND applied successfully
    updates_found_and_applied_successfully = False
    
    try:
        updater = GitUpdater(
            repo_path=repo_path,
            allow_remote_scripts=allow_remote_scripts,
            post_op_script_name=post_op_script_name
        )
        
        # 1. Check if updates are available FIRST
        # This call will also perform a 'git fetch' internally to get the latest remote state.
        has_updates, commits_behind = updater.check_for_updates()

        # Decide whether to call updater.update()
        # It runs if updates are available OR if 'run_post_install_script_force' is True
        should_perform_update_operation = has_updates or run_post_install_script_force

        if has_updates:
            print(f"Found {commits_behind} new commit(s). Preparing to update...")
        elif run_post_install_script_force:
            print("No new commits found, but forcing post-operation script execution.")
        else:
            print("Repository is already up to date. No update operation needed.")
            # In this path, updater.update() is NOT called, so post-update.py will NOT run.

        if should_perform_update_operation:
            # 2. Attempt to apply updates (or just trigger post-op script)
            success_of_update_operation = updater.update(
                remote="origin",      # Or your desired remote
                branch=None,          # Uses current branch, or specify "main", "dev"
                force=force_update,   # Use the new 'force_update' parameter
                stash_changes=True    # Recommended: automatically stash local changes
            )
            
            if has_updates and success_of_update_operation:
                print("Repository updated successfully!")
                updates_found_and_applied_successfully = True
            elif has_updates and not success_of_update_operation:
                print("Repository update failed to apply new changes.")
            elif not has_updates and success_of_update_operation: # Only true if run_post_install_script_force was True
                print("No new commits, but post-operation script executed successfully.")
            elif not has_updates and not success_of_update_operation: # Should be rare if no updates, but could happen if force_update and issues
                print("No new commits and post-operation script execution failed (possibly due to forced update issues).")
        
        print("--- Auto Git Update Check Finished ---")

    except ValueError as ve:
        print(f"ERROR: {ve}", file=sys.stderr)
        print("Please ensure the specified path is a valid Git repository.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during update: {e}", file=sys.stderr)
    
    finally:
        # This is where you would put your "additional action" that runs ONLY IF
        # updates were found AND successfully applied.
        if updates_found_and_applied_successfully:
            print("\n--- Performing conditional post-successful-update action ---")
            # --- YOUR CUSTOM ACTION HERE ---
            # Example: Restart a service, trigger a deployment, send a specific notification
            # import subprocess
            # subprocess.run(["echo", "Running deployment script!"], check=False) 
            # -------------------------------
            print("--- Conditional action finished ---")
        else:
            print("\n--- No conditional action performed (no updates or update failed) ---")


if __name__ == "__main__":
    # --- Example Usage ---
    # 1. Default run (post-op script runs only if updates found)
    # run_auto_update() 

    # 2. Force post-op script execution even if no updates
    # run_auto_update(run_post_install_script_force=True)

    # 3. Force update (hard reset) even if local changes, AND run post-op script only if updates
    # run_auto_update(force_update=True) 

    # 4. Force post-op script execution AND force update if there are changes
    run_auto_update(
        run_post_install_script_force=True,
        force_update=False
    )
