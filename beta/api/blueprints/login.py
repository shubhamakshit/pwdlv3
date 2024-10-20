from mainLogic.startup.Login.call_login import LoginInterface
from mainLogic.utils.glv_var import PREFS_FILE
from mainLogic.startup.Login.sudat import Login
from beta.update import UpdateJSONFile
from flask import jsonify, request, Blueprint

login = Blueprint('login', __name__)


@login.route('/api/otp', methods=['POST'])
@login.route('/otp', methods=['POST'])
def send_otp():
    data = request.json
    if 'phone' not in data:
        return jsonify({'error': 'Phone number is required'}), 400

    phone = data['phone']
    if LoginInterface.check_valid_10_dig_number(phone) is False:
        return jsonify({'error': 'Invalid phone number'}), 400

    lg = Login(phone)
    if lg.gen_otp() is False:
        return jsonify({'error': 'Failed to send OTP'}), 500
    else:
        return jsonify({'success': 'OTP sent successfully'}), 200

@login.route('/api/verify-otp', methods=['POST'])
@login.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    if 'phone' not in data or 'otp' not in data:
        return jsonify({'error': 'Phone number and OTP are required'}), 400

    phone = data['phone']
    otp = data['otp']
    if LoginInterface.check_valid_10_dig_number(phone) is False:
        return jsonify({'error': 'Invalid phone number'}), 400

    lg = Login(phone)
    if lg.login(otp) is False:
        return jsonify({'error': 'Invalid OTP'}), 400
    else:
        u = UpdateJSONFile(PREFS_FILE)
        u.update('token',lg.token)
        return jsonify({'success': 'OTP verified successfully','token':lg.token}), 200


