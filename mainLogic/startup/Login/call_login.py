from mainLogic.startup.Login.sudat import Login
from mainLogic.utils.glv import Global
import json

from mainLogic.utils.glv_var import debugger


class LoginInterface:

    @staticmethod
    def check_valid_10_dig_number(num):
        import re
        return bool(re.match(r'^\d{10}$', num))

    @staticmethod
    def cli(debug=False):

        ph_num = input("Enter your 10 digit phone number: ") if not debug else "1234567890"

        if not LoginInterface.check_valid_10_dig_number(ph_num):
            print("Please enter a valid 10 digit phone number.")
            return

        lg = Login(ph_num, debug=debug)

        if lg.gen_otp():
            if lg.login(input("Enter the OTP: ")):

                token = lg.token


                if debug:
                    token = json.dumps(token, indent=4)
                    print(token)

                from beta.update import UpdateJSONFile

                from mainLogic.utils.glv_var import PREFS_FILE
                u = UpdateJSONFile(PREFS_FILE, debug=debug)

                # convert to json(dict) if possible

                if isinstance(token, str):
                    try:
                        token = json.loads(token)
                        debugger.info(f"Debug Mode: Token: {token}, type: {type(token)}")
                    except json.JSONDecodeError:
                        print("Token is not a valid JSON string.")
                        return

                if debug:
                    print("Debug Mode: Updating token")
                    debugger.debug(f"Debug Mode: Token: {token}, type: {type(token)}")

                u.update('token', token, debug=debug)

                debugger.info("Token updated successfully.")
            else:
                debugger.error("Login failed.")
        else:
            debugger.error("Failed to generate OTP.")
