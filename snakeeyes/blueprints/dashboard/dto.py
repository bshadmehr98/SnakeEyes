from snakeeyes.extentions import api
from flask_restx import fields
from snakeeyes.blueprints.dto import GeneralDTO

AuthDTO = api.inherit(
    "Token",
    GeneralDTO,
    {
        "access_token": fields.String(readonly=True, description="Access Token"),
    },
)

DashboardUserDTO = api.inherit(
    "DashboardUser",
    GeneralDTO,
    {
        "email": fields.String(required=True, description="Access Token"),
        "raw_password": fields.String(description="Refresh Token"),
        "role": fields.String(readonly=True, description="Role"),
    },
)
