# `login.py`

This script defines the routes for user authentication, including sending and verifying OTPs.

## Blueprint

The script creates a Flask Blueprint named `login`.

```python
login = Blueprint('login', __name__)
```

## Routes

### `/api/otp` or `/otp`

*   **Description:** Sends an OTP to the user's phone number.
*   **Method:** `POST`
*   **Request Body:** A JSON object containing the following field:
    *   `phone` (str): The user's 10-digit phone number.
*   **Returns:** A success message if the OTP is sent successfully, or an error message if the phone number is invalid or the OTP fails to send.

### `/api/verify-otp` or `/verify-otp`

*   **Description:** Verifies the OTP entered by the user.
*   **Method:** `POST`
*   **Request Body:** A JSON object containing the following fields:
    *   `phone` (str): The user's 10-digit phone number.
    *   `otp` (str): The OTP entered by the user.
*   **Returns:** A success message and the user's token if the OTP is verified successfully. Otherwise, it returns an error message.
*   **Functionality:**
    *   Retrieves the phone number and OTP from the request body.
    *   Verifies the OTP using the `Login` class.
    *   If the OTP is valid, it updates the user's token in the `defaults.json` file.
    *   It also increments the `user_update_index` in the `defaults.json` file.
