"""
Obsolete module:
no longer used in the project
used when key.old.py was being used
"""

import base64

def base64_to_hex(base64_str):
    # Replace special characters not in base64 list with '/'
    base64_str = base64_str.replace('-', '+').replace('_', '/')

    # Add padding if necessary
    padding = len(base64_str) % 4
    if padding:
        base64_str += '=' * (4 - padding)

    # Convert base64 to bytes
    base64_bytes = base64_str.encode('utf-8')

    # Decode base64 bytes to hex bytes
    hex_bytes = base64.b64decode(base64_bytes).hex()

    return hex_bytes

def cookies_dict_to_str(cookies):
    return ';'.join([f'{key}={value}' for key, value in cookies.items()])

