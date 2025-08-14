# `while_dl_and_post_dl.py`

This script defines the routes for monitoring the download progress and retrieving the downloaded files.

## Blueprint

The script creates a Flask Blueprint named `dl_and_post_dl`.

```python
dl_and_post_dl = Blueprint('dl_and_post_dl', __name__)
```

## Managers and Output Directory

It initializes the `Boss`, which in turn initializes the `ClientManager` and `TaskManager`. It also sets the output directory for the downloaded videos.

```python
client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR
```

## Routes

### `/api/progress/<task_id>` or `/progress/<task_id>`

*   **Description:** Returns the progress of a download task.
*   **Method:** `GET`
*   **URL Parameters:**
    *   `task_id` (str): The ID of the task.
*   **Returns:** A JSON object containing the progress of the task.

### `/api/get-file/<task_id>/<name>` or `/get-file/<task_id>/<name>`

*   **Description:** Returns the downloaded video file.
*   **Method:** `GET`
*   **URL Parameters:**
    *   `task_id` (str): The ID of the task.
    *   `name` (str): The name of the video.
*   **Returns:** The video file as an attachment, or an error page if the file is not found.
*   **Functionality:**
    *   Retrieves the task information from the `client_manager`.
    *   Constructs the file path to the downloaded video.
    *   If the file exists, it sends the file as an attachment.
    *   If the file does not exist, it renders an error page.
