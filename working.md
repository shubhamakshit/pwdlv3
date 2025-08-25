# `mainLogic` Developer Documentation

This document provides a comprehensive technical overview of the `mainLogic` directory, which serves as the core engine for the `pwdl-v3` application. It is intended for developers who need to understand the application's architecture, data flow, and the responsibilities of each module.

## 1. High-Level Architecture

The `mainLogic` directory is designed as a sequential pipeline that handles the entire process of downloading a video from the source platform. The process can be broken down into four main stages, orchestrated by a central `Main` class:

1.  **Startup & Configuration:** Pre-flight checks, loading user preferences, and validating authentication tokens.
2.  **Information Gathering:** Fetching decryption keys and parsing the video manifest (MPD) file to get segment URLs.
3.  **Execution Pipeline (The "Big 4"):** A four-step process for downloading, decrypting, merging, and cleaning up the video and audio files. This is thematically named after the Hogwarts houses.
4.  **Utilities & Error Handling:** A collection of helper modules and a structured error-handling system that supports the entire pipeline.

---

## 2. Core Execution Flow

A typical download operation follows this sequence of events:

1.  **Entry Point (`pwdl.py` -> `downloader.py`):** The user's command-line arguments are parsed in `pwdl.py` and passed to the `downloader.main()` function. This function acts as the primary entry point into the `mainLogic`.

2.  **Startup Checks (`startup/checkup.py`):**
    *   The `CheckState` class is instantiated.
    *   It verifies that required executables (`ffmpeg`, `mp4decrypt`) are available on the system PATH or in user-defined locations.
    *   It loads user settings from `preferences.json` via `startup/userPrefs.py`.
    *   Crucially, it validates the user's authentication token by making a test request to the API.

3.  **Orchestration (`main.py`):**
    *   The `Main` class is instantiated with all the necessary parameters (video ID, name, paths, token, etc.).
    *   The `Main.process()` method is called, which kicks off the entire download pipeline.

4.  **Key & URL Fetching (`main.py` -> `big4/Ravenclaw_decrypt/key.py`):**
    *   The `Main` class first instantiates `LicenseKeyFetcher`.
    *   `LicenseKeyFetcher.get_key()` is called. This complex method communicates with the platform's API to retrieve the `kid` (Key ID) and the decryption `key` for the requested video.
    *   As part of this process, it also retrieves the URL for the MPD (MPEG-DASH) manifest file.

5.  **MPD Parsing (`main.py` -> `utils/MPDParser.py`):**
    *   The `MPDParser` class is instantiated with the manifest URL.
    *   It downloads and parses the XML-based MPD file.
    *   It extracts the URLs for the initialization segments and all the individual video and audio segments.

6.  **The "Big 4" Execution Pipeline:** The `Main.process()` method then calls each of the "Big 4" modules in order.

    *   **A. Download (`big4/Gryffindor_downloadv3.py`):**
        *   The `DownloaderV3` class handles the concurrent download of all video and audio segments using a thread pool for efficiency.
        *   It tracks progress and reports success or failure for each segment.
        *   Once all segments are downloaded, it concatenates them into two separate encrypted files: `[name]-Video-enc.mp4` and `[name]-Audio-enc.mp4`.

    *   **B. Decrypt (`big4/Ravenclaw_decrypt/decrypt.py`):**
        *   The `Decrypt` class uses the `mp4decrypt` command-line tool.
        *   It runs `mp4decrypt` with the previously fetched `key` on both the encrypted video and audio files.
        *   This produces two new decrypted files: `[name]-Video.mp4` and `[name]-Audio.mp4`.

    *   **C. Merge (`big4/Slytherin_merge.py`):**
        *   The `Merge` class uses the `ffmpeg` command-line tool.
        *   It takes the decrypted video and audio files as input and merges them into a single, final output file: `[name].mp4`.

    *   **D. Cleanup (`big4/Hufflepuff_cleanup.py`):**
        *   The `Clean` class removes all the intermediate files created during the process (encrypted segments, concatenated encrypted files, and separate decrypted files), leaving only the final merged MP4.

---

## 3. Directory & Module Breakdown

### 3.1. Top-Level Modules

-   **`downloader.py`**: The main entry point from the command line. It parses arguments, initiates the startup checks, and calls `main.py` to start the download process for single videos or CSV lists. It also handles starting the Web UI or the interactive shell.
-   **`main.py`**: The central orchestrator. The `Main` class initializes all parameters and executes the entire download pipeline in the correct order.
-   **`error.py`**: Defines a structured system for error handling. It contains a dictionary of predefined errors (`errorList`) and a custom `PwdlError` exception class that allows for clean, consistent error reporting and exiting.

### 3.2. `big4/` - The Core Pipeline

This directory contains the four main processing stages of the download.

-   **`Gryffindor_downloadv3.py`**:
    *   **`DownloaderV3`**: A robust, multi-threaded downloader for DASH segments.
    *   **`ProgressTracker`**: A helper class to manage and display download progress using `tqdm`.
-   **`Ravenclaw_decrypt/`**: Handles all cryptographic and key-related operations.
    *   **`key.py` -> `LicenseKeyFetcher`**: The critical module for authenticating with the API and fetching the decryption key and MPD URL.
    *   **`decrypt.py` -> `Decrypt`**: A wrapper around the `mp4decrypt` executable to decrypt the downloaded media files.
-   **`Slytherin_merge.py`**:
    *   **`Merge`**: A simple wrapper around the `ffmpeg` executable to merge the final audio and video streams.
-   **`Hufflepuff_cleanup.py`**:
    *   **`Clean`**: Responsible for deleting all temporary files created during the download and decryption process.

### 3.3. `startup/` - Initialization & Configuration

This directory handles everything that needs to happen before the main download process can begin.

-   **`checkup.py` -> `CheckState`**: Performs essential pre-flight checks. It verifies that dependencies like `ffmpeg` are installed and that a valid, non-expired user token exists in the preferences.
-   **`userPrefs.py` -> `PreferencesLoader`**: Loads and parses the `preferences.json` file, making user settings available to the rest of the application. It supports variable substitution (e.g., `$home`).
-   **`Login/`**: Contains the logic for the interactive user login flow.
    *   **`call_login.py` -> `LoginInterface`**: Provides the command-line interface for the user to enter their phone number and OTP.
    *   **`sudat.py` -> `Login`**: Handles the actual API calls for sending the OTP and verifying it to retrieve a new authentication token.

### 3.4. `utils/` - Shared Utilities

This directory provides a collection of helper modules and classes used throughout the `mainLogic`.

-   **`Debugger.py` -> `Debugger`**: A custom logging class that provides color-coded, formatted output with timestamps and file locations for easier debugging.
-   **`Endpoint.py` -> `Endpoint`**: A simple wrapper around the `requests` library to make API calls.
-   **`glv.py` & `glv_var.py`**: Used for managing global-like variables and application-wide state (e.g., preferences, paths, the global `debugger` instance) without using actual Python globals.
-   **`MPDParser.py` -> `MPDParser`**: A specialized parser for the MPEG-DASH manifest file (`.mpd`). It extracts the base URL and the list of all audio and video segments that need to be downloaded.
-   **`process.py` -> `shell`**: A utility function for executing shell commands and capturing their output.
-   **`os2.py` -> `SysFunc`**: Provides OS-related utility functions, such as checking if a command exists (`which`) or creating directories.
-   **`basicUtils.py` & `gen_utils.py`**: Contain various other helper functions, such as creating safe filenames or getting absolute paths.
