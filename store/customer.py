import csv
import io
import json
import datetime

from redis import Redis
from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, Category, CategoryProduct, OrderProduct, Order
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from adminDecorator import roleCheck
from json import dumps

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@roleCheck("customer")
def search():
    product_name = ""
    category_name = ""
    for arg in request.args.items():
        if arg[0] == "name":
            product_name = arg[1]
        if arg[0] == "category":
            category_name = arg[1]
    categories = []
    products = []
    if category_name != "" and product_name != "":
        categories = Category.query.join(CategoryProduct).filter(
            Category.category_name.like(f"%{category_name}%")) \
            .join(Product).filter(Product.name.like(f"%{product_name}%")).all()
        products = Product.query.join(CategoryProduct).filter(
            Product.name.like(f"%{product_name}%")) \
            .join(Category).filter(Category.category_name.like(f"%{category_name}%")).all()
    elif category_name != "":
        categories = Category.query.join(CategoryProduct).filter(
            Category.category_name.like(f"%{category_name}%")) \
            .join(Product).all()
        products = Product.query.join(CategoryProduct) \
            .join(Category).filter(Category.category_name.like(f"%{category_name}%")).all()
    elif product_name != "":
        categories = Category.query.join(CategoryProduct).join(Product).filter(
            Product.name.like(f"%{product_name}%")) \
            .all()
        products = Product.query.join(CategoryProduct).filter(
            Product.name.like(f"%{product_name}%")) \
            .join(Category).all()
    else:
        categories = Category.query.join(CategoryProduct).join(Product).all()
        products = Product.query.join(CategoryProduct).join(Category).all()
    categoriesJSON = [category.category_name for category in categories]
    productsJSON = [{"categories": [category.category_name for category in product.categories] \
                        , "id": product.id, "name": product.name, "price": product.price, "quantity": product.amount} \
                    for product in products]
    return jsonify(categories=categoriesJSON, products=productsJSON), 200


@application.route("/order", methods=["POST"])
@roleCheck("customer")
def order():
    orders = request.json.get("requests", "")
    if not orders:
        return jsonify(message="Field requests is missing."), 400
    objectCounter = 0
    totalPrice = 0
    status = True
    orderDB = Order(email=get_jwt_identity(), totalPrice=0, status=False, timestamp=datetime.datetime.now().isoformat())
    database.session.add(orderDB)
    database.session.commit()
    for order in orders:
        id = order["id"]
        amount = order["quantity"]
        if not id:
            return jsonify(message=f"Product id is missing for request number {objectCounter}."), 400
        if not amount:
            return jsonify(message=f"Product quantity is missing for request number {objectCounter}."), 400
        if id <= 0:
            return jsonify(message=f"“Invalid product id for request number {objectCounter}."), 400
        if amount <= 0:
            return jsonify(message=f"“Invalid product quantity for request number {objectCounter}."), 400

        product = Product.query.filter(Product.id == id).first()
        if not product:
            return jsonify(message=f"“Invalid product for request number {objectCounter}."), 400

        orderProduct = None
        if product.amount > amount:
            orderProduct = OrderProduct(order_id=orderDB.id, product_id=product.id, amount=amount, amountRecieved=amount, isBought=True)
            product.amount -= amount

        else:
            status = False
            amountRecieved = product.amount
            product.amount = 0
            orderProduct = OrderProduct(order_id=orderDB.id, product_id=product.id, amount=amount, amountRecieved=amountRecieved, isBought=False)

        totalPrice += product.price * amount
        database.session.add(product)
        database.session.add(orderProduct)
        database.session.commit()

        objectCounter += 1

    orderDB.status = status
    orderDB.totalPrice = totalPrice
    database.session.add(orderDB)
    database.session.commit()
    return jsonify(id=orderDB.id), 200

@application.route("/status", methods=["GET"])
@roleCheck("customer")
def status():
    email = get_jwt_identity()
    orders = Order.query.filter(Order.email == email).all()
    ordersJSON = [{"products": [{"categories":[category.category_name for category in product.categories], "name": product.name,"price" : product.price, "recieved": OrderProduct.query.filter(and_(OrderProduct.order_id == order.id, OrderProduct.product_id == product.id)).first().amountRecieved,"requested": OrderProduct.query.filter(and_(OrderProduct.order_id == order.id, OrderProduct.product_id == product.id)).first().amount}for product in order.products], "price":order.totalPrice, "status": ("COMPLETE" if order.status == True else "PENDING"), "timestamp": order.timestamp.isoformat()} for order in orders]
    return jsonify(orders=ordersJSON), 200


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5005)
