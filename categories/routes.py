from ecommerce_blueprint_version import categories
from flask import render_template, url_for, redirect, request, Blueprint, jsonify
import json

categories = Blueprint('categories', __name__)

from ecommerce_blueprint_version import db
from ecommerce_blueprint_version.models import Category, ProductCategory
from ecommerce_blueprint_version.auth.utils import isUserAdmin
from ecommerce_blueprint_version.main.utils import save_picture
from ecommerce_blueprint_version.categories.forms import addCategoryForm
from ecommerce_blueprint_version.products.utils import getPriceRangeFromVariants, getProductsByCategoryId

@categories.route("/categories")
def get_categories_for_client():
    original_format_categories = Category.query.all()
    formated_categories = {}
    print(original_format_categories)
    # Since the categories is of sqlalchemy query result object, we have to abstract to a new dict
    for category in original_format_categories:
        formated_categories[category.categoryid] = {"id": category.categoryid, "category_name_en": category.category_name_en,
                           "category_name_fr": category.category_name_fr, "category_name_zh": category.category_name_zh, "imgs": category.category_img}

    return jsonify({"categories": formated_categories}), 200
    # Note: when creating the json data, the key should always be wrapped by DOUBLE quote


@categories.route("/category")
def get_category_and_products_for_client():
    categoryId = request.args.get("categoryId")

    products_by_categoryId = getProductsByCategoryId(categoryId)

    print("products_by_categoryId", products_by_categoryId)

    # Get products data saved in the res object
    products = []
    for product in products_by_categoryId:
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

    return jsonify({"products": products}), 200


@categories.route("/admin/category/<int:category_id>")
def category(category_id):
    if isUserAdmin():
        category = Category.query.get_or_404(category_id)
        return render_template('adminCategory.html', category=category)
    return redirect(url_for('auth.login_admin'))


@categories.route("/admin/categories/new", methods=['GET', 'POST'])
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
            return redirect(url_for('categories.getCategories'))
        return render_template("addCategory.html", form=form)
    return redirect(url_for('auth.login_admin'))

# In this version, there is no way to remove an existing img


@categories.route("/admin/categories/<int:category_id>/update", methods=['GET', 'POST'])
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
            return redirect(url_for('categories.getCategories'))
        elif request.method == 'GET':
            form.category_name_zh.data = category.category_name_zh
            form.category_name_en.data = category.category_name_en
            form.category_name_fr.data = category.category_name_fr
            form.category_img.data = category.category_img
        return render_template('addCategory.html', legend="Update Category", form=form)
    return redirect(url_for('auth.login_admin'))


@categories.route("/admin/category/<int:category_id>/delete", methods=['POST'])
def delete_category(category_id):
    if isUserAdmin():
        ProductCategory.query.filter_by(categoryid=category_id).delete()
        db.session.commit()
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('categories.getCategories'))
    return redirect(url_for('auth.login_admin'))


@categories.route("/admin/categories")
def getCategories():
    if isUserAdmin():
        categories = Category.query.all()
        return render_template('adminCategories.html', categories=categories)
    return redirect(url_for('auth.login_admin'))

