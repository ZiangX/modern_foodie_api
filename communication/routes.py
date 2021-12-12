from flask import render_template, url_for, redirect, request, Blueprint, jsonify
from twilio.rest import Client

from ecommerce_blueprint_version import db, bcrypt
from ecommerce_blueprint_version.auth.utils import *


communication = Blueprint('communication', __name__)

# Need to handle the request abuse
@communication.route("/sendCode", methods=['POST'])
@token_required
def send_code(current_user):
    target_phone, message = request.get_json().get("phone"), request.get_json().get("message")
    print('info', target_phone, message)

    # TODO https://mail.google.com/mail/u/0/#inbox/FMfcgzGllMQwdrcpmdLDnRPTNwQmgzTq: Need to replace a new token since the old one was exposed
    account_sid = 'AC50f2794d189a34c9d2e4955a8b2b743f' 
    auth_token = 'c63951b66b7fea3ae00bbdc6465a227d'
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create(  
                                messaging_service_sid='MG2a81332b43ba0d193134d375e957b36c', 
                                body=message,      
                                to=target_phone 
                            ) 
    return "code_sent", 200
