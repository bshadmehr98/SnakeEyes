from snakeeyes.signals import connect_signal
from snakeeyes.blueprints.calendar.models import UserWorkingPlan, UserEvents


@connect_signal("initiate-user-data")
def initiate_user_data(user):
    try:
        UserWorkingPlan(user=user).save()
        UserEvents(user=user).save()
    except Exception:
        user.error_in_initiating_user = True
        user.save()
