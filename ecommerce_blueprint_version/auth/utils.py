import hashlib, jwt
from flask import session, request, current_app, url_for
from functools import wraps
from flask_mail import Message

from ecommerce_blueprint_version.models import User
from ecommerce_blueprint_version import mail


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return 'token_missing', 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return 'token_invalid', 401

        return f(current_user, *args, **kwargs)

    return decorated


# To check if there is an user related to this username and password 
def is_valid(email, password):
    user = User.query.filter(User.email == email).first()
    if user is None:
        return False
    else:
        if not user.password == hashlib.md5(password.encode()).hexdigest():
            return False
        else:
            return True


# check if user is an admin
def isUserAdmin():
    # ProductCategory.query.filter_by(productid=product.productid).first()
    if 'email' in session and session['email'] in current_app.config['ADMIN_TEAM']:
        return True
    return False


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='Modern foodie',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)