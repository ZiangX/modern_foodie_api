import hashlib
import os
import secrets
import json
import random
import jwt
from datetime import datetime, timedelta
from functools import wraps
from PIL import Image
from flask import (render_template, request, jsonify, g, session)
from ecommerce import app
from ecommerce.forms import *
from plotly.offline import plot
import plotly.graph_objs as go
from flask import Markup
from ecommerce.models import *


app.config['SECRET_KEY'] = 'thisissecret'

# @app.before_request
# def load_logged_in_user():  # You can name whatever you want for the function name
#     user_id = session.get('user_id')
#     print('before request, user id is ', user_id)
#     if user_id is None:
#         g.user = None
#     else:
#         g.user = User.query.filter(User.userid == user_id).first()


# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return 'Please log in first', 400

#         return view(**kwargs)

#     return wrapped_view


# def isUserAdmin(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return 'Please log in first', 400
#         else:
#             userId = User.query.with_entities(User.userid).filter(
#                 User.email == g.user.email).first()
#             currentUser = User.query.get_or_404(userId)
#             if currentUser.username == 'zuck':
#                 print('You are an admin', userId,
#                       currentUser, currentUser.username)
#                 return view(**kwargs)
#             return 'You are not an admin', 400

#     return wrapped_view
#     # ProductCategory.query.filter_by(productid=product.productid).first()

# ======================================
# Client site methods
# ======================================

@app.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE')
    response.headers.set('Access-Control-Allow-Headers', '*')

    return response


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        formData = request.get_json()
        email, password = formData.get('email'), formData.get('password')

        user = User.query.filter(User.email == email).first()

        if user is None:
            return 'not_find_email', 400
        else:
            if not user.password == hashlib.md5(password.encode()).hexdigest():
                return 'password_not_correct', 400
            else:
                token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow(
                ) + timedelta(minutes=300)}, app.config['SECRET_KEY'])
                return jsonify({'token': token.decode('UTF-8')}), 200


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    # This part will be handle in the frontend   
    return "logout_successfully", 200


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        formData = request.get_json()

        # Make sure username, pwd and email are not empty in the frontend
        username, email, password = formData.get(
            'username'), formData.get('email'), formData.get('password')

        if User.query.filter(User.username == username).first():
            return 'username_taken', 400
        if User.query.filter(User.email == email).first():
            return 'email_taken', 400

        user = User(username=username, password=hashlib.md5(
            password.encode()).hexdigest(), email=email, public_id=random.randrange(1000, 10000, 2))
        db.session.add(user)
        db.session.commit()
        return "register_successfully", 201


@app.route("/userInfo", methods=['GET', 'POST'])
@token_required
def user_info(current_user):
    if request.method == 'GET':
        return jsonify({"userInfo": {"username": current_user.username, "fname": current_user.fname, "lname": current_user.lname, "address": current_user.address1, "city": current_user.city, "province": current_user.state,
                                        "country": current_user.country, "postcode": current_user.zipcode, "email": current_user.email, "phone": current_user.phone
                                        }}), 200
    else:
        newUserInfo = request.get_json()
        current_user.fname = newUserInfo.get("fname")
        current_user.lname = newUserInfo.get("lname")
        current_user.address1 = newUserInfo.get("address")
        current_user.city = newUserInfo.get("city")
        current_user.state = newUserInfo.get("province")
        current_user.country = newUserInfo.get("country")
        current_user.zipcode = newUserInfo.get("postcode")
        # Email cannot be null, so it should always has value
        current_user.email = newUserInfo.get("email")
        current_user.phone = newUserInfo.get("phone")
        db.session.commit()
        return "Update successfully", 200


@app.route("/updatePassword", methods=['POST'])
@token_required
def update_password(current_user):
    requestData = request.get_json()
    oldPassword, newPassword = requestData.get(
        "oldPassword"), requestData.get("newPassword")
    userValidation = is_valid(current_user.email, oldPassword)
    if userValidation:
        current_user.password = hashlib.md5(newPassword.encode()).hexdigest()
        db.session.commit()
        return "Update successfully", 200
    return "Password is not correct", 401


