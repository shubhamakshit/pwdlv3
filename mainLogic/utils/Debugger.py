import inspect
import os
import time
import re

class Debugger:
    COLORS = {
        "CYAN": "\033[96m",
        "BRIGHT_CYAN": "\033[1;96m",
        "DIM_CYAN": "\033[2;96m",
        "YELLOW": "\033[93m",
        "BRIGHT_YELLOW": "\033[1;93m",
        "DIM_YELLOW": "\033[2;93m",
        "MAGENTA": "\033[95m",
        "BRIGHT_MAGENTA": "\033[1;95m",
        "DIM_MAGENTA": "\033[2;95m",
        "RED": "\033[91m",
        "BRIGHT_RED": "\033[1;91m",
        "DIM_RED": "\033[2;91m",
        "GREEN": "\033[92m",
        "BRIGHT_GREEN": "\033[1;92m",
        "DIM_GREEN": "\033[2;92m",
        "RESET": "\033[0m",
    }

    LEVELS = {
        "INFO": 0,
        "SUCCESS": 0,
        "DEBUG": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4,
    }

    COLOR_MAP = {
        "INFO": "BRIGHT_CYAN",
        "SUCCESS": "BRIGHT_GREEN",
        "DEBUG": "BRIGHT_YELLOW",
        "WARNING": "BRIGHT_MAGENTA",
        "ERROR": "BRIGHT_RED",
        "CRITICAL": "BRIGHT_RED",
    }

    DIM_COLOR_MAP = {
        "INFO": "DIM_CYAN",
        "SUCCESS": "DIM_GREEN",
        "DEBUG": "DIM_YELLOW",
        "WARNING": "DIM_MAGENTA",
        "ERROR": "DIM_RED",
        "CRITICAL": "DIM_RED",
    }

    def __init__(self, enabled=True, level="INFO", show_time=True, show_location=True, column_widths=None):
        self.enabled = enabled
        self.level = self.LEVELS.get(level.upper(), 0)
        self.show_time = show_time
        self.show_location = show_location
        self.column_widths = column_widths or {"level": 10, "time": 20, "location": 20, "message": 50}

        # To ensure consistent spacing, we need to track actual visible text lengths
        # when ANSI color codes are used
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def _get_location(self):
        """
        Get the location of the calling code outside of the Debugger class.
        """
        # Get the frame at the specified depth
        current_frame = inspect.currentframe()

        # Find the caller frame (outside of the Debugger class)
        caller_frame = current_frame
        for _ in range(10):  # Limit to 10 frames to avoid infinite loop
            if caller_frame.f_back is None:
                break

            caller_frame = caller_frame.f_back
            # Get the code object for the frame
            code = caller_frame.f_code

            # If this frame is not from Debugger.py, we've found our caller
            if os.path.basename(code.co_filename) != "Debugger.py":
                break

        filename = os.path.basename(caller_frame.f_code.co_filename)
        lineno = caller_frame.f_lineno
        return f"{filename}:{lineno}"

    def _strip_ansi(self, text):
        """Remove ANSI escape sequences from text to get true visible length"""
        return self.ansi_escape.sub('', text)

    def _ljust_with_ansi(self, text, width):
        """Left justify text accounting for ANSI color codes"""
        visible_text = self._strip_ansi(text)
        padding = max(0, width - len(visible_text))
        return text + ' ' * padding

    def _format(self, level, message):
        parts = []

        # Get the dim color for the level
        dim_color = self.COLORS.get(self.DIM_COLOR_MAP.get(level, ""), "")
        # Get the bright color for the message
        bright_color = self.COLORS.get(self.COLOR_MAP.get(level, ""), "")
        reset = self.COLORS["RESET"]

        # Format level with consistent padding regardless of ANSI codes
        level_text = f"{dim_color}[{level}]{reset}"
        level_str = self._ljust_with_ansi(level_text, self.column_widths["level"])

        # Format other components
        time_text = time.strftime("[%Y-%m-%d %H:%M:%S]") if self.show_time else ""
        time_str = self._ljust_with_ansi(time_text, self.column_widths["time"])

        location_text = f"[{self._get_location()}]" if self.show_location else ""
        location_str = self._ljust_with_ansi(location_text, self.column_widths["location"])

        message_str = f"{bright_color}{message}{reset}"

        # Combine into a table-like structure
        parts.append(f"{level_str} {time_str} {location_str} {message_str}")

        return "".join(parts)

    def log(self, message, level="INFO"):
        if not self.enabled or self.LEVELS.get(level, 0) < self.level:
            return

        print(self._format(level, message))

    def info(self, message):
        self.log(message, "INFO")

    def debug(self, message):
        self.log(message, "DEBUG")

    def warning(self, message):
        self.log(message, "WARNING")

    def error(self, message):
        self.log(message, "ERROR")

    def critical(self, message):
        self.log(message, "CRITICAL")

    def success(self, message):
        self.log(message, "SUCCESS")