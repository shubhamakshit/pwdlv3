# Documentation for `mainLogic/big4/Ravenclaw_decrypt/key.py`

This document provides a line-by-line explanation of the `key.py` file. This is arguably one of the most complex and critical modules in the entire application. It is responsible for reverse-engineering the platform's license protocol to acquire the decryption key for a given video.

**Motto:** Ravenclaw is known for wisdom, wit, and intellect. This module embodies that spirit by unraveling the complex, multi-step process the platform uses to protect its content keys.

## Overview

The `LicenseKeyFetcher` class encapsulates the entire logic for obtaining the video decryption key. The process involves several steps:
1.  Getting a signed URL for the video manifest.
2.  Parsing the manifest to find the Key ID (`kid`).
3.  Performing a series of cryptographic transformations on the `kid` and the user's `token` to generate a one-time password (OTP).
4.  Using this OTP to make a final license request to get the actual decryption key.

---

## Class: `LicenseKeyFetcher`

### `__init__(self, token, random_id)`
-   The constructor simply stores the user's authentication `token` and a `random_id`, which are required for the API requests.

### Cryptographic and Encoding Helpers

These methods are small, specialized helpers used in the key generation algorithm.

-   **`key_char_at(self, key, i)`**: A simple helper to get the character code from a key, wrapping around if the index `i` is larger than the key length.
-   **`b64_encode(self, data)`**: A standard Base64 encoder.
-   **`xor_encrypt(self, data)`**:
    ```python
    return [ord(c) ^ self.key_char_at(self.token, i) for i, c in enumerate(data)]
    ```
    -   **Complex Logic:** This is not standard encryption, but a custom XOR cipher. It iterates through the input `data` string and XORs the character code of each character with a character from the user's `token`. This is a reversible operation that obfuscates the data.
-   **`insert_zeros(self, hex_string)`**:
    ```python
    result = "00"
    for i in range(0, len(hex_string), 2):
        result += hex_string[i:i+2]
        if i + 2 < len(hex_string):
            result += "00"
    return result
    ```
    -   **Non-obvious Logic:** This function takes a hex string (e.g., "aabbcc") and inserts "00" between each byte, and also prepends "00". The result for "aabbcc" would be "00aa00bb00cc". This is a very specific format required by the platform's license server.
-   **`get_key_final(self, otp)`**: This performs the final XOR decryption on the OTP received from the server to reveal the actual content key. It's the reverse of the `xor_encrypt` logic.

### `get_key(self, id, batch_name, ...)`

This is the main public method that orchestrates the entire key-fetching process.

1.  **Get Video URL:**
    ```python
    url_op = Endpoints(verbose=True).set_token(self.token,self.random_id).process("lecture",lecture_id=id,batch_name=batch_name)
    url = url_op['url']
    signature = url_op['signedUrl']
    url = Download.buildUrl(url,signature)
    ```
    -   It uses the `Endpoints` helper to make an API call to get the base video URL and a `signedUrl` (which is essentially a signature or policy).
    -   `Download.buildUrl` combines these to create the full, authenticated URL for the video's MPD manifest.

2.  **Extract Key ID (`kid`):**
    ```python
    kid = self.extract_kid_from_mpd(url).replace("-", "")
    ```
    -   It downloads the MPD file from the `url` and uses a regular expression (`extract_kid_from_mpd`) to find the `default_KID` value within the XML content. The dashes are removed as required by the subsequent steps.

3.  **Generate OTP Key:**
    ```python
    otp_key = self.b64_encode(self.xor_encrypt(kid))
    ```
    -   The `kid` is first "encrypted" using the custom XOR cipher with the user's token.
    -   The result is then Base64 encoded. This `otp_key` is the payload that will be sent to the license server.

4.  **Format OTP Key:**
    ```python
    encoded_otp_key_step1 = otp_key.encode('utf-8').hex()
    encoded_otp_key = self.insert_zeros(encoded_otp_key_step1)
    ```
    -   The `otp_key` is converted to its hexadecimal representation.
    -   The `insert_zeros` function is called to format it into the specific "00xx00yy00zz" format required by the server.

5.  **Request License:**
    ```python
    license_url = self.build_license_url(encoded_otp_key)
    # ...
    endpoint = Endpoint(url=license_url, method='GET', headers=headers)
    response, status_code, _ = endpoint.fetch()
    ```
    -   It constructs the final license URL using the specially formatted OTP key.
    -   It makes a GET request to this URL with a specific set of headers that mimic a real browser request.

6.  **Extract Final Key:**
    ```python
    if status_code == 200:
        if 'data' in response and 'otp' in response['data']:
            key = self.get_key_final(response['data']['otp'])
            return (kid,key,url)
    ```
    -   If the request is successful, the server returns a JSON object containing the final, encrypted OTP.
    -   `self.get_key_final()` is called to perform the final XOR decryption on this payload.
    -   The result, `key`, is the **actual decryption key** for the video content.
    -   The function returns the `kid`, the final `key`, and the `url` of the MPD manifest.
