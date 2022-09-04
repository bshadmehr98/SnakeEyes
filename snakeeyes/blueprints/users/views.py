from flask_restx import Resource
from snakeeyes.extentions import api
from snakeeyes.blueprints.users.dto import UserDTO
from snakeeyes.blueprints.dto import GeneralDTO
from flask_restx import marshal
from snakeeyes.blueprints.users.models import User
from lib.auth import platform_authorized
from flask import request
from bson.objectid import ObjectId
import pytz

users = api.namespace("users", description="Users CRUD")


@users.route("")
class UsersList(Resource):
    @users.expect(UserDTO, validate=True)
    @users.marshal_with(UserDTO, code=201, skip_none=True)
    @platform_authorized
    def post(self):
        data = marshal(api.payload, UserDTO)
        user, created = User.get_or_create(
            data["email"], request.platform, data["timezone"]
        )
        if created:
            message = "User created"
        else:
            user.regenerate_token()
            if data["timezone"] != user.timezone:
                user.timezone = data["timezone"]
                user.save()
            message = "User token changed"
        response = user.to_mongo()
        response["message"] = message
        return response, 201

    @users.marshal_with(UserDTO, code=200, skip_none=True)
    @platform_authorized
    def get(self):
        try:
            users = User.objects(platform=request.platform)
            print(users)
        except Exception:
            return {"message": "User not found"}, 404
        return [user.to_mongo() for user in users], 200


@users.route("/<string:id>")
@users.response(404, "User not found")
@users.param("id", "The user identifier")
class Users(Resource):
    @users.marshal_with(UserDTO, skip_none=True)
    @platform_authorized
    def get(self, id):
        user = User.objects(token=id).first()
        if user is not None:
            response = user.to_mongo()
            response["message"] = "message"
            return response, 200
        return {"message": "User not found"}, 404

    @users.doc("delete_user")
    @users.response(204, "User deleted")
    @platform_authorized
    def delete(self, id):
        user = User.objects(token=id).first()
        if user is not None:
            user.delete()
            return {"message": "User deleted"}, 200
        return {"message": "User not found"}, 404

    @users.doc("update_user")
    @users.response(204, "User deleted")
    @users.expect(UserDTO)
    @users.marshal_with(UserDTO, code=200, skip_none=True)
    @platform_authorized
    def patch(self, id):
        user = User.objects(token=id).first()
        if user is not None:
            data = marshal(api.payload, UserDTO)
            if data["timezone"] not in pytz.all_timezones:
                return {"message": "Invalid timezone"}, 400
            user.timezone = data["timezone"]
            user.save()
            return user.to_mongo(), 200
        return {"message": "User not found"}, 404
