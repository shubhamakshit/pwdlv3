# Documentation for `mainLogic/utils/glv_var.py`

This document provides a line-by-line explanation of the `glv_var.py` file. This module is a cornerstone of the application's configuration and state management.

## Overview

"glv" likely stands for "global-like variables." This module's purpose is to provide a centralized place to define and access application-wide variables and state without polluting the global namespace with actual Python `global` variables. This is a cleaner and more maintainable approach to managing shared state.

---

## Module-Level Code

### `vars` Dictionary

```python
vars = {
            "$script": BasicUtils.abspath(os.path.dirname(__file__) + (
                '/../..' if not os.path.exists(os.path.dirname(__file__) + '../pwdl.py') else '')),
            "$home": os.path.expanduser("~") if os.name == 'posix' else os.getenv('USERPROFILE'),
        }
```
-   This dictionary is the heart of the variable substitution system used by `userPrefs.py`.
-   **`$script`**:
    -   **Complex Logic:** This is a clever piece of logic to determine the root directory of the project.
    -   `os.path.dirname(__file__)` gets the current directory (`utils`).
    -   The `if` statement checks if `pwdl.py` exists one level up. This is a way to determine if the script is being run from a standard development environment or perhaps a bundled executable where the structure might differ.
    -   Based on the check, it navigates up two levels (`/../..`) to find the project root.
    -   This makes the `$script` variable reliably point to the project's root directory, which is essential for creating portable paths in the `preferences.json` file.
-   **`$home`**: This provides a cross-platform way to get the user's home directory.

### `debugger` Instance

```python
debugger = Debugger(enabled=True,show_location=True)
```
-   This line creates a single, shared instance of the `Debugger` class.
-   By importing `debugger` from this module, all other files in the application can share and use the exact same logger instance, ensuring consistent output and configuration.

### `PREFS_FILE` and `EXECUTABLES`

```python
env_file = os.getenv('PWDL_PREF_FILE')
# ...
PREFS_FILE = os.path.join(vars["$script"], 'preferences.json')

EXECUTABLES = ['ffmpeg', 'mp4decrypt']
```
-   **`PREFS_FILE`**: This logic determines the path to the `preferences.json` file.
    -   It first checks if an environment variable `PWDL_PREF_FILE` is set, allowing the user to override the default location.
    -   If not, it defaults to `preferences.json` in the project's root directory (as determined by the `$script` variable).
-   **`EXECUTABLES`**: This is a simple list that defines the names of the command-line tools that the `checkup.py` module needs to verify are installed. This centralizes the dependency list.
