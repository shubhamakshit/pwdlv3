# Documentation for `mainLogic/big4/Gryffindor_downloadv3.py`

This document provides a line-by-line explanation of the `Gryffindor_downloadv3.py` file. This module is responsible for the first and most intensive stage of the pipeline: downloading all the necessary video and audio segments.

**Motto:** Gryffindor is known for courage and determination. This downloader bravely faces the task of fetching hundreds of segments concurrently and reliably.

## Overview

The core of this module is the `DownloaderV3` class, which is a modern, multi-threaded downloader designed to fetch DASH (Dynamic Adaptive Streaming over HTTP) video and audio segments efficiently. It uses a thread pool to download multiple segments in parallel, significantly speeding up the process.

---

## Helper Classes

### `DownloadResult`

```python
@dataclass
class DownloadResult:
    init_file: Optional[Path]
    segments_dir: Path
    total_segments: int
    successful_segments: int
    failed_segments: List[int]
    encoded_file: str = ""
```
-   **`@dataclass`**: This is a simple data class used to structure the results of a download operation for a single media type (either audio or video). It provides a clean way to pass information like file paths, segment counts, and success/failure status to the next stage of the pipeline.
-   `encoded_file`: This field is added after the download is complete. It holds the path to the single file created by concatenating all the downloaded segments.

### `ProgressTracker` & `CombinedProgressTracker`

These classes manage the progress reporting for the downloads.

-   **`ProgressTracker`**:
    -   Wraps the `tqdm` library to create and update a progress bar for a single download stream (e.g., just the video segments).
    -   It uses a `threading.Lock` to ensure that progress updates from multiple download threads are handled safely without race conditions.
-   **`CombinedProgressTracker`**:
    -   This class aggregates progress from both the audio and video `ProgressTracker` instances.
    -   It's used to provide a single, unified callback (`progress_callback`) that reports the status of both downloads simultaneously, which is useful for a UI.

---

## Class: `DownloaderV3`

### `__init__(self, ...)`

The constructor initializes the downloader with configuration settings.

-   It takes parameters for temporary and output directories, verbosity, a progress callback function, and the maximum number of worker threads (`max_workers`).
-   It creates the necessary output directories for audio and video.

### `_download_segment(self, url, output_path, retry_count=3)`

This private method handles the download of a single segment.

-   It uses the `requests` library to fetch the content from the given `url`.
-   `response.raise_for_status()`: This is a key line that automatically checks if the HTTP request was successful (i.e., status code 200). If not, it raises an exception.
-   It includes a retry loop (`for attempt in range(retry_count)`) to make the download more resilient to temporary network errors.

### `_process_segment(self, args)`

This method acts as a wrapper that is executed by each thread in the thread pool.

-   It unpacks its arguments, which include the URL, output path, and the shared `progress_tracker` instance.
-   It calls `_download_segment` to perform the actual download.
-   Crucially, after the download attempt, it calls `progress_tracker.update()`. This is how the central progress bar is updated from multiple concurrent threads in a thread-safe manner.

### `_download_media(self, media_data, media_type, output_dir)`

This is the main logic for downloading one entire media stream (either all audio or all video).

```python
        progress_tracker = ProgressTracker(...)
```
-   Creates a `ProgressTracker` instance for this specific media type.

```python
        if "init" in media_data:
            # ... download init segment
```
-   It first downloads the `init` segment, which is a small but essential file required for the media to be decoded correctly.

```python
        download_tasks = []
        for segment_num, segment_url in media_data["segments"].items():
            # ...
            download_tasks.append(...)
```
-   It prepares a list of `download_tasks`. Each task is a tuple containing all the information needed to download one segment (URL, output path, segment number, and a reference to the progress tracker).

```python
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_segment, task) for task in download_tasks]
            # ...
```
-   **Core Logic:** This is where the concurrent downloading happens.
    -   A `ThreadPoolExecutor` is created with the specified number of worker threads.
    -   `executor.submit()` sends each task in the `download_tasks` list to the thread pool for execution. This is non-blocking; the code continues immediately.
    -   `concurrent.futures.as_completed(futures)`: This function waits for any of the threads to finish its task and yields the result. The loop processes results as they become available, which is more efficient than waiting for all of them to complete.

```python
        return DownloadResult(...)
```
-   Once all segments are downloaded, it returns a `DownloadResult` object summarizing the outcome.

### `download_audio(...)`, `download_video(...)`, `download_all(...)`

-   `download_audio` and `download_video` are public methods that simply call `_download_media` with the correct parameters for "audio" or "video".
-   `download_all` is the main public method. It uses another `ThreadPoolExecutor` to run `download_audio` and `download_video` simultaneously in two separate threads, further optimizing the process.
