from flask import render_template, url_for, redirect, request, Blueprint, jsonify

orders = Blueprint('orders', __name__)

from ecommerce_blueprint_version.models import Product, Category, ProductCategory, Cart
from ecommerce_blueprint_version.auth.utils import token_required
from ecommerce_blueprint_version.orders.utils import place_order, get_orders

@orders.route("/placeOrder", methods=['GET', 'POST'])
@token_required
def placeOrder(current_user):
    # TODO If putting a try except, the error message will be despressed
    # try:
    # Get all request data
    req = request.get_json()
    orderData, totalPrice = req.get('orderData'), req.get('totalPrice')

    # TODO in the frontend, make sure the order request passed in is in Chinese
    username, ordernumber = place_order(current_user, orderData, totalPrice)
    # if email:
    #     sendEmailconfirmation(
    #         email, username, ordernumber, phonenumber, provider)
    return jsonify({"orderInfo": (username, ordernumber)}), 200
    # except:
    #     return {'message': 'Sorry something wrong here'}, 400
    # return render_template("OrderPage.html", email=email, username=username, ordernumber=ordernumber,
    #                        address=address, fullname=fullname, phonenumber=phonenumber)


@orders.route("/orders")
@token_required
def getOrders(current_user):
    # Get the user
    # userId = User.query.with_entities(User.userid).filter(
    #     User.email == session['email']).first()
    # userId = userId[0]

    ordersData = get_orders(current_user)

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


