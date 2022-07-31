import mongoengine
from snakeeyes.extentions import db
import uuid
from mongoengine.queryset.visitor import Q
from snakeeyes.blueprints.users.models import User
import itertools
from mongoengine.errors import ValidationError

mongoengine.EmbeddedDocumentListField


class WorkingPlanRecord(db.EmbeddedDocument):
    from_hour = db.IntField()
    to_hour = db.IntField()


class UserWorkingPlan(db.Document):
    user = db.ReferenceField(User, unique=True)
    plan = db.MapField(db.EmbeddedDocumentListField(WorkingPlanRecord))

    def clean(self):
        for day in self.plan:
            records = self.plan[day]
            ranges = [range(r.from_hour, r.to_hour) for r in records]
            for comb in itertools.combinations(ranges, 2):
                intersection = set(comb[0]).intersection(comb[1])
                if intersection:
                    raise ValidationError("Values intersect.")


class Action(db.EmbeddedDocument):
    url = db.StringField()

    def __str__(self):
        return self.url


class UserSingleEvent(db.EmbeddedDocument):
    date = db.DateTimeField()
    start = db.DateTimeField()
    duration = db.IntField()
    title = db.StringField()
    token = db.StringField(required=True)
    actions = db.EmbeddedDocumentListField(Action)


class UserRepeatedEvent(db.EmbeddedDocument):
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    day_of_week = db.ListField(db.IntField())
    day_of_month = db.ListField(db.IntField())
    day_of_year = db.ListField(db.IntField())
    start_hour = db.IntField()
    duration = db.IntField()
    title = db.StringField()
    token = db.StringField(required=True)
    actions = db.EmbeddedDocumentListField(Action)


class UserEvents(db.Document):
    user = db.ReferenceField(User, unique=True)
    single_events = db.EmbeddedDocumentListField(UserSingleEvent)
    repeated_events = db.EmbeddedDocumentListField(UserRepeatedEvent)


class EventTemplate(db.Document):
    is_active = db.Bool
    single_events = db.EmbeddedDocumentListField(UserSingleEvent)
    repeated_events = db.EmbeddedDocumentListField(UserRepeatedEvent)
