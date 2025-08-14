# `admin_routes.py`

This script defines the admin routes for the Flask application, which are used to manage tasks and clients.

## Blueprint

The script creates a Flask Blueprint named `admin`.

```python
admin = Blueprint('admin', __name__)
```

## Routes

### `/admin/tasks`

*   **Description:** Returns a list of all active tasks.
*   **Method:** `GET`
*   **Returns:** A JSON object containing a list of all tasks.

### `/admin/clients`

*   **Description:** Returns a list of all connected clients.
*   **Method:** `GET`
*   **Returns:** A JSON object containing a list of all clients.

### `/admin/server/shutdown`

*   **Description:** Shuts down the server. This route is currently commented out.
*   **Method:** `POST`
*   **Returns:** A string indicating that the server is shutting down.
