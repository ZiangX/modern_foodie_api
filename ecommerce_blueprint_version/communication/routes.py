from flask import current_app, url_for, redirect, request, Blueprint, jsonify
from twilio.rest import Client
from datetime import datetime
import random

from ecommerce_blueprint_version import db
from ecommerce_blueprint_version.auth.utils import *


communication = Blueprint('communication', __name__)

@communication.route("/phoneNumberVerification", methods=['POST', 'GET'])
@token_required
def send_code(current_user):
    if request.method == 'GET':
        target_phone, message = request.args.get("phone"), request.args.get("message")
        print('info', target_phone, message)

        account_sid = current_app.config['TWILIO_ACCOUNT_SID'] 
        auth_token = current_app.config['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        # Prevent someone from abusing api
        if current_user.phone_verification_code_sent_time:
            request_interval = int((datetime.utcnow() - current_user.phone_verification_code_sent_time).total_seconds())
            if request_interval < 60:
                return jsonify({'next_request_waiting_time': 60 - request_interval}), 400

        generated_code = random.randrange(100000, 1000000, 2)
        client.messages.create(  
            messaging_service_sid=current_app.config['MESSAGING_SERVICE_SID'], 
            body=f"{message} {str(generated_code)}",
            to=target_phone 
        )
        User.query.filter_by(userid=current_user.userid).update({"phone_verification_code": generated_code, "phone_verification_code_sent_time": datetime.utcnow()})
        db.session.commit()
        return "code_sent", 200
    else:
        code, phone = request.get_json().get("code"), request.get_json().get("phone")
        try:
            code = int(code.replace(" ", ""))
            print("code is", code)
        except:
            return "code_malformed", 400

        if current_user.phone_verification_code == code:
            User.query.filter_by(userid=current_user.userid).update({"phone": phone})
            db.session.commit()
            return "code_correct", 200
        return "code_incorrect", 400

