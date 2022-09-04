import datetime as dt
from mongoengine import DoesNotExist
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
    UserSingleEventDTO,
)
from snakeeyes.blueprints.calendar.models import UserEvents, UserSingleEvent, Action
from dateutil import parser
from flask_restx import reqparse
import uuid
import pytz
from dateutil import tz

calendar = api.namespace("calendar", description="calendar")

queries = reqparse.RequestParser()
queries.add_argument("from", type=str, required=True)
queries.add_argument("to", type=str, required=True)
queries.add_argument("timezone", type=str, required=True)


@calendar.route("/<string:user_id>/plan")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Plan records cannot intersect")
@calendar.response(200, "Data updated")
class PlanAPI(Resource):
    @calendar.marshal_with(UserPlanDTO, 200, skip_none=True)
    def get(self, user_id):
        try:
            user_id = ObjectId(user_id)
        except Exception:
            return {"message": "Invalid user ID"}, 400

        try:
            user_plan = UserWorkingPlan.objects.get(user=user_id)
        except DoesNotExist:
            return {"message": "User plan not found"}, 400
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

        try:
            user_id = ObjectId(user_id)
        except Exception:
            return {"message": "Invalid user ID"}, 400

        try:
            user_plan = UserWorkingPlan.objects.get(user=user_id)
        except DoesNotExist:
            return {"message": "User plan not found"}, 400
        user_plan.plan = plan.plan

        response = dict()
        try:
            user_plan.save()
            response["message"] = "Data updated"
        except ValidationError as e:
            response["message"] = e.errors["__all__"]
            return response, 400
        return response, 200

@calendar.route("/<string:user_id>/plan/records")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Plan records cannot intersect")
@calendar.response(200, "Data updated")
class PlanRecordAPI(Resource):
    @calendar.expect(queries)
    def get(self, user_id):
        try:
            user_id = ObjectId(user_id)
        except Exception:
            return {"message": "Invalid user ID"}, 400

        from_dt = request.args.get("from", None)
        to_dt = request.args.get("to", None)
        given_timezone = request.args.get("timezone", None)
        if from_dt is None or to_dt is None or given_timezone is None:
            return {"message": "from_dt, to_dt and timezone should be provided"}, 400
        from_dt = parser.parse(from_dt).replace(tzinfo=None)
        to_dt = parser.parse(to_dt).replace(tzinfo=None)
        try:
            user_plan = UserWorkingPlan.objects.get(user=user_id)
        except DoesNotExist:
            return {"message": "User plan not found"}, 400

        user_timezone = tz.gettz(user_plan.user.timezone)

        start_dt = from_dt
        start_dt -= dt.timedelta(days=1)
        res = []
        while start_dt <= to_dt:
            start_dt += dt.timedelta(days=1)
            if str(start_dt.weekday()) in user_plan.plan and len(user_plan.plan[str(start_dt.weekday())]) > 0:
                for p in user_plan.plan[str(start_dt.weekday())]:
                    final = start_dt + dt.timedelta(seconds=p.from_hour)
                    final = final.replace(tzinfo=user_timezone)
                    final = final.astimezone(pytz.timezone(given_timezone))
                    res.append(final)
        response = {}
        for r in res:
            if str(r.date()) not in response:
                response[str(r.date())] = []
            response[str(r.date())].append({"dt": str(r), "taken": False})
        return response, 200
