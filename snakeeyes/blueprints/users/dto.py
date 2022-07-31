from snakeeyes.extentions import api
from flask_restx import fields
from snakeeyes.blueprints.dto import GeneralDTO

UserDTO = api.inherit(
    "User",
    GeneralDTO,
    {
        "email": fields.String(required=True, description="User email"),
        "token": fields.String(readonly=True, description="User token"),
        "timezone": fields.String(required=True, description="User timezone"),
    },
)
