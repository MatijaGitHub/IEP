from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, Role
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from adminDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)


def password_check(passwd):
    val = True
    if len(passwd) < 8:
        val = False
    if len(passwd) > 256:
        val = False
    if not any(char.isdigit() for char in passwd):
        val = False
    if not any(char.isupper() for char in passwd):
        val = False
    if not any(char.islower() for char in passwd):
        val = False
    return val
@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", "")

    emailEmpty = len(email) == 0
    emailTooLong = len(email) > 256
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0


    if emailEmpty:
        return jsonify(message="Field email is missing."), 400
    if passwordEmpty:
        return jsonify(message="Field password is missing."), 400
    if forenameEmpty:
        return jsonify(message="Field forename is missing."), 400
    if surnameEmpty:
        return jsonify(message="Field surname is missing."), 400

    result = parseaddr(email)
    if (len(result[1]) == 0 or emailTooLong):
        return jsonify(message="Invalid email."), 400
    if not password_check(password):
        return jsonify(message="Invalid password."), 400
    if User.query.filter_by(email = email).first():
        return jsonify(message="Email already exists."), 400

    role = 1 if isCustomer else 2
    user = User(email=email, password=password, forename=forename, surname=surname, my_role=role)
    database.session.add(user)
    database.session.commit()
    return Response("Registration successful!", status=200)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    emailTooLong = len(email) > 256

    if emailEmpty:
        return jsonify(message="Field email is missing."), 400
    if passwordEmpty:
        return jsonify(message="Field password is missing."), 400
    result = parseaddr(email)
    if len(result[1]) == 0 or emailTooLong:
        return jsonify(message="Invalid email."), 400
    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if not user:
        return jsonify(message="Invalid credentials."), 400

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "role": user.my_role
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken), 200

@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"]
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200

@application.route("/delete" , methods=["POST"])
@roleCheck("admin")
@jwt_required()
def delete():
    email = request.json.get("email","")
    emailEmpty = len(email) == 0
    emailTooLong = len(email) > 256

    if emailEmpty:
        return jsonify(message="Field email is missing."), 400


    result = parseaddr(email)
    if len(result[1]) == 0 or emailTooLong:
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify(message="Unknown user."), 400
    database.session.delete(user)
    database.session.commit()
    return Response(status=200)

if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
