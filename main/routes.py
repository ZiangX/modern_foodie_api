from flask import render_template, url_for, redirect, request, Blueprint

main = Blueprint('main', __name__)

from ecommerce_blueprint_version import db
from ecommerce_blueprint_version.models import Product, Category, ProductCategory, Cart
from ecommerce_blueprint_version.auth.utils import isUserAdmin
from ecommerce_blueprint_version.products.forms import addProductForm

@main.route("/home")
def home():
    return "Hello"
