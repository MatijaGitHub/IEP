import csv
import io
from redis import Redis
from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, Category
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from adminDecorator import roleCheck
from json import dumps



application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/update", methods=["POST"])
@roleCheck("storekeeper")
def update():
    try:
        file = request.files["file"]
    except:
        return jsonify(message="Field file is missing."), 400
    if not file:
        return jsonify(message="Field file is missing."), 400
    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    products = []
    line = 0
    for row in reader:
        if len(row) != 4:
            return jsonify(message=f"Incorrect number of values on line {line}."), 400
        categories = row[0].split("|")

        name = row[1]
        amount = ""
        try:
            amount = int(row[2])
        except:
            return jsonify(message=f"Incorrect quantity on line {line}."), 400
        if not isinstance(amount,int) or int(amount) <= 0:
            return jsonify(message=f"Incorrect quantity on line {line}."), 400

        try:
            cost = float(row[3])
        except:
            return jsonify(message=f"Incorrect price on line {line}."), 400
        if float(cost) <= 0:
            return jsonify(message=f"Incorrect price on line {line}."), 400

        product = {
            "categories": categories,
            "name": name,
            "amount": amount,
            "price": cost,
            "orders": []
        }
        products.append(product)
        line += 1
    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.rpush(Configuration.REDIS_PRODUCTS_LIST, dumps(products))
    return Response(status=200)


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5006)
