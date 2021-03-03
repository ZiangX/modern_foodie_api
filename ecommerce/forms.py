import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import session
from flask import url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, RadioField, FloatField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Optional
from wtforms import MultipleFileField

from ecommerce.models import *
# from ecommerce import mysql


def getAllProducts():
    products = Product.query.join(ProductCategory, Product.productid == ProductCategory.productid) \
        .join(Category, Category.categoryid == ProductCategory.categoryid) \
        .order_by(Category.categoryid.desc()) \
        .all()
    return products
    # .add_columns(Product.productid, Product.product_name_zh, Product.product_name_en, Product.product_name_fr,
    #              Product.price, Product.description_zh, Product.description_en, Product.description_fr,
    #              Product.product_imgs, Product.quantity) \

# Only get categories with products attached
def getAllCategories():
    categories = Category.query.join(ProductCategory, Category.categoryid == ProductCategory.categoryid) \
        .join(Product, Product.productid == ProductCategory.productid) \
        .order_by(Category.categoryid.desc()) \
        .all()
    return categories

def getProductByProductId(productId):
    productByProductId = Product.query.filter(
        Product.productid == productId).first()
    return productByProductId

def getCategoryByCategoryId(categoryId):
    categoryByCategoryId = Product.query.join(ProductCategory, Product.productid == ProductCategory.productid) \
        .join(Category, Category.categoryid == ProductCategory.categoryid) \
        .add_columns(Category.categoryid, Category.category_name_zh, Category.category_name_en, Category.category_name_fr, Category.category_img) \
        .filter(Category.categoryid == int(categoryId)) \
        .all()
    return categoryByCategoryId


def getPriceRangeFromVariants(variants):
    max, min = float(variants[0].get("variant_price")), float(variants[0].get("variant_price"))
    for variant in variants:
        print('price', variant, variant.get("variant_price"))
        price = float(variant.get("variant_price"))
        if price > max:
            max = price
        elif price < min:
            min = price
    return (min, max)


# This function create two dimenstions array with sub array from the passed in array, and the max length of sub array is 6
def massageItemData(data):
    ans = []
    i = 0
    print('data', data)
    while i < len(data):
        curr = []
        for j in range(6):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

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


def getLoginUserDetails():
    productCountinCartForGivenUser = 0

    if 'email' not in session:
        loggedIn = False
        firstName = ''
    else:
        loggedIn = True
        userid, firstName = User.query.with_entities(User.userid, User.fname).filter(
            User.email == session['email']).first()

        productCountinCart = []

        # for Cart in Cart.query.filter(Cart.userId == userId).distinct(Products.productId):
        for cart in Cart.query.filter(Cart.userid == userid).all():
            productCountinCart.append(cart.productid)
            productCountinCartForGivenUser = len(productCountinCart)

    return (loggedIn, firstName, productCountinCartForGivenUser)



def extractAndPersistUserDataFromForm(request):
    password = request.form['password']
    email = request.form['email']
    username = request.form['username']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    address1 = request.form['address1']
    zipcode = request.form['zipcode']
    city = request.form['city']
    state = request.form['state']
    country = request.form['country']
    phone = request.form['phone']

    user = User(fname=firstName, lname=lastName, password=hashlib.md5(password.encode()).hexdigest(), username=username,
                address1=address1, city=city, state=state, country=country, zipcode=zipcode, email=email, phone=phone)
    db.session.add(user)
    db.session.flush()
    db.session.commit()
    return "Registered Successfully"


def isUserLoggedIn():
    if 'email' not in session:
        return False
    else:
        return True


# check if user is an admin.html
def isUserAdmin():
    if isUserLoggedIn():
        # ProductCategory.query.filter_by(productid=product.productid).first()
        if session['email'] == 'ziangxuu@gmail.com':
            return True
    return False

# Using Flask-SQL Alchemy SubQuery


def extractAndPersistKartDetailsUsingSubquery(productId):
    userId = User.query.with_entities(User.userid).filter(
        User.email == session['email']).first()
    userId = userId[0]

    subqury = Cart.query.filter(Cart.userid == userId).filter(
        Cart.productid == productId).subquery()
    qry = db.session.query(Cart.quantity).select_entity_from(subqury).all()
    print(userId, qry)
    if len(qry) == 0:
        cart = Cart(userid=userId, productid=productId, quantity=1)
    else:
        cart = Cart(userid=userId, productid=productId, quantity=qry[0][0] + 1)

    db.session.merge(cart)
    db.session.flush()
    db.session.commit()

# Using Flask-SQL Alchemy query


