from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from ecommerce_blueprint_version import db

class User(db.Model):
    __table_args__ = {'extend_existing': True}

    # nullable default is true, unique is false
    userid = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(40), nullable=False)
    fname = db.Column(db.String(20), nullable=True)
    lname = db.Column(db.String(20), nullable=True)
    password = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(100), unique=False, nullable=True)
    city = db.Column(db.String(20), unique=False, nullable=True)
    province = db.Column(db.String(20), unique=False, nullable=True)
    country = db.Column(db.String(20), unique=False, nullable=True)
    postcode = db.Column(db.String(20), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # When ppl remove the phone, we need to allow many empty string fields exisiting at the same time
    phone = db.Column(db.Integer, unique=False, nullable=True)
    created_on = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'userid': self.userid}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            userid = s.loads(token)['userid']
        except:
            return None
        return User.query.get(userid)


class Category(db.Model):
    __table_args__ = {'extend_existing': True}
    categoryid = db.Column(db.Integer, primary_key=True)
    category_name_zh = db.Column(db.String(100), nullable=False)
    category_name_en = db.Column(db.String(100), nullable=False)
    category_name_fr = db.Column(db.String(100), nullable=False)
    category_img = db.Column(
        db.String(50), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)


class Product(db.Model):
    __table_args__ = {'extend_existing': True}
    productid = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), nullable=True)
    product_name_zh = db.Column(db.String(100), nullable=False)
    product_name_en = db.Column(db.String(100), nullable=False)
    product_name_fr = db.Column(db.String(100), nullable=False)
    description_zh = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.String(100), nullable=False)
    description_fr = db.Column(db.String(100), nullable=False)
    product_imgs = db.Column(db.JSON, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.FLOAT, nullable=True)
    variants = db.Column(db.JSON, nullable=True)


class ProductCategory(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    categoryid = db.Column(db.Integer, db.ForeignKey(
        'category.categoryid'), nullable=False)
    productid = db.Column(db.Integer, db.ForeignKey(
        'product.productid'), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)


class Cart(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey(
        'user.userid'), nullable=False)
    productid = db.Column(db.Integer, db.ForeignKey(
        'product.productid'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Cart('{self.userid}', '{self.productid}, '{self.quantity}')"


class Order(db.Model):
    __table_args__ = {'extend_existing': True}
    orderid = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_price = db.Column(db.FLOAT, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey(
        'user.userid'), nullable=False)



# TODO: Since the project involves the variant, it is better to create a new model for the variant,
# but due to the large workload, the variant info will be saved in the product model.
class OrderedProduct(db.Model):
    __table_args__ = {'extend_existing': True}
    ordproductid = db.Column(db.Integer, primary_key=True)
    orderid = db.Column(db.Integer, db.ForeignKey(
        'order.orderid'), nullable=False)
    productid = db.Column(db.Integer, db.ForeignKey(
        'product.productid'), nullable=False)
    variant_name_zh = db.Column(db.String(100), nullable=True)
    variant_name_en = db.Column(db.String(100), nullable=True)
    variant_name_fr = db.Column(db.String(100), nullable=True)
    # The price could be the variant price or the product price
    price = db.Column(db.FLOAT, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sum = db.Column(db.FLOAT, nullable=False)
