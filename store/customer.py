import csv
import io
from redis import Redis
from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, Category, CategoryProduct
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
#@roleCheck("customer")
def search():
    product_name = ""
    category_name = ""
    for arg in request.args.items():
        if arg[0] == "name":
            product_name = arg[1]
        if arg[0] == "category":
            category_name = arg[1]
    categories = []
    if category_name != "" and product_name != "":
        categories = Category.query.join(CategoryProduct).filter(Category.category_name.like(f"%{category_name}%"))\
          .join(Product).filter(Product.name.like(f"%{product_name}%")).all()
        return jsonify(categories=[category.category_name for category in categories]),200
    elif category_name != "":
        pass
    elif product_name != "":
        pass
    else:
        pass
    return Response(status=400)





if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5005)
