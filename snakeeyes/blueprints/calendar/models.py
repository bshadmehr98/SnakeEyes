import mongoengine
from snakeeyes.extentions import db
import uuid
from mongoengine.queryset.visitor import Q
from snakeeyes.blueprints.users.models import User
import itertools
from mongoengine.errors import ValidationError
import datetime as dt
from mongoengine import queryset


class WorkingPlanRecord(db.EmbeddedDocument):
    from_hour = db.IntField()
    to_hour = db.IntField()


class UserWorkingPlan(db.Document):
    user = db.ReferenceField(User, unique=True)
    plan = db.MapField(db.EmbeddedDocumentListField(WorkingPlanRecord))

    def clean(self):
        for day in self.plan:
            records = self.plan[day]
            for r in records:
                if r.from_hour < 0 or r.to_hour < 0:
                    raise ValidationError("Hour cant be less than 0")
                if r.from_hour > r.to_hour:
                    raise ValidationError("Start hour should be before end hour")
            ranges = [range(r.from_hour, r.to_hour) for r in records]
                
            for comb in itertools.combinations(ranges, 2):
                intersection = set(comb[0]).intersection(comb[1])
                if intersection:
                    raise ValidationError("Plan records cannot intersect")


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

    def get_dates(self):
        results = []
        d = self.start_date
        d -= dt.timedelta(days=1)
        while d <= self.end_date:
            d += dt.timedelta(days=1)
            if self.day_of_week:
                if d.timetuple().tm_wday not in self.day_of_week:
                    continue
            if self.day_of_month:
                if d.timetuple().tm_mday not in self.day_of_week:
                    continue
            if self.day_of_year:
                if d.timetuple().tm_yday not in self.day_of_week:
                    continue
            results.append(d)
        return results


class EventTemplate(db.Document):
    is_active = db.BooleanField()
    token = db.StringField(required=True)
    platform = db.ReferenceField("Platform", reverse_delete_rule=queryset.NULLIFY)
    single_events = db.EmbeddedDocumentListField(UserSingleEvent)
    repeated_events = db.EmbeddedDocumentListField(UserRepeatedEvent)


class UserEvents(db.Document):
    user = db.ReferenceField(User, unique=True)
    single_events = db.EmbeddedDocumentListField(UserSingleEvent)
    repeated_events = db.EmbeddedDocumentListField(UserRepeatedEvent)
    templates = db.ListField(db.ReferenceField(EventTemplate, reverse_delete_rule=queryset.PULL))
