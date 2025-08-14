# Documentation for `mainLogic/error.py`

This document provides a line-by-line explanation of the `error.py` file. This module establishes a centralized and structured error-handling framework for the application.

## Overview

The purpose of this module is to define a standard way of representing, reporting, and handling errors. It consists of two main components:
1.  **`errorList`**: A dictionary that acts as a registry for all known application errors.
2.  **`PwdlError`**: A custom base exception class from which all specific application errors inherit.

This system ensures that error messages are consistent and that the application can exit with a specific, meaningful error code.

---

## `errorList` Dictionary

This is the central registry for all predictable errors in the application.

```python
errorList = {
    "unknownError": {
        "code": 100,
        "func": lambda: debugger.error("Unknown error. Exiting..."),
        "message_template": "An unknown error has occurred. Please check the logs for details."
    },
    # ... other errors
}
```

-   **Structure:** Each entry in the dictionary represents a specific error and contains three key-value pairs:
    -   `"code"`: A unique integer exit code that the application will terminate with if this error occurs. This is useful for scripting and automated error detection.
    -   `"func"`: A lambda function that is called to log a developer-facing error message to the console. This often includes more technical detail than the user-facing message.
    -   `"message_template"`: A user-friendly message that explains the error. It can contain placeholders (e.g., `{fileName}`) that are filled in when the error is raised.

---

## `PwdlError` Base Class

This is the custom base exception for the application. All specific error classes inherit from it.

```python
class PwdlError(Exception):
    def __init__(self, message, code=999, func=None, verbose=False):
        self.message = message
        self.code = code
        self.func = func
        self.verbose = verbose
        super().__init__(self.message)
```

-   **`__init__`**: The constructor takes the error message, code, and the associated logging function. It calls the parent `Exception` constructor with the message.

```python
    def __str__(self):
        return f"Pwdlv3: {self.message} Failed with code {self.code}"
```
-   **`__str__`**: This method provides a standardized string representation for the error, which is useful for logging.

```python
    def exit(self):
        debugger.error(self.__str__())
        exit(self.code)
```
-   **`exit()`**: This is a critical convenience method. When called, it logs the formatted error message using the `debugger` and then terminates the application with the specific error code. This ensures a consistent exit procedure for all handled errors.

---

## Specific Error Classes

The module then defines a series of classes, one for each error in the `errorList`. These classes inherit from `PwdlError` and make raising specific errors much cleaner and more readable.

```python
class CsvFileNotFound(PwdlError):
    def __init__(self, fileName):
        super().__init__(errorList["csvFileNotFound"]["message_template"].format(fileName=fileName),
                         errorList["csvFileNotFound"]["code"],
                         errorList["csvFileNotFound"]["func"])
```

-   **Example (`CsvFileNotFound`):**
    -   It inherits from `PwdlError`.
    -   Its `__init__` method takes the specific information needed for this error (the `fileName`).
    -   It calls the parent `PwdlError` constructor, pulling the `message_template`, `code`, and `func` directly from the `errorList` dictionary.
    -   It uses `.format(fileName=fileName)` to inject the specific file name into the user-friendly message template.

-   **Usage:** This design makes the error-handling code elsewhere in the application very clean. Instead of manually looking up error codes and messages, a developer can simply do:
    ```python
    # In another file
    from mainLogic.error import CsvFileNotFound

    if not os.path.exists(my_csv_file):
        raise CsvFileNotFound(my_csv_file)
        # Or, to exit immediately:
        # CsvFileNotFound(my_csv_file).exit()
    ```
This approach centralizes error definitions, making them easy to manage and update, while keeping the error-raising logic in the rest of the code simple and readable.
