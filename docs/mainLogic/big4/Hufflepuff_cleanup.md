# Documentation for `mainLogic/big4/Hufflepuff_cleanup.py`

This document provides a line-by-line explanation of the `Hufflepuff_cleanup.py` file. This module is responsible for the final stage of the "Big 4" pipeline: cleaning up all intermediate files.

**Motto:** Hufflepuff values hard work, patience, and justice. This module works patiently in the background to ensure the workspace is left just and tidy.

## Overview

The `Clean` class provides a simple and straightforward way to remove the temporary files created during the download and decryption process. Its main goal is to leave only the final merged video file in the output directory, removing all the intermediate artifacts.

---

## Class: `Clean`

### `removeFile(self, file, verbose)`

This is a private helper method that safely removes a single file.

```python
    def removeFile(self,file,verbose):
        from mainLogic.utils.glv_var import debugger
        try:
            os.remove(file)
            if verbose: debugger.success(f"Removed file: {file}")
        except:
            from mainLogic.utils.glv_var import debugger
            debugger.error(f"Could not remove file: {file}")
```
-   **Local Import:** The `debugger` is imported inside the method. While this works, it's unconventional. A module-level import is more standard.
-   **Error Handling:** It uses a `try...except` block to handle the file removal. This is important because a file might have already been deleted or might not have been created in the first place if a previous step failed. The `except` block prevents the entire script from crashing if a single file can't be removed.
-   It logs a success or error message depending on the outcome.

### `remove(self, path, file, verbose=True)`

This is the main public method that orchestrates the cleanup of all temporary files.

```python
    def remove(self,path,file,verbose=True):
        audio_enc = f"{path}/{file}-Audio-enc.mp4"
        video_enc = f"{path}/{file}-Video-enc.mp4"

        audio = f"{path}/{file}-Audio.mp4"
        video = f"{path}/{file}-Video.mp4"
```
-   **File Path Construction:** It constructs the full paths to the four main intermediate files that need to be deleted:
    1.  `audio_enc`: The concatenated, encrypted audio file.
    2.  `video_enc`: The concatenated, encrypted video file.
    3.  `audio`: The decrypted, but separate, audio file.
    4.  `video`: The decrypted, but separate, video file.

-   The rest of the method is a series of calls to the `self.removeFile()` helper for each of the files listed above, with logging messages in between if `verbose` mode is active. This ensures that all temporary artifacts from the download and decryption stages are removed, leaving only the final merged product.
