# Documentation for `mainLogic/utils/Debugger.py`

This document provides a line-by-line explanation of the `Debugger.py` file. This module provides a powerful, custom logging utility used throughout the application.

## Overview

The standard `print()` function is often insufficient for complex applications. The `Debugger` class was created to provide a more structured, informative, and visually appealing way to log information. Its key features include:
1.  **Log Levels:** Supports different severity levels (INFO, DEBUG, WARNING, ERROR).
2.  **Color-Coded Output:** Uses ANSI escape codes to color-code output based on severity, making logs easier to read.
3.  **Metadata:** Automatically includes timestamps and the location (file and line number) of the log call.
4.  **Variable Inspection:** Provides advanced methods (`var`, `var_dict`, etc.) to intelligently pretty-print variables and data structures.

---

## Class: `Debugger`

### `__init__(self, ...)`
-   The constructor initializes the logger.
-   `enabled`: A global switch to turn all logging on or off.
-   `level`: Sets the minimum severity level to display (e.g., if set to "WARNING", INFO and DEBUG messages will be ignored).
-   `show_time`, `show_location`: Toggles for the metadata.
-   `column_widths`: A dictionary to control the spacing of the output, creating a clean, table-like format.

### `_get_location(self)`
-   **Complex Logic:** This private method uses Python's `inspect` module to "walk" up the call stack.
-   Its goal is to find the first frame in the stack that is **not** inside the `Debugger.py` file itself.
-   This allows it to pinpoint the exact file and line number where the `debugger.info()` (or other logging method) was called from, which is invaluable for tracing code execution.

### `_format(self, level, message)`
-   This method is responsible for assembling the final, formatted log string.
-   It fetches the correct colors from the `COLOR_MAP` dictionary based on the log `level`.
-   It calls `_get_location()` and `time.strftime()` to get the metadata.
-   It uses helper methods (`_ljust_with_ansi`, `_strip_ansi`) to ensure that the columns are perfectly aligned, even with the presence of non-printable ANSI color codes.

### `log(self, message, level="INFO")` and Level-Specific Methods
-   `log()` is the core logging method. It first checks if the logger is enabled and if the message's `level` meets the configured threshold. If so, it calls `_format()` and prints the result.
-   `info()`, `debug()`, `warning()`, `error()`, `success()` are all convenience methods that simply call `log()` with the appropriate `level` string.

### Variable Inspection Methods (`var`, `var_dict`, etc.)

This is the most advanced feature of the `Debugger`. These methods are designed to print variables and their contents in a readable, indented format.

-   **`_get_variable_name(self, var, ...)`**:
    -   **Very Complex Logic:** This is another advanced use of the `inspect` module. It attempts to find the original name of the variable that was passed to the function.
    -   It does this by reading the source code of the line that called the `var()` method and using a regular expression to extract the text inside the parentheses. For example, if the code is `debugger.var(my_variable)`, this method is designed to return the string `"my_variable"`.

-   **`_inspect_var(self, variable, var_name, is_nested=False)`**:
    -   This is the central dispatcher for variable inspection.
    -   It checks the `type` of the variable.
    -   If it's a simple type (like a string or number), it prints it directly.
    -   If it's a complex type (like a dictionary or list), it calls a more specialized inspection method (e.g., `_inspect_dict`).

-   **`_inspect_dict(self, dictionary, ...)`** and **`_inspect_list(self, lst, ...)`**:
    -   These methods handle the pretty-printing of dictionaries and lists.
    -   They print the container's type and size.
    -   They then iterate through the items, recursively calling `_inspect_var` for each item.
    -   They use an `_indent_level` attribute to add indentation for nested structures, making the output look like a clean tree.

-   **`var_dict()`, `var_list()`, etc.**:
    -   These are the public-facing convenience methods. A user can call `debugger.var_dict(my_dict)` to ensure that the variable being inspected is actually a dictionary, providing an extra layer of type safety in debugging.
