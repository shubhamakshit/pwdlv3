import os
import sys
from mainLogic.utils.glv_var import debugger
import requests

from mainLogic.utils import glv_var
from mainLogic.utils.glv import Global


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

    def __init__(self, username,debug=False):
        self.username = username
        self.password = None
        self.token = None
        self.token_url = "https://api.penpencil.co/v3/oauth/token"
        self.wa_otp = "https://api.penpencil.co/v1/users/get-otp?smsType=1"
        self.debug = debug
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

    # change phone to wa for whatsapp 
    def gen_otp(self, otp_type="phone"):
        payload = {
            "username": self.username,
            "countryCode": "+91",
            "organizationId": "5eb393ee95fab7468a79d189"
        }

        if self.debug:
            debugger.debug("Debug Mode: OTP Generation")
            return True


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

        if self.debug:
            # generate {"randomId":,"token":,"refresh_token":,"expires_in":} with random values

            debugger.debug("Generating random token for debugging purposes")

            import json
            import random
            import string

            def random_string(length):
                letters = string.ascii_letters
                return ''.join(random.choice(letters) for i in range(length))

            self.token = {
                "randomId": "a3e290fa-ea36-4012-9124-8908794c33aa",
                "token": random_string(10),
                "refresh_token": random_string(10),
                "expires_in": random.randint(1, 100)
            }

            return True





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

            #from mainLogic.utils.dependency_checker import re_check_dependencies
            #re_check_dependencies()

            debugger.success(f"""
            Login Successful!
            Token: {self.token}
            Reloaded Preferences!
            """)

            return True

        else:
            return False

