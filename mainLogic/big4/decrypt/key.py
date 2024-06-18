import requests
import re
import base64
import json
from mainLogic.big4.dl import DL
from mainLogic.utils.glv import Global

class LicenseKeyFetcher:
    def __init__(self, token):
        self.token = token

    def build_license_url(self, encoded_otp_key):
        return f"https://api.penpencil.co/v1/videos/get-otp?key={encoded_otp_key}&isEncoded=true"

    def get_headers(self):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,la;q=0.8",
            "authorization": f"Bearer {self.token}",
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

    def key_char_at(self, key, i):
        return ord(key[i % len(key)])

    def b64_encode(self, data):
        if not data:
            return data
        encoded = base64.b64encode(bytes(data)).decode('utf-8')
        return encoded

    def get_key_final(self, otp):
        decoded_bytes = base64.b64decode(otp)
        length = len(decoded_bytes)
        decoded_ints = [int(byte) for byte in decoded_bytes]

        result = "".join(
            chr(
                decoded_ints[i] ^ ord(self.token[i % len(self.token)])
            )
            for i in range(length)
        )

        return result

    def xor_encrypt(self, data):
        return [ord(c) ^ self.key_char_at(self.token, i) for i, c in enumerate(data)]

    def insert_zeros(self, hex_string):
        result = "00"
        for i in range(0, len(hex_string), 2):
            result += hex_string[i:i+2]
            if i + 2 < len(hex_string):
                result += "00"
        return result

    def extract_kid_from_mpd(self, url):
        response = requests.get(url)
        response.raise_for_status()
        mpd_content = response.text
        pattern = r'default_KID="([0-9a-fA-F-]+)"'
        match = re.search(pattern, mpd_content)
        return match.group(1) if match else None

    def get_key(self, id, verbose=True):
        if verbose: Global.hr()

        if verbose: Global.dprint("Beginning to get the key for the video... & Audio :) ")
        if verbose: Global.dprint(f"ID: {id}")
        if verbose: Global.dprint("Building the URL to get the key...")

        try:
            url = DL.buildUrl(id)
            if verbose: Global.sprint(f"URL: {url}")

            if verbose: Global.dprint("Extracting the KID from the MPD file...")
            kid = self.extract_kid_from_mpd(url).replace("-", "")
            if verbose: Global.sprint(f"KID: {kid}")

            if verbose: Global.dprint("Encrypting the KID to get the key...")
            otp_key = self.b64_encode(self.xor_encrypt(kid))
            if verbose: Global.sprint(f"OTP Key: {otp_key}")

            if verbose: Global.dprint("Encoding the OTP key to hex...")
            encoded_otp_key_step1 = otp_key.encode('utf-8').hex()
            encoded_otp_key = self.insert_zeros(encoded_otp_key_step1)
            if verbose: Global.sprint(f"Encoded OTP Key: {encoded_otp_key}")

            if verbose: Global.dprint("Building the license URL...")
            license_url = self.build_license_url(encoded_otp_key)
            if verbose: Global.sprint(f"License URL: {license_url}")

            if verbose: Global.dprint("Getting the headers...")
            headers = self.get_headers()
            if verbose: Global.sprint(f"Headers: {json.dumps(headers, indent=4)}")

            if verbose: Global.dprint("Making a request to the server to get the license (key)...")
            response = requests.get(license_url, headers=headers)
            if verbose: Global.sprint(f"Response: {response}")

            if response.status_code == 200:
                if 'data' in response.json() and 'otp' in response.json()['data']:
                    if verbose: Global.sprint("Key received successfully!")
                    key = self.get_key_final(response.json()['data']['otp'])
                    if verbose: Global.sprint(f"Key: {key}")

                    if verbose:Global.hr()
                    return (kid,key)
            else:
                Global.errprint("Could not get the key from the server. Exiting...")
                return None

        except Exception as e:
            Global.errprint(f"An error occurred while getting the key: {e}")
            return None

# Example usage
# TOKEN = "your_token_here"
# fetcher = LicenseKeyFetcher(TOKEN)
# key = fetcher.get_key(video_id)
