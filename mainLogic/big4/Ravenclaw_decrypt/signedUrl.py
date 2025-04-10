import requests
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger


def get_signed_url(token, random_id, id, verbose=True):
    import requests
    import json

    if verbose:
        Global.hr()
        debugger.success("Getting the signed URL for the video...")
        debugger.debug(f"ID: {id}")
        debugger.success("Building the URL to get the signed URL...")

    url = "https://api.penpencil.co/v3/files/send-analytics-data"

    payload = json.dumps({
        "url": f"https://d1d34p8vz63oiq.cloudfront.net/{id}/master.mpd"
    })

    if verbose: debugger.debug(f"Payload: {payload}")

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {token}',
        'client-id': '5eb393ee95fab7468a79d189',
        'client-type': 'WEB',
        'client-version': '200',
        'content-type': 'application/json',
        'origin': 'https://www.pw.live',
        'priority': 'u=1, i',
        'randomid': f'{random_id}',
        'referer': 'https://www.pw.live/',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Cookie': 'CloudFront-Key-Pair-Id=PcRg7Y9%2F0diC%2F2hZTHy4I%2BIuN0EByyr4RFCFVc1E%2FeA%3D; CloudFront-Policy=YywI4NUCKSlG7EoTcFkfbBRpXkDB0sI1SLC%2BLe%2BdZ9Ch4saC5iHtpcexkUGKdb3tUvRXIa%2BoAm3%2FSdejhZBJtSUQX2TinfL0U%2Bll31h4uHNjbIW2T9skU2LIg5ykrFFyadAcF%2FxF%2BBiW5PVnzOVEQUUhr%2FS4zRF2WYgsGVLDgR6u5HWtbpM4j7U%2B%2F9Nuw9f0Bglfi512wrReXipC0%2FWbdMJVPEJRbLkNlYk0TsqMhdi%2Fgqv%2FdpGopX6oWu0uSh0%2FBLOvz9PJTjdrSw1rOBLpIozUHSkuW5AMJEpGMFYUPdc%3D; CloudFront-Signature=u68TnXDNbJnOhiaaj7J4uLs49Xf%2FMSH93aseVMqfIrZaWhBA%2Fpb%2FEh0vRDMqTXv8pPv6O2mbZjcKR%2FCJ4deJ%2FC2GwM8%2BeG8qDIK6OsfBTQgMny3gbqwCnIpKttnFVXTkBvLKDCYKyyqdAT3%2Fu9sK65FNp4hfJTAp7cJIENw9nvo%2Bxg8BA5JYOJpysnT0vJiDRxFFikAjk9H3rA%2F2yfexbjRp3WA0Eyb3OZn1Y5p%2Ff6QKKW4jaLSBxMoYmxuxFEgsQZ42zDDTqJMJk89vrO131HYrnSM%2B%2FKPWjYcfd10Knamtp9shJE9BWMGbCxjqlV6rj0GmgBSi%2ByRXEVk8Lehvp2V89ujenBcsq9vkoE5OvNPfh3eoixK5haAzFIjmb0dSdoGjGt4706cnQl0ZJCCNHd30Nra7V6tFfLsj%2FdrP6KYfPDNWNOBVRGiOU53BCNZl1mdwKdzP8bP9%2FdjXg7Qaow%3D%3D'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if verbose: debugger.success(f"Response: {json.dumps(response.json(), indent=8)}"); Global.hr()

    return response.json()



