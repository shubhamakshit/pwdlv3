# `custom.py`

This script defines a custom Blueprint class, `CustomBlueprint`, which extends the functionality of the default Flask Blueprint. It also includes a test API blueprint to demonstrate its usage.

## `serialize(obj)`

*   **Description:** A helper function to recursively serialize Python objects to a dictionary. It can handle nested objects, lists, dictionaries, and datetime objects.

## Class `CustomBlueprint`

This class provides a custom Blueprint with additional features like enhanced error handling and CORS support.

### `__init__(self, blueprint_name, url_prefix=None, enable_cors=False, **kwargs)`

*   **Description:** Initializes the `CustomBlueprint`.
*   **Arguments:**
    *   `blueprint_name` (str): The name of the blueprint.
    *   `url_prefix` (str): The URL prefix for the blueprint.
    *   `enable_cors` (bool): If `True`, it enables CORS for the blueprint.

### `add_route(self, url, func, **options)`

*   **Description:** Adds a route to the blueprint with a wrapper that handles exceptions.

### `add_json_route(self, url, func, **options)`

*   **Description:** Adds a route that automatically returns JSON responses.

### `_wrap_view_function(self, func)`

*   **Description:** A private method that wraps a view function with a try-except block to catch and log any exceptions.

### `_setup_default_error_handlers(self)`

*   **Description:** Sets up default error handlers for 403, 404, and 500 errors.

### `_setup_cors(self)`

*   **Description:** Sets up CORS headers for the blueprint.

### `register_blueprint(self, app)`

*   **Description:** Registers the blueprint with the Flask application.

## Test API Blueprint

The script creates a test API blueprint to demonstrate the usage of the `CustomBlueprint` class.

### `test_api_bp`

*   **Description:** A `CustomBlueprint` instance for testing the `ScraperModule`.

### `test_batch_api()`

*   **Description:** An endpoint to test the `ScraperModule` by fetching batch details.
*   **Query Parameters:**
    *   `batch_name` (str): The name of the batch.
*   **Returns:** A JSON object containing the batch details, or an error message if the request fails.

## Exported Blueprints

The script exports a list of custom blueprints to be registered with the Flask application.

```python
custom_blueprints = [test_api_bp]
```
