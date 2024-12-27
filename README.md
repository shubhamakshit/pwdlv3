# Table of Contents
1. [Project Information](#project-information)
2. [Tools Used](#tools-used)
3. [Getting Started](#getting-started)
    - [Windows](#windows)
    - [Linux](#linux)
4. [Usage](#usage)
5. [API Reference](#api-reference)
6. [Docker Usage](#docker-usage)
7. [Shell Usage (Beta)](#shell-usage-beta)
8. [Error Codes](#error-codes)
9. [Contributing](#contributing)
10. [License](#license)

# Project Information
`pwdlv3` is a project aimed at downloading videos from pw.live. It is written in Python and JavaScript, and uses pip for dependency management.

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?name=pwdl&type=docker&image=shubhamakshit%2Fpwdl&instance_type=free&ports=14325%3Bhttp%3B%2F&hc_protocol%5B14325%5D=tcp&hc_grace_period%5B14325%5D=5&hc_interval%5B14325%5D=30&hc_restart_limit%5B14325%5D=3&hc_timeout%5B14325%5D=5&hc_path%5B14325%5D=%2F&hc_method%5B14325%5D=get)

# Tools Used

- **Python**: Backend logic scripting.
- **JavaScript**: Frontend logic handling.
- **pip**: Dependency management.
- **Flask**: HTTP requests handling and web UI rendering.
- **Docker**: Containerization for consistent application deployment.
- **VSD**: Downloading MPD (MPEG-DASH) files. [More about VSD](https://github.com/clitic/vsd).
- **Bento4's mp4decrypt**: Decrypting encrypted MP4 files.
- **FFmpeg**: Merging audio and video files.

# Getting Started

## Windows
1. Clone the repository:
   ```bash
   git clone https://github.com/username/pwdlv3.git
   ```
2. Navigate to the project directory:
   ```bash
   cd pwdlv3
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the setup script:
   ```bash
   pwdl.bat
   ```

## Linux
1. Clone the repository:
   ```bash
   git clone https://github.com/username/pwdlv3.git
   ```
2. Navigate to the project directory:
   ```bash
   cd pwdlv3
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the setup script:
   ```bash
   ./setup.sh
   ```

# Usage

Run the project with the following command:

```bash
python pwdl.py --options
```

- Download a single video:
  ```bash
  python pwdl.py --id VIDEO_ID --name VIDEO_NAME
  ```
- Download multiple videos from a CSV file:
  ```bash
  python pwdl.py --csv-file FILE_PATH
  ```
- Start the shell:
  ```bash
  python pwdl.py --shell
  ```
- Start the WebUI:
  ```bash
  python pwdl.py --webui
  ```

# API Reference

The project provides several API endpoints for interacting with the video downloading service:

- **POST /api/create_task**: Create a new download task.
  - **Request Body**: JSON with 'id' (video ID) and 'name' (output file name).
  - **Response**: JSON with 'task_id'.
  
- **GET /api/progress/<task_id>**: Get the progress of a download task.
  - **Response**: JSON with progress information.
  
- **GET /api/get-file/<task_id>/<name>**: Download the completed video file.
  - **Response**: Video file download.
  
- **GET /key/vid_id**: Get the decryption key for a video.
  - **Query Parameters**: 'vid_id' and 'token'.
  - **Response**: JSON with 'key'.

These endpoints are also available without the '/api' prefix. For example, use `/create_task` instead of `/api/create_task`.

# Docker Usage

The Dockerfile is used to create a Docker image that encapsulates the entire application, including all dependencies.

## Building the Docker Image

Navigate to the project directory and run:

```bash
docker build -t shubhamakshit/pwdl .
```

## Running the Docker Image

Run the Docker image with:

```bash
docker run -p 5000:5000 shubhamakshit/pwdl
```

Access the application at `http://localhost:5000`.

# Shell Usage (Beta)

Start the interactive shell with:

```bash
python pwdl.py --shell
```

Available commands:

- `get_key <vid_id> <token>`: Get the decryption key for a video.
- `tkn-up <token>`: Update the token in the default settings.
- `exit`: Exit the shell.

Note: This feature is in beta and may change.

# Error Codes

| Code | Description |
| ---- | ----------- |
| 0 | No error |
| 1 | defaults.json not found |
| 2 | Dependency not found |
| 3 | Dependency not found in default settings |
| 4 | CSV file not found |
| 5 | Download failed |
| 6 | Could not make directory |
| 7 | Token not found in default settings |
| 8 | Overwrite aborted by user |
| 22 | Can't load file |
| 23 | Flare is not started |
| 24 | Request failed due to unknown reason |
| 25 | Key extraction failed |
| 26 | Key not provided |
| 27 | Could not download audio |
| 28 | Could not download video |
| 29 | Could not decrypt audio |
| 30 | Could not decrypt video |
| 31 | Method is patched |
| 32 | Could not extract key |

# Contributing

Instructions for how to contribute to the project will be provided here.

# License

Information about the project's license will be provided here.
