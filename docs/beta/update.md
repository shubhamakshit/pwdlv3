# `update.py`

This script provides a class `UpdateJSONFile` for easy handling of JSON file updates.

## Class `UpdateJSONFile`

This class is used to load, update, and save JSON files.

### `__init__(self, file_path, debug=False)`

*   **Description:** Initializes the `UpdateJSONFile` object.
*   **Arguments:**
    *   `file_path` (str): The path to the JSON file.
    *   `debug` (bool): If `True`, it will print debug messages.
*   **Functionality:**
    *   Loads the JSON data from the given file path.
    *   If `debug` is `True`, it prints the loaded data.

### `load(self)`

*   **Description:** Loads the JSON data from the file.
*   **Functionality:**
    *   Opens the file in read mode.
    *   Loads the JSON data into the `self.data` attribute.

### `save(self)`

*   **Description:** Saves the JSON data to the file.
*   **Functionality:**
    *   Opens the file in write mode.
    *   Dumps the JSON data from `self.data` to the file with an indent of 4.
    *   Verifies that the data was saved correctly.

### `update(self, key, value, debug=False)`

*   **Description:** Updates a key-value pair in the JSON data.
*   **Arguments:**
    *   `key` (str): The key to be updated.
    *   `value` (any): The new value for the key.
    *   `debug` (bool): If `True`, it will print debug messages.
*   **Functionality:**
    *   Updates the value of the given key in `self.data`.
    *   Calls the `save()` method to save the updated data.
