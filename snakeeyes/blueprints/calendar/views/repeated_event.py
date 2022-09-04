import datetime

from flask_restx import Resource
from snakeeyes.extentions import api
from flask_restx import marshal
from snakeeyes.blueprints.users.models import User
from lib.auth import platform_authorized
from flask import request
from snakeeyes.blueprints.dto import GeneralDTO
from snakeeyes.blueprints.calendar.models import UserRepeatedEvent
from bson.objectid import ObjectId
from mongoengine.errors import ValidationError
from snakeeyes.blueprints.calendar.dto import (
    UserRepeatedEventDTO
)
from snakeeyes.blueprints.calendar.models import UserEvents, UserSingleEvent, Action
from dateutil import parser
from flask_restx import reqparse
import uuid

calendar = api.namespace("calendar", description="calendar")

queries = reqparse.RequestParser()
queries.add_argument("from", type=str, required=False)
queries.add_argument("to", type=str, required=False)


@calendar.route("/<string:user_id>/event/repeated")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
@calendar.response(201, "Created")
class RepeatedEventListAPI(Resource):
    @calendar.expect(UserRepeatedEventDTO, validate=True)
    @calendar.marshal_with(UserRepeatedEventDTO, 200, skip_none=True)
    def post(self, user_id):
        data = marshal(api.payload, UserRepeatedEventDTO)
        repeated = UserRepeatedEvent(
            start_date=parser.parse(data["start_date"]).date(),
            end_date=parser.parse(data["end_date"]).date(),
            day_of_week=data["day_of_week"],
            day_of_month=data["day_of_month"],
            day_of_year=data["day_of_year"],
            start_hour=data["start_hour"],
            duration=data["duration"],
            title=data["title"],
            token=str(uuid.uuid4()),
            actions=[Action(url=a) for a in data["actions"]],
        )
        update_count = UserEvents.objects(user=ObjectId(user_id)).update_one(add_to_set__repeated_events=[repeated])
        if update_count <= 0:
            return {"message": "Events record not found"}, 404
        return repeated, 200

    @calendar.marshal_with(UserRepeatedEventDTO, 200, skip_none=True)
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
        for event in events.repeated_events:
            should_add = True
            if from_dt is not None:
                if (event.start_date is not None and event.start_date < from_dt) and (
                        event.end_date is not None and event.end_date < from_dt):
                    should_add = False
            if to_dt is not None:
                if (event.start_date is not None and event.start_date > to_dt) and (
                        event.end_date is not None and event.end_date > to_dt):
                    should_add = False
            if should_add:
                results.append(event)
        return results, 200

@calendar.route("/<string:user_id>/event/repeated/<string:event_id>")
@calendar.param("user_id", "The user identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
class SingleEventAPI(Resource):
    @calendar.marshal_with(UserRepeatedEventDTO, 200, skip_none=True)
    def get(self, user_id, event_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        results = []
        for event in events.repeated_events:
            if event.token == event_id:
                return event, 200
        return {"message": "Event not found"}, 404

    @calendar.marshal_with(GeneralDTO, 200, skip_none=True)
    def delete(self, user_id, event_id):
        try:
            UserEvents.objects(user=ObjectId(user_id)).update_one(
                pull__repeated_events__token=event_id
            )
        except Exception as e:
            return {"message": e}, 500
        return {"message": "Deleted successfully!"}, 200

    @calendar.marshal_with(UserRepeatedEventDTO, 200, skip_none=True)
    def patch(self, user_id, event_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404
        data = marshal(api.payload, UserRepeatedEventDTO)
        for event in events.repeated_events:
            if event.token == event_id:
                events.repeated_events.remove(event)
                if data["start_date"] != None:
                    event.start_date = data["start_date"]
                if data["end_date"] != None:
                    event.end_date = data["end_date"]
                if data["day_of_week"] != None:
                    event.day_of_week = data["day_of_week"]
                if data["day_of_month"] != None:
                    event.day_of_month = data["day_of_month"]
                if data["day_of_year"] != None:
                    event.day_of_year = data["day_of_year"]
                if data["start_hour"] != None:
                    event.start_hour = data["start_hour"]
                if data["duration"] != None:
                    event.duration = data["duration"]
                if data["title"] != None:
                    event.title = data["title"]
                if data["actions"] != None:
                    event.actions = [Action(url=a) for a in data["actions"]]
                events.repeated_events.append(event)
                events.save()
                return event, 200
        return {"message": "Event not found"}, 404
