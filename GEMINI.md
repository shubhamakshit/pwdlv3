# GEMINI.md - Your AI Assistant for PWDLv3

This document provides a comprehensive overview of the PWDLv3 project, its structure, and how to work with it. It is intended to be used as a reference for developers and as a context for AI assistants like Gemini.

## Project Overview

PWDLv3 is a Python-based application for downloading video content from the pw.live platform. It provides both a command-line interface (CLI) and a web-based user interface (web UI) for a seamless user experience.

The project is structured into several key components:

*   **Command-Line Interface (CLI):** The entry point for the CLI is `pwdl.py`. It uses the `argparse` library to provide a rich set of command-line arguments for various functionalities, including downloading single videos, batch downloading from a CSV file, managing user sessions, and starting the web UI.

*   **Web UI Backend:** The web UI backend is a Flask application defined in `beta/api/api.py`. It exposes a RESTful API that is consumed by the web UI frontend. The backend is organized into several blueprints, each responsible for a specific set of functionalities, such as user authentication, task management, and content scraping.

*   **Core Logic:** The core logic of the application is located in the `mainLogic` directory. It is responsible for handling the entire download and processing pipeline, which includes:
    *   Fetching decryption keys.
    *   Parsing MPD files.
    *   Downloading video and audio segments.
    *   Decrypting the downloaded content.
    *   Merging the decrypted audio and video into a single MP4 file.
    *   Cleaning up temporary files.

*   **Dependencies:** The project's dependencies are listed in the `requirements.txt` file. Key dependencies include:
    *   `requests`: For making HTTP requests to the pw.live API.
    *   `flask`: For the web UI backend.
    *   `pycryptodome`: For cryptographic operations.
    *   `argparse`: For parsing command-line arguments.
    *   `prompt-toolkit`, `rich`, `tqdm`: For creating a rich command-line user experience.
    *   `pymongo`: For interacting with a MongoDB database.

## Building and Running

### Prerequisites

*   Python 3.x
*   The dependencies listed in the `requirements.txt` file.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/shubhamakshit/pwdlv3.git
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

*   **Command-Line Interface (CLI):**
    The CLI can be started by running the `pwdl.py` script with the desired arguments. For example, to see the available options, run:
    ```bash
    python pwdl.py --help
    ```

*   **Web UI:**
    The web UI can be started by running the `pwdl.py` script with the `--webui` argument:
    ```bash
    python pwdl.py --webui
    ```
    This will start the Flask development server, and the web UI will be accessible at `http://localhost:5000` by default. The web UI frontend is hosted separately at [pwdl-webui.vercel.app](https://pwdl-webui.vercel.app).

## Development Conventions

*   **Code Style:** The project follows the PEP 8 style guide for Python code.
*   **Modularity:** The project is organized into modules and packages, with a clear separation of concerns. The Flask application is organized into blueprints, and the core logic is separated into different classes, each responsible for a specific task.
*   **Naming Conventions:** The project uses a mix of `camelCase` and `snake_case` for variable and function names. The core download logic classes in `mainLogic/big4` use a fun Harry Potter theme for their names (`Gryffindor_downloadv3`, `Hufflepuff_cleanup`, `Ravenclaw_decrypt`, `Slytherin_merge`).
*   **Error Handling:** The project has a custom error handling mechanism defined in `mainLogic/error.py`.
*   **Debugging:** The project uses a custom `Debugger` class for logging and debugging, which can be found in `mainLogic/utils/Debugger.py`.

## Utility Scripts

This project includes several utility scripts (`.pwdl.py` files) that leverage the core `ScraperModule` to perform specific tasks.

### `list_subjects.pwdl.py`

This script is a powerful tool for inspecting the contents of a batch. It can display a hierarchical view of all subjects, chapters, and lectures, or provide a filtered list of the latest lectures.

**Core Functionality:**

*   Connects to the batch API using the common `ScraperModule`.
*   Fetches and displays content in a structured, tabular format using the `tabulate` library.
*   Can export the fetched data to `json` or `csv` files.

**Usage and Options:**

*   **Default (Display All):** Shows a nested view of all subjects, their chapters, and their lectures.
    ```bash
    python list_subjects.pwdl.py --batch <batch-slug>
    ```

*   **Export All:** Exports the entire nested data structure to a JSON file, or a flattened list of lectures to a CSV file.
    ```bash
    python list_subjects.pwdl.py --batch <batch-slug> --export json
    python list_subjects.pwdl.py --batch <batch-slug> --export csv
    ```

*   **Latest Lectures:** Shows only the single most recent lecture for each subject. This is useful for quickly seeing what's new.
    ```bash
    python list_subjects.pwdl.py --batch <batch-slug> --latest
    ```

*   **Filter by Keyword:** Searches the subject slug and lecture titles for a keyword. This can be combined with `--latest`.
    ```bash
    python list_subjects.pwdl.py --batch <batch-slug> --filter "chemistry"
    python list_subjects.pwdl.py --batch <batch-slug> --latest --filter "physics"
    ```
*   **Exporting Filtered Results:** The `--export` option can be combined with `--latest` and `--filter` to save the specific results.
    ```bash
    python list_subjects.pwdl.py --batch <batch-slug> --latest --export csv
    ```
