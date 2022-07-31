from flask_restx import Resource
from snakeeyes.extentions import api
from flask_restx import marshal
from snakeeyes.blueprints.users.models import User
from lib.auth import platform_authorized
from flask import request
from snakeeyes.blueprints.dto import GeneralDTO
from snakeeyes.blueprints.calendar.models import WorkingPlanRecord, UserWorkingPlan
from bson.objectid import ObjectId
from mongoengine.errors import ValidationError
from snakeeyes.signals import get_signal

general = api.namespace("general", description="general")


@general.route("")
class TestAPI(Resource):
    @general.marshal_with(GeneralDTO)
    def get(self):
        get_signal("sample").send(3)
        return {}, 200
