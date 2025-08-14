# Documentation for `mainLogic/startup/userPrefs.py`

This document provides a line-by-line explanation of the `userPrefs.py` file. This module is responsible for loading and parsing the user's configuration from the `preferences.json` file.

## Overview

The `PreferencesLoader` class is a simple yet powerful configuration loader. Its key feature is the ability to substitute variables within the JSON file, allowing for more flexible and portable configurations.

---

## Global Variables

```python
from mainLogic.utils.glv_var import vars, PREFS_FILE as pf,debugger

PREFS_FILE = pf
```
-   It imports `vars`, a dictionary of predefined variables (like `$script` and `$home`), and `PREFS_FILE`, the default path to the preferences file, from the global-like `glv_var` module.

---

## Class: `PreferencesLoader`

### `__init__(self, file_name=None, verbose=True)`

-   The constructor sets the `file_name` for the preferences file. If a `file_name` is provided, it overrides the default.
-   It immediately calls `self.load_preferences()` to load and process the file upon instantiation.

### `load_preferences(self)`

This is the core method of the class.

```python
        try:
            with open(self.file_name, 'r') as json_file:
                contents = json_file.read()
```
-   It opens and reads the entire `preferences.json` file into a single string variable named `contents`.

```python
                for var in vars:
                    contents = contents.replace(var, str(vars[var]))
```
-   **Variable Substitution:** This is the most important logic in the file. It iterates through the predefined variables (e.g., `"$script"`, `"$home"`) from `glv_var.vars`.
-   For each variable, it performs a simple string replacement on the `contents` of the JSON file. For example, every instance of the string `"$home"` in the file will be replaced with the actual home directory path (e.g., `/home/user`).
-   This allows users to create portable configurations, like setting a download directory to `"$home/Downloads"`, which will work on any system.

```python
                contents.replace('\', '/')
```
-   **Path Normalization:** This line replaces all backslashes (`\`) with forward slashes (`/`). This is a good practice for ensuring cross-platform compatibility, as forward slashes work as path separators on Windows, Linux, and macOS.

```python
                self.prefs = json.loads(contents)
```
-   After all the variable substitutions and path normalizations are done, it uses `json.loads()` to parse the modified string into a Python dictionary, which is stored in `self.prefs`.

```python
        except FileNotFoundError:
            CantLoadFile(self.file_name).exit()
```
-   If the `preferences.json` file does not exist, it uses the custom `CantLoadFile` error to terminate the application gracefully.

### `print_preferences(self)`
-   A simple debugging method that uses the custom `debugger` to print the loaded preferences in a formatted way. This is called if `verbose=True` is passed to the constructor.

```
