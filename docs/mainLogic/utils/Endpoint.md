# Documentation for `mainLogic/utils/Endpoint.py`

This document provides a line-by-line explanation of the `Endpoint.py` file. This module provides a simple, reusable wrapper around the `requests` library for making HTTP API calls.

## Overview

The `Endpoint` class is a data structure that encapsulates all the information needed to make a single API request: the URL, HTTP method, headers, and payload. It standardizes the process of fetching data from an API within the application.

---

## Class: `Endpoint`

### `__init__(self, url=None, method='GET', ...)`

-   The constructor initializes an `Endpoint` object.
-   It takes all the standard components of an HTTP request as parameters.
-   It sets default values for common parameters (e.g., `method='GET'`, `headers={}`).

### Dunder Methods (`__str__`, `__repr__`, `__eq__`, etc.)

-   The class implements several "dunder" (double underscore) methods to make it behave like a standard Python data object.
-   `__str__` and `__repr__` provide a clean string representation for logging and debugging.
-   `__eq__` and `__ne__` allow two `Endpoint` objects to be compared for equality.

### `fetch(self)`

This is the main method that executes the HTTP request.

```python
    def fetch(self):
        import requests
        response = requests.request(
            method=self.method,
            url=self.url,
            headers=self.headers,
            data=self.payload,
            files=self.files
        )
```
-   **Local Import:** `requests` is imported locally to keep the module's initial load time fast and to avoid making `requests` a hard dependency for parts of the app that might only import this file without calling `fetch`.
-   `requests.request(...)`: This is the core call to the `requests` library. It's a versatile method that can handle any HTTP method (`GET`, `POST`, etc.) based on the `self.method` attribute. It passes all the stored attributes (headers, payload) directly to the library.

```python
        response_obj = None
        try:
            response_obj = response.json()
        except:
            response_obj = response.text
```
-   **Robust JSON Parsing:** This is a critical piece of error handling.
    -   It first **tries** to parse the response from the server as JSON using `response.json()`.
    -   If the server returns something that isn't valid JSON (like an HTML error page or plain text), `response.json()` would crash. The `except` block catches this and gracefully falls back to treating the response as plain `response.text`.
    -   This makes the `fetch` method resilient to unexpected server responses.

```python
        finally:
            if self.post_function:
                if callable(self.post_function):
                    self.post_function(response_obj)
                else:
                    raise ValueError('post_function must be callable')
```
-   **Callback Functionality:** This `finally` block provides an optional hook.
    -   If a `post_function` was passed to the constructor, it will be called here with the response object.
    -   This allows for custom processing to be attached to an endpoint directly (e.g., logging the result, saving it to a file) without modifying the `Endpoint` class itself.

```python
        return response_obj, response.status_code, response
```
-   The method returns a tuple containing the parsed response object (either a dictionary or a string), the integer HTTP status code (e.g., `200`, `404`), and the original `response` object from the `requests` library, which contains more detailed information if needed.
