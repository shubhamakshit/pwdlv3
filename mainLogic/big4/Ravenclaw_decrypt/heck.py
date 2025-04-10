from Crypto.Cipher import AES
from base64 import b64decode
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger

# Constants (keys should be of correct length for AES, e.g., 16, 24, or 32 bytes)
VIDEO_ENCRYPTION_KEY = 'pw3c199c2911cb437a907b1k0907c17n'
INITIALISATION_VECTOR = '5184781c32kkc4e8'


# Function to Ravenclaw_decrypt a single cookie value
def get_decrypt_cookie(encrypted_cookie):
    key = VIDEO_ENCRYPTION_KEY.encode('utf-8')
    iv = INITIALISATION_VECTOR.encode('utf-8')
    encrypted_cookie_bytes = b64decode(encrypted_cookie)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_cookie_bytes)

    # Remove padding
    decrypted = decrypted[:-decrypted[-1]]

    return decrypted.decode('utf-8')


# Function to split and Ravenclaw_decrypt the cookie string
def cookie_splitter(cookie, verbose=False):
    decrypted_cookie = ''
    cookie_parts = cookie.split('&')

    for i in range(3):  # Decrypt first 3 key-value pairs
        key, encrypted_value = cookie_parts[i].split('=', 1)
        decrypted_value = get_decrypt_cookie(encrypted_value)

        if verbose: debugger.debug(f"Decrypted {key}: {decrypted_value}")

        decrypted_cookie += f"{key}={decrypted_value}&"

    if verbose: Global.hr()
    return decrypted_cookie.rstrip('&')


# a method that converts the signed url to COOKIES
# Policy -> CloudFront-Policy
# Signature -> CloudFront-Signature
# Key-Pair-Id -> CloudFront-Key-Pair-Id

def get_cookiees_from_url(query_string):
    # Remove the str before '?' if it exists
    if "?" in query_string:
        query_string = query_string.split('?')[1]

    # Split the query string by '&' to get each key-value pair
    params = query_string.split('&')

    # Create a dictionary to store the key-value pairs
    result = {}

    # Map the query string keys to CloudFront-specific names
    mappings = {
        'Policy': 'CloudFront-Policy',
        'Signature': 'CloudFront-Signature',
        'Key-Pair-Id': 'CloudFront-Key-Pair-Id'
    }

    # Iterate over the parameters and replace keys as necessary
    for param in params:
        key, value = param.split('=')
        if key in mappings:
            key = mappings[key]
        result[key] = value

    return result