def extractAndPersistKartDetailsUsingkwargs(productId):
    userId = User.query.with_entities(User.userid).filter(
        User.email == session['email']).first()
    userId = userId[0]

    kwargs = {'userid': userId, 'productid': productId}
    quantity = Cart.query.with_entities(
        Cart.quantity).filter_by(**kwargs).first()

    if quantity is not None:
        cart = Cart(userid=userId, productid=productId,
                    quantity=quantity[0] + 1)
    else:
        cart = Cart(userid=userId, productid=productId, quantity=1)

    db.session.merge(cart)
    db.session.flush()
    db.session.commit()


class addCategoryForm(FlaskForm):
    category_name_zh = StringField(
        'Category Name in Chinese', validators=[DataRequired()])
    category_name_en = StringField(
        'Category Name in English', validators=[DataRequired()])
    category_name_fr = StringField(
        'Category Name in French', validators=[DataRequired()])
    category_img = FileField('Category Image', validators=[
        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')


class addProductForm(FlaskForm):
    category = SelectField('Category:', coerce=int, id='select_category')
    sku = IntegerField('Product SKU (optional):', validators=[Optional()])
    product_name_zh = StringField(
        'Product Name in Chinese:', validators=[DataRequired()])
    product_name_en = StringField(
        'Product Name in English:', validators=[DataRequired()])
    product_name_fr = StringField(
        'Product Name in French:', validators=[DataRequired()])
    description_zh = TextAreaField(
        'Product Description in Chinese:', validators=[DataRequired()])
    description_en = TextAreaField(
        'Product Description in English:', validators=[DataRequired()])
    description_fr = TextAreaField(
        'Product Description in French:', validators=[DataRequired()])
    productPrice = FloatField('Product Price:', validators=[Optional()])
    productVariant1 = StringField('Product variant 1:', validators=[Optional()])
    productVariant2 = StringField('Product variant 2:', validators=[Optional()])
    productVariant3 = StringField('Product variant 3:', validators=[Optional()])
    productVariant4 = StringField('Product variant 4:', validators=[Optional()])
    productVariant5 = StringField('Product variant 5:', validators=[Optional()])
    productQuantity = IntegerField(
        'Product Quantity:', validators=[DataRequired()])
    product_imgs = MultipleFileField('Product Images', validators=[
        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')


# flask form for checkout details
class checkoutForm(FlaskForm):
    fullname = StringField('Full Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    address = TextAreaField('address',
                            validators=[DataRequired()])
    city = StringField('city',
                       validators=[DataRequired(), Length(min=2, max=20)])
    state = StringField('state',
                        validators=[DataRequired(), Length(min=2, max=20)])
    zip = StringField('zip',
                      validators=[DataRequired(), Length(min=2, max=6)])
    cctype = RadioField('cardtype')
    cardname = StringField('cardnumber',
                           validators=[DataRequired(), Length(min=12, max=12)])
    ccnumber = StringField('Credit card number',
                           validators=[DataRequired()])

    expmonth = StringField('Exp Month',
                           validators=[DataRequired(), Length(min=12, max=12)])
    expyear = StringField('Expiry Year',
                          validators=[DataRequired(), Length(min=4, max=4)])
    cvv = StringField('CVV',
                      validators=[DataRequired(), Length(min=3, max=4)])
    submit = SubmitField('MAKE PAYMENT')


# Gets form data for the sales transaction
def extractOrderdetails(current_user, orderData, totalPrice):

    # TODO Need to check the user is logged in or not when entering the checkout page in the frontend
    orderdate = datetime.utcnow()
    # Since using with_entities, the result will be a tuple, we need to get the first element by using index 0
    userId, username = current_user.userid, current_user.username

    # This part simply create an order with order date, total_price and userId
    order = Order(order_date=orderdate, total_price=totalPrice, userid=userId)
    db.session.add(order)
    db.session.flush()
    db.session.commit()
    # Get the orderid 
    orderid = Order.query.with_entities(Order.orderid).filter(Order.userid == userId).order_by(
        Order.orderid.desc()).first()
    orderid = orderid[0]
    print("orderid", orderid)

    # add details to ordered_products table
    addOrderedproducts(userId, orderid, orderData)
    
    # remove ordered products from cart after transaction is successful
    # removeordprodfromcart(userId)
    # sendtextconfirmation(phone,fullname,orderid)
    return (username, orderid)


# adds data to orderdproduct table

def addOrderedproducts(userId, orderid, orderData):
    # Since the cart data is saved in the localstorage, this function will not be used in this version
    # cart = Cart.query.with_entities(
    #     Cart.productid, Cart.quantity).filter(Cart.userid == userId)

    # Need to add orderproduct price and variant columns. Since we treat variants as different product, 
    # so two variants of the same product will run OrderedProduct twice
    for item in orderData:
        orderedproduct = OrderedProduct(
            orderid=orderid, productid=item.get("productid"), variant_name_zh=item.get("variant_name_zh"), variant_name_en=item.get("variant_name_en")
            , variant_name_fr=item.get("variant_name_fr"), price=item.get("price"), quantity=item.get("quantity"), sum=item.get("sum"))
        db.session.add(orderedproduct)
        db.session.flush()
        db.session.commit()

# sends email for order confirmation
def sendEmailconfirmation(email, username, ordernumber, phonenumber, provider):
    msg = MIMEMultipart()
    sitemail = "stargadgets@engineer.com"
    msg['Subject'] = "Your Order has been placed for " + username
    msg['From'] = sitemail
    msg['To'] = email
    text = "Hello!\nThank you for shopping with us.Your order No is:" + \
        str(ordernumber[0])
    html = """\
        <html>
          <head></head>
          <body>
            <p><br>
               Please stay tuned for more fabulous offers and gadgets.You can visit your account for more details on this order.<br> 
               <br>Please write to us at <u>stargadgets@engineer.com</u> for any assistance.</br>
               <br></br>
               <br></br>
               Thank you!
               <br></br>
               StarGadgets Team          
            </p>
          </body>
        </html>
        """
    msg1 = MIMEText(text, 'plain')
    msg2 = MIMEText(html, 'html')
    msg.attach(msg1)
    msg.attach(msg2)
    server = smtplib.SMTP(host='smtp.mail.com', port=587)
    server.connect('smtp.mail.com', 587)
    # Extended Simple Mail Transfer Protocol (ESMTP) command sent by an email server to identify itself when connecting to another email.

    server.ehlo()
    # upgrade insecure connection to secure
    server.starttls()
    server.ehlo()
    server.login("stargadgets@engineer.com", "stargadget@123")
    server.ehlo()
    server.sendmail(sitemail, email, msg.as_string())
    # hack to send text confirmation using emailsms gateway
    if (provider == "Tmobile"):
        phonenumber = phonenumber + "@tmomail.net"
    if (provider == "ATT"):
        phonenumber = phonenumber + "@txt.att.net"
    server.sendmail(sitemail, phonenumber, msg.as_string())
    server.quit()

# ======================================
# START CART MODULE
# ======================================

# Gets products in the cart
def getusercartdetails():
    userId = User.query.with_entities(User.userid).filter(
        User.email == session['email']).first()

    productsincart = Product.query.join(Cart, Product.productid == Cart.productid) \
        .add_columns(Product.productid, Product.product_name_zh, Product.product_name_en, Product.product_name_fr,
                     Product.discounted_price, Cart.quantity, Product.product_imgs) \
        .add_columns(Product.discounted_price * Cart.quantity).filter(
        Cart.userid == userId)
    totalsum = 0

    for row in productsincart:
        totalsum += row[6]

    tax = ("%.2f" % (.06 * float(totalsum)))

    totalsum = float("%.2f" % (1.06 * float(totalsum)))
    return (productsincart, totalsum, tax)


# Removes products from cart when user clicks remove
def removeProductFromCart(productId):
    userId = User.query.with_entities(User.userid).filter(
        User.email == session['email']).first()
    userId = userId[0]
    kwargs = {'userid': userId, 'productid': productId}
    cart = Cart.query.filter_by(**kwargs).first()
    if productId is not None:
        db.session.delete(cart)
        db.session.commit()
        flash("Product has been removed from cart !!")
    else:
        flash("failed to remove Product cart please try again !!")
    return redirect(url_for('cart'))


# removes all sold products from cart for the user
def removeordprodfromcart(userId):
    userid = userId
    db.session.query(Cart).filter(Cart.userid == userid).delete()
    db.session.commit()


# except:
#     "no tls please try again later"
#     return False

# def sendTextnotification(phone,fullname,orderid):


# problem 1--TextMagic lots of unknown packages
# username = "akankshanegi"
# token = "di18DWYaXQRT3KqDLn8wfYpr5utQl3"
# client = TextmagicRestClient(username, token)
#
# message = client.messages.create(phones="8478486054", text="Hello TextMagic")

# problem 2--TWILIO not free need to buy a paid number
# # the following line needs your Twilio Account SID and Auth Token
# client = Client("AC488c3b9e98a6bbbf84d5002631f2fd63", "f1b4ca2a3913f5f39ba6a7cf44afb77f")
#
# # change the "from_" number to your Twilio number and the "to" number
# # to the phone number you signed up for Twilio with, or upgrade your
# # account to send SMS to any phone number
# client.messages.create(to="+18478486054",
#                        from_="+15005550006",
#                        body="Hello from Python!")


# END CART MODULE
