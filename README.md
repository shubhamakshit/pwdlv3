# PhysicsWallah M3u8 Parser

This is a Python script that parses M3u8 files. It uses the argparse library to handle command-line arguments.

## Dependencies

The script requires the following executables to be available in the PATH or the user should provide the path to the executables:

- ffmpeg
- mp4decrypt
- nm3


- `requests`: A library for making HTTP requests. It abstracts the complexities of making requests behind a simple API, allowing you to send HTTP/1.1 requests.

- `colorama`: Makes ANSI escape character sequences work on Windows and Unix systems, allowing colored terminal text and cursor positioning.

- `argparse`: Provides a way to specify command line arguments and options the program is supposed to accept.

- `bs4` (BeautifulSoup4): A library for pulling data out of HTML and XML files. It provides Pythonic idioms for iterating, searching, and modifying the parse tree.

- `flask`: A micro web framework written in Python. It does not require particular tools or libraries, it has no database abstraction layer, form validation, or any other components where pre-existing third-party libraries provide common functions.

- `flask_socketio`: Gives Flask applications access to low latency bi-directional communications between the clients and the server. The client-side application can use any of the Socket.IO official clients libraries in Javascript, C++, Java and Swift, or any compatible client to establish a permanent connection to the server.

To install these dependencies, you would typically run `pip install -r requirements.txt` in your command line.

or if you want to install them individually, you can run the following commands:

`pip install requests colorama argparse bs4 flask flask_socketio`

## Usage

You can use the script with the following command-line arguments:

- `--csv-file`: Input csv file. Legacy Support too.
- `--id`: PhysicsWallh Video Id for single usage. Incompatible with --csv-file. Must be used with --name.
- `--name`: Name for the output file. Incompatible with --csv-file. Must be used with --url.
- `--dir`: Output Directory.
- `--verbose`: Verbose Output.
- `--version`: Shows the version of the program.
- `--simulate`: Simulate the download process. No files will be downloaded.

## Example

```bash
python pwdl.py --csv-file input.csv --dir ./output --verbose
```

This will parse the M3u8 files listed in `input.csv` and save the output in the `./output` directory. The `--verbose` flag is used to enable verbose output.

## Error Handling

The script has built-in error handling. If an error occurs during the parsing of a file, the script will print an error message and continue with the next file. If both csv file and id (or name) is provided, the script will exit with error code 3.

## User Preferences

User preferences can be loaded from a `defaults.json` file. These preferences include the temporary directory (`tmpDir`), verbosity of output (`verbose`), and whether to display a horizontal rule (`hr`). If these preferences are not set in the `defaults.json` file, the script will use default values.

## Simulation Mode

The script includes a simulation mode, which can be enabled with the `--simulate` flag. In this mode, the script will print the files that would be processed, but no files will be downloaded.

## Error Codes


| Error Name                       | Error Code | Error Message                                         |
|----------------------------------|------------|-------------------------------------------------------|
| noError                          | 0          | None                                                  |
| defaultsNotFound                 | 1          | defaults.json not found. Exiting...                   |
| dependencyNotFound               | 2          | Dependency not found. Exiting...                      |
| dependencyNotFoundInPrefs        | 3          | Dependency not found in default settings. Exiting...  |
| csvFileNotFound                  | 4          | CSV file {fileName} not found. Exiting...             |
| downloadFailed                   | 5          | Download failed for {name} with id {id}. Exiting...   |
| cantLoadFile                     | 22         | Can't load file {fileName}                            |
| flareNotStarted                  | 23         | Flare is not started. Start the flare server first.   |
| requestFailedDueToUnknownReason  | 24         | Request failed due to unknown reason. Status Code: {status_code} |
| keyExtractionFailed              | 25         | Key extraction failed for id -> {id}. Exiting...      |
| keyNotProvided                   | 26         | Key not provided. Exiting...                          |
| couldNotDownloadAudio            | 27         | Could not download audio for id -> {id} Exiting...    |
| couldNotDownloadVideo            | 28         | Could not download video for {id} Exiting...          |
| couldNotDecryptAudio             | 29         | Could not decrypt audio. Exiting...                   |
| couldNotDecryptVideo             | 30         | Could not decrypt video. Exiting...                   |
| methodPatched                    | 31         | Method is patched. Exiting...                         |
| couldNotExtractKey               | 32         | Could not extract key. Exiting...                     |

Please note that the `{fileName}`, `{name}`, `{id}`, and `{status_code}` in the Error Message column are placeholders and will be replaced with actual values when the error occurs.