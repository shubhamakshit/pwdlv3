import requests

def checkFlare(flareUrl="http://localhost:8191/v1"):
    
    url = f"{flareUrl}"
    headers = {"Content-Type": "application/json"}
    data = {
        "cmd": "request.get",
        "url": "http://www.google.com/",
        "maxTimeout": 60000
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.ok
    except Exception as e:
        return False

