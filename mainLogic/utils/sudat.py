import requests


class Login:


    @staticmethod
    def headers():
        return {
            'accept': 'application/json, text/plain, */*',
            'client-id': '5eb393ee95fab7468a79d189',
            'client-type': 'WEB',
            'client-version': '6.0.6',
            'content-type': 'application/json',
            'priority': 'u=1, i',
            'randomid': 'a3e290fa-ea36-4012-9124-8908794c33aa',
        }

    def __init__(self, username):
        self.username = username
        self.password = None
        self.token = None
        self.token_url = "https://api.penpencil.co/v3/oauth/token"
        self.wa_otp = "https://api.penpencil.co/v1/users/get-otp?smsType=1"
        self.otp = "https://api.penpencil.co/v1/users/get-otp?smsType=0"
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'client-id': '5eb393ee95fab7468a79d189',
            'client-type': 'WEB',
            'client-version': '6.0.6',
            'content-type': 'application/json',
            'priority': 'u=1, i',
            'randomid': 'a3e290fa-ea36-4012-9124-8908794c33aa',
        }

    def gen_otp(self, otp_type="wa"):
        payload = {
            "username": self.username,
            "countryCode": "+91",
            "organizationId": "5eb393ee95fab7468a79d189"
        }

        if otp_type == "wa":
            url = self.wa_otp
        else:
            url = self.otp

        response = requests.post(url, headers=self.headers, json=payload)
        #print(response.json())
        if response.status_code == 201 or response.status_code == 200:
            return True
        else:
            print(response.json())
            return False

    def login(self, otp):
        payload = {
            "username": self.username,
            "otp": otp,
            "client_id": "system-admin",
            "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
            "grant_type": "password",
            "organizationId": "5eb393ee95fab7468a79d189",
            "latitude": 0,
            "longitude": 0
        }

        response = requests.post(self.token_url, headers=self.headers, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            self.token = response.json().get('data')
            return True
        else:
            return False

