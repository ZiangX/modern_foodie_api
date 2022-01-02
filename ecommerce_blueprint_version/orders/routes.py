from flask import request, Blueprint, jsonify, redirect, url_for, render_template

orders = Blueprint('orders', __name__)

from ecommerce_blueprint_version.auth.utils import token_required, isUserAdmin
from ecommerce_blueprint_version.orders.utils import place_order, get_orders, import_excel, convert_float_to_int
from ecommerce_blueprint_version.orders.forms import importExcelForm


@orders.route("/admin/importExcel", methods=['GET', 'POST'])
def importExcel():
    if isUserAdmin():
        form = importExcelForm()
        if form.validate_on_submit():
            sheetValues = import_excel(form.excel_file.data)
            if form.confirm.data:
                print(form.confirm.data)
                # category = Category(category_name_zh=form.category_name_zh.data, category_name_en=form.category_name_en.data,
                #                     category_name_fr=form.category_name_fr.data, category_img=category_icon,
                #                     )
                # db.session.add(category)
                # db.session.commit()
                # return redirect(url_for('admin.html'))
                return render_template("importExcel.html", form=form, sheetValues=sheetValues, convert_float_to_int=convert_float_to_int, uploadSuccess=True)
            return render_template("importExcel.html", form=form, sheetValues=sheetValues, convert_float_to_int=convert_float_to_int)
        return render_template("importExcel.html", form=form)
    return redirect(url_for('auth.login_admin'))


@orders.route("/placeOrder", methods=['GET', 'POST'])
@token_required
def placeOrder(current_user):
    # Get all request data
    req = request.get_json()
    orderData, totalPrice = req.get('orderData'), req.get('totalPrice')

    # TODO in the frontend, make sure the order request passed in is in Chinese
    username, ordernumber = place_order(current_user, orderData, totalPrice)
    # if email:
    #     sendEmailconfirmation(
    #         email, username, ordernumber, phonenumber, provider)
    return jsonify({"orderInfo": (username, ordernumber)}), 200


@orders.route("/orders")
@token_required
def getOrders(current_user):
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


