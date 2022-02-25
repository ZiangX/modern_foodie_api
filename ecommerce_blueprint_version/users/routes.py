from flask import render_template, url_for, redirect, request, Blueprint, jsonify

from ecommerce_blueprint_version import db, bcrypt
from ecommerce_blueprint_version.auth.utils import *


users = Blueprint('users', __name__)


@users.route("/userInfo", methods=['GET', 'POST'])
@token_required
def user_info(current_user):
    if request.method == 'GET':
        sign_in_from_facebook = True if current_user.facebook_uid else False

        return jsonify({"userInfo": {"username": current_user.username, "sign_in_from_facebook": sign_in_from_facebook, "address": current_user.address, "city": current_user.city, 
            "province": current_user.province, "postcode": current_user.postcode, "email": current_user.email, "phone": current_user.phone
        }}), 200
    else:
        # Email and username cannot have duplicates
        newUserInfo = request.get_json()
        if not newUserInfo:
            return "field_cannot_be_null", 200
        email = newUserInfo.get("email")
        phone = newUserInfo.get("phone")
        print(current_user.phone, phone, current_user.email, email)
        if email and current_user.email != email and User.query.filter(User.email == email).first():
            return 'email_taken', 400
        if phone and current_user.phone != phone and User.query.filter(User.phone == phone).first():
            return 'phone_taken', 400

        # If adding .first(), it wont work, since the update property dont work with that
        User.query.filter_by(userid=current_user.userid).update(newUserInfo)
        db.session.commit()
        return "updated", 200

# Since for the admin side, users cannot be verified by tokens like the frontend. 
# The session could be the way to verify users role
@users.route("/admin-dashboard")
def admin_dashboard():
    if isUserAdmin():
        return render_template('admin.html')
    print('not admin')
    return redirect(url_for('auth.login_admin'))


# Get all users from db
@users.route("/admin/users")
def getUsers():
    if isUserAdmin():
        users = User.query.all()
        return render_template('adminUsers.html', users=users)
    return redirect(url_for('auth.login_admin'))
