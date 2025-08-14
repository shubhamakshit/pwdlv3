# Documentation for `mainLogic/utils/MPDParser.py`

This document provides a line-by-line explanation of the `MPDParser.py` file. This is a crucial utility module responsible for parsing MPEG-DASH manifest files.

## Overview

A DASH manifest (`.mpd` file) is an XML document that describes how a video is structured. It doesn't contain the video itself, but rather the locations of all the small video and audio segments that need to be downloaded. The `MPDParser` class is designed to:
1.  Fetch the `.mpd` file from a given URL.
2.  Parse the complex XML structure.
3.  Extract the URLs for the initialization files and all the individual media segments.

---

## Class: `MPDParser`

### `__init__(self, url, ...)`
-   The constructor stores the manifest `url` and a `signature` (the part of the URL after `?`, which often contains authentication tokens).

### `pre_process(self)`
```python
    def pre_process(self):
        if self.extractSignature:
            if "?" in self.url:
                self.base_url, self.signature = self.url.split("?", 1)
                if self.base_url.endswith("/master.mpd"):
                    self.base_url = self.base_url.split("master.mpd")[0]
```
-   **URL Parsing:** This method intelligently splits the manifest URL into two parts:
    -   `base_url`: The path to the directory on the server containing the media segments (e.g., `https://server.com/path/to/video/`).
    -   `signature`: The query string used for authentication (e.g., `token=...&expires=...`).
-   This is necessary because the segment URLs listed inside the MPD file are often relative, and they need to be combined with the `base_url` and `signature` to be downloaded.

### `build_url(self, media, segment=None)`
-   This is a helper method that constructs a full, downloadable URL for a segment.
-   It takes a relative `media` path (from inside the MPD file) and combines it with the `self.base_url` and `self.signature` extracted earlier.
-   `url = url.replace("$Number$", str(segment))`: This is a key part. The MPD manifest uses a template system. The path for segments is often given as `segment-$Number$.m4s`. This line replaces the `$Number$` placeholder with the actual segment number (e.g., 1, 2, 3...).

### `parse(self)`
```python
    def parse(self):
        manifest_xml = self.load_manifest()
        if manifest_xml:
            self.mpd_dict = self.to_dict(manifest_xml)
```
-   This method orchestrates the parsing. It first calls `self.load_manifest()` to download the raw XML content.
-   Then, it calls `self.to_dict()`, which uses the `xmltodict` library to convert the complex XML string into a much more manageable Python dictionary (`self.mpd_dict`).

### `get_adaptation_sets(self)`
-   In DASH terminology, an "Adaptation Set" is a group of related media streams. For example, there will be one for audio and one for video. This method navigates the parsed dictionary to find and return these sets.

### `get_audio_set(self)` & `get_video_set(self)`
-   These methods filter the adaptation sets to find the one with `@contentType` equal to "audio" or "video", respectively.

### `get_segment_template(self, adaptation_set, ...)`
-   This method dives deeper into an adaptation set to find the `SegmentTemplate`. This is the dictionary that contains the all-important template URLs (`@initialization` and `@media`) and the `@startNumber` for the segments.

### `get_segment_urls(self)`
-   This is the main public method of the class and the final goal of the parsing process.

```python
    def get_segment_urls(self):
        result = {
            'video': {'init': None, 'segments': {}},
            'audio': {'init': None, 'segments': {}}
        }
```
-   It initializes a `result` dictionary to hold the final URLs.

```python
        # Process video segments
        video_set = self.get_video_set()
        video_template, vid_start_number_str, vid_init, vid_media, vid_timescale = self.get_segment_template(video_set, video_type="720")
```
-   It gets the video adaptation set and extracts the segment template information from it.

```python
        result['video']['init'] = self.build_url(vid_init)
```
-   It builds the full URL for the video initialization segment.

```python
        vid_timeline = self.get_timeline_info(video_template)
        # ...
        end = 0
        if vid_timeline:
            for _, S_element in enumerate(vid_timeline):
                if "@r" in S_element:
                    end += int(S_element["@r"])
                end += 1
```
-   **Complex Logic:** This is the most complex part of the parser. The `SegmentTimeline` in the MPD file describes the number and duration of segments.
    -   An `<S>` element represents a segment.
    -   Sometimes, an `<S>` element will have an `@r` attribute, which stands for "repeat". For example, `<S d="2000" r="99" />` means there are 100 segments (1 + 99 repeats) of the same duration.
    -   This loop correctly calculates the total number of segments by accounting for these repeat attributes. The final `end` variable holds the total segment count.

```python
        for i in range(int(vid_start_number_str), end + 1):
            result['video']['segments'][i] = self.build_url(vid_media, i)
```
-   Finally, it loops from the start number to the calculated end number, calling `self.build_url()` for each number to generate the complete list of all video segment URLs.
-   It then repeats this entire process for the audio stream.
-   The method returns the `result` dictionary, which now contains two lists: one of all audio segment URLs and one of all video segment URLs, ready to be passed to the downloader.
