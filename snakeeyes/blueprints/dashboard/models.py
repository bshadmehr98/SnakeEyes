from snakeeyes.extentions import db
import uuid
from mongoengine.queryset.visitor import Q
import bcrypt


class DashboardUser(db.Document):
    ROLES_ADMIN = "A"
    ROLES_MEMBER = "M"
    ROLES = ((ROLES_ADMIN, "Admin"), (ROLES_MEMBER, "Member"))

    email = db.StringField(unique=True)
    password = db.StringField()
    role = db.StringField(max_length=3, choices=ROLES, default=ROLES_MEMBER)


    @classmethod
    def get_or_create(cls, email, password):
        user = DashboardUser.objects(email=email).first()
        if user is not None:
            return user, False
        salt = bcrypt.gensalt()
        hashed_pass = bcrypt.hashpw(password.encode("utf-8"), salt).decode()
        user = cls(email=email, password=hashed_pass)
        user.save()
        return user, True

    def check_secret(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
