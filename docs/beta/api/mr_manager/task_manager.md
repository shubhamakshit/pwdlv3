# `task_manager.py`

This script defines the `TaskManager` class, which is responsible for creating, running, and monitoring download tasks.

## Class `TaskManager`

This class manages all the download tasks.

### `__init__(self, client_manager)`

*   **Description:** Initializes the `TaskManager` object.
*   **Arguments:**
    *   `client_manager` (`ClientManager`): An instance of the `ClientManager` class.
*   **Functionality:**
    *   Initializes the `tasks` and `inactive_tasks` dictionaries.
    *   Creates a lock for thread safety.

### Task Creation and Execution

*   `create_task(self, client_id, session_id, target, *args, inactive=False)`: Creates a new download task.
    *   If `inactive` is `False`, it starts the task in a new thread.
    *   If `inactive` is `True`, it adds the task to the `inactive_tasks` dictionary.
*   `start_task(self, task_id)`: Starts an inactive task.
*   `_run_task(self, task_info, target, *args)`: The private method that runs the task in a separate thread. It calls the `target` function with the provided arguments and a `progress_callback` function.

### Task Monitoring

*   `handle_completion(self, task_id)`: A callback function that is called when a task is completed.
*   `_update_progress(self, task_id, progress)`: A private method that updates the progress of a task.
*   `get_progress(self, task_id)`: Retrieves the progress of a task.

### Helper Methods

*   `_get_target_function(self, task_id)`: A private method that retrieves the target function for an inactive task.
