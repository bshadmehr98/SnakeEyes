import mongoengine
from snakeeyes.extentions import db
import uuid
from mongoengine.queryset.visitor import Q
from snakeeyes.blueprints.platforms.models import Platform
from datetime import timezone as tz
import pytz
from snakeeyes.signals import get_signal
from mongoengine import queryset

mongoengine.ReferenceField


class User(db.Document):
    ROLES_ADMIN = "A"
    ROLES_MEMBER = "M"
    ROLES = ((ROLES_ADMIN, "Admin"), (ROLES_MEMBER, "Member"))

    email = db.StringField(unique=True)
    username = db.StringField(unique_with="email")
    role = db.StringField(max_length=3, choices=ROLES, default=ROLES_MEMBER)
    platform = db.ReferenceField(Platform, reverse_delete_rule=queryset.NULLIFY)
    token = db.StringField(required=True)
    active = db.BooleanField(default=True)
    timezone = db.StringField(required=True, default=tz.utc)
    token_history = db.ListField(db.StringField())
    error_in_initiating_user = db.BooleanField(default=False)

    def save(self, *args, **kwargs):
        get_signal("user-model-before-save").send(self)
        should_initiate = False
        if not self.token:
            self.token = str(uuid.uuid4())
            should_initiate = True

        response = super(User, self).save(*args, **kwargs)
        if should_initiate:
            get_signal("initiate-user-data").send(self)
        return response

    @classmethod
    def find_by_identity(cls, identity):
        return User.objects(Q(email=identity) | Q(username=identity)).first()

    @classmethod
    def get_or_create(cls, email, platform=None, timezone=None):
        user = cls.find_by_identity(email)
        if user is not None:
            return user, False
        user = cls(email=email, platform=platform)
        if timezone is not None:
            user.timezone = timezone
        user.save()
        return user, True

    @classmethod
    def get_new_token(cls):
        return str(uuid.uuid4())

    def regenerate_token(self):
        self.token_history.append(self.token)
        self.token = str(uuid.uuid4())
        self.save()
