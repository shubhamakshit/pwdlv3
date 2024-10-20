from mainLogic.startup.Login.sudat import Login


class LoginInterface:

    @staticmethod
    def check_valid_10_dig_number(num):
        import re
        return bool(re.match(r'^\d{10}$', num))

    @staticmethod
    def cli():
        ph_num = input("Enter your 10 digit phone number: ")
        if not LoginInterface.check_valid_10_dig_number(ph_num):
            print("Please enter a valid 10 digit phone number.")
            return

        lg = Login(ph_num)

        if lg.gen_otp():
            if lg.login(input("Enter the OTP: ")):
                print("Login successful.")

                token = lg.token
                from beta.update import UpdateJSONFile
                from mainLogic.utils.glv_var import PREFS_FILE
                u = UpdateJSONFile(PREFS_FILE)
                u.update('token', token)

                print("Token updated successfully.")
            else:
                print("Login failed.")
        else:
            print("Failed to generate OTP.")
            
