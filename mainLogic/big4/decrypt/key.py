import requests
import re
import base64
from mainLogic.big4.dl import DL
import json
from mainLogic.utils.glv import Global

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTgxNjE5OTAuOTc3LCJkYXRhIjp7Il9pZCI6IjY0MzE3NTQyNDBlOTc5MDAxODAwMjAyYiIsInVzZXJuYW1lIjoiOTQ3MjUwNzEwMCIsImZpcnN0TmFtZSI6IkFrc2hpdCBTaHViaGFtIiwibGFzdE5hbWUiOiIiLCJvcmdhbml6YXRpb24iOnsiX2lkIjoiNWViMzkzZWU5NWZhYjc0NjhhNzlkMTg5Iiwid2Vic2l0ZSI6InBoeXNpY3N3YWxsYWguY29tIiwibmFtZSI6IlBoeXNpY3N3YWxsYWgifSwiZW1haWwiOiJha3NoaXRzaHViaGFtbWFzQGdtYWlsLmNvbSIsInJvbGVzIjpbIjViMjdiZDk2NTg0MmY5NTBhNzc4YzZlZiJdLCJjb3VudHJ5R3JvdXAiOiJJTiIsInR5cGUiOiJVU0VSIn0sImlhdCI6MTcxNzU1NzE5MH0.784n5z-sDxhNgZrG23oPmwPqh2qaj05MwHmr3bg3TRY"

def buildLicenseUrl(encoded_otp_key):
    return f"https://api.penpencil.co/v1/videos/get-otp?key={encoded_otp_key}&isEncoded=true"

def getHeaders():
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,la;q=0.8",
        "authorization": f"Bearer {TOKEN}",
        "cache-control": "no-cache",
        "client-id": "5eb393ee95fab7468a79d189",
        "client-type": "WEB",
        "client-version": "200",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://www.pw.live",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "randomid": "180ff4c6-9ec3-4329-b1b5-1ad2f6746795",
        "referer": "https://www.pw.live/",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    return headers

# required by xor_encrypt
def key_char_at(key, i):
    return ord(key[i % len(key)])

# converts the xor_encrypted data to base64 (xor_encrypt was given TOKEN, kid)
def b64_encode(data):
    if not data:
        return data
    encoded = base64.b64encode(bytes(data)).decode('utf-8')
    return encoded

# converts the base64 encoded data to hex
# the received OTP is base64 encoded, so we need to convert it to hex
# the otp is nothing but key for decryption
# key type: clearkeys
# code copied from 'https://github.com/jarvistuts/Penpencil_Keys/blob/main/penpencil.py'
# originally by 'https://github.com/ItsVJp'
#
def get_key_final(otp: str, token: str) -> str:
    decoded_bytes = base64.b64decode(otp)
    length = len(decoded_bytes)
    decoded_ints = [int(byte) for byte in decoded_bytes]

    result = "".join(
        chr(
            decoded_ints[i] ^ ord(token[i % len(token)])
        )
        for i in range(length)
    )

    return result


# encrypting algorithm for the kid so that the request to the server remains secure
def xor_encrypt(token, data):
    return [ord(c) ^ key_char_at(token, i) for i, c in enumerate(data)]

# custom function to insert zeros in the hex string (as the hex string is completely void of padding)
# current logic [start_with_ '00' -> add '00' every 2 characters -> end must not contain '00']
def insert_zeros(hex_string):
    # Initialize an empty result string
    result = "00"
    # Loop through the input string two characters at a time
    for i in range(0, len(hex_string), 2):

        # Append the current two characters to the result
        result += hex_string[i:i+2]
        # If we're not at the end of the string, append "00"
        if i + 2 < len(hex_string):
            result += "00"
    return result

def extract_kid_from_mpd(url):
    # Fetch the MPD file content
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors

    # Extract the content as a string
    mpd_content = response.text

    # Define the regex pattern to find default_KID
    pattern = r'default_KID="([0-9a-fA-F-]+)"'

    # Search for the pattern in the MPD content
    match = re.search(pattern, mpd_content)

    # Return the KID if found, otherwise return None
    if match:
        return match.group(1)
    else:
        return None

def getKey(id,verbose=True):

    Global.hr();

    if verbose: Global.dprint("Beginning to get the key for the video... & Audio :) ")
    if verbose: Global.dprint(f"ID: {id}"); Global.dprint("Building the URL to get the key...")

    try:
        url = DL.buildUrl(id)
        if verbose: Global.sprint(f"URL: {url}")

        if verbose: Global.dprint("Extracting the KID from the MPD file...")
        kid = extract_kid_from_mpd(url).replace("-", "")
        if verbose: Global.sprint(f"KID: {kid}")

        if verbose: Global.dprint("Encrypting the KID to get the key...")
        otp_key = b64_encode(xor_encrypt(TOKEN, kid))
        if verbose: Global.sprint(f"OTP Key: {otp_key}")

        if verbose: Global.dprint("Encoding the OTP key to hex...")
        encoded_otp_key_step1 = otp_key.encode('utf-8').hex()
        encoded_otp_key = insert_zeros(encoded_otp_key_step1)
        if verbose: Global.sprint(f"Encoded OTP Key: {encoded_otp_key}")

        if verbose: Global.dprint("Building the license URL...")
        license_url = buildLicenseUrl(encoded_otp_key)
        if verbose: Global.sprint(f"License URL: {license_url}")

        if verbose: Global.dprint("Getting the headers...")
        headers = getHeaders()
        if verbose: Global.sprint(f"Headers: {json.dumps(headers, indent=4)}")

        if verbose: Global.dprint("Making a request to the server to get the license (key)...")
        # make a request to the server to get the license(key)
        response = requests.get(license_url, headers=headers)
        if verbose: Global.sprint(f"Response: {response}")

        # get the key from the response
        if response.status_code == 200:
            if 'data' in response.json():
                if 'otp' in response.json()['data']:
                    if verbose: Global.sprint("Key received successfully!")
                    key = get_key_final(response.json()['data']['otp'], TOKEN)
                    if verbose: Global.sprint(f"Key: {key}")

                    Global.hr()
                    return key
        else:
            Global.errprint("Could not get the key from the server. Exiting...")
            return None

    except Exception as e:
        Global.errprint(f"An error occurred while getting the key: {e}")
        return None


