import datetime
from platform import platform

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
    EventTemplateDTO
)
from snakeeyes.blueprints.calendar.models import UserRepeatedEvent, UserSingleEvent, EventTemplate, Action, UserEvents
from dateutil import parser
from flask_restx import reqparse
import uuid
from mongoengine import queryset

calendar = api.namespace("calendar", description="calendar")

queries = reqparse.RequestParser()
queries.add_argument("from", type=str, required=False)
queries.add_argument("to", type=str, required=False)


@calendar.route("/template")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
@calendar.response(201, "Created")
class EventTemplateListAPI(Resource):
    @calendar.expect(EventTemplateDTO, validate=True)
    @calendar.marshal_with(EventTemplateDTO, 200, skip_none=True)
    @platform_authorized
    def post(self):
        data = marshal(api.payload, EventTemplateDTO)
        token=str(uuid.uuid4())
        for event in data["single_events"]:
            event["actions"] = [Action(url=a) for a in event["actions"]]
            event["token"] = token
            del event["message"]
        for event in data["repeated_events"]:
            event["actions"] = [Action(url=a) for a in event["actions"]]
            event["token"] = token
            del event["message"]
        event = EventTemplate(
            is_active=True,
            platform=request.platform,
            token=token,
            single_events=data["single_events"],
            repeated_events=data["repeated_events"],
        )
        event.save()
        return event, 200

@calendar.route("/template/<string:template_id>")
@calendar.param("template_id", "The template identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
@calendar.response(201, "Created")
class EventTemplateAPI(Resource):
    @platform_authorized
    def delete(self, template_id):
        try:
            template = EventTemplate.objects.get(id=ObjectId(template_id))
        except Exception as e:
            return {"message": "EventTemplate record not found"}, 404

        template.delete()
        return {}, 200

    @platform_authorized
    @calendar.marshal_with(EventTemplateDTO, 200, skip_none=True)
    def get(self, template_id):
        try:
            template = EventTemplate.objects.get(id=ObjectId(template_id))
        except Exception as e:
            return {"message": "EventTemplate record not found"}, 404

        return template, 200

    @calendar.expect(EventTemplateDTO, validate=True)
    @calendar.marshal_with(EventTemplateDTO, 200, skip_none=True)
    @platform_authorized
    def put(self, template_id):
        try:
            template = EventTemplate.objects.get(id=ObjectId(template_id))
        except Exception as e:
            return {"message": "EventTemplate record not found"}, 404
        data = marshal(api.payload, EventTemplateDTO)
        for event in data["single_events"]:
            event["actions"] = [Action(url=a) for a in event["actions"]]
            event["token"] = template.token
            del event["message"]
        for event in data["repeated_events"]:
            event["actions"] = [Action(url=a) for a in event["actions"]]
            event["token"] = template.token
            del event["message"]
        template.is_active=data["is_active"]
        template.single_events = [UserSingleEvent(**e) for e in data["single_events"]]
        template.repeated_events = [UserRepeatedEvent(**e) for e in data["repeated_events"]]
        template.save()
        return template, 200



@calendar.route("/template/<string:user_id>/<string:template_id>/")
@calendar.param("user_id", "The user identifier")
@calendar.param("template_id", "The template identifier")
@calendar.response(400, "Bad Request")
@calendar.response(200, "Data updated")
@calendar.response(201, "Created")
class UserEventTemplateAPI(Resource):
    @calendar.marshal_with(EventTemplateDTO, 200, skip_none=True)
    @platform_authorized
    def post(self, user_id, template_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404

        try:
            template = EventTemplate.objects.get(id=ObjectId(template_id))
        except Exception as e:
            return {"message": "EventTemplate record not found"}, 404

        if template not in events.templates:
            events.templates.append(template)
            events.save()
        return {}, 200


    @calendar.marshal_with(EventTemplateDTO, 200, skip_none=True)
    @platform_authorized
    def delete(self, user_id, template_id):
        try:
            events = UserEvents.objects.get(user=ObjectId(user_id))
        except Exception as e:
            return {"message": "Events record not found"}, 404

        try:
            template = EventTemplate.objects.get(id=ObjectId(template_id))
        except Exception as e:
            return {"message": "EventTemplate record not found"}, 404

        if template in events.templates:
            events.templates.remove(template)
            events.save()
        return {}, 200
