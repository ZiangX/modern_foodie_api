from flask import render_template, url_for, redirect, request, Blueprint, jsonify
import json

products = Blueprint('products', __name__)

from ecommerce_blueprint_version import db
from ecommerce_blueprint_version.models import Product, Category, ProductCategory, Cart
from ecommerce_blueprint_version.auth.utils import isUserAdmin
from ecommerce_blueprint_version.main.utils import save_picture
from ecommerce_blueprint_version.products.forms import addProductForm
from ecommerce_blueprint_version.products.utils import getAllProducts, getPriceRangeFromVariants, getProductByProductId


@products.route("/products")
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
            price = product.price

        # This api request doesn't need all detail of a product
        products.append({"id": product.productid, "product_name_zh": product.product_name_zh, "product_name_en": product.product_name_en, 
            "product_name_fr": product.product_name_fr, "description_zh": product.description_zh, "description_en": product.description_en, 
            "description_fr": product.description_fr, "price": price, "imgs": json.loads(product.product_imgs), "variants": json.loads(product.variants)
            })

    return jsonify({"products": products}), 200


@products.route("/product")
def productClient():
    productid = request.args.get('productId')
    product = getProductByProductId(int(productid))
    print('product', product)

    if product.price is None:
        variants = json.loads(product.variants)
        price = getPriceRangeFromVariants(variants)
    else:
        price = product.price

    productDetail = {
        "productid": product.productid, "product_name_zh": product.product_name_zh, "product_name_en": product.product_name_en,
        "product_name_fr": product.product_name_fr, "description_zh": product.description_zh, "description_en": product.description_en,
        "description_fr": product.description_fr, "price": price, "imgs": json.loads(product.product_imgs), "variants": json.loads(product.variants)
    }

    return jsonify({"product": productDetail}), 200


@products.route("/admin/products")
def getProducts():
    if isUserAdmin():
        products = Product.query.all()
        return render_template('adminProducts.html', products=products)
    return redirect(url_for('auth.login_admin'))


@products.route("/admin/product/<int:product_id>")
def product(product_id):
    if isUserAdmin():
        product = Product.query.get_or_404(product_id)
        # Load json from db
        product.product_imgs = json.loads(product.product_imgs)
        return render_template('adminProduct.html', product=product)
    return redirect(url_for('auth.login_admin'))


@products.route("/admin/products/new", methods=['GET', 'POST'])
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

            product = Product(product_name_zh=form.product_name_zh.data, product_name_en=form.product_name_en.data, product_name_fr=form.product_name_fr.data,
                              description_zh=form.description_zh.data, description_en=form.description_en.data, description_fr=form.description_fr.data,
                              product_imgs=json.dumps(product_icons), quantity=form.productQuantity.data, price=form.productPrice.data, variants=json.dumps(variants)
                              )
            db.session.add(product)
            db.session.commit()
            product_category = ProductCategory(
                categoryid=form.category.data, productid=product.productid)
            db.session.add(product_category)
            db.session.commit()
            return redirect(url_for('products.getProducts'))
        return render_template("addProduct.html", form=form, legend="New Product")
    return redirect(url_for('auth.login_admin'))


@products.route("/admin/product/<int:product_id>/update", methods=['GET', 'POST'])
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
            return redirect(url_for('products.getProducts'))
        elif request.method == 'GET':
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
    return redirect(url_for('auth.login_admin'))


@products.route("/admin/product/<int:product_id>/delete", methods=['POST'])
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
    return redirect(url_for('auth.login_admin'))

