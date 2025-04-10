import re
import base64
import json

from mainLogic.big4.Ravenclaw_decrypt.heck import cookie_splitter, get_cookiees_from_url
from mainLogic.big4.Gryffindor_downloadv2 import Download
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger
from mainLogic.utils.keyUtils import cookies_dict_to_str
from mainLogic.utils.Endpoint import Endpoint

class LicenseKeyFetcher:
    def __init__(self, token, random_id):
        self.url = None
        self.token = token
        self.random_id = random_id
        self.cookies = None

    def build_license_url(self, encoded_otp_key):
        return f"https://api.penpencil.co/v1/videos/get-otp?key={encoded_otp_key}&isEncoded=true"

    def get_otp_headers(self):
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
        endpoint = Endpoint(url=url, method='GET')
        response, status_code, _ = endpoint.fetch()
        if status_code != 200:
            raise Exception(f"Failed to fetch MPD content. Status code: {status_code}")
        mpd_content = response
        pattern = r'default_KID="([0-9a-fA-F-]+)"'
        match = re.search(pattern, mpd_content)
        return match.group(1) if match else None

    def set_cookies(self, url):
        self.cookies = cookies_dict_to_str(get_cookiees_from_url(url))

    def get_key(self, id, verbose=True):
        if verbose: Global.hr()

        if verbose: debugger.debug("Beginning to get the key for the video... & Audio :) ")
        if verbose: debugger.debug(f"ID: {id}")
        if verbose: debugger.debug("Building the URL to get the key...")

        try:
            from mainLogic.big4.Ravenclaw_decrypt.signedUrl import get_signed_url

            policy_string = get_signed_url(token=self.token, random_id=self.random_id, id=id, verbose=verbose)['data']
            add_on = cookie_splitter(policy_string, verbose)

            url = Download.buildUrl(id)+f"{add_on}"
            self.url = url
            self.set_cookies(url)

            if verbose: debugger.success(f"URL: {url}")
            if verbose:
                Global.hr()
                debugger.success(f"Cookies: {self.cookies}")

            if verbose: debugger.debug("Extracting the KID from the MPD file...")
            kid = self.extract_kid_from_mpd(url).replace("-", "")
            if verbose: debugger.success(f"KID: {kid}")

            if verbose: debugger.debug("Encrypting the KID to get the key...")
            otp_key = self.b64_encode(self.xor_encrypt(kid))
            if verbose: debugger.success(f"OTP Key: {otp_key}")

            if verbose: debugger.debug("Encoding the OTP key to hex...")
            encoded_otp_key_step1 = otp_key.encode('utf-8').hex()
            encoded_otp_key = self.insert_zeros(encoded_otp_key_step1)
            if verbose: debugger.success(f"Encoded OTP Key: {encoded_otp_key}")

            if verbose: debugger.debug("Building the license URL...")
            license_url = self.build_license_url(encoded_otp_key)
            if verbose: debugger.success(f"License URL: {license_url}")

            if verbose: debugger.debug("Getting the headers...")
            headers = self.get_otp_headers()
            if verbose: debugger.success(f"Headers: {json.dumps(headers, indent=4)}")

            if verbose: debugger.debug("Making a request to the server to get the license (key)...")
            endpoint = Endpoint(url=license_url, method='GET', headers=headers)
            response, status_code, _ = endpoint.fetch()
            if verbose: debugger.success(f"Response: {response}")

            if status_code == 200:
                if 'data' in response and 'otp' in response['data']:
                    if verbose: debugger.success("Key received successfully!")
                    key = self.get_key_final(response['data']['otp'])
                    if verbose: debugger.success(f"Key: {key}")

                    if verbose:Global.hr()
                    return (kid,key)
            else:
                debugger.error("Could not get the key from the server. Exiting...")
                return None

        except Exception as e:
            debugger.error(f"An error occurred while getting the key: {e}")
            return None
