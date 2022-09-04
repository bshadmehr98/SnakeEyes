from xmlrpc.client import Boolean
from snakeeyes.extentions import api
from flask_restx import fields
from snakeeyes.blueprints.dto import GeneralDTO

PlanRecordlDTO = api.model(
    "PlanRecord",
    {
        "from_hour": fields.Integer(description="Start"),
        "to_hour": fields.Integer(description="End"),
    },
)

UserPlanDTO = api.inherit(
    "UserPlan",
    GeneralDTO,
    {
        "0": fields.List(fields.Nested(PlanRecordlDTO)),
        "1": fields.List(fields.Nested(PlanRecordlDTO)),
        "2": fields.List(fields.Nested(PlanRecordlDTO)),
        "3": fields.List(fields.Nested(PlanRecordlDTO)),
        "4": fields.List(fields.Nested(PlanRecordlDTO)),
        "5": fields.List(fields.Nested(PlanRecordlDTO)),
        "6": fields.List(fields.Nested(PlanRecordlDTO)),
    },
)

UserEventValidateRequestDTO = api.inherit(
    "UserEventValidateRequestDTO",
    GeneralDTO,
    {
        "start": fields.Integer(description="Start"),
        "end": fields.Integer(description="End"),
    },
)

UserSingleEventDTO = api.inherit(
    "UserSingleEvent",
    GeneralDTO,
    {
        "date": fields.DateTime(required=True, description="Date"),
        "start": fields.DateTime(required=True, description="Start"),
        "duration": fields.Integer(required=True, description="Duration in seconds"),
        "title": fields.String(required=True, description="Title"),
        "token": fields.String(readonly=True, description="Token"),
        "actions": fields.List(fields.String(), required=True, description="actions"),
    },
)

UserRepeatedEventDTO = api.inherit(
    "UserRepeatedEvent",
    GeneralDTO,
    {
        "start_date": fields.DateTime(required=True, description="Start Date"),
        "end_date": fields.DateTime(required=True, description="End Date"),
        "day_of_week": fields.List(fields.Integer(min=0, max=6), description="Day Of Week"),
        "day_of_month": fields.List(fields.Integer(min=0, max=30), description="Day Of Month"),
        "day_of_year": fields.List(fields.Integer(min=0, max=355), description="Day Of Year"),
        "start_hour": fields.Integer(required=True, description="Start Hour"),
        "duration": fields.Integer(required=True, description="Duration"),
        "title": fields.String(required=True, description="Title"),
        "token": fields.String(readonly=True, description="Token"),
        "actions": fields.List(fields.String(), required=True, description="actions"),
    },
)

UserEventDTO = api.inherit(
    "UserEventDTO",
    GeneralDTO,
    {
        "date": fields.DateTime(required=True, description="Date"),
        "start": fields.DateTime(required=True, description="Start"),
        "duration": fields.Integer(required=True, description="Duration in seconds"),
        "title": fields.String(required=True, description="Title"),
        "token": fields.String(readonly=True, description="Token"),
        "actions": fields.List(fields.String(), required=True, description="actions"),
        "type": fields.String(readonly=True, description="Type"),
    },
)

EventTemplateDTO = api.inherit(
    "EventTemplateDTO",
    GeneralDTO,
    {
        "id": fields.String(readonly=True, description="Template id"),
        "is_active": fields.Boolean(required=True, description="Is Active"),
        "token": fields.String(readonly=True, description="Token"),
        "single_events": fields.List(fields.Nested(UserSingleEventDTO), required=False, description="Single Events"),
        "repeated_events": fields.List(fields.Nested(UserRepeatedEventDTO), required=False, description="Single Events"),
    },
)
