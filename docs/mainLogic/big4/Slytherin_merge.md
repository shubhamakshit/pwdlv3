# Documentation for `mainLogic/big4/Slytherin_merge.py`

This document provides a line-by-line explanation of the `Slytherin_merge.py` file. This module is responsible for the third stage of the "Big 4" pipeline: merging the separate decrypted audio and video files into a single, final MP4 file.

**Motto:** Slytherin is known for ambition and resourcefulness. This module ambitiously combines the final pieces into a complete product.

## Overview

The `Merge` class is a simple wrapper around the `ffmpeg` command-line tool. Its purpose is to construct and execute the correct `ffmpeg` command to combine the two media streams without re-encoding them, which is very fast and preserves the original quality.

---

## Class: `Merge`

### `mergeCommandBuilder(self, ffmpeg_path, input1, input2, output, overwrite=False)`

This is a helper method that builds the final `ffmpeg` command string.

```python
    def mergeCommandBuilder(self,ffmpeg_path,input1,input2,output,overwrite=False):
        return f'{ffmpeg_path} {"-y" if overwrite else ""} -i {input1} -i {input2} -c copy {output}'
```
-   **Command Breakdown:**
    -   `{ffmpeg_path}`: The path to the `ffmpeg` executable.
    -   `{"-y" if overwrite else ""}`: This is a conditional part of the f-string. It adds the `-y` flag (which tells `ffmpeg` to automatically overwrite output files) only if the `overwrite` parameter is `True`.
    -   `-i {input1}`: Specifies the first input file (e.g., the decrypted video file).
    -   `-i {input2}`: Specifies the second input file (e.g., the decrypted audio file).
    -   `-c copy`: This is the most important part for efficiency. `-c` is short for `-codec`, and `copy` tells `ffmpeg` to **copy** the streams directly without re-encoding them. This is known as a "remux" operation.
    -   `{output}`: The path for the final, merged output file.

### `ffmpegMerge(self, input1, input2, output, ffmpeg_path="ffmpeg", verbose=False)`

This is the main public method that performs the merge operation.

```python
        input1,input2,output = SysFunc.modify_path(input1),SysFunc.modify_path(input2),SysFunc.modify_path(output)
```
-   `SysFunc.modify_path`: This utility function likely handles path normalization, such as enclosing paths with spaces in quotes, to ensure they are interpreted correctly by the shell.

```python
        if os.path.exists(output):
            debugger.error("Warninbg: Output file already exists. Overwriting...")
            consent = input("Do you want to continue? (y/n): ")
            if consent.lower() != 'y':
                OverwriteAbortedByUser().exit()
```
-   **User Safety:** This block checks if the final output file already exists. To prevent accidental data loss, it prompts the user for consent before overwriting the file. If the user does not enter 'y', it calls the custom `OverwriteAbortedByUser` error to terminate the process cleanly.

```python
        if verbose:
            debugger.debug(f"Running: {self.mergeCommandBuilder(ffmpeg_path,input1,input2,output,overwrite=True)}")
            shell(self.mergeCommandBuilder(ffmpeg_path,input1,input2,output,overwrite=True),filter='.*')
        else:
            shell(self.mergeCommandBuilder(ffmpeg_path,input1,input2,output,overwrite=True), stderr="", stdout="")
```
-   This block executes the merge command.
-   It calls the `mergeCommandBuilder` to get the command string. Note that it hardcodes `overwrite=True` because the user has already given consent in the previous step.
-   It uses the `shell` utility to run the command.
-   If `verbose` is true, it prints the command being run and shows all of its output (`filter='.*'`).
-   If not verbose, it suppresses the `stdout` and `stderr` from `ffmpeg` to keep the console clean.
