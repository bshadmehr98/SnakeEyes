import functools
from flask import request
from snakeeyes.blueprints.platforms.models import Platform
from snakeeyes.blueprints.users.models import User
from bson.objectid import ObjectId
from lib.jwt import decode_access_token


def platform_authorized(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        token = request.headers.get("Platform-Token", None)
        secret = request.headers.get("Platform-Secret", None)
        if token is None or secret is None:
            return {"message": "Unauthorized"}, 401
        platform = Platform.objects(token=token).first()
        if platform is None:
            return {"message": "Unauthorized"}, 401
        if not platform.check_secret(secret):
            return {"message": "Unauthorized"}, 401
        request.platform = platform
        value = func(*args, **kwargs)
        return value

    return wrapper_decorator


def should_authenticate(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        token = request.headers.get("Access-Token", None)
        claims = decode_access_token(token)
        if "user_id" not in claims:
            return {"message": "Unauthorized"}, 401
        user = Platform.objects(id=ObjectId(claims["user_id"])).first()
        if user is None:
            return {"message": "Unauthorized"}, 401
        request.user = user
        value = func(*args, **kwargs)
        return value

    return wrapper_decorator
