# Table of Contents
1. [Project Information](#project-information)
2. [Tools Used](#tools-used)
3. [Getting Started](#getting-started)
    - [Windows](#windows)
    - [Linux](#linux)
4. [Usage](#usage)
5. [API Reference](#api-reference)
6. [Docker Usage](#docker-usage)
7. [Error Codes](#error-codes)
8. [Contributing](#contributing)
9. [License](#license)

# Project Information
pwdlv3 is a project aimed at downloading videos from pw.live. It is written in Python and JavaScript, and uses pip for dependency management.

# Tools Used

- **Python**: The main programming language used for developing the project. It is used for scripting the backend logic of the application.

- **JavaScript**: Used for handling frontend logic of the application.

- **pip**: The package installer for Python. It is used for managing project dependencies.

- **Flask**: A micro web framework written in Python. It is used for handling HTTP requests and rendering the web user interface.

- **Docker**: A platform used for containerization. It is used to create, deploy, and run the application by using containerization. It ensures that the application works uniformly across different computing environments.

- **VSD**: A tool used for downloading MPD (MPEG-DASH) files. It is an essential part of the video downloading process. You can find more about it [here](https://github.com/clitic/vsd).

- **Bento4's mp4decrypt**: A tool used for decrypting encrypted MP4 files. It is a part of the Bento4 toolkit and is used in the process of downloading and decrypting videos.

- **FFmpeg**: A tool used for handling multimedia data. It is used for merging audio and video files in the project.



# Getting Started

## Windows
1. Clone the repository: `git clone https://github.com/username/pwdlv3.git`
2. Navigate to the project directory: `cd pwdlv3`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Run the setup script: `pwdl.bat`

## Linux
1. Clone the repository: `git clone https://github.com/username/pwdlv3.git`
2. Navigate to the project directory: `cd pwdlv3`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Run the setup script: `./setup.sh`

# Usage
To run the project, use the following command:

```bash
python pwdl.py --options
```

- To download a single video: `python pwdl.py --id VIDEO_ID --name VIDEO_NAME`
- To download multiple videos from a CSV file: `python pwdl.py --csv-file FILE_PATH`
- To start the shell: `python pwdl.py --shell`
- To start the WebUI: `python pwdl.py --webui`

# API Reference

The project provides several API endpoints for interacting with the video downloading service. Here are the available endpoints:

- **/api/create_task (POST)**: This endpoint is used to create a new download task. It requires a JSON body with 'id' and 'name' fields. The 'id' is the video ID and 'name' is the name of the output file. It returns a JSON response with a 'task_id' field.

- **/api/progress/<task_id> (GET)**: This endpoint is used to get the progress of a download task. Replace `<task_id>` with the ID of the task. It returns a JSON response with the progress information.

- **/api/get-file/<task_id>/<name> (GET)**: This endpoint is used to download the completed video file. Replace `<task_id>` with the ID of the task and `<name>` with the name of the video. It returns the video file as a download.

- **/key/vid_id (GET)**: This endpoint is used to get the decryption key for a video. It requires 'vid_id' and 'token' as query parameters. It returns a JSON response with a 'key' field.

Please note that these endpoints are also available without the '/api' prefix. For example, you can use '/create_task' instead of '/api/create_task'.

Sure, here's an updated section for "Docker Usage" in your README.md file. It includes a brief description of the Dockerfile and instructions on how to build and run the Docker image.

# Docker Usage

The Dockerfile in this project is used to create a Docker image that encapsulates the entire application, including all its dependencies. This makes it easy to run the application on any system that has Docker installed, without worrying about installing the correct versions of the dependencies.

The Docker image is named `shubhamakshit:pwdl`.

## Building the Docker Image

To build the Docker image, navigate to the project directory and run the following command:

```bash
docker build -t pwdl .
```

This command builds a Docker image using the Dockerfile in the current directory, and tags the image with the name `shubhamakshit/pwdl`.

## Running the Docker Image

To run the Docker image, use the following command:

```bash
docker run -p 5000:5000 shubhamakshit/pwdl
```

This command runs the Docker image and maps port 5000 in the container to port 5000 on the host machine. This allows you to access the application at `http://localhost:5000`.

Sure, here's an updated section for "Shell Usage" in your README.md file. It includes a brief description of the shell and instructions on how to use it.


# Shell Usage (Beta)

The project includes a shell interface for interacting with the video downloading service. This is currently in beta and may not have all the features of the main application.

To start the shell, use the following command:

```bash
python pwdl.py --shell
```

This will start an interactive shell where you can enter commands directly.

Here are some of the available commands:

- `get_key <vid_id> <token>`: This command is used to get the decryption key for a video. Replace `<vid_id>` with the video ID and `<token>` with your token.

- `tkn-up <token>`: This command is used to update the token in the default settings. Replace `<token>` with your new token.  

- `exit`: This command is used to exit the shell.

Please note that these commands are subject to change as the shell is still in beta.




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

[//]: # (# Contributing)

[//]: # (Instructions for how to contribute to the project.)

[//]: # ()
[//]: # (# License)

[//]: # (Information about the project's license.)

w

