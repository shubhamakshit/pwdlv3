# Documentation for `mainLogic/startup/Login/call_login.py`

This document provides a line-by-line explanation of the `call_login.py` file. This module provides the user-facing command-line interface (CLI) for the login process.

## Overview

The `LoginInterface` class is a static class (i.e., it only contains static methods) that handles the user interaction part of logging in. It prompts the user for their phone number and the received OTP, and then uses another module (`sudat.py`) to handle the actual API communication.

---

## Class: `LoginInterface`

### `check_valid_10_dig_number(num)`

```python
    @staticmethod
    def check_valid_10_dig_number(num):
        import re
        return bool(re.match(r'^\d{10}$', num))
```
-   **`@staticmethod`**: This decorator indicates that the method belongs to the class but does not operate on an instance of the class (`self`).
-   **Logic**: It uses a regular expression (`r'^\d{10}$'`) to validate that the input `num` is a string containing exactly 10 digits from start (`^`) to finish (`$`).

### `cli(phone=None, debug=False)`

This is the main method that drives the interactive login process.

```python
        whatsapp = False
        if phone and phone[:2] == "wa":
            whatsapp = True
            phone = phone[2:]
```
-   **Feature Flag:** This block checks if the phone number is prefixed with "wa". This is a hidden feature that allows the user to request the OTP via WhatsApp instead of SMS. If found, it sets a flag and strips the prefix from the number.

```python
        ph_num = phone if phone else (input("Enter your 10 digit phone number: ") if not debug else "1234567890")
```
-   **Input Handling:** This line gets the phone number.
    -   If a `phone` number was passed directly to the function, it uses it.
    -   If not, it prompts the user to `input()` their number.
    -   If it's in `debug` mode, it uses a hardcoded number to bypass the prompt.

```python
        lg = Login(ph_num, debug=debug)
```
-   It instantiates the `Login` class from `sudat.py`, which will handle the API calls.

```python
        if lg.gen_otp(otp_type="wa" if whatsapp else "phone"):
```
-   It calls the `gen_otp` method on the `Login` object, passing the appropriate `otp_type` based on the "wa" prefix check. This triggers the API call to send the OTP to the user.

```python
            if lg.login(input("Enter the OTP: ")):
```
-   If the OTP was sent successfully, it prompts the user to enter the OTP they received.
-   The entered OTP is then passed to the `lg.login()` method, which sends it back to the API for verification.

```python
                token = lg.token
                # ...
                from beta.update import UpdateJSONFile
                u = UpdateJSONFile(PREFS_FILE, debug=debug)
                u.update('token',lg.token)
```
-   **Success Case:** If `lg.login()` returns `True`, it means the login was successful.
-   It retrieves the new authentication `token` from the `lg` object.
-   It then uses a helper class, `UpdateJSONFile`, to save this new token directly into the `preferences.json` file, overwriting the old one.

```python
                try:
                    u.update("user_update_index",u.data.get("user_update_index",0)+1)
                except Exception as e:
                    debugger.error(f" Error updating user_update_index: {e}")
```
-   **Interesting Logic:** This attempts to increment a `user_update_index` in the preferences file. This is likely used by other parts of the application (like the `Syncer`) to detect that user data has changed and that a data re-sync might be necessary.
