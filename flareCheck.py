import requests

def checkFlare(flareUrl="localhost:8191"):
    
    url = f"http://{flareUrl}/v1"
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

