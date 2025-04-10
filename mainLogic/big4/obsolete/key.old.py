# import requests
# import json
# from bs4 import BeautifulSoup as BS
# import re
# from utils.keyUtils import base64_to_hex
# from utils.glv import Global
# import error
#
#
# def log_info(id, verbose, attempt=0):
#     if verbose:
#         debugger.debug("Starting the script for key extraction" +( f" Retry: {attempt}" if attempt > 0 else ""))
#         debugger.success(f'id -> {id}')
#         debugger.success("Sending request to the server")
#         debugger.debug(f"Hardcoded URL: request.get -> http://studyrays.site/drmplayer.php?v=https://d1d34p8vz63oiq"
#                       f".cloudfront.net/{id}/master.mpd")
#
#
# def send_request(id):
#     try:
#
#         import http.client
#
#         conn = http.client.HTTPSConnection("api.scrapingant.com")
#
#         conn.request("GET",
#                      f"/v2/general?url=https%3A%2F%2Fstudyrays.site%2Fdrmplayer.php%3Fv%3Dhttps%3A%2F%2Fd1d34p8vz63oiq.cloudfront.net%2F{id}%2Fmaster.mpd&x-api-key=806b77b95dd643caae01d4e240da9159&proxy_type=residential&proxy_country=IN&browser=false")
#
#         res = conn.getresponse()
#
#         return res.read()
#
#     except requests.exceptions.RequestException as e:
#         error.errorList["flareNotStarted"]["func"]()
#         exit(error.errorList["flareNotStarted"]["code"])
#
#
# def parse_response(response):
#     try:
#
#         return response.decode('utf-8')
#
#     except (KeyError, json.JSONDecodeError):
#         error.errorList["requestFailedDueToUnknownReason"]["func"](response.status_code)
#         exit(error.errorList["requestFailedDueToUnknownReason"]["code"])
#
#
# def extract_key(html):
#
#     soup = BS(html, 'html.parser')
#     scripts = soup.find_all('script')
#
#     for script in scripts:
#         script_content = script.text
#         if 'const protData' in script_content:
#             protData_script = script_content
#             break
#     else:
#         return None
#
#     pattern = r'const\s+protData\s*=\s*({.*?});'
#     match = re.search(pattern, protData_script, re.DOTALL)
#
#     if match:
#         protData_content = match.group(1)
#         keylist = json.loads(protData_content)['org.w3.clearkey']['clearkeys']
#         for kid in keylist:
#             return base64_to_hex(keylist[kid])
#     return None
#
# # main function
# def getKey(id, verbose=True,retries=2):
#
#     for attempt in range(retries):
#         log_info(id, verbose, attempt)
#
#         response = send_request(id)
#         html = parse_response(response)
#
#         key = extract_key(html)
#         if key:
#             return key
#         else:
#             if verbose:
#                 debugger.success("protData variable not found in the script. Retrying!")
#     return -1