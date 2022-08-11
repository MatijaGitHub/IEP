import csv
import io
from json import loads
from sys import stdout
from redis import Redis
from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, Category, CategoryProduct
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from adminDecorator import roleCheck

if (__name__ == "__main__"):
    application = Flask(__name__)
    application.config.from_object(Configuration)
    database.init_app(application)
    while True:
        with application.app_context():
            with Redis(Configuration.REDIS_HOST) as redis:
                products = loads(redis.blpop(Configuration.REDIS_PRODUCTS_LIST)[1])
                print("Products ack!")
                stdout.flush()
                for product in products:
                    product_exists = Product.query.filter_by(name=product["name"]).first()
                    if not product_exists:
                        added_product = Product(name=product["name"], price=product["price"], amount=product["amount"])
                        database.session.add(added_product)
                        database.session.commit()
                        for category in product["categories"]:
                            category_exists = Category.query.filter_by(category_name=category).first()
                            if not category_exists:
                                added_category = Category(category_name=category)
                                database.session.add(added_category)
                                database.session.flush()
                            database.session.add(CategoryProduct(product_id=added_product.id, category_id=added_category.id))
                            database.session.commit()
                    else:
                        equal = True
                        if len(product_exists.categories) != len(product["categories"]):
                            equal = False
                        if equal:
                            for category in product_exists.categories:
                                if not category.category_name in product["categories"]:
                                    equal = False
                                    break
                        if not equal:
                            continue
                        else:
                            cA = product_exists.amount
                            cP = product_exists.price
                            dA = product["amount"]
                            dP = product["price"]
                            newQuantity = product_exists.amount + product["amount"]
                            newPrice = (cA * cP + dA * dP)/(dA + cA)
                            product_exists.price = newPrice
                            product_exists.amount = newQuantity
                            database.session.add(product_exists)
                            database.session.commit()



