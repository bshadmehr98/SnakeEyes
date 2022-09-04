from flask_restx import Resource
from snakeeyes.extentions import api
from snakeeyes.blueprints.dashboard.dto import DashboardUserDTO, AuthDTO
from snakeeyes.blueprints.dto import GeneralDTO
from flask_restx import marshal
from snakeeyes.blueprints.dashboard.models import DashboardUser
from flask import request
from bson.objectid import ObjectId
import pytz
from lib.jwt import get_access_token

auth = api.namespace("auth", description="Auth")


@auth.route("/signup")
class Signup(Resource):
    @auth.marshal_with(AuthDTO, skip_none=True)
    @auth.expect(DashboardUserDTO)
    def post(self):
        data = marshal(api.payload, DashboardUserDTO)
        user = DashboardUser.objects(email=data["email"]).first()
        if user is not None:
            return {"message": "Email already exists"}, 200
        user, _ = DashboardUser.get_or_create(data["email"], data["raw_password"])
        token = get_access_token(str(user.id), user.role)
        return {"access_token": token}, 201


@auth.route("/login")
class Login(Resource):
    @auth.marshal_with(AuthDTO, skip_none=True)
    @auth.expect(DashboardUserDTO)
    def post(self):
        data = marshal(api.payload, DashboardUserDTO)
        user = DashboardUser.objects(email=data["email"]).first()
        if user is None:
            return {"message": "User not found"}, 404
        if not user.check_secret(data["raw_password"]):
            return {"message": "User not found"}, 404
        token = get_access_token(str(user.id), user.role)
        return {"access_token": token}, 201
