# `boss_manager.py`

This script defines the `Boss` class, which acts as a central point for managing clients and tasks.

## Class `Boss`

This class is a simple container for the `ClientManager` and `TaskManager` instances. It also defines the output directory for the downloaded videos.

### Attributes

*   `client_manager`: An instance of the `ClientManager` class, initialized with the `clients.json` file.
*   `task_manager`: An instance of the `TaskManager` class, initialized with the `client_manager` instance.
*   `OUT_DIR`: The output directory for the downloaded videos, which is set to the `api_webdl_directory` from the `glv_var` module.
