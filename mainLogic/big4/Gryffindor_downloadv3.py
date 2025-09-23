import os
import requests
from urllib.parse import urlparse, unquote
from typing import Dict, Optional, Callable, List, Tuple, Any
from pathlib import Path
import concurrent.futures
from threading import Lock
from mainLogic.error import debugger
from tqdm import tqdm
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DownloadResult:
    init_file: Optional[Path]
    segments_dir: Path
    total_segments: int
    successful_segments: int
    failed_segments: List[int]
    encoded_file: str = ""

class ProgressTracker:
    def __init__(self, total_segments: int, media_type: str, show_tqdm: bool = True):
        self.total = total_segments
        self.current = 0
        self.media_type = media_type
        self.lock = Lock()
        self.failed_segments = []
        if show_tqdm:
            self.pbar = tqdm(
                total=total_segments,
                desc=f"{media_type.capitalize()} Progress",
                unit='segment',
            )
        else:
            self.pbar = None

    def update(self, segment_num: int, success: bool = True) -> Dict:
        with self.lock:
            self.current += 1
            if not success:
                self.failed_segments.append(segment_num)

            if self.pbar:
                self.pbar.update(1)

            return {
                "type": self.media_type,
                "total": self.total,
                "current": self.current,
                "percentage": (self.current / self.total) * 100,
                "segment_num": segment_num,
                "success": success,
                "failed_segments": self.failed_segments.copy(),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }

    def close(self):
        if self.pbar:
            self.pbar.close()

class CombinedProgressTracker:
    def __init__(self, callback: Optional[Callable[[Dict], None]] = None):
        self.callback = callback
        self.lock = Lock()
        self.audio_data = {}
        self.video_data = {}

    def update(self, progress_info: Dict):
        with self.lock:
            media_type = progress_info["type"]

            if media_type == "audio":
                self.audio_data = progress_info
            elif media_type == "video":
                self.video_data = progress_info

            if self.callback:
                combined_data = {
                    "audio": self.audio_data,
                    "video": self.video_data
                }
                self.callback(combined_data)

class DownloaderV3:
    def __init__(
            self,
            tmp_dir: str = "tmp",
            out_dir: str = "output",
            verbose: bool = False,
            progress_callback: Optional[Callable[[Dict], None]] = None,
            max_workers: int = 16,
            audio_dir: Optional[str] = "audio",
            video_dir: Optional[str] = "video",
            show_progress_bar: bool = True
    ):
        self.tmp_dir = Path(tmp_dir)
        self.out_dir = Path(out_dir)
        self.verbose = verbose
        self.progress_callback = progress_callback
        self.max_workers = max(4, min(16, max_workers))
        self.show_progress_bar = show_progress_bar

        self.audio_dir = self.out_dir / audio_dir if audio_dir else self.out_dir
        self.video_dir = self.out_dir / video_dir if video_dir else self.out_dir

        for directory in [self.tmp_dir, self.audio_dir, self.video_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.debugger = debugger
        self.combined_tracker = None

    def _get_file_name_from_url(self, url: str, index: int = 0, media_type: str = "") -> str:
        parsed_url = urlparse(url)
        base_name = unquote(os.path.basename(parsed_url.path))

        if self.audio_dir == self.video_dir:
            return f"{index:04d}-{media_type}-{base_name}"
        return base_name

    def _download_segment(self, url: str, output_path: Path, retry_count: int = 3) -> bool:
        for attempt in range(retry_count):
            try:
                response = requests.get(url, allow_redirects=True)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            except Exception as e:
                if attempt == retry_count - 1:
                    self.debugger.error(f"Failed to download {url}: {str(e)}")
                    return False
                self.debugger.warning(f"Retry {attempt + 1}/{retry_count} for {url}")
        return False

    def _process_segment(self, args: tuple) -> bool:
        url, output_path, segment_num, progress_tracker = args

        success = self._download_segment(url, output_path)
        progress_info = progress_tracker.update(segment_num, success)

        # If we have a combined tracker, use it instead of direct callback
        if self.combined_tracker:
            self.combined_tracker.update(progress_info)
        elif self.progress_callback:
            self.progress_callback(progress_info)

        return success

    def _download_media(self, media_data: Dict, media_type: str, output_dir: Path) -> DownloadResult:
        if not media_data or "segments" not in media_data:
            self.debugger.warning(f"No {media_type} data provided")
            return DownloadResult(None, output_dir, 0, 0, [])

        total_segments = len(media_data["segments"])
        init_file_path = None

        progress_tracker = ProgressTracker(
            total_segments,
            media_type,
            self.show_progress_bar
        )

        # Download init segment first
        if "init" in media_data:
            init_filename = self._get_file_name_from_url(media_data["init"], 0, media_type)
            init_file_path = output_dir / init_filename
            if not self._download_segment(media_data["init"], init_file_path):
                self.debugger.error(f"Failed to download {media_type} init segment")
                return DownloadResult(None, output_dir, total_segments, 0, list(range(1, total_segments + 1)))

        # Prepare segment download tasks
        download_tasks = []
        for segment_num, segment_url in media_data["segments"].items():
            segment_filename = self._get_file_name_from_url(
                segment_url, int(segment_num), media_type
            )
            segment_path = output_dir / segment_filename

            download_tasks.append((
                segment_url,
                segment_path,
                int(segment_num),
                progress_tracker
            ))

        successful_segments = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_segment, task) for task in download_tasks]

            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    successful_segments += 1

        progress_tracker.close()

        return DownloadResult(
            init_file_path,
            output_dir,
            total_segments,
            successful_segments,
            progress_tracker.failed_segments
        )

    def download_audio(self, urls: Dict) -> DownloadResult:
        if not urls.get("audio"):
            self.debugger.warning("No audio URLs provided")
            return DownloadResult(None, self.audio_dir, 0, 0, [])
        return self._download_media(urls["audio"], "audio", self.audio_dir)

    def download_video(self, urls: Dict) -> DownloadResult:
        if not urls.get("video"):
            self.debugger.warning("No video URLs provided")
            return DownloadResult(None, self.video_dir, 0, 0, [])
        return self._download_media(urls["video"], "video", self.video_dir)

    def download_all(self, urls: Dict) -> Dict[str, DownloadResult]:
        # Create a combined progress tracker if we have a callback
        if self.progress_callback:
            self.combined_tracker = CombinedProgressTracker(self.progress_callback)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                audio_future = executor.submit(self.download_audio, urls)
                video_future = executor.submit(self.download_video, urls)

                results = {
                    "audio": audio_future.result(),
                    "video": video_future.result()
                }
        finally:
            # Reset the combined tracker to avoid affecting future downloads
            self.combined_tracker = None

        return results
