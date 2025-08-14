# `api_dl.py`

This script handles the download process of a video from PW.

## Function `download_pw_video`

This function is responsible for downloading a video from PW, and it takes several arguments to perform the download.

### `download_pw_video(task_id, name, id, batch_name, topic_name, lecture_url, out_dir, client_id, session_id, progress_callback)`

*   **Description:** Downloads a video from PW.
*   **Arguments:**
    *   `task_id` (str): The ID of the task.
    *   `name` (str): The name of the video.
    *   `id` (str): The ID of the video.
    *   `batch_name` (str): The name of the batch.
    *   `topic_name` (str): The name of the topic.
    *   `lecture_url` (str): The URL of the lecture.
    *   `out_dir` (str): The output directory.
    *   `client_id` (str): The ID of the client.
    *   `session_id` (str): The ID of the session.
    *   `progress_callback` (function): A callback function to report the progress of the download.
*   **Functionality:**
    *   Creates the output directory if it doesn't exist.
    *   Checks the state of the application.
    *   Deletes old files from the webdl directory.
    *   Calls the `Main` class from `mainLogic.main` to process the video.
*   **Raises:**
    *   `Exception`: If the ID is invalid or if an error occurs while processing the video.
