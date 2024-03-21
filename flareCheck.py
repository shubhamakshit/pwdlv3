import requests

def checkFlare():
    url = "http://localhost:8191/v1"
    headers = {"Content-Type": "application/json"}
    data = {
        "cmd": "request.get",
        "url": "http://www.google.com/",
        "maxTimeout": 60000
    }
    response = requests.post(url, headers=headers, json=data)
    return response.ok

