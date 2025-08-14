# `client_info_routes.py`

This script defines the routes for managing client information.

## Blueprint

The script creates a Flask Blueprint named `client_info`.

```python
client_info = Blueprint('client_info', __name__)
```

## Routes

### `/api/client/register`

*   **Description:** Registers a new client.
*   **Method:** `POST`
*   **Request Body:** A JSON object containing the client's information.
*   **Returns:** A JSON object containing the new client's information, including a unique `client_id`.

### `/api/client/info`

*   **Description:** Returns information about a specific client.
*   **Method:** `GET`
*   **Query Parameters:**
    *   `client_id` (str): The ID of the client.
*   **Returns:** A JSON object containing the client's information, or a 404 error if the client is not found.
