# Documentation for `mainLogic/utils/glv.py`

This document provides a line-by-line explanation of the `glv.py` file. This module provides a small set of global utility functions, primarily for colored console output.

## Overview

This module complements `glv_var.py`. While `glv_var` holds the shared *data* and *state*, `glv` provides shared *functionality*. The `Global` class is a collection of static methods for printing colored text to the console, which is used for making the application's output more readable.

---

## Class: `Global`

This class only contains static methods, meaning it's used as a namespace and is not intended to be instantiated.

### `__init__(self, vout=True, outDir="./")`
-   This constructor is present but is not actually used in the application, as the class's methods are all static.

### `set_color(color, style=None)` and `reset()`
-   These are low-level helper methods that directly print the ANSI escape codes to the terminal to change the text color and style. `reset()` changes the color back to the default. They use the `colorama` library, which ensures that these codes work on Windows as well as Linux/macOS.

### `print_colored(text, color, style=None)`
-   This is a convenience wrapper that combines the two methods above. It sets a color, prints the text, and then immediately resets the color.

### `dprint(text)`, `errprint(text)`, `sprint(text)`
-   These are specialized versions of `print_colored` for common use cases:
    -   `dprint`: Prints "debug" text in yellow.
    -   `errprint`: Prints "error" text in red.
    -   `sprint`: Prints "success" text in green.

### `hr()`
```python
    @staticmethod
    def hr():
        if Global.disable_hr:
            return

        columns, _ = shutil.get_terminal_size()
        print("-" * columns)
```
-   **`hr`** stands for "horizontal rule."
-   This method prints a line of dashes (`-`) that spans the entire width of the terminal.
-   `shutil.get_terminal_size()`: This function dynamically gets the current width of the user's console in characters.
-   `Global.disable_hr`: This checks a flag that can be set in the user's preferences. This allows users who might be parsing the script's output to disable these decorative lines. This is a small but thoughtful feature for advanced users.
