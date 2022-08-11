from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Response


def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request()
            claims = get_jwt()
            roleID = 3 if role == "admin" else 0
            if ("role" in claims) and roleID == claims["role"]:
                return function(*arguments, **keywordArguments)
            else:
                return Response("Permission denied!", status=403)

        return decorator

    return innerRole
