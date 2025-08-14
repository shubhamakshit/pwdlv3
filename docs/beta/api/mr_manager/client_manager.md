# `client_manager.py`

This script defines the `ClientManager` class, which is responsible for managing clients, sessions, and tasks. It provides methods for adding, removing, and updating clients, sessions, and tasks, as well as for retrieving information about them.

## Class `ClientManager`

This class manages all the client-related data.

### `__init__(self, json_file_path)`

*   **Description:** Initializes the `ClientManager` object.
*   **Arguments:**
    *   `json_file_path` (str): The path to the JSON file where the client data is stored.
*   **Functionality:**
    *   Loads the client data from the JSON file.

### Data Persistence

*   `load_data()`: Loads the client data from the JSON file.
*   `save_data()`: Saves the client data to the JSON file.

### Client Management

*   `client_exists(self, client_id)`: Checks if a client exists.
*   `add_client(self, client_id="anonymous", name="")`: Adds a new client.
*   `remove_client(self, client_id)`: Removes a client.
*   `set_client_name(self, client_id, name)`: Sets the name of a client.
*   `get_client_info(self, client_id)`: Retrieves information about a client.
*   `delete_client(self, client_id)`: Deletes a client.

### Session Management

*   `session_exists(self, client_id, session_id)`: Checks if a session exists for a client.
*   `add_session(self, client_id="anonymous", session_id="anonymous")`: Adds a new session for a client.
*   `remove_session(self, client_id, session_id)`: Removes a session from a client.
*   `set_session_name(self, client_id, session_id, name)`: Sets the name of a session.
*   `delete_session(self, client_id, session_id)`: Deletes a session from a client.
*   `merge_sessions(self, client_id, session_id_1, session_id_2)`: Merges two sessions for a client.

### Task Management

*   `add_task(self, client_id, session_id, task_id, task_info)`: Adds a new task to a session.
*   `get_tasks(self, client_id, session_id=None)`: Retrieves all tasks for a client, or for a specific session.
*   `get_task(self, task_id)`: Retrieves a specific task by its ID.
*   `update_task(self, task_info)`: Updates the information of a task.
*   `remove_task(self, client_id, session_id, task_id)`: Removes a task from a session.
*   `get_progress(self, task_id)`: Retrieves the progress of a task.
