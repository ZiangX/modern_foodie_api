from datetime import datetime
from ecommerce import db

db.Model.metadata.reflect(db.engine)


class User(db.Model):
    __table_args__ = {'extend_existing': True}

    # nullable default is true, unique is false
    userid = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    fname = db.Column(db.String(20), nullable=True)
    lname = db.Column(db.String(20), nullable=True)
    password = db.Column(db.Text, nullable=False)
    address1 = db.Column(db.String(20), unique=False, nullable=True)
    city = db.Column(db.String(20), unique=False, nullable=True)
    state = db.Column(db.String(20), unique=False, nullable=True)
    country = db.Column(db.String(20), unique=False, nullable=True)
    zipcode = db.Column(db.String(20), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    created_on = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # def __repr__(self):
    #     return f"User('id: {self.userid}','{self.username}','{self.fname}', '{self.lname}'), 'password : {self.password}', " \
    #            f"'{self.address1}', '{self.city}', '{self.state}', '{self.country}'," \
    #            f"'{self.zipcode}','{self.email}','{self.phone}')"


class Category(db.Model):
    __table_args__ = {'extend_existing': True}
    categoryid = db.Column(db.Integer, primary_key=True)
    category_name_zh = db.Column(db.String(100), nullable=False)
    category_name_en = db.Column(db.String(100), nullable=False)
    category_name_fr = db.Column(db.String(100), nullable=False)
    category_img = db.Column(
        db.String(50), nullable=True, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

    # def __repr__(self):
    #     return f"Category('{self.categoryid}', '{self.category_name}')"


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

    # def __repr__(self):
    #     return f"Product('{self.productid}','{self.product_name}','{self.description}', '{self.product_imgs}',  '{self.quantity}', '{self.regular_price}', '{self.discounted_price}')"


class ProductCategory(db.Model):
    __table_args__ = {'extend_existing': True}
    categoryid = db.Column(db.Integer, db.ForeignKey(
        'category.categoryid'), nullable=False, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey(
        'product.productid'), nullable=False, primary_key=True)
    created_on = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    # def __repr__(self):
    #     return f"Product('{self.categoryid}', '{self.productid}')"


class Cart(db.Model):
    __table_args__ = {'extend_existing': True}
    userid = db.Column(db.Integer, db.ForeignKey(
        'user.userid'), nullable=False, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey(
        'product.productid'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Cart('{self.userid}', '{self.productid}, '{self.quantity}')"


class Order(db.Model):
    __table_args__ = {'extend_existing': True}
    orderid = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.FLOAT, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey(
        'user.userid'), nullable=False)

    # def __repr__(self):
    #     return f"Order('{self.orderid}', '{self.order_date}','{self.total_price}','{self.userid}'')"

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

    # def __repr__(self):
    #     return f"Order('{self.ordproductid}', '{self.orderid}','{self.productid}','{self.quantity}')"


class SaleTransaction(db.Model):
    __table_args__ = {'extend_existing': True}
    transactionid = db.Column(db.Integer, primary_key=True)
    orderid = db.Column(db.Integer, db.ForeignKey(
        'order.orderid'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.FLOAT, nullable=False)
    cc_number = db.Column(db.String(50), nullable=False)
    cc_type = db.Column(db.String(50), nullable=False)
    response = db.Column(db.String(50), nullable=False)

    # def __repr__(self):
    #     return f"Order('{self.transactionid}', '{self.orderid}','{self.transactiondate}','{self.amount}', '{self.cc_number}','{self.cc_type}','{self.response}')"
