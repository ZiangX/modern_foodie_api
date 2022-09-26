from flask import render_template, url_for, redirect, request, Blueprint, session, jsonify, current_app
import random, jwt

auth = Blueprint('auth', __name__)

from ecommerce_blueprint_version import db
# Since utils imports User model, no need to import again
from ecommerce_blueprint_version.auth.utils import *
from ecommerce_blueprint_version.auth.forms import ResetPasswordForm


# Even though some hacker can call this endpoint directly, they will need to login as well
@auth.route("/", methods=['GET'])
def signin_admin():
    print('session', session)
    if 'email' in session:
        return redirect(url_for('users.admin_dashboard'))
    else:
        return redirect(url_for('auth.login_admin'))


@auth.route("/register", methods=['POST'])
def register():
    formData = request.get_json()

    # Make sure username, pwd and email are not empty in the frontend
    username, email, password = formData.get(
        'username'), formData.get('email'), formData.get('password')

    # Prevent someone create account from postman and crash the server
    if not username or not email or not password:
        return 'form_incomplete', 400

    if User.query.filter(User.email == email).first():
        return 'email_taken', 400

    user = User(username=username, password=hashlib.md5(
        password.encode()).hexdigest(), email=email, public_id=random.randrange(10000000, 100000000, 2))
    db.session.add(user)
    db.session.commit()

    return "register_successfully", 201


@auth.route("/login", methods=['POST'])
def login():
    formData = request.get_json()
    email, password = formData.get('email'), formData.get('password')

    user = User.query.filter(User.email == email).first()

    if user is None:
        return 'not_find_email', 400
    else:
        if user.password != hashlib.md5(password.encode()).hexdigest():
            return 'password_not_correct', 400
        else:
            token = jwt.encode({'public_id': user.public_id}, current_app.config['SECRET_KEY'], "HS256")
            return jsonify({'token': token.decode("utf-8")}), 200


@auth.route("/fb-signin", methods=['POST'])
def fb_signin():
    formData = request.get_json()
    facebook_uid, username, email = formData.get('facebook_uid'), formData.get('username'), formData.get('email')

    if not username:
        return 'username_missing', 400
    elif not email:
        return 'email_missing', 400
    elif not facebook_uid:
        return 'sign_in_fail_please_contact_us', 400

    user = User.query.filter(User.email == email).first()
    print(user)
    if user is None:
        # Create new account
        user = User(username=username, password="temporary_password", 
            email=email, public_id=random.randrange(10000000, 100000000, 2), facebook_uid=facebook_uid)
        db.session.add(user)
        db.session.commit()
    else:
        if user.facebook_uid != facebook_uid:
            return 'email_of_this_facebook_has_been_registered', 400
        
    token = jwt.encode({'public_id': user.public_id}, current_app.config['SECRET_KEY'], "HS256")
    return jsonify({'token': token.decode("utf-8")}), 200

@auth.route("/login-admin", methods=['POST', 'GET'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            if isUserAdmin():
                # session['email'] = email
                return redirect(url_for('users.admin_dashboard'))
            return 'You are not an admin'
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


@auth.route("/logout-admin", methods=['POST', 'GET'])
def logout_admin():
    session.clear()
    return render_template('login.html')


@auth.route("/updatePassword", methods=['POST'])
@token_required
def update_password(current_user):
    requestData = request.get_json()
    oldPassword, newPassword = requestData.get(
        "oldPassword"), requestData.get("newPassword")
    userValidation = is_valid(current_user.email, oldPassword)
    if userValidation:
        current_user.password = hashlib.md5(newPassword.encode()).hexdigest()
        db.session.commit()
        return "updated", 200
    return "old_password_incorrect", 401


# When user forgets their pwd
@auth.route("/request_reset_password", methods=['POST'])
def request_reset_password():
    requestData = request.get_json()
    email = requestData.get("email")
    user = User.query.filter(User.email==email).first()
    if user:
        send_reset_email(user)
        return "reset_email_sent", 200
    return "cannot_find_email", 400


@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password():
    requestData = request.get_json()
    token, password = requestData.get('token'), requestData.get('password')
    user = User.verify_reset_token(token)
    if user is None:
        return "reset_password_token_invalid", 400

    user.password = hashlib.md5(password.encode()).hexdigest()
    db.session.commit()
    
    return "password_reset_successfully", 200
