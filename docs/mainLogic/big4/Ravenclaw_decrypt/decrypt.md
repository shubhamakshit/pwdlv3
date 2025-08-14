# Documentation for `mainLogic/big4/Ravenclaw_decrypt/decrypt.py`

This document provides a line-by-line explanation of the `decrypt.py` file. This module is responsible for the second stage of the "Big 4" pipeline: decrypting the downloaded media files.

**Motto:** Ravenclaw represents wisdom and problem-solving. This module applies that by using the correct key and tool to unlock the encrypted content.

## Overview

The `Decrypt` class is a straightforward wrapper around the `mp4decrypt` command-line tool. Its primary job is to construct the correct command with the necessary arguments (input file, output file, and decryption key) and execute it.

---

## Class: `Decrypt`

### `decrypt(self, path, name, key, mp4d="mp4decrypt", out="None", outfile="", outdir="", verbose=True, suppress_exit=False)`

This is the core method that performs the decryption. The `decryptAudio` and `decryptVideo` methods are just convenient wrappers around this one.

-   **Parameters:**
    -   `path`: The directory where the encrypted file is located.
    -   `name`: The base name of the encrypted file (e.g., `My-Video-Video-enc`).
    -   `key`: The decryption key fetched by `LicenseKeyFetcher`.
    -   `mp4d`: The path to the `mp4decrypt` executable.
    -   `out`: A string ("Audio" or "Video") to identify the media type.
    -   `outfile`, `outdir`: Specify the output filename and directory.
    -   `verbose`, `suppress_exit`: Control flags.

```python
        path = BasicUtils.abspath(path)
```
-   Ensures the input path is an absolute path to prevent ambiguity.

```python
        extension = "mp4" # temporary fix
```
-   **Hardcoded Value:** This line hardcodes the extension to `.mp4`. The commented-out code above it suggests there was previous logic to handle different extensions like `.m4a` for audio, but it has been simplified. This is a point of potential maintenance or future improvement.

```python
        file = f'{"" if not outfile else outfile+"-" }{out}.mp4'

        file = os.path.join(
            outdir if outdir else path,
            file
        )
```
-   This block constructs the full path for the **output file**. For example, if `outfile` is "My-Video" and `out` is "Video", the result will be `My-Video-Video.mp4` inside the specified `outdir`.

```python
        decrypt_command = f'{mp4d} --key 1:{key} {path}/{name}.{extension} {file}'
```
-   **Command Construction:** This is the most important line. It builds the exact command to be executed in the shell.
    -   `{mp4d}`: The path to the `mp4decrypt` tool.
    -   `--key 1:{key}`: This is the standard syntax for `mp4decrypt`. It tells the tool to use the provided `{key}` for the track with ID `1`.
    -   `{path}/{name}.{extension}`: The full path to the **input** (encrypted) file.
    -   `{file}`: The full path to the **output** (decrypted) file.

```python
        code = shell(f'{decrypt_command}',stderr="",stdout="")
```
-   This line executes the constructed command using the `shell` utility from `utils/process.py`. The `stderr=""` and `stdout=""` arguments are used to suppress the output from `mp4decrypt` unless verbose mode is active elsewhere.

```python
        if code == 0:
            debugger.debug(f"{out} Decrypted Successfully")
            return os.path.abspath(file)
        else:
            # ... error handling ...
```
-   It checks the `exit code` of the shell command. An exit code of `0` universally signifies success.
-   If successful, it returns the absolute path to the newly created decrypted file.
-   If it fails, it uses the custom error classes (`CouldNotDecryptAudio`, `CouldNotDecryptVideo`) to report the failure and, if `suppress_exit` is `False`, terminates the application.

### `decryptAudio(...)` and `decryptVideo(...)`

```python
    def decryptAudio(self,path,name,key,mp4d="mp4decrypt",outfile='None',outdir=None,verbose=True,suppress_exit=False):
        return self.decrypt(path,name,key,mp4d,"Audio",outfile,outdir,verbose,suppress_exit=suppress_exit)
```
-   These are simply public-facing convenience methods. They call the main `decrypt` method with the `out` parameter pre-filled as either "Audio" or "Video", making the code in `main.py` slightly more readable.
