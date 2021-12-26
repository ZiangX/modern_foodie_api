from flask import current_app, url_for, redirect, request, Blueprint, jsonify
from twilio.rest import Client
from datetime import datetime

from ecommerce_blueprint_version import db
from ecommerce_blueprint_version.auth.utils import *


communication = Blueprint('communication', __name__)

# Need to handle the request abuse
@communication.route("/sendCode", methods=['POST'])
@token_required
def send_code(current_user):
    target_phone, message = request.get_json().get("phone"), request.get_json().get("message")
    print('info', target_phone, message)

    account_sid = current_app.config['TWILIO_ACCOUNT_SID'] 
    auth_token = current_app.config['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token) 
    
    # message = client.messages.create(  
    #                             messaging_service_sid=current_app.config['MESSAGING_SERVICE_SID'], 
    #                             body=message,      
    #                             to=target_phone 
    #                         )


    User.query.filter_by(userid=current_user.userid).update({"phone_verification_code": 332211, "phone_verification_code_sent_time": datetime.utcnow()})
    db.session.commit()
    return "code_sent", 200
