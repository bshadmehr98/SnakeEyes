from snakeeyes.extentions import api
from flask_restx import fields


GeneralDTO = api.model(
    "General",
    {
        "message": fields.String(readonly=True, description="API message"),
    },
)
