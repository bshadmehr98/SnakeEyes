from snakeeyes.extentions import api
from snakeeyes.blueprints.calendar.views.plan import PlanAPI, PlanValidateAPI
from snakeeyes.blueprints.calendar.views.single_event import (
    SingleEventListAPI,
    SingleEventAPI,
)
from snakeeyes.blueprints.calendar.views import repeated_event

calendar = api.namespace("calendar", description="calendar")
