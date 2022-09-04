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
)
from snakeeyes.blueprints.calendar.models import UserEvents, UserSingleEvent, Action
from dateutil import parser
from flask_restx import reqparse
import uuid

calendar = api.namespace("calendar", description="calendar")

queries = reqparse.RequestParser()
queries.add_argument("from", type=str, required=False)
queries.add_argument("to", type=str, required=False)


@calendar.route("/<string:user_id>/event/single")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
class SingleEventListAPI(Resource):
    @calendar.expect(UserSingleEventDTO, validate=True)
    @calendar.marshal_with(UserSingleEventDTO, 200, skip_none=True)
    def post(self, user_id):
        data = marshal(api.payload, UserSingleEventDTO)
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        single = UserSingleEvent(
            date=parser.parse(data["date"]).date(),
            start=parser.parse(data["start"]),
            duration=data["duration"],
            title=data["title"],
            token=str(uuid.uuid4()),
            actions=[Action(url=a) for a in data["actions"]],
        )
        events.single_events.append(single)
        events.save()
        return single, 200

    @calendar.marshal_with(UserSingleEventDTO, 200, skip_none=True)
    @calendar.expect(queries)
    def get(self, user_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        from_dt = request.args.get("from", None)
        to_dt = request.args.get("to", None)
        if from_dt is not None:
            from_dt = parser.parse(from_dt).replace(tzinfo=None)
        if to_dt is not None:
            to_dt = parser.parse(to_dt).replace(tzinfo=None)
        results = []
        for event in events.single_events:
            should_add = True
            if from_dt is not None:
                if event.date < from_dt:
                    should_add = False
            if to_dt is not None:
                if event.date > to_dt:
                    should_add = False
            if should_add:
                results.append(event)
        return results, 200


@calendar.route("/<string:user_id>/event/single/<string:event_id>")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
class SingleEventAPI(Resource):
    @calendar.marshal_with(UserSingleEventDTO, 200, skip_none=True)
    @platform_authorized
    def get(self, user_id, event_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        results = []
        for event in events.single_events:
            if event.token == event_id:
                return event, 200
        return {"message": "Event not found"}, 404

    @calendar.marshal_with(GeneralDTO, 200, skip_none=True)
    @platform_authorized
    def delete(self, user_id, event_id):
        try:
            UserEvents.objects(user=ObjectId(user_id)).update_one(
                pull__single_events__token=event_id
            )
        except Exception as e:
            return {"message": e}, 500
        return {"message": "Deleted successfully!"}, 200

    @calendar.marshal_with(UserSingleEventDTO, 200, skip_none=True)
    @platform_authorized
    def patch(self, user_id, event_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        if events is not None:
            event = None
            data = marshal(api.payload, UserSingleEventDTO)
            for e in events.single_events:
                if e.token == event_id:
                    event = e
                    events.single_events.remove(e)
            if event == None:
                return {"message": "Invalid token ID"}, 404
            if data["date"] != None:
                event.date = data["date"]
            if data["start"] != None:
                event.start = data["start"]
            if data["duration"] != None:
                event.duration = data["duration"]
            if data["title"] != None:
                event.title = data["title"]
            if data["actions"] != None:
                event.actions = [Action(url=a) for a in data["actions"]]
            events.single_events.append(event)
            events.save()
        return {"message": "Single event updated"}, 200
