import csv
import io
import json
import datetime
from sys import stdout

from sqlalchemy import func
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



@application.route("/productStatistics", methods=["GET"])
@roleCheck("admin")
def productStatistics():
    sumRecieved = func.sum(OrderProduct.amountRecieved)
    sumRequested = func.sum(OrderProduct.amount)
    statistics = OrderProduct.query.group_by(OrderProduct.product_id).with_entities(OrderProduct.product_id,sumRecieved,sumRequested-sumRecieved).having(sumRecieved > 0).all()
    statisticsJSON = [{"name" : Product.query.filter(Product.id == product[0]).first().name, "sold": int(product[1]), "waiting": int(product[2])} for product in statistics]
    return jsonify(statistics=statisticsJSON), 200

@application.route("/categoryStatistics", methods=["GET"])
@roleCheck("admin")
def categoryStatistics():
    sumRecieved = func.sum(OrderProduct.amountRecieved)
    sortedCategories = Category.query.join(CategoryProduct).join(OrderProduct, CategoryProduct.product_id == OrderProduct.product_id)\
        .group_by(Category.id).order_by(sumRecieved.desc()).order_by(Category.category_name).with_entities(Category.category_name).all()
    print(sortedCategories)
    stdout.flush()
    statistics = [c[0] for c in sortedCategories]

    return jsonify(statistics=statistics), 200



if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5004)