@app.route("/categories")
def categoriesClient():
    categoriesData = getAllCategories()
    categories = []

    # Since the movies is of sqlalchemy query result object, we have to abstract to a new dict
    for category in categoriesData:
        categories.append({"id": category.categoryid, "category_name_en": category.category_name_en,
                           "category_name_fr": category.category_name_fr, "category_name_zh": category.category_name_zh, "imgs": category.category_img})

    return jsonify({"categories": categories}), 200
    # Note: when creating the json data, the key should always be wrapped by DOUBLE quote


@app.route("/products")
def productsClient():
    productsData = getAllProducts()
    products = []

    # Use to print out the object key pairs inside the query
    # for u in productsData:
    #     print(u.__dict__)

    for product in productsData:
        # Retrive the price range from variants, if the price is none
        if product.price is None:
            variants = json.loads(product.variants)
            price = getPriceRangeFromVariants(variants)
        else:
            price = str(product.price)

        # This api request doesn't need all detail of a product
        products.append({"id": product.productid, "product_name_zh": product.product_name_zh, "product_name_en": product.product_name_en, "product_name_fr": product.product_name_fr,
                         "price": price, "imgs": json.loads(product.product_imgs)
                         })

    return jsonify({"products": products}), 200

# Get a specific category and all products under it


@app.route("/category")
def categoryClient():
    categoryId = request.args.get("categoryId")
    productsAndCategory = []

    categoryAndProducts = getCategoryByCategoryId(categoryId)

    print("categoryAndProducts", categoryAndProducts)

    # Get the category data saved in the res object
    product, categoryid, category_name_zh, category_name_en, category_name_fr, category_img = categoryAndProducts[
        0]
    productsAndCategory.append({
        "categoryid": categoryid, "category_name_zh": category_name_zh, "category_name_en": category_name_en,
        "category_name_fr": category_name_fr, "category_img": category_img
    })

    # Get products data saved in the res object
    products = []
    for productDetail in categoryAndProducts:
        product = productDetail[0]
        # Retrive the price range from variants, if the price is none
        if product.price is None:
            variants = json.loads(product.variants)
            price = getPriceRangeFromVariants(variants)
        else:
            price = str(product.price)
        products.append({
            "productid": product.productid, "product_name_zh": product.product_name_zh, "product_name_en": product.product_name_en,
            "product_name_fr": product.product_name_fr, "price": price, "imgs": json.loads(product.product_imgs)
        })
    productsAndCategory.append({"products": products})

    return jsonify({"categoryAndProducts": productsAndCategory}), 200
    # return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName,
    #                        noOfItems=noOfItems, categoryName=categoryName)


@app.route("/product")
def productClient():
    productid = request.args.get('productId')
    product = getProductByProductId(int(productid))
    print('product', product)

    if product.price is None:
        variants = json.loads(product.variants)
        price = getPriceRangeFromVariants(variants)
    else:
        price = str(product.price)

    productDetail = {
        "productid": product.productid, "product_name_zh": product.product_name_zh, "product_name_en": product.product_name_en,
        "product_name_fr": product.product_name_fr, "description_zh": product.description_zh, "description_en": product.description_en,
        "description_fr": product.description_fr, "price": price, "imgs": json.loads(product.product_imgs), "variants": json.loads(product.variants)
    }

    return jsonify({"product": productDetail}), 200


@app.route("/createOrder", methods=['GET', 'POST'])
@token_required
def createOrder(current_user):
    # TODO If putting a try except, the error message will be despressed
    # try:
    # Get all request data
    req = request.get_json()
    orderData, totalPrice = req.get('orderData'), req.get('totalPrice')

    # TODO in the frontend, make sure the order request passed in is in Chinese
    username, ordernumber = extractOrderdetails(current_user, orderData, totalPrice)
    # if email:
    #     sendEmailconfirmation(
    #         email, username, ordernumber, phonenumber, provider)
    return jsonify({"orderInfo": (username, ordernumber)}), 200
    # except:
    #     return {'message': 'Sorry something wrong here'}, 400
    # return render_template("OrderPage.html", email=email, username=username, ordernumber=ordernumber,
    #                        address=address, fullname=fullname, phonenumber=phonenumber)


