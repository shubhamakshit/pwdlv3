import requests
import json
from utils.keyUtils import base64_to_hex
from utils.glv import Global
import error

def getKey(id, verbose=True,flare_url='http://localhost:8191/v1',retries=2):
    """
    Retrieves the encryption keys for a given ID.

    Args:
        id (str): The ID used to retrieve the encryption keys.
        glv (object, optional): An instance of the Global class. Defaults to None.

    Returns:
        str: The encryption key in hexadecimal format, or -1 if the key extraction fails.
    """
    for i in range(retries):

        if verbose:
            Global.dprint("Starting the script for key extraction" + f"Retry: {i}" if i > 0 else "")
        if verbose:
            Global.sprint(f'id -> {id}')

        if verbose:
            Global.sprint("Sending request to the server")
            Global.dprint("Hardcoded URL: request.get -> http://studyrays.site/drmplayer.php?v=https://d1d34p8vz63oiq"
                          ".cloudfront.net/{id}/master.mpd")

        # Send a POST request to the server to get the encryption keys
        url = f"{flare_url}"
        headers = {"Content-Type": "application/json"}
        data = {
            "cmd": "request.get",
            "url": f"http://studyrays.site/drmplayer.php?v=https://d1d34p8vz63oiq.cloudfront.net/{id}/master.mpd",
            "maxTimeout": 60000
        }

        try:
            response = requests.post(url, headers=headers, json=data)
        except requests.exceptions.RequestException as e:
            error.errorList["flareNotStarted"]["func"]()
            exit(error.errorList["flareNotStarted"]["code"])

        if response.status_code != 200:
            error.errorList["requestFailedDueToUnknownReason"]["func"](response.status_code)
            exit(error.errorList["requestFailedDueToUnknownReason"]["code"])


        # HTML response from the server is processed to extract the encryption keys
        html = str(response.json()['solution']['response'])

        from bs4 import BeautifulSoup as BS

        soup = BS(html, 'html.parser')
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.text
            if 'const protData' in script_content:
                # Extract the script containing 'const protData'
                protData_script = script_content
                break
        else:
            # Handle case when 'protData' variable is not found
            protData_script = None

        # Now you have the script containing 'protData' in 'protData_script' variable
        import re

        # Regular expression pattern to match the protData variable assignment
        pattern = r'const\s+protData\s*=\s*({.*?});'

        # Search for the pattern in the script content
        match = re.search(pattern, str(protData_script), re.DOTALL)

        if match:
            # Extract the content of the protData variable
            protData_content = match.group(1)
            keylist = json.loads(protData_content)['org.w3.clearkey']['clearkeys']
            for kid in keylist:
                # Convert the base64 encoded key to hexadecimal format
                return base64_to_hex(keylist[kid])
        else:
            print("protData variable not found in the script. Retrying!")
    return -1

        
