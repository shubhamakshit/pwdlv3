import inspect
import os
import time
import re
import traceback

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
        "BLUE": "\033[94m",
        "BRIGHT_BLUE": "\033[1;94m",
        "DIM_BLUE": "\033[2;94m",
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
        "VAR": "BRIGHT_BLUE",
    }

    DIM_COLOR_MAP = {
        "INFO": "DIM_CYAN",
        "SUCCESS": "DIM_GREEN",
        "DEBUG": "DIM_YELLOW",
        "WARNING": "DIM_MAGENTA",
        "ERROR": "DIM_RED",
        "CRITICAL": "DIM_RED",
        "VAR": "DIM_BLUE",
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

    def _get_variable_name(self, var, frame_depth=2):
        """
        Dynamically get the variable name by inspecting the source code.

        Args:
            var: The variable to find the name for
            frame_depth: How many frames to go back to find the caller

        Returns:
            str: The variable name or "unknown" if not found
        """
        try:
            # Get the frame that called this function
            frame = inspect.currentframe()
            for _ in range(frame_depth):
                if frame.f_back is None:
                    break
                frame = frame.f_back

            # Get the line of code that called this function
            context = inspect.getframeinfo(frame).code_context
            if not context:
                return "unknown"

            # Extract the line
            caller_line = context[0].strip()

            # Regular expression to match common variable inspection patterns
            # This captures variable names inside function calls like:
            # debug.var(my_variable), debug.var_dict(my_dict), etc.
            matches = re.findall(r'(?:var\w*)\s*\(\s*([^,)]+)', caller_line)

            if matches:
                return matches[0].strip()

            # Fall back to inspecting local variables
            for var_name, var_val in frame.f_locals.items():
                if var_val is var:
                    return var_name

            return "unknown"

        except Exception:
            return "unknown"
        finally:
            # Ensure we clean up the frame reference to avoid memory leaks
            del frame

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

    # --- Variable inspection methods ---

    def var(self, *args, **kwargs):
        """
        General-purpose variable inspector that accepts multiple variables.

        Args:
            *args: Variables to inspect
            **kwargs: Variables with custom names as keyword arguments

        Usage:
            debug.var(x)                   # Single variable, auto-detected name
            debug.var(x, y, z)             # Multiple variables with auto-detected names
            debug.var(result=x)            # Custom name 'result' for variable x
            debug.var(x, y, result=z)      # Mix of auto-detected and custom names
        """
        # Handle positional arguments (auto-detect names)
        for arg in args:
            var_name = self._get_variable_name(arg)
            self._inspect_var(arg, var_name)

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            self._inspect_var(value, name)

    def _inspect_var(self, variable, var_name):
        """
        Helper method to inspect a single variable

        Args:
            variable: The variable to inspect
            var_name: Name to display for the variable
        """
        var_type = type(variable).__name__

        # For simple types, just show the value
        if isinstance(variable, (int, float, bool, str)):
            value_str = repr(variable)
            self.log(f"{var_name} ({var_type}) = {value_str}", "VAR")

        # For more complex types, use type-specific methods
        elif isinstance(variable, dict):
            self.var_dict(variable, var_name)
        elif isinstance(variable, (list, tuple)):
            self.var_list(variable, var_name)
        elif isinstance(variable, set):
            self.var_set(variable, var_name)
        else:
            # For other objects, show the representation
            value_str = repr(variable)
            self.log(f"{var_name} ({var_type}) = {value_str}", "VAR")

    def var_dict(self, *args, **kwargs):
        """
        Display dictionaries with formatted output

        Args:
            *args: Dictionaries to inspect with auto-detected names
            **kwargs: Dictionaries with custom names as keyword arguments

        Usage:
            debug.var_dict(my_dict)               # Auto-detected name
            debug.var_dict(my_dict, other_dict)   # Multiple dictionaries
            debug.var_dict(config=my_dict)        # Custom name 'config'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            dictionary = args[0]
            var_name = self._get_variable_name(dictionary)
            self._inspect_dict(dictionary, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            if isinstance(arg, dict):
                var_name = self._get_variable_name(arg)
                self._inspect_dict(arg, var_name)
            else:
                var_type = type(arg).__name__
                var_name = self._get_variable_name(arg)
                self.log(f"{var_name} is not a dictionary (got {var_type})", "WARNING")

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            if isinstance(value, dict):
                self._inspect_dict(value, name)
            else:
                var_type = type(value).__name__
                self.log(f"{name} is not a dictionary (got {var_type})", "WARNING")

    def _inspect_dict(self, dictionary, var_name):
        """
        Helper method to inspect a single dictionary

        Args:
            dictionary: The dictionary to inspect
            var_name: Name to display for the dictionary
        """
        self.log(f"{var_name} (dict) with {len(dictionary)} items:", "VAR")

        if not dictionary:
            self.log("  {}", "VAR")
            return

        self.log("{", "VAR")
        for key, value in dictionary.items():
            key_repr = repr(key)
            if isinstance(value, (int, float, bool, str)):
                value_repr = repr(value)
                self.log(f"  {key_repr}: {value_repr}", "VAR")
            else:
                value_type = type(value).__name__
                self.log(f"  {key_repr}: <{value_type}>", "VAR")
        self.log("}", "VAR")

    def var_list(self, *args, **kwargs):
        """
        Display lists or tuples with formatted output

        Args:
            *args: Lists/tuples to inspect with auto-detected names
            **kwargs: Lists/tuples with custom names as keyword arguments

        Usage:
            debug.var_list(my_list)               # Auto-detected name
            debug.var_list(my_list, my_tuple)     # Multiple sequences
            debug.var_list(numbers=my_list)       # Custom name 'numbers'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            lst = args[0]
            var_name = self._get_variable_name(lst)
            self._inspect_list(lst, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            if isinstance(arg, (list, tuple)):
                var_name = self._get_variable_name(arg)
                self._inspect_list(arg, var_name)
            else:
                var_type = type(arg).__name__
                var_name = self._get_variable_name(arg)
                self.log(f"{var_name} is not a list or tuple (got {var_type})", "WARNING")

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                self._inspect_list(value, name)
            else:
                var_type = type(value).__name__
                self.log(f"{name} is not a list or tuple (got {var_type})", "WARNING")

    def _inspect_list(self, lst, var_name):
        """
        Helper method to inspect a single list or tuple

        Args:
            lst: The list or tuple to inspect
            var_name: Name to display for the list or tuple
        """
        container_type = "list" if isinstance(lst, list) else "tuple"
        self.log(f"{var_name} ({container_type}) with {len(lst)} items:", "VAR")

        if not lst:
            self.log(f"  {'[]' if container_type == 'list' else '()'}", "VAR")
            return

        opening = "[" if container_type == "list" else "("
        closing = "]" if container_type == "list" else ")"

        self.log(opening, "VAR")
        for i, item in enumerate(lst):
            if isinstance(item, (int, float, bool, str)):
                item_repr = repr(item)
                self.log(f"  {i}: {item_repr}", "VAR")
            else:
                item_type = type(item).__name__
                self.log(f"  {i}: <{item_type}>", "VAR")
        self.log(closing, "VAR")

    def var_set(self, *args, **kwargs):
        """
        Display sets with formatted output

        Args:
            *args: Sets to inspect with auto-detected names
            **kwargs: Sets with custom names as keyword arguments

        Usage:
            debug.var_set(my_set)            # Auto-detected name
            debug.var_set(set1, set2)        # Multiple sets
            debug.var_set(unique=my_set)     # Custom name 'unique'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            s = args[0]
            var_name = self._get_variable_name(s)
            self._inspect_set(s, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            if isinstance(arg, set):
                var_name = self._get_variable_name(arg)
                self._inspect_set(arg, var_name)
            else:
                var_type = type(arg).__name__
                var_name = self._get_variable_name(arg)
                self.log(f"{var_name} is not a set (got {var_type})", "WARNING")

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            if isinstance(value, set):
                self._inspect_set(value, name)
            else:
                var_type = type(value).__name__
                self.log(f"{name} is not a set (got {var_type})", "WARNING")

    def _inspect_set(self, s, var_name):
        """
        Helper method to inspect a single set

        Args:
            s: The set to inspect
            var_name: Name to display for the set
        """
        self.log(f"{var_name} (set) with {len(s)} items:", "VAR")

        if not s:
            self.log("  {}", "VAR")
            return

        self.log("{", "VAR")
        for i, item in enumerate(s):
            if isinstance(item, (int, float, bool, str)):
                item_repr = repr(item)
                self.log(f"  {item_repr}", "VAR")
            else:
                item_type = type(item).__name__
                self.log(f"  <{item_type}>", "VAR")
        self.log("}", "VAR")

    def var_bool(self, *args, **kwargs):
        """
        Display booleans with formatted output

        Args:
            *args: Booleans to inspect with auto-detected names
            **kwargs: Booleans with custom names as keyword arguments

        Usage:
            debug.var_bool(is_valid)                # Auto-detected name
            debug.var_bool(is_valid, is_admin)      # Multiple booleans
            debug.var_bool(success=is_valid)        # Custom name 'success'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            boolean = args[0]
            var_name = self._get_variable_name(boolean)
            self._inspect_bool(boolean, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            if isinstance(arg, bool):
                var_name = self._get_variable_name(arg)
                self._inspect_bool(arg, var_name)
            else:
                var_type = type(arg).__name__
                var_name = self._get_variable_name(arg)
                self.log(f"{var_name} is not a boolean (got {var_type})", "WARNING")

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            if isinstance(value, bool):
                self._inspect_bool(value, name)
            else:
                var_type = type(value).__name__
                self.log(f"{name} is not a boolean (got {var_type})", "WARNING")

    def _inspect_bool(self, boolean, var_name):
        """
        Helper method to inspect a single boolean

        Args:
            boolean: The boolean to inspect
            var_name: Name to display for the boolean
        """
        value_str = str(boolean)
        self.log(f"{var_name} (bool) = {value_str}", "VAR")

    def var_num(self, *args, **kwargs):
        """
        Display numbers with formatted output

        Args:
            *args: Numbers to inspect with auto-detected names
            **kwargs: Numbers with custom names as keyword arguments

        Usage:
            debug.var_num(count)                # Auto-detected name
            debug.var_num(x, y, z)              # Multiple numbers
            debug.var_num(total=sum_value)      # Custom name 'total'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            number = args[0]
            var_name = self._get_variable_name(number)
            self._inspect_num(number, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            if isinstance(arg, (int, float)):
                var_name = self._get_variable_name(arg)
                self._inspect_num(arg, var_name)
            else:
                var_type = type(arg).__name__
                var_name = self._get_variable_name(arg)
                self.log(f"{var_name} is not a number (got {var_type})", "WARNING")

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            if isinstance(value, (int, float)):
                self._inspect_num(value, name)
            else:
                var_type = type(value).__name__
                self.log(f"{name} is not a number (got {var_type})", "WARNING")

    def _inspect_num(self, number, var_name):
        """
        Helper method to inspect a single number

        Args:
            number: The number to inspect
            var_name: Name to display for the number
        """
        num_type = "int" if isinstance(number, int) else "float"
        self.log(f"{var_name} ({num_type}) = {number}", "VAR")

    def var_str(self, *args, **kwargs):
        """
        Display strings with formatted output

        Args:
            *args: Strings to inspect with auto-detected names
            **kwargs: Strings with custom names as keyword arguments

        Usage:
            debug.var_str(name)                 # Auto-detected name
            debug.var_str(first, last)          # Multiple strings
            debug.var_str(greeting=message)     # Custom name 'greeting'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            string = args[0]
            var_name = self._get_variable_name(string)
            self._inspect_str(string, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            if isinstance(arg, str):
                var_name = self._get_variable_name(arg)
                self._inspect_str(arg, var_name)
            else:
                var_type = type(arg).__name__
                var_name = self._get_variable_name(arg)
                self.log(f"{var_name} is not a string (got {var_type})", "WARNING")

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            if isinstance(value, str):
                self._inspect_str(value, name)
            else:
                var_type = type(value).__name__
                self.log(f"{name} is not a string (got {var_type})", "WARNING")

    def _inspect_str(self, string, var_name):
        """
        Helper method to inspect a single string

        Args:
            string: The string to inspect
            var_name: Name to display for the string
        """
        self.log(f"{var_name} (str) length={len(string)}", "VAR")
        self.log(f'  "{string}"', "VAR")

    def var_type(self, *args, **kwargs):
        """
        Display the type hierarchy of objects

        Args:
            *args: Objects to inspect with auto-detected names
            **kwargs: Objects with custom names as keyword arguments

        Usage:
            debug.var_type(obj)                 # Auto-detected name
            debug.var_type(obj1, obj2)          # Multiple objects
            debug.var_type(instance=obj)        # Custom name 'instance'
        """
        # If no kwargs and only one positional arg, use legacy behavior
        if len(args) == 1 and not kwargs:
            obj = args[0]
            var_name = self._get_variable_name(obj)
            self._inspect_type(obj, var_name)
            return

        # Handle positional arguments (auto-detect names)
        for arg in args:
            var_name = self._get_variable_name(arg)
            self._inspect_type(arg, var_name)

        # Handle keyword arguments (custom names)
        for name, value in kwargs.items():
            self._inspect_type(value, name)

    def _inspect_type(self, obj, var_name):
        """
        Helper method to inspect the type of a single object

        Args:
            obj: The object to inspect
            var_name: Name to display for the object
        """
        mro = type(obj).__mro__
        type_names = [t.__name__ for t in mro]
        self.log(f"{var_name} type hierarchy:", "VAR")
        for i, name in enumerate(type_names):
            indent = "  " * i
            self.log(f"{indent}└─ {name}", "VAR")