@app.route("/orders")
@token_required
def orders(current_user):
    # Get the user
    # userId = User.query.with_entities(User.userid).filter(
    #     User.email == session['email']).first()
    # userId = userId[0]

    ordersData = Order.query.join(OrderedProduct, Order.orderid == OrderedProduct.orderid) \
        .join(Product, OrderedProduct.productid == Product.productid) \
        .with_entities(Order.orderid, Order.order_date, Order.total_price,
                        Product.productid, Product.product_name_zh, Product.product_name_en, Product.product_name_fr,
                        OrderedProduct.variant_name_zh, OrderedProduct.variant_name_en, OrderedProduct.variant_name_fr, OrderedProduct.price,
                        OrderedProduct.quantity, OrderedProduct.sum
                        ) \
        .filter(Order.userid == current_user.userid) \
        .order_by(Order.orderid.desc()) \
        .all()

    ordered_products = []
    orders = []
    for i in range(len(ordersData)):
        print(i, ordersData[i])
        orderid, order_date, total_price, productid, product_name_zh, product_name_en, product_name_fr, variant_name_zh, variant_name_en, variant_name_fr, price, quantity, sum = ordersData[
            i]
        if i != len(ordersData)-1:
            next_orderid = ordersData[i+1][0]
        else:
            # When the element is the last one, set next_orderid to None
            next_orderid = None
        ordered_products.append({
            "product_name_zh": product_name_zh, "product_name_en": product_name_en, "product_name_fr": product_name_fr,
            "variant_name_zh": variant_name_zh, "variant_name_en": variant_name_en, "variant_name_fr": variant_name_fr,
            "price": price, "quantity": quantity, "sum": sum
        })
        # When the orderid is different to the next one or it is the last one
        if next_orderid is None or orderid != next_orderid:
            orders.append({"orderid": orderid, "order_date": order_date,
                            "total_price": total_price, "ordered_products": ordered_products})
            ordered_products = []
    return jsonify({"orders": orders}), 200


# ======================================
# Admin site methods
# ======================================

@app.route("/")
@app.route("/signInAdmin")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

# Only for logging in using Admin site


