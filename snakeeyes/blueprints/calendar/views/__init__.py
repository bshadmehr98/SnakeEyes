from snakeeyes.extentions import api
from snakeeyes.blueprints.calendar.views.plan import PlanAPI
from snakeeyes.blueprints.calendar.views.single_event import (
    SingleEventListAPI,
    SingleEventAPI,
)
from snakeeyes.blueprints.calendar.views.events import ListEventsAPI
from snakeeyes.blueprints.calendar.views import repeated_event
from snakeeyes.blueprints.calendar.views import template

calendar = api.namespace("calendar", description="calendar")
