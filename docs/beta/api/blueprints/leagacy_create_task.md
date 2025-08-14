# `leagacy_create_task.py`

This script defines the legacy route for creating a new download task.

## Blueprint

The script creates a Flask Blueprint named `legacy_create_task`.

```python
legacy_create_task = Blueprint('legacy_create_task', __name__)
```

## Managers and Output Directory

It initializes the `Boss`, which in turn initializes the `ClientManager` and `TaskManager`. It also sets the output directory for the downloaded videos.

```python
client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR
```

## Routes

### `/api/create_task` or `/create_task`

*   **Description:** Creates a new download task.
*   **Method:** `POST`
*   **Request Body:** A JSON object containing the following fields:
    *   `client_id` (str, optional): The ID of the client. Defaults to `anonymous`.
    *   `session_id` (str, optional): The ID of the session. Defaults to `anonymous`.
    *   `id` (str): The ID of the video to be downloaded.
    *   `name` (str): The name of the video.
*   **Returns:** A JSON object containing the `task_id` of the newly created task, or a 400 error if `id` or `name` are not provided.
*   **Functionality:**
    *   Retrieves the client ID, session ID, video ID, and video name from the request body.
    *   Generates a safe folder name for the video.
    *   Adds the client and session to the respective managers.
    *   Creates a new task using the `task_manager` and the `download_pw_video` function.
