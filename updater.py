#!/usr/bin/env python3
"""
Git Repository Updater
A comprehensive utility for managing Git repository updates, rollbacks, and version control.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pathlib import Path

# Import the debugger from your project structure
try:
    from mainLogic.utils.glv_var import debugger
except ImportError:
    # Fallback debugger if import fails
    class FallbackDebugger:
        def log(self, message, level="INFO"):
            print(f"[{level}] {message}")
        def info(self, message): self.log(message, "INFO")
        def debug(self, message): self.log(message, "DEBUG")
        def warning(self, message): self.log(message, "WARNING")
        def error(self, message): self.log(message, "ERROR")
        def critical(self, message): self.log(message, "CRITICAL")
        def success(self, message): self.log(message, "SUCCESS")
        def var(self, *args, **kwargs): print(f"VAR: {args} {kwargs}")
    
    debugger = FallbackDebugger()


class GitUpdater:
    """
    A comprehensive Git repository updater with logging and version management.
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize the GitUpdater.
        
        Args:
            repo_path (str): Path to the Git repository (defaults to current directory)
        """
        self.repo_path = Path(repo_path).resolve()
        self.backup_file = self.repo_path / ".git_updater_backup.json"
        
        debugger.info(f"Initializing GitUpdater for repository: {self.repo_path}")
        
        if not self._is_git_repo():
            debugger.error(f"Directory {self.repo_path} is not a Git repository")
            raise ValueError(f"Directory {self.repo_path} is not a Git repository")
        
        debugger.success("GitUpdater initialized successfully")
    
    def _is_git_repo(self) -> bool:
        """Check if the current directory is a Git repository."""
        git_dir = self.repo_path / ".git"
        return git_dir.exists()
    
    def _run_git_command(self, command: List[str], capture_output: bool = True, 
                        check: bool = True) -> subprocess.CompletedProcess:
        """
        Execute a Git command and handle logging.
        
        Args:
            command (List[str]): The Git command to execute
            capture_output (bool): Whether to capture command output
            check (bool): Whether to raise exception on command failure
            
        Returns:
            subprocess.CompletedProcess: The result of the command execution
        """
        full_command = ["git"] + command
        debugger.debug(f"Executing Git command: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=check
            )
            
            if result.stdout:
                debugger.debug(f"Git stdout: {result.stdout.strip()}")
            if result.stderr:
                debugger.warning(f"Git stderr: {result.stderr.strip()}")
                
            return result
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Git command failed: {' '.join(full_command)}")
            debugger.error(f"Exit code: {e.returncode}")
            if e.stdout:
                debugger.error(f"Stdout: {e.stdout}")
            if e.stderr:
                debugger.error(f"Stderr: {e.stderr}")
            raise
    
    def get_current_commit(self) -> str:
        """Get the current commit hash."""
        result = self._run_git_command(["rev-parse", "HEAD"])
        commit_hash = result.stdout.strip()
        debugger.info(f"Current commit: {commit_hash}")
        return commit_hash
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        result = self._run_git_command(["branch", "--show-current"])
        branch = result.stdout.strip()
        debugger.info(f"Current branch: {branch}")
        return branch
    
    def get_status(self) -> str:
        """Get the current Git status."""
        result = self._run_git_command(["status", "--porcelain"])
        status = result.stdout.strip()
        debugger.var("Git status", status=status)
        return status
    
    def is_clean(self) -> bool:
        """Check if the working directory is clean."""
        status = self.get_status()
        is_clean = len(status) == 0
        debugger.info(f"Working directory clean: {is_clean}")
        return is_clean
    
    def save_current_state(self) -> Dict:
        """Save the current state for potential rollback."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "commit": self.get_current_commit(),
            "branch": self.get_current_branch(),
            "status": self.get_status()
        }
        
        try:
            with open(self.backup_file, "w") as f:
                json.dump(state, f, indent=2)
            debugger.success(f"Current state saved to {self.backup_file}")
        except Exception as e:
            debugger.error(f"Failed to save current state: {e}")
            
        debugger.var("Saved state", **state)
        return state
    
    def fetch_updates(self, remote: str = "origin") -> bool:
        """
        Fetch updates from remote repository.
        
        Args:
            remote (str): Remote name (default: origin)
            
        Returns:
            bool: True if fetch was successful
        """
        debugger.info(f"Fetching updates from remote '{remote}'...")
        
        try:
            self._run_git_command(["fetch", remote])
            debugger.success(f"Successfully fetched updates from '{remote}'")
            return True
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to fetch updates from '{remote}': {e}")
            return False
    
    def check_for_updates(self, remote: str = "origin", branch: str = None) -> Tuple[bool, int]:
        """
        Check if there are updates available.
        
        Args:
            remote (str): Remote name
            branch (str): Branch name (uses current branch if None)
            
        Returns:
            Tuple[bool, int]: (has_updates, commits_behind)
        """
        if branch is None:
            branch = self.get_current_branch()
        
        debugger.info(f"Checking for updates on {remote}/{branch}...")
        
        # Fetch first to get latest remote info
        if not self.fetch_updates(remote):
            return False, 0
        
        try:
            # Get commit count between local and remote
            result = self._run_git_command([
                "rev-list", "--count", f"HEAD..{remote}/{branch}"
            ])
            commits_behind = int(result.stdout.strip())
            has_updates = commits_behind > 0
            
            debugger.info(f"Repository is {commits_behind} commits behind {remote}/{branch}")
            debugger.var("Update check", has_updates=has_updates, commits_behind=commits_behind)
            
            return has_updates, commits_behind
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to check for updates: {e}")
            return False, 0
    
    def stash_changes(self, message: str = None) -> bool:
        """
        Stash current changes.
        
        Args:
            message (str): Optional stash message
            
        Returns:
            bool: True if stash was successful
        """
        if self.is_clean():
            debugger.info("No changes to stash")
            return True
        
        stash_msg = message or f"Auto-stash before update at {datetime.now().isoformat()}"
        debugger.info(f"Stashing changes: {stash_msg}")
        
        try:
            self._run_git_command(["stash", "push", "-m", stash_msg])
            debugger.success("Changes stashed successfully")
            return True
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to stash changes: {e}")
            return False
    
    def pop_stash(self) -> bool:
        """
        Pop the most recent stash.
        
        Returns:
            bool: True if stash was popped successfully
        """
        debugger.info("Attempting to pop stash...")
        
        try:
            # Check if there are any stashes
            result = self._run_git_command(["stash", "list"])
            if not result.stdout.strip():
                debugger.info("No stashes available to pop")
                return True
            
            self._run_git_command(["stash", "pop"])
            debugger.success("Stash popped successfully")
            return True
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to pop stash: {e}")
            return False
    
    def update(self, remote: str = "origin", branch: str = None, 
               force: bool = False, stash_changes: bool = True) -> bool:
        """
        Update the repository to the latest version.
        
        Args:
            remote (str): Remote name
            branch (str): Branch name (uses current branch if None)
            force (bool): Force update even if there are local changes
            stash_changes (bool): Automatically stash local changes
            
        Returns:
            bool: True if update was successful
        """
        if branch is None:
            branch = self.get_current_branch()
        
        debugger.info(f"Starting update process for {remote}/{branch}")
        debugger.var("Update parameters", remote=remote, branch=branch, force=force, stash_changes=stash_changes)
        
        # Save current state for potential rollback
        self.save_current_state()
        
        # Check if we have local changes
        if not self.is_clean():
            if stash_changes:
                debugger.warning("Local changes detected, stashing them...")
                if not self.stash_changes():
                    debugger.error("Failed to stash changes")
                    if not force:
                        return False
            elif not force:
                debugger.error("Local changes detected. Use force=True or stash_changes=True")
                return False
            else:
                debugger.warning("Force update enabled, proceeding despite local changes")
        
        try:
            # Fetch updates
            if not self.fetch_updates(remote):
                return False
            
            # Check for updates
            has_updates, commits_behind = self.check_for_updates(remote, branch)
            
            if not has_updates:
                debugger.info("Repository is already up to date")
                return True
            
            debugger.info(f"Updating repository ({commits_behind} commits behind)...")
            
            # Perform the update
            if force:
                debugger.warning("Performing force update...")
                self._run_git_command(["reset", "--hard", f"{remote}/{branch}"])
            else:
                self._run_git_command(["merge", f"{remote}/{branch}"])
            
            debugger.success(f"Successfully updated to latest {remote}/{branch}")
            
            # Show what changed
            self.show_recent_commits(5)
            
            return True
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Update failed: {e}")
            return False
    
    def rollback_to_commit(self, commit_hash: str, force: bool = False) -> bool:
        """
        Rollback to a specific commit.
        
        Args:
            commit_hash (str): The commit hash to rollback to
            force (bool): Force rollback even if there are local changes
            
        Returns:
            bool: True if rollback was successful
        """
        debugger.info(f"Rolling back to commit: {commit_hash}")
        
        # Save current state
        self.save_current_state()
        
        # Check for local changes
        if not self.is_clean() and not force:
            debugger.error("Local changes detected. Use force=True to proceed")
            return False
        
        try:
            # Verify the commit exists
            self._run_git_command(["cat-file", "-e", commit_hash])
            
            # Perform rollback
            if force:
                self._run_git_command(["reset", "--hard", commit_hash])
            else:
                self._run_git_command(["reset", "--soft", commit_hash])
            
            debugger.success(f"Successfully rolled back to {commit_hash}")
            return True
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Rollback failed: {e}")
            return False
    
    def go_to_version(self, version_ref: str, force: bool = False) -> bool:
        """
        Go to a specific version (tag, branch, or commit).
        
        Args:
            version_ref (str): Version reference (tag, branch, or commit hash)
            force (bool): Force checkout even if there are local changes
            
        Returns:
            bool: True if checkout was successful
        """
        debugger.info(f"Going to version: {version_ref}")
        
        # Save current state
        self.save_current_state()
        
        # Check for local changes
        if not self.is_clean():
            if force:
                debugger.warning("Force checkout enabled, discarding local changes")
            else:
                debugger.error("Local changes detected. Use force=True to discard them")
                return False
        
        try:
            # Checkout the version
            checkout_args = ["checkout"]
            if force:
                checkout_args.append("--force")
            checkout_args.append(version_ref)
            
            self._run_git_command(checkout_args)
            debugger.success(f"Successfully checked out {version_ref}")
            
            # Show current state
            current_commit = self.get_current_commit()
            current_branch = self.get_current_branch()
            debugger.info(f"Now on: {current_branch} ({current_commit[:8]})")
            
            return True
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to checkout {version_ref}: {e}")
            return False
    
    def show_recent_commits(self, count: int = 10) -> List[Dict]:
        """
        Show recent commits.
        
        Args:
            count (int): Number of commits to show
            
        Returns:
            List[Dict]: List of commit information
        """
        debugger.info(f"Showing {count} recent commits...")
        
        try:
            result = self._run_git_command([
                "log", f"-{count}", "--pretty=format:%H|%an|%ad|%s", "--date=short"
            ])
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    hash_val, author, date, message = line.split('|', 3)
                    commit_info = {
                        "hash": hash_val,
                        "author": author,
                        "date": date,
                        "message": message
                    }
                    commits.append(commit_info)
                    debugger.info(f"  {hash_val[:8]} | {date} | {author} | {message}")
            
            debugger.var("Recent commits", commits=commits)
            return commits
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to get recent commits: {e}")
            return []
    
    def list_tags(self) -> List[str]:
        """
        List all available tags.
        
        Returns:
            List[str]: List of tag names
        """
        debugger.info("Listing available tags...")
        
        try:
            result = self._run_git_command(["tag", "--sort=-version:refname"])
            tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
            
            debugger.info(f"Found {len(tags)} tags:")
            for tag in tags[:10]:  # Show first 10 tags
                debugger.info(f"  {tag}")
            
            if len(tags) > 10:
                debugger.info(f"  ... and {len(tags) - 10} more")
            
            debugger.var("Available tags", tags=tags)
            return tags
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to list tags: {e}")
            return []
    
    def get_remote_info(self) -> Dict[str, str]:
        """
        Get information about remote repositories.
        
        Returns:
            Dict[str, str]: Dictionary of remote names and URLs
        """
        debugger.info("Getting remote repository information...")
        
        try:
            result = self._run_git_command(["remote", "-v"])
            remotes = {}
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        url = parts[1]
                        if name not in remotes:
                            remotes[name] = url
            
            debugger.info("Remote repositories:")
            for name, url in remotes.items():
                debugger.info(f"  {name}: {url}")
            
            debugger.var("Remote info", remotes=remotes)
            return remotes
            
        except subprocess.CalledProcessError as e:
            debugger.error(f"Failed to get remote info: {e}")
            return {}


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Repository Updater")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    parser.add_argument("--branch", help="Branch name (default: current branch)")
    parser.add_argument("--force", action="store_true", help="Force operation")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update repository")
    update_parser.add_argument("--no-stash", action="store_true", help="Don't stash changes")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to commit")
    rollback_parser.add_argument("commit", help="Commit hash to rollback to")
    
    # Go to version command
    version_parser = subparsers.add_parser("goto", help="Go to specific version")
    version_parser.add_argument("version", help="Version reference (tag, branch, or commit)")
    
    # Status command
    subparsers.add_parser("status", help="Show repository status")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show commit history")
    history_parser.add_argument("--count", type=int, default=10, help="Number of commits to show")
    
    # Tags command
    subparsers.add_parser("tags", help="List available tags")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        updater = GitUpdater(args.repo)
        
        if args.command == "update":
            success = updater.update(
                remote=args.remote,
                branch=args.branch,
                force=args.force,
                stash_changes=not args.no_stash
            )
            sys.exit(0 if success else 1)
            
        elif args.command == "rollback":
            success = updater.rollback_to_commit(args.commit, force=args.force)
            sys.exit(0 if success else 1)
            
        elif args.command == "goto":
            success = updater.go_to_version(args.version, force=args.force)
            sys.exit(0 if success else 1)
            
        elif args.command == "status":
            print(f"Repository: {updater.repo_path}")
            print(f"Current branch: {updater.get_current_branch()}")
            print(f"Current commit: {updater.get_current_commit()}")
            print(f"Working directory clean: {updater.is_clean()}")
            has_updates, commits_behind = updater.check_for_updates(args.remote, args.branch)
            print(f"Updates available: {has_updates} ({commits_behind} commits behind)")
            
        elif args.command == "history":
            updater.show_recent_commits(args.count)
            
        elif args.command == "tags":
            updater.list_tags()
            
    except Exception as e:
        debugger.critical(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