@app.route("/loginAdmin", methods=['POST', 'GET'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            # If the is_valid is passed, means he is an user
            session['email'] = email
            print('Saved in session', session)
            if isUserAdmin():
                return redirect('admin')
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


@app.route("/logoutAdmin")
def logoutAdmin():
    # session.pop('email', None)
    session.clear()
    return redirect(url_for('root'))


@app.route("/registerationFormAdmin")
def registrationForm():
    return render_template("register.html")


@app.route("/registerAdmin", methods=['GET', 'POST'])
def registerAdmin():
    if request.method == 'POST':
        # Parse form data
        msg = extractAndPersistUserDataFromForm(request)
        return render_template("login.html", error=msg)


@app.route("/admin", methods=['GET'])
def root():
    if isUserAdmin():
        return render_template('admin.html')
    return redirect(url_for('loginAdmin'))

# Category functions are all tested,


@app.route("/admin/category/<int:category_id>", methods=['GET'])
def category(category_id):
    if isUserAdmin():
        category = Category.query.get_or_404(category_id)
        return render_template('adminCategory.html', category=category)
    return redirect(url_for('loginAdmin'))


@app.route("/admin/categories/new", methods=['GET', 'POST'])
def addCategory():
    if isUserAdmin():
        form = addCategoryForm()
        # safer way in case the image is not included in the form, since the img can be null
        category_icon = ""
        if form.validate_on_submit():
            if form.category_img.data:
                category_icon = save_picture(form.category_img.data)
            category = Category(category_name_zh=form.category_name_zh.data, category_name_en=form.category_name_en.data,
                                category_name_fr=form.category_name_fr.data, category_img=category_icon,
                                )
            db.session.add(category)
            db.session.commit()
            flash(
                f'Category {form.category_name_en.data}! added successfully', 'success')
            return redirect(url_for('getCategories'))
        return render_template("addCategory.html", form=form)
    return redirect(url_for('loginAdmin'))

# In this version, there is no way to remove an existing img


@app.route("/admin/categories/<int:category_id>/update", methods=['GET', 'POST'])
def update_category(category_id):
    if isUserAdmin():
        category = Category.query.get_or_404(category_id)
        form = addCategoryForm()
        if form.validate_on_submit():
            # If img is empty, we simply dont update the db, so no need to make a variable like "create" method
            if form.category_img.data:
                category.category_img = save_picture(form.category_img.data)
            category.category_name_zh = form.category_name_zh.data
            category.category_name_en = form.category_name_en.data
            category.category_name_fr = form.category_name_fr.data
            db.session.commit()
            flash('This category has been updated!', 'success')
            return redirect(url_for('getCategories'))
        elif request.method == 'GET':
            form.category_name_zh.data = category.category_name_zh
            form.category_name_en.data = category.category_name_en
            form.category_name_fr.data = category.category_name_fr
            form.category_img.data = category.category_img
        return render_template('addCategory.html', legend="Update Category", form=form)
    return redirect(url_for('loginAdmin'))


@app.route("/admin/category/<int:category_id>/delete", methods=['POST'])
def delete_category(category_id):
    if isUserAdmin():
        ProductCategory.query.filter_by(categoryid=category_id).delete()
        db.session.commit()
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        flash('Your category has been deleted!', 'success')
    return redirect(url_for('loginAdmin'))


@app.route("/admin/categories", methods=['GET'])
def getCategories():
    if isUserAdmin():
        categories = Category.query.all()
        # Query for number of products on a category:
        # cur = mysql.connection.cursor()
        # cur.execute('SELECT category.categoryid, category.category_name, COUNT(product_category.productid) as noOfProducts FROM category LEFT JOIN product_category ON category.categoryid = product_category.categoryid GROUP BY category.categoryid')
        # categories = cur.fetchall()
        # print('categories', categories, categories.category_name.get('os'))
        return render_template('adminCategories.html', categories=categories)
    return redirect(url_for('loginAdmin'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/uploads', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# All fns are tested, while creating product has ever thrown an issue with uploading img once


@app.route("/admin/products", methods=['GET'])
def getProducts():
    if isUserAdmin():
        products = Product.query.all()
        return render_template('adminProducts.html', products=products)
    return redirect(url_for('loginAdmin'))


@app.route("/admin/product/<int:product_id>", methods=['GET'])
def product(product_id):
    if isUserAdmin():
        product = Product.query.get_or_404(product_id)
        # Load json from db
        product.product_imgs = json.loads(product.product_imgs)
        return render_template('adminProduct.html', product=product)
    return redirect(url_for('loginAdmin'))


@app.route("/admin/products/new", methods=['GET', 'POST'])
def addProduct():
    if isUserAdmin():
        form = addProductForm()
        form.category.choices = [(row.categoryid, row.category_name_zh)
                                 for row in Category.query.all()]
        product_icons = []  # safer way in case the image is not included in the form
        if form.validate_on_submit():
            # Since the product_imgs has the format of <FileStorage: '' ('application/octet-stream')>, a simple if statement cannot detect if it is empty,
            # we need to access its filename to assure it is not blank
            for img in form.product_imgs.data:
                if(img.filename):
                    img_reference = save_picture(img)
                    product_icons.append(img_reference)

            variants = []
            for variant in [form.productVariant1, form.productVariant2, form.productVariant3, form.productVariant4, form.productVariant5]:
                # Make sure it is not empty string
                variant = str(variant.data)
                print(variant)
                if variant is not None and len(variant) > 0:
                    variantData = variant.split(", ")
                    print('variantData', variantData)
                    variants.append({"variant_name_zh": variantData[0], "variant_name_en": variantData[1],
                                     "variant_name_fr": variantData[2], "variant_price": variantData[3]})
            print("variants", variants)

            product = Product(sku=form.sku.data, product_name_zh=form.product_name_zh.data, product_name_en=form.product_name_en.data, product_name_fr=form.product_name_fr.data,
                              description_zh=form.description_zh.data, description_en=form.description_en.data, description_fr=form.description_fr.data,
                              product_imgs=json.dumps(product_icons), quantity=form.productQuantity.data, price=form.productPrice.data, variants=json.dumps(variants)
                              )
            db.session.add(product)
            db.session.commit()
            product_category = ProductCategory(
                categoryid=form.category.data, productid=product.productid)
            db.session.add(product_category)
            db.session.commit()
            flash(
                f'Product {form.product_name_en} added successfully', 'success')
            return redirect(url_for('getProducts'))
        return render_template("addProduct.html", form=form, legend="New Product")
    return redirect(url_for('loginAdmin'))


@app.route("/admin/product/<int:product_id>/update", methods=['GET', 'POST'])
def update_product(product_id):
    if isUserAdmin():
        product = Product.query.get_or_404(product_id)
        form = addProductForm()
        form.category.choices = [(row.categoryid, row.category_name_en)
                                 for row in Category.query.all()]
        if form.validate_on_submit():
            product_icons = []
            for img in form.product_imgs.data:
                # print('img filename', img.filename)
                if(img.filename):
                    img_reference = save_picture(img)
                    product_icons.append(img_reference)
            # Only update product if product_icons has data inside
            if(len(product_icons) != 0):
                product.product_imgs = json.dumps(product_icons)

            product.sku = form.sku.data
            product.product_name_zh = form.product_name_zh.data
            product.product_name_en = form.product_name_en.data
            product.product_name_fr = form.product_name_fr.data
            product.description_zh = form.description_zh.data
            product.description_en = form.description_en.data
            product.description_fr = form.description_fr.data
            product.quantity = form.productQuantity.data
            product.price = form.productPrice.data

            variants = []
            for variant in [form.productVariant1, form.productVariant2, form.productVariant3, form.productVariant4, form.productVariant5]:
                # Make sure it is not empty string
                variant = str(variant.data)
                print('variantRaw', variant)
                if variant is not None and len(variant) > 0:
                    variantData = variant.split(", ")
                    print('variantData', variantData)
                    variants.append({"variant_name_zh": variantData[0], "variant_name_en": variantData[1],
                                     "variant_name_fr": variantData[2], "variant_price": variantData[3]})
            print("variants", variants)
            product.variants = json.dumps(variants)
            db.session.commit()

            product_category = ProductCategory.query.filter_by(
                productid=product.productid).first()
            if form.category.data != product_category.categoryid:
                new_product_category = ProductCategory(
                    categoryid=form.category.data, productid=product.productid)
                db.session.add(new_product_category)
                db.session.commit()
                db.session.delete(product_category)
                db.session.commit()
            flash('This product has been updated!', 'success')
            return redirect(url_for('getProducts'))
        elif request.method == 'GET':
            form.sku.data = product.sku
            form.product_name_zh.data = product.product_name_zh
            form.product_name_en.data = product.product_name_en
            form.product_name_fr.data = product.product_name_fr
            form.description_zh.data = product.description_zh
            form.description_en.data = product.description_en
            form.description_fr.data = product.description_fr
            form.productPrice.data = product.price
            form.productQuantity.data = product.quantity
            # Load json from db
            form.product_imgs.data = json.loads(product.product_imgs)
            variants = json.loads(product.variants)
            form_productVariants = [form.productVariant1, form.productVariant2,
                                    form.productVariant3, form.productVariant4, form.productVariant5]
            for i in range(len(variants)):
                variant_name_zh, variant_name_en, variant_name_fr, variant_price = variants[i].get("variant_name_zh"), variants[i].get(
                    "variant_name_en"), variants[i].get("variant_name_fr"), variants[i].get("variant_price")
                form_productVariants[i].data = f"{variant_name_zh}, {variant_name_en}, {variant_name_fr}, {variant_price}"
        return render_template('addProduct.html', legend="Update Product", form=form)
    return redirect(url_for('loginAdmin'))


@app.route("/admin/product/<int:product_id>/delete", methods=['POST'])
def delete_product(product_id):
    if isUserAdmin():
        product_category = ProductCategory.query.filter_by(
            productid=product_id).first()
        if product_category is not None:
            db.session.delete(product_category)
            db.session.commit()
        Cart.query.filter_by(productid=product_id).delete()
        db.session.commit()
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Your product has been deleted!', 'success')
    return redirect(url_for('loginAdmin'))


@app.route("/admin/users", methods=['GET'])
def getUsers():
    if isUserAdmin():
        users = User.query.all()
        # cur = mysql.connection.cursor()
        # cur.execute('SELECT u.fname, u.lname, u.email, u.active, u.city, u.state, COUNT(o.orderid) as noOfOrders FROM `user` u LEFT JOIN `order` o ON u.userid = o.userid GROUP BY u.userid')
        # users = cur.fetchall()
        return render_template('adminUsers.html', users=users)
    return redirect(url_for('loginAdmin'))
