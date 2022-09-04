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
    UserSingleEventDTO,
    UserEventDTO,
)
from snakeeyes.blueprints.calendar.models import UserEvents, UserSingleEvent, Action
from dateutil import parser
from flask_restx import reqparse
import uuid
import datetime as dt

calendar = api.namespace("calendar", description="calendar")

queries = reqparse.RequestParser()
queries.add_argument("from", type=str, required=False)
queries.add_argument("to", type=str, required=False)


@calendar.route("/<string:user_id>/events")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
class ListEventsAPI(Resource):
    @calendar.marshal_with(UserEventDTO, 200, skip_none=True)
    @calendar.expect(queries)
    def get(self, user_id):
        from_dt = request.args.get("from", None)
        to_dt = request.args.get("to", None)
        if from_dt is not None:
            from_dt = parser.parse(from_dt).replace(tzinfo=None)
        if to_dt is not None:
            to_dt = parser.parse(to_dt).replace(tzinfo=None)
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        results = []
        single_events = events.single_events
        for template in events.templates:
            if template.is_active is False:
                continue
            if template.single_events:
                single_events.extend(template.single_events)
        for e in single_events:
            if from_dt is not None and e.date < from_dt:
                continue
            if to_dt is not None and e.date > to_dt:
                continue
            results.append({
                "date": e.date,
                "start": e.start,
                "duration": e.duration,
                "title": e.title,
                "token": e.token,
                "actions": e.actions,
                "type": "single",
            })
        repeated_events = events.repeated_events
        for template in events.templates:
            if template.is_active is False:
                continue
            if template.repeated_events:
                repeated_events.extend(template.repeated_events)
        for e in repeated_events:
            dates = e.get_dates()
            for d in dates:
                if from_dt is not None and d < from_dt:
                    continue
                if to_dt is not None and d > to_dt:
                    continue
                results.append({
                    "date": d,
                    "start": d + dt.timedelta(seconds=e.start_hour),
                    "duration": e.duration,
                    "title": e.title,
                    "token": e.token,
                    "actions": e.actions,
                    "type": "repeated",
                })
        return results, 200
