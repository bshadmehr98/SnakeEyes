from snakeeyes.extentions import db
import uuid
from mongoengine.queryset.visitor import Q
import secrets
import bcrypt


class Platform(db.Document):
    name = db.StringField(unique=True)
    token = db.StringField(required=True)
    secret = db.StringField(required=True)
    active = db.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
            secret = self.secret.encode("utf-8")

            salt = bcrypt.gensalt()
            self.secret = bcrypt.hashpw(secret, salt).decode()

        return super(Platform, self).save(*args, **kwargs)

    def check_secret(self, secret):
        return bcrypt.checkpw(secret.encode("utf-8"), self.secret.encode("utf-8"))
