# `util.py`

This script provides utility functions for various tasks.

## Functions

### `extract_uuid(text)`

*   **Description:** Extracts UUIDs from a string using a regular expression.
*   **Arguments:**
    *   `text` (str): The string to search for UUIDs.
*   **Returns:**
    *   A list of extracted UUIDs, or an empty list if none are found.

### `generate_safe_file_name(name)`

*   **Description:** Generates a safe file name by replacing spaces with underscores and removing special characters.
*   **Arguments:**
    *   `name` (str): The original name to be converted.
*   **Returns:**
    *   A string that is a safe file name.
