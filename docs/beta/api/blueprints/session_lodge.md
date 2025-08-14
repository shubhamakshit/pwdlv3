# `session_lodge.py`

This script defines the routes for managing client sessions, including creating sessions, starting tasks, deleting clients and sessions, and merging sessions.

## Blueprint

The script creates a Flask Blueprint named `session_lodge`.

```python
session_lodge = Blueprint('session_lodge', __name__)
```

## Managers and Output Directory

It initializes the `Boss`, which in turn initializes the `ClientManager` and `TaskManager`. It also sets the output directory for the downloaded videos.

```python
client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR
```

## Routes

### `/api/client/<client_id>/<session_id>/create_session` or `/client/<client_id>/<session_id>/create_session`

*   **Description:** Creates a new session for a client and adds a batch of download tasks to it.
*   **Method:** `POST`
*   **URL Parameters:**
    *   `client_id` (str): The ID of the client.
    *   `session_id` (str): The ID of the session.
*   **Request Body:** A JSON object containing the following fields:
    *   `client_name` (str, optional): The name of the client.
    *   `ids` (list): A list of video IDs to be downloaded.
    *   `names` (list): A list of video names.
    *   `batch_names` (list): A list of batch names.
    *   `topic_names` (list, optional): A list of topic names.
    *   `lecture_urls` (list, optional): A list of lecture URLs.
*   **Returns:** A JSON object containing a list of `task_ids` for the newly created tasks, or a 400 error if the input is invalid.
*   **Functionality:**
    *   Creates a new client if it doesn't exist.
    *   Creates a new session if it doesn't exist.
    *   Creates a new download task for each video in the request.

### `/api/start/<task_id>` or `/start/<task_id>`

*   **Description:** Starts a previously created download task.
*   **Method:** `GET` or `POST`
*   **URL Parameters:**
    *   `task_id` (str): The ID of the task to be started.
*   **Returns:** A success message if the task is started successfully, or an error message if the task fails to start.

### `/api/client/<client_id>/delete_client` or `/client/<client_id>/delete_client`

*   **Description:** Deletes a client and all of their associated data.
*   **Method:** `GET`
*   **URL Parameters:**
    *   `client_id` (str): The ID of the client to be deleted.
*   **Returns:** A success message if the client is deleted successfully.

### `/api/client/<client_id>/<session_id>/delete_session` or `/client/<client_id>/<session_id>/delete_session`

*   **Description:** Deletes a session for a client.
*   **Method:** `GET`
*   **URL Parameters:**
    *   `client_id` (str): The ID of the client.
    *   `session_id` (str): The ID of the session to be deleted.
*   **Returns:** A success message if the session is deleted successfully.

### `/api/client/<client_id>/merge_sessions` or `/client/<client_id>/merge_sessions`

*   **Description:** Merges two sessions for a client.
*   **Method:** `POST`
*   **URL Parameters:**
    *   `client_id` (str): The ID of the client.
*   **Request Body:** A JSON object containing the following field:
    *   `session_ids` (list): A list of two session IDs to be merged.
*   **Returns:** A success message if the sessions are merged successfully, or an error message if the request is invalid.
*   **Functionality:**
    *   Merges the tasks from the second session into the first session.
    *   Moves the files from the second session's directory to the first session's directory.
    *   Deletes the second session.
