import datetime

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
from snakeeyes.blueprints.calendar.dto import (
    UserPlanDTO,
    UserPlanValidateRequestDTO,
    UserSingleEventDTO,
)
from snakeeyes.blueprints.calendar.models import UserEvents, UserSingleEvent, Action
from dateutil import parser
from flask_restx import reqparse
import uuid

calendar = api.namespace("calendar", description="calendar")


@calendar.route("/<string:user_id>/plan")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Plan records cannot intersect")
@calendar.response(200, "Data updated")
class PlanAPI(Resource):
    @calendar.marshal_with(UserPlanDTO, 200, skip_none=True)
    def get(self, user_id):
        user_plan = UserWorkingPlan.objects.get(user=ObjectId(user_id))
        return user_plan.plan, 200

    @calendar.expect(UserPlanDTO, validate=True)
    @calendar.marshal_with(GeneralDTO, 200, skip_none=True)
    def post(self, user_id):
        data = marshal(api.payload, UserPlanDTO)
        plan = UserWorkingPlan()
        for day in data:
            if data[day] is None:
                continue
            plan.plan[day] = []
            for record in data[day]:
                plan.plan[day].append(
                    WorkingPlanRecord(
                        from_hour=record["from_hour"], to_hour=record["to_hour"]
                    )
                )

        user_plan = UserWorkingPlan.objects.get(user=ObjectId(user_id))
        user_plan.plan = plan.plan

        response = dict()
        try:
            user_plan.save()
            response["message"] = "Data updated"
        except ValidationError:
            response["message"] = "Plan records cannot intersect"
            return response, 400
        return response, 200


@calendar.route("/plan/<string:user_id>/validate")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Data not valid")
@calendar.response(200, "Data is valid")
class PlanValidateAPI(Resource):
    @calendar.expect(UserPlanValidateRequestDTO, validate=True)
    @calendar.marshal_with(GeneralDTO, 200, skip_none=True)
    def post(self, user_id):
        data = marshal(api.payload, UserPlanDTO)
        plan = UserWorkingPlan()
        for day in data:
            if data[day] is None:
                continue
            plan.plan[day] = []
            for record in data[day]:
                plan.plan[day].append(
                    WorkingPlanRecord(
                        from_hour=record["from_hour"], to_hour=record["to_hour"]
                    )
                )

        user_plan = UserWorkingPlan.objects.get(user=ObjectId(user_id))
        user_plan.plan = plan.plan

        response = dict()
        try:
            user_plan.save()
            response["message"] = "Data updated"
        except ValidationError:
            response["message"] = "Plan records cannot intersect"
            return response, 400
        return response, 200
