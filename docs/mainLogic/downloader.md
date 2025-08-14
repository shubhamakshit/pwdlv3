# Documentation for `mainLogic/downloader.py`

This document provides a line-by-line explanation of the `downloader.py` file. This module serves as the primary entry point for the application when run from the command line.

## Overview

This module is responsible for:
1.  Orchestrating the application's startup sequence based on command-line arguments.
2.  Handling the processing of a CSV file for batch downloads.
3.  Initiating single video downloads.
4.  Starting the Web UI or the interactive shell.

It acts as a high-level controller that gathers all necessary information and passes it down to the `Main` class (`main.py`) for the actual download pipeline execution.

---

## Functions

### `start_shell()`
A simple function that imports and calls the `main` function from `beta/shellLogic/shell.py` to start the interactive shell.

### `start_webui(port, verbose, no_reloader=False)`
This function is responsible for launching the Flask web server.

```python
def start_webui(port, verbose, no_reloader=False):
    """Start the WebUI if requested."""
    from run import app
```
-   **Local Import:** `app` (the Flask application instance) is imported locally within the function. This is a good practice to prevent circular dependencies and to ensure the app is only imported when needed.

```python
    if 'webui-port' in prefs and port == -1 and port <= glv_var.MINIMUM_PORT:
        port = prefs['webui-port']
```
-   This logic determines the port to use. If a `--webui` flag was given without a specific port (`port == -1`), it checks if a default port is defined in the user's preferences.

```python
    debug_mode = True if verbose else False
    use_reloader = not no_reloader if debug_mode else False
    app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=use_reloader)
```
-   **Conditional Debugging:** This block configures and runs the Flask app.
    -   `debug_mode` is enabled if the `--verbose` flag is present.
    -   `use_reloader` is a crucial piece of logic: the reloader is enabled (`True`) only if `debug_mode` is on AND the `--no-reloader` flag was **not** used. This gives the user fine-grained control over the development server's behavior.
    -   `host="0.0.0.0"` makes the server accessible from other devices on the same network.

### `download_process(...)`
This function wraps the call to the `Main` class for a single video download.

```python
def download_process(
        id, name,batch_name,topic_name,lecture_url,
        state, verbose, simulate=False
):
```
-   It takes all the necessary metadata for a download, along with the application `state` (containing paths to executables) and a `simulate` flag.

```python
    if simulate:
        # ...
        return
```
-   If simulation mode is on, it prints the details and exits without performing any real operations.

```python
    try:
        Main(...).process()
    except Exception as e:
        # ... (error handling)
```
-   This is the core of the function. It instantiates the `Main` class with all the provided arguments and immediately calls the `.process()` method to start the download pipeline.
-   It includes error handling to catch any failures during the process and exit gracefully.

### `handle_csv_file(...)`
This function is responsible for reading and parsing a CSV file for batch downloads.

```python
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        sniffer = csv.Sniffer()
        try:
            sample = f.read(2048)
            has_header = sniffer.has_header(sample)
        except csv.Error:
            has_header = False
        f.seek(0)
```
-   **CSV Sniffing:** This is a robust way to handle CSV files that may or may not have a header row. The `csv.Sniffer` attempts to automatically detect if a header is present by analyzing a sample of the file.

```python
        if has_header:
            reader = csv.DictReader(f)
        else:
            reader = csv.reader(f)
```
-   Based on the sniffing result, it creates either a `DictReader` (which reads rows as dictionaries, using the header) or a standard `reader` (which reads rows as lists).

```python
        header_aliases = { ... }
```
-   **Flexible Headers:** This dictionary is a key feature for user-friendliness. It allows the CSV to have different column names for the same data (e.g., `id`, `lecture id`, `video id` are all treated as the video ID).

```python
        for i, row_data in enumerate(reader):
            # ...
```
-   The code then iterates through each row of the CSV file.

-   **Inside the Loop:**
    -   It uses a helper function `get_val_from_dict` (if a header exists) or direct list indexing to extract the data from the row.
    -   It performs validation to ensure that the required fields (`id` and `name`) are present.
    -   It gives precedence to values in the CSV over the command-line arguments (e.g., a `batch_name` in the CSV will override the one from `--batch-name`).
    -   Finally, for each valid row, it calls `download_process()` to start the download for that video.

### `main(...)`
This is the main orchestrator function for the module.

```python
def main(csv_file=None,
         id=None, name=None,batch_name=None,topic_name=None,lecture_url=None,
         directory=None, verbose=False, shell=False, webui_port=None, no_reloader=False, tmp_dir=None,
         new_downloader=False,
         simulate=False):
```
-   It accepts all possible command-line arguments, with `None` or `False` as defaults.

```python
    ch = CheckState()
    state = ch.checkup(EXECUTABLES, directory=directory,tmp_dir=tmp_dir, verbose=verbose, do_raise=False)
    prefs = state['prefs']
```
-   **Startup:** It immediately performs the startup checks by calling `CheckState.checkup()`. This ensures all dependencies and configurations are valid before proceeding. The returned `state` contains necessary paths and the loaded `prefs`.

```python
    if webui_port is not None:
        start_webui(webui_port, glv.vout, no_reloader=no_reloader)
```
-   If the `--webui` flag was used, it calls `start_webui` and the script effectively becomes a web server.

```python
    if csv_file:
        handle_csv_file(csv_file, state, batch_name, glv.vout, simulate=False)
    elif id and name:
        download_process(...)
```
-   This is the main control flow logic.
    -   If a `--csv-file` is provided, it calls `handle_csv_file`.
    -   If an `--id` and `--name` are provided, it calls `download_process` for a single download.
    -   It also includes logic to prevent running if both a CSV and a single ID are provided simultaneously.
