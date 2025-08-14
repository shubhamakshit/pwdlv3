# `api_pref_manager.py`

This script defines the routes for managing the application's preferences.

## Blueprint

The script creates a Flask Blueprint named `api_prefs`.

```python
api_prefs = Blueprint('api_prefs', __name__)
```

## Routes

### `/api/prefs/defaults.json` or `/prefs/defaults.json`

*   **Description:** Returns the current preferences from the `defaults.json` file.
*   **Method:** `GET`
*   **Returns:** A JSON object containing the preferences, or a 404 error if the file is not found.

### `/api/update/defaults.json` or `/update/defaults.json`

*   **Description:** Updates the preferences in the `defaults.json` file.
*   **Method:** `POST`
*   **Request Body:** A JSON object containing the preferences to be updated.
*   **Returns:** The updated preferences as a JSON object, a 404 error if the file is not found, or a 400 error if the request body is not valid JSON.
*   **Functionality:**
    *   Reads the existing preferences from the file.
    *   Updates the preferences with the data from the request.
    *   Saves the updated preferences back to the file.
    *   Re-checks the application's dependencies.
