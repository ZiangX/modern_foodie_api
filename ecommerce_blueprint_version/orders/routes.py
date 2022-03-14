from flask import request, Blueprint, jsonify, redirect, url_for, render_template

orders = Blueprint('orders', __name__)

from ecommerce_blueprint_version.auth.utils import token_required, isUserAdmin
from ecommerce_blueprint_version.orders.utils import *
from ecommerce_blueprint_version.orders.forms import importExcelForm


@orders.route("/admin/importExcel", methods=['GET', 'POST'])
def importExcel():
    if isUserAdmin():
        form = importExcelForm()
        if form.validate_on_submit():
            sheetValues = import_excel(form.excel_file.data)
            if form.confirm.data:
                order_id, wechat_name, recipient, phone, price, note, address = '', '', '', '', '', '', ''
                for value in sheetValues:
                    # if order id is not null and different than the last row
                    if value[0] and order_id != value[0]:
                        order_id, wechat_name, recipient, phone = value[0:4]
                        price, note, address = value[5:]
                        # Convert order_id to int
                        if isinstance(order_id, float):
                            order_id = convert_float_to_int(order_id)
                        # convert order_id from string to int, and filter out the non numeric letter
                        if isinstance(order_id, str):
                            numeric_filter = filter(str.isdigit, order_id)
                            order_id = int("".join(numeric_filter))


                    ordered_product = value[4]
                    price = value[5] if value[5] else price                  
                    print(order_id, wechat_name, recipient, phone, ordered_product, price, note, address)
                    order = WeChatOrder(order_id=order_id, wechat_name=wechat_name, recipient=recipient, 
                        phone=phone, orderedProducts=ordered_product, price=price, note=note, address=address
                    )
                    db.session.add(order)
                    db.session.commit()
                return render_template("importExcel.html", form=form, sheetValues=sheetValues, convert_float_to_int=convert_float_to_int, uploadSuccess=True)
            return render_template("importExcel.html", form=form, sheetValues=sheetValues, convert_float_to_int=convert_float_to_int)
        return render_template("importExcel.html", form=form)
    return redirect(url_for('auth.login_admin'))
    

@orders.route("/placeOrder", methods=['GET', 'POST'])
@token_required
def placeOrder(current_user):
    # Get all request data
    req = request.get_json()
    orderData, totalPrice, address, note, shipping_fee = req.get('orderData'), req.get('totalPrice'), req.get('address'), req.get('note'), req.get('shipping_fee')

    # TODO in the frontend, make sure the order request passed in is in Chinese
    username, ordernumber = place_order(current_user, orderData, totalPrice, address, note, shipping_fee)
    # if email:
    #     sendEmailconfirmation(
    #         email, username, ordernumber, phonenumber, provider)
    return jsonify({"orderInfo": (username, ordernumber)}), 200


@orders.route("/orders")
@token_required
def getOrders(current_user):
    if current_user.email in ['ziangxuu@gmail.com', 'modernfoodieMTL@gmail.com', 'jaytq19921228@gmail.com']:
        order_id = int(request.args.get('orderId')) if request.args.get('orderId') else None
        if order_id:
            print(order_id)
            wechat_orders = WeChatOrder.query.filter(WeChatOrder.order_id==order_id).all()
        else:
            wechat_orders = WeChatOrder.query.all()
        formated_wechat_orders = []
        for order in wechat_orders:
            formated_wechat_orders.append({"order_id": order.order_id, "wechat_name": order.wechat_name, "recipient": order.recipient, 
                "phone": order.phone, "orderedProducts": order.orderedProducts, "price": order.price, "note": order.note, "address": order.address})
        # print(formated_wechat_orders)
        return jsonify({"formated_wechat_orders": formated_wechat_orders}), 200

    ordersData = get_orders(current_user)

    ordered_products = []
    orders = []

    for i in range(len(ordersData)):
        print(i, ordersData[i])
        orderid, order_date, total_price, address, shipping_fee, note, productid, product_name_zh, product_name_en, product_name_fr, variant_name_zh, variant_name_en, variant_name_fr, price, quantity, sum = ordersData[
            i]
        if i != len(ordersData)-1:
            next_orderid = ordersData[i+1][0]
        else:
            # When the element is the last one, set next_orderid to None
            next_orderid = None
        ordered_products.append({
            "product_name_zh": product_name_zh, "product_name_en": product_name_en, "product_name_fr": product_name_fr,
            "variant_name_zh": variant_name_zh, "variant_name_en": variant_name_en, "variant_name_fr": variant_name_fr,
            "productid": productid, "price": price, "quantity": quantity, "sum": sum
        })
        # When the orderid is different to the next one or it is the last one
        if next_orderid is None or orderid != next_orderid:
            orders.append({"order_id": orderid, "order_date": order_date, "address": address, "shipping_fee": shipping_fee, "note": note,
                            "total_price": total_price, "ordered_products": ordered_products})
            ordered_products = []
    return jsonify({"orders": orders}), 200


