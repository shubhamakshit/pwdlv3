# Documentation for `mainLogic/startup/checkup.py`

This document provides a line-by-line explanation of the `checkup.py` file. This module is critical for ensuring the application's environment is correctly configured before any processing begins.

## Overview

The `CheckState` class is a pre-flight checker. Its main purpose is to validate the user's environment and configuration. It performs several key tasks:
1.  Loads user preferences.
2.  Checks for the existence of required command-line tools (like `ffmpeg`).
3.  Validates the user's authentication token to ensure it's valid and not expired.
4.  Sets up the temporary and final output directories.

---

## Class: `CheckState`

### `__init__(self)`
-   The constructor is simple and primarily sets a default `random_id`, a value needed for certain API communications.

### `setup_tmp_dir(self, tmp_dir, verbose=True)`
-   A straightforward helper method that checks if the specified temporary directory exists and creates it if it doesn't. It includes error handling in case of permission issues.

### `post_checkup(self, prefs, skip_tmp_dir=False, verbose=True)`
-   This method handles final setup tasks after the main checks are done.
-   It ensures the temporary and final output directories exist.
-   `Global.disable_hr = not prefs.get('hr', True)`: This line reads a boolean from the user's preferences to determine whether to show the horizontal rule (`---`) in the console output, allowing for UI customization.

### `validate_token(self, token_data, verbose=False)`
-   This method is responsible for parsing the token data stored in `preferences.json`.
-   The token can be stored as a raw string or a JSON object. This method handles both cases, attempting to parse a JSON string if it receives one.
-   It extracts the `access_token` and `random_id` from the dictionary, which are the two components needed for authentication.

### `check_token(self, token, random_id, ...)`
-   **Crucial Method:** This method performs a live check of the authentication token.
-   It instantiates `LicenseKeyFetcher` and calls its `get_key()` method with a hardcoded, known-valid video ID.
-   If `get_key()` succeeds, it means the token is valid and can be used for subsequent requests.
-   If it fails, it raises a `TokenInvalid` exception, signaling that the user needs to log in again. This is the primary mechanism for detecting an expired or invalid token.

### `checkup(self, executable, ...)`
-   This is the main public method of the class, orchestrating all the pre-flight checks.

1.  **Load Preferences:**
    ```python
    prefs = self.load_preferences(verbose)
    ```
    -   It starts by loading all user settings from the JSON file.

2.  **Check for Patched Method:**
    ```python
    if self.is_method_patched(prefs, do_raise):
        return state
    ```
    -   This checks for a `patched: true` flag in the preferences. This is a kill-switch mechanism that allows the developer to remotely disable the application if the platform's API changes in a way that breaks the tool.

3.  **Check Executables:**
    ```python
    state.update(self.check_executables(executable, prefs, verbose, do_raise))
    ```
    -   It calls a helper (`check_executables`) that iterates through a list of required tools (e.g., `['ffmpeg', 'mp4decrypt']`).
    -   The helper first checks if the tool is available on the system's PATH.
    -   If not, it checks the user's preferences to see if a direct path to the executable has been provided.
    -   If the executable cannot be found in either location, it raises a `DependencyNotFound` error.

4.  **Validate Token:**
    ```python
    if not glv_var.vars.get('ig_token'):
        # ... token validation logic ...
    ```
    -   This block is skipped if the `--ignore-token` flag was used.
    -   It gets the token data from `prefs`, calls `self.validate_token()` to parse it, and then calls `self.check_token()` to perform the live validation against the API.
    -   If any step fails, it raises the appropriate error (`TokenNotFound` or `TokenInvalid`).

5.  **Finalize State:**
    ```python
    state['prefs'] = prefs
    prefs['dir'] = directory
    self.post_checkup(prefs, verbose)
    return state
    ```
    -   It populates the `state` dictionary with all the validated information (paths to executables, the valid token, preferences).
    -   This `state` object is then returned to the `downloader.main` function, which uses it to instantiate the `Main` class.
