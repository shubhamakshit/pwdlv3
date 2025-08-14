# Documentation for `mainLogic/main.py`

This document provides a line-by-line explanation of the `main.py` file, which serves as the central orchestrator for the entire download pipeline.

## Overview

The `Main` class in this file is the heart of the download process. It's instantiated with all the necessary configuration and data (like video ID, token, paths), and its `process()` method executes the entire workflow—from fetching keys to downloading, decrypting, merging, and cleaning up.

---

## Class: `Main`

### `__init__(self, ...)`

This is the constructor for the `Main` class. It initializes the state required for a download job.

```python
class Main:
    def __init__(self,
                 id,
                 name=None,
                 batch_name=None,
                 topic_name=None,
                 lecture_url=None,
                 directory="./",
                 tmpDir="/*auto*/",
                 vsdPath='nm3',
                 ffmpeg="ffmpeg",
                 mp4d="mp4decrypt",
                 tui=True,
                 token=None, random_id=None, verbose=True, suppress_exit=False, progress_callback=None):
```

-   **Parameters:**
    -   `id`, `name`, `batch_name`, `topic_name`, `lecture_url`: Core metadata about the video to be downloaded.
    -   `directory`: The final output directory for the merged video.
    -   `tmpDir`: The directory for storing intermediate files. The special value `/*auto*/` signifies that a default path (`./tmp/`) should be used.
    -   `ffmpeg`, `mp4d`: Paths to the required command-line tools.
    -   `tui`: A boolean to enable/disable the Text-based User Interface for progress.
    -   `token`, `random_id`: Authentication credentials.
    -   `verbose`, `suppress_exit`, `progress_callback`: Control flags for output verbosity, error handling behavior, and progress reporting.

```python
        os2 = SysFunc()
```
-   Instantiates `SysFunc` from `utils/os2.py`, a helper class for OS-level operations like creating directories.

```python
        self.tmpDir = BasicUtils.abspath(tmpDir) if tmpDir != '/*auto*/' else BasicUtils.abspath('./tmp/')
```
-   **Complex Logic:** This line resolves the temporary directory path. If `tmpDir` is the special string `/*auto*/`, it defaults to `./tmp/`. Otherwise, it uses the provided path. `BasicUtils.abspath` ensures the path is absolute.

```python
        try:
            os2.create_dir(self.tmpDir, verbose=verbose)
        except Exception as e:
            if verbose:
                debugger.error(f"Error creating tmp directory: {e}")
                self.tmpDir = "./"
```
-   Safely creates the temporary directory. If it fails (e.g., due to permissions), it gracefully falls back to using the current directory.

### `process(self)`

This is the main method that executes the entire download pipeline step-by-step.

```python
        TOKEN = self.token
        RANDOM_ID = self.random_id
        fetcher = LicenseKeyFetcher(TOKEN, RANDOM_ID)
```
-   Initializes the `LicenseKeyFetcher` with the user's credentials, preparing to fetch the decryption key.

```python
        try:
            # ... (verbose logging)
            key = fetcher.get_key(
                id=self.id,batch_name=self.batch_name,khazana_topic_name=self.topic_name,khazana_url=self.lecture_url,
                verbose=self.verbose)[1]
            cookies = fetcher.cookies
        except Exception as e:
            raise TypeError(f"ID is invalid (if the token is valid) ")
```
-   **Key Step:** This block calls `fetcher.get_key()` to perform one of the most critical tasks: communicating with the API to get the decryption key.
-   It passes all relevant IDs and names. The `[1]` at the end is important: `get_key` returns a tuple `(kid, key, url)`, and this selects only the `key`.
-   If this step fails, it raises a `TypeError`, indicating a fundamental issue with the video ID or token.

```python
        urls = MPDParser(fetcher.url).pre_process().parse().get_segment_urls()
```
-   **Method Chaining:** This line elegantly uses method chaining to process the video manifest:
    1.  `MPDParser(fetcher.url)`: Initializes the parser with the MPD URL obtained from the `fetcher`.
    2.  `.pre_process()`: Cleans up the URL.
    3.  `.parse()`: Downloads and parses the XML content of the manifest.
    4.  `.get_segment_urls()`: Extracts the list of all video and audio segment URLs.

```python
        download_out_dir = os.path.join(self.tmpDir, self.id)
```
-   Defines a unique temporary subdirectory for this specific download, preventing conflicts between concurrent downloads.

```python
        downloader = DownloaderV3(...)
```
-   Initializes the modern, multi-threaded downloader from `Gryffindor_downloadv3.py`.

```python
        if self.tui:
            downloader = update_downloader_v3_with_tui(downloader)
```
-   If the TUI is enabled, this line "decorates" or wraps the downloader instance with TUI capabilities, allowing it to render progress bars in the terminal.

```python
        results = downloader.download_all(urls)
```
-   Starts the download of all video and audio segments concurrently. `results` will be a dictionary containing `DownloadResult` objects for both audio and video.

```python
        for media_type, result in results.items():
            # ... (logging)
            results[media_type].encoded_file = SysFunc.concatenate_mp4_segments(str(result.segments_dir),output_filename=f"{self.name}-{media_type.title()}-enc.mp4",cleanup=True)
```
-   After downloading, this loop iterates through the audio and video results.
-   **Key Step:** `SysFunc.concatenate_mp4_segments` is called to combine the many small downloaded segment files into a single, larger encrypted file (e.g., `My-Video-Video-enc.mp4`). The `cleanup=True` argument ensures the individual segment files are deleted after concatenation.
-   The path to this new concatenated file is stored back in the `results` dictionary for the next stage.

```python
        decrypt = Decrypt()
        decrypted_audio = decrypt.decryptAudio(...)
        decrypted_video = decrypt.decryptVideo(...)
```
-   Initializes the `Decrypt` class and calls it twice—once for the encrypted audio file and once for the video file—using the `key` obtained earlier. This produces two decrypted files.

```python
        try:
            import shutil
            shutil.rmtree(download_out_dir, ignore_errors=True)
        except Exception as e:
            debugger.error(f"Failed to remove temp dir {download_out_dir}")
```
-   This block cleans up the temporary directory that held the downloaded segments. `ignore_errors=True` makes this a robust, non-blocking operation.

```python
        merge = Merge()
        merge.ffmpegMerge(...)
```
-   Initializes the `Merge` class and calls `ffmpegMerge` to combine the decrypted audio and video files into the final, playable MP4 file.

```python
        clean = Clean()
        clean.remove(self.directory, f'{self.name}', self.verbose)
```
-   Initializes the `Clean` class and calls `remove` to delete the last remaining intermediate files (the separate decrypted audio and video files), completing the pipeline.
