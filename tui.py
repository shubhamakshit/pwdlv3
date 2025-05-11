import os
import time
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional, Callable
from pathlib import Path
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.live import Live
from rich.table import Table
from rich.text import Text
import concurrent.futures

from mainLogic.big4 import Gryffindor_downloadv3
from mainLogic.big4.Gryffindor_downloadv3 import DownloadResult


class DownloaderTUI:
    """Advanced Terminal User Interface for the Downloader using rich library"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console()
        self.lock = Lock()
        self.log_messages: List[Dict] = []
        self.max_log_lines = 20

        # Progress trackers
        self.audio_progress = None
        self.audio_task_id = None
        self.video_progress = None
        self.video_task_id = None

        # Stats
        self.audio_stats = {"total": 0, "successful": 0, "failed": []}
        self.video_stats = {"total": 0, "successful": 0, "failed": []}
        self.download_start_time = None

        # Layout elements
        self.layout = self._make_layout()
        self.progress_container = Progress()
        self.live = None

    def _make_layout(self) -> Layout:
        """Create the layout structure for the TUI"""
        layout = Layout(name="root")

        # Split the screen into top and bottom sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )

        # Split the main section into status and logs
        layout["main"].split_row(
            Layout(name="status", ratio=1),
            Layout(name="logs", ratio=2)
        )

        # Split the status section into progress and stats
        layout["status"].split(
            Layout(name="progress", ratio=1),
            Layout(name="stats", ratio=1)
        )

        return layout

    def start(self):
        """Initialize and start the live display"""
        self.download_start_time = time.time()

        # Initialize progress tracking
        self.progress_container = Progress()

        # Create the live display
        self.live = Live(
            self._generate_layout(),
            refresh_per_second=4,
            console=self.console
        )
        self.live.start()

    def stop(self):
        """Stop the live display"""
        if self.live:
            self.live.stop()

    def log(self, message: str, level: str = "INFO"):
        """Add a log message"""
        with self.lock:
            timestamp = datetime.utcnow().strftime("%H:%M:%S")

            # Set color based on level
            if level == "ERROR":
                color = "red"
            elif level == "WARNING":
                color = "yellow"
            elif level == "DEBUG":
                color = "blue"
            else:
                color = "green"

            self.log_messages.append({
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "color": color
            })

            # Keep logs to the maximum number
            while len(self.log_messages) > self.max_log_lines:
                self.log_messages.pop(0)

            self._update_display()

    def _update_display(self):
        """Update the live display with current state"""
        if self.live:
            self.live.update(self._generate_layout())

    def _generate_layout(self):
        """Generate the complete layout with current state"""
        # Header
        header_text = Text("Media Downloader", style="bold white on blue")
        elapsed = ""
        if self.download_start_time:
            elapsed_secs = int(time.time() - self.download_start_time)
            elapsed = f" • Elapsed: {elapsed_secs // 60}m {elapsed_secs % 60}s"
        header_text.append(elapsed, style="white on blue")
        self.layout["header"].update(Panel(header_text, border_style="blue"))

        # Progress section
        progress_panel = self._generate_progress_panel()
        self.layout["progress"].update(progress_panel)

        # Stats section
        stats_panel = self._generate_stats_panel()
        self.layout["stats"].update(stats_panel)

        # Logs section
        logs_panel = self._generate_logs_panel()
        self.layout["logs"].update(logs_panel)

        # Footer
        footer_text = Text("Press Ctrl+C to cancel", style="italic")
        self.layout["footer"].update(Panel(footer_text))

        return self.layout

    def _generate_progress_panel(self):
        """Generate the progress panel with progress bars"""
        progress = Progress()

        # Re-create audio progress bar if needed
        if self.audio_stats["total"] > 0:
            audio_task = progress.add_task(
                "[cyan]Audio Download",
                total=self.audio_stats["total"],
                completed=self.audio_stats["successful"] + len(self.audio_stats["failed"])
            )

        # Re-create video progress bar if needed
        if self.video_stats["total"] > 0:
            video_task = progress.add_task(
                "[magenta]Video Download",
                total=self.video_stats["total"],
                completed=self.video_stats["successful"] + len(self.video_stats["failed"])
            )

        return Panel(progress, title="Download Progress", border_style="green")

    def _generate_stats_panel(self):
        """Generate the stats panel with download statistics"""
        table = Table(show_header=True, header_style="bold")
        table.add_column("Media")
        table.add_column("Total")
        table.add_column("Successful")
        table.add_column("Failed")
        table.add_column("Completion")

        # Add audio stats
        if self.audio_stats["total"] > 0:
            completion = 100 * (self.audio_stats["successful"] + len(self.audio_stats["failed"])) / self.audio_stats["total"]
            table.add_row(
                "Audio",
                str(self.audio_stats["total"]),
                str(self.audio_stats["successful"]),
                str(len(self.audio_stats["failed"])),
                f"{completion:.1f}%"
            )

        # Add video stats
        if self.video_stats["total"] > 0:
            completion = 100 * (self.video_stats["successful"] + len(self.video_stats["failed"])) / self.video_stats["total"]
            table.add_row(
                "Video",
                str(self.video_stats["total"]),
                str(self.video_stats["successful"]),
                str(len(self.video_stats["failed"])),
                f"{completion:.1f}%"
            )

        return Panel(table, title="Download Statistics", border_style="green")

    def _generate_logs_panel(self):
        """Generate the logs panel with colorized log messages"""
        log_text = Text()

        for log in self.log_messages:
            timestamp = log["timestamp"]
            level = log["level"]
            message = log["message"]
            color = log["color"]

            log_text.append(f"[{timestamp}] ", style="dim")
            log_text.append(f"[{level}] ", style=f"bold {color}")
            log_text.append(f"{message}\n", style=color if level != "INFO" else "")

        return Panel(log_text, title="Logs", border_style="blue")

    def setup_audio_progress(self, total_segments: int):
        """Setup the audio progress tracking"""
        with self.lock:
            self.audio_stats["total"] = total_segments
            self.audio_stats["successful"] = 0
            self.audio_stats["failed"] = []
            self._update_display()

    def setup_video_progress(self, total_segments: int):
        """Setup the video progress tracking"""
        with self.lock:
            self.video_stats["total"] = total_segments
            self.video_stats["successful"] = 0
            self.video_stats["failed"] = []
            self._update_display()

    def update_progress(self, media_type: str, segment_num: int, success: bool):
        """Update progress for a specific media type"""
        with self.lock:
            if media_type == "audio":
                stats = self.audio_stats
            else:  # video
                stats = self.video_stats

            if success:
                stats["successful"] += 1
            else:
                stats["failed"].append(segment_num)

            self._update_display()

            # Return progress info in the same format as before
            return {
                "type": media_type,
                "total": stats["total"],
                "current": stats["successful"] + len(stats["failed"]),
                "percentage": ((stats["successful"] + len(stats["failed"])) / stats["total"]) * 100 if stats["total"] > 0 else 0,
                "segment_num": segment_num,
                "success": success,
                "failed_segments": stats["failed"].copy(),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }

# Modified ProgressTracker to work with the new TUI
class ProgressTracker:
    def __init__(self, total_segments: int, media_type: str, tui: DownloaderTUI, show_tqdm: bool = False):
        self.total = total_segments
        self.current = 0
        self.media_type = media_type
        self.lock = Lock()
        self.failed_segments = []
        self.tui = tui

        # Setup progress in TUI
        if media_type == "audio":
            self.tui.setup_audio_progress(total_segments)
        else:
            self.tui.setup_video_progress(total_segments)

        self.tui.log(f"Starting {media_type} download: {total_segments} segments", "INFO")

    def update(self, segment_num: int, success: bool = True) -> Dict:
        with self.lock:
            self.current += 1
            if not success:
                self.failed_segments.append(segment_num)

            # Log the update
            msg = f"{self.media_type} segment {segment_num} {'✓' if success else '✗'}"
            if not success:
                self.tui.log(msg, "ERROR")
            elif self.tui.verbose:
                self.tui.log(msg, "DEBUG")

            # Update TUI progress
            return self.tui.update_progress(self.media_type, segment_num, success)

    def close(self):
        self.tui.log(f"{self.media_type.capitalize()} download complete: {self.current - len(self.failed_segments)}/{self.total} segments successful", "INFO")

# Example of how to modify the DownloaderV3 class to use the new TUI
def update_downloader_v3_with_tui(downloader:Gryffindor_downloadv3.DownloaderV3):
    # Replace the TerminalOutput with our new TUI
    downloader.terminal = DownloaderTUI(downloader.verbose)
    downloader.terminal.start()

    # Override the original _download_media method to use our new ProgressTracker
    #   original_download_media = downloader._download_media

    def _download_media_with_tui(media_data, media_type, output_dir):
        # Same implementation but using our TUI-enabled ProgressTracker
        if not media_data or "segments" not in media_data:
            downloader.terminal.log(f"No {media_type} data provided", "WARNING")
            downloader.debugger.warning(f"No {media_type} data provided")
            return DownloadResult(None, output_dir, 0, 0, [])

        total_segments = len(media_data["segments"])
        init_file_path = None

        progress_tracker = ProgressTracker(
            total_segments,
            media_type,
            downloader.terminal,
            False  # No need for tqdm progress bars
        )

        # Rest of the original _download_media implementation...
        # Download init segment first
        if "init" in media_data:
            init_filename = downloader._get_file_name_from_url(media_data["init"], 0, media_type)
            init_file_path = output_dir / init_filename
            if not downloader._download_segment(media_data["init"], init_file_path):
                downloader.terminal.log(f"Failed to download {media_type} init segment", "ERROR")
                downloader.debugger.error(f"Failed to download {media_type} init segment")
                return DownloadResult(None, output_dir, total_segments, 0, list(range(1, total_segments + 1)))

            downloader.terminal.log(f"Downloaded {media_type} init segment: {init_filename}", "INFO")
            if downloader.verbose:
                downloader.debugger.info(f"Downloaded {media_type} init segment: {init_filename}")

        # Prepare segment download tasks
        download_tasks = []
        for segment_num, segment_url in media_data["segments"].items():
            segment_filename = downloader._get_file_name_from_url(
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=downloader.max_workers) as executor:
            futures = [executor.submit(downloader._process_segment, task) for task in download_tasks]

            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    successful_segments += 1

        # Final status update
        downloader.terminal.log(
            f"{media_type.capitalize()} download complete: {successful_segments}/{total_segments} segments successful",
            "INFO"
        )

        progress_tracker.close()

        return DownloadResult(
            init_file_path,
            output_dir,
            total_segments,
            successful_segments,
            progress_tracker.failed_segments
        )

    # Replace the original method with our enhanced version
    downloader._download_media = _download_media_with_tui

    # Make sure to stop the TUI when done
    original_download_all = downloader.download_all
    def download_all_with_tui(urls):
        try:
            return original_download_all(urls)
        finally:
            downloader.terminal.stop()

    downloader.download_all = download_all_with_tui

    return downloader

# Usage example:
"""
# Import the original downloader
from mainLogic.downloader import DownloaderV3

# Create the downloader
downloader = DownloaderV3(
    tmp_dir="tmp",
    out_dir="output",
    verbose=True,
    max_workers=8
)

# Apply our TUI enhancements
downloader = update_downloader_v3_with_tui(downloader)

# Use the enhanced downloader
results = downloader.download_all(urls_dict)
"